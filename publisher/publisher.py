import argparse
import datetime
import git
import inflection
import os
import pytz
import re
import shlex
import shutil
import yaml
import titlecase
from PIL import Image
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description="Preprocess Obsidian-generated Markdown files for compatibility with the customized TeXify3 Hugo theme by converting 'tags' YAML to 'topics' and appending file creation & publishing date metadata to the YAML header.")
    parser.add_argument("--dest", help="Destination directory | Usually the Hugo content/blog directory.", required=True)
    parser.add_argument("--idest", help="Destination directory to place compressed images | Usually the Hugo static/images directory.", required=True)
    parser.add_argument("--imgdirs", nargs="+", help="Source directories to get image files from.", required=True)
    parser.add_argument("--source", nargs="+", help="Source markdown files.", required=True)
    args = parser.parse_args()
    
    if not os.path.isdir(args.dest):
    	parser.error(f'The destination directory "{args.dest}" is not a valid directory.')

    if not os.path.isdir(args.idest):
    	parser.error(f'The images destination directory "{args.idest}" is not a valid directory.')

    is_markdown_file = lambda file_path: os.path.isfile(file_path) and file_path.endswith('.md')
    invalid_sources = [src_path for src_path in args.source if not is_markdown_file(src_path)]
    if invalid_sources:
    	parser.error(f'The following files are not valid Markdown files:\n{"\n".join(invalid_sources)}')
    invalid_idirs = [src_dir for src_dir in args.imgdirs if not os.path.isdir(src_dir)]
    if invalid_idirs:
    	parser.error(f'The following source directories are not valid:\n{"\n".join(invalid_idirs)}')

    return args.source, args.dest, args.imgdirs, args.idest

def get_date_of_creation(file_path):
	file_path = os.path.abspath(file_path)
	repo = git.Repo(file_path, search_parent_directories=True)
	log = repo.git.log("--follow", "--format=%ad", "--", file_path)
	if not log:
		local_timezone = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
		dt = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
		return dt.replace(tzinfo=local_timezone).strftime('%Y-%m-%d %H:%M:%S%z')
	else:
		return datetime.datetime.strptime(log.split('\n')[-1], '%a %b %d %H:%M:%S %Y %z')

def optimize_image(src_path, dst_dir, base_name, max_width=1920, webp_quality=85, png_optimize=True):
	"""
	Optimize an image for web display:
	- Resize if width > max_width (default 1920px for retina displays)
	- Convert to WebP at specified quality (default 85%)
	- Also save optimized PNG as fallback
	- Maintains aspect ratio

	Returns: tuple of (webp_path, png_path)
	"""
	try:
		with Image.open(src_path) as img:
			original_mode = img.mode
			width, height = img.size

			if width > max_width:
				ratio = max_width / width
				new_width = max_width
				new_height = int(height * ratio)
				img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
				print(f"  Resized {os.path.basename(src_path)} from {width}x{height} to {new_width}x{new_height}")

			webp_path = os.path.join(dst_dir, base_name + '.webp')
			png_path = os.path.join(dst_dir, base_name + '.png')

			# WebP compresses better without alpha channel, so flatten to white background
			if original_mode in ('RGBA', 'LA'):
				webp_img = Image.new('RGB', img.size, (255, 255, 255))
				if img.mode == 'RGBA':
					webp_img.paste(img, mask=img.split()[3])
				else:
					webp_img.paste(img)
				webp_img.save(webp_path, 'WEBP', quality=webp_quality, method=6)
			else:
				rgb_img = img.convert('RGB')
				rgb_img.save(webp_path, 'WEBP', quality=webp_quality, method=6)

			# PNG fallback preserves transparency for older browsers
			if png_optimize:
				img.save(png_path, 'PNG', optimize=True)
			else:
				img.save(png_path, 'PNG')

			original_size = os.path.getsize(src_path)
			webp_size = os.path.getsize(webp_path)
			png_size = os.path.getsize(png_path)
			savings = ((original_size - webp_size) / original_size) * 100

			print(f"  Optimized {os.path.basename(src_path)}: {original_size//1024}KB → WebP: {webp_size//1024}KB, PNG: {png_size//1024}KB ({savings:.1f}% savings)")

			return webp_path, png_path

	except Exception as e:
		print(f"  Warning: Could not optimize {src_path}: {str(e)}")
		print(f"  Falling back to simple copy")
		fallback_path = os.path.join(dst_dir, base_name + os.path.splitext(src_path)[1])
		shutil.copy2(src_path, fallback_path)
		return fallback_path, fallback_path

def process_file(src_path, dst_dir, img_dirs, idst_dir):
	try:
		# Declare useful util fns / metadata
		split_yaml_header = lambda content: ("", content) if content[0:3] != '---' else content.split('---\n', 2)[1:]
		filename = os.path.splitext(os.path.basename(src_path))[0]
		image_deps = set()

		# Read & Parse source file
		with open(src_path, 'r') as file:
			contents = file.read()
		header, content = split_yaml_header(contents)
		
		# Parse & construct updated header
		header = yaml.safe_load(header) if header else {}
		header['topics'] = header.pop('tags') if 'tags' in header else []
		if 'date' not in header:
			header['date'] = datetime.datetime.now(datetime.timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S%z')
		header['doc'] = get_date_of_creation(src_path)
		header['title'] = titlecase.titlecase(filename).replace(';', ':')
		header['author'] = 'Kishore Kumar'

		# Parse & construct updated contents
		def handle_wikilink(name):
			return f'[{name}](/blog/{inflection.parameterize(name)})'

		def handle_image(name, deps):
			deps.add(name)
			basename, ext = os.path.splitext(os.path.basename(name))
			# Reference .webp in markdown (Hugo render hook will handle fallback)
			return f'![{basename}](/images/{inflection.parameterize(basename)}.webp)\n'

		content = re.sub(r'!\[\[(.*?)\]\]', lambda match: handle_image(match.group(1), image_deps), content)	
		content = re.sub(r'\[\[(.*?)\]\]', lambda match: handle_wikilink(match.group(1)), content)

		# Sync images folder with unsatisfied dependencies and compress
		image_src_paths = []
		for d in img_dirs:
			satisfied = set()
			for root, _, files in os.walk(d):
				for imgname in image_deps:
					if imgname in files:
						satisfied.add(imgname)
						image_src_paths.append(os.path.join(root, imgname))
			image_deps = image_deps - satisfied
		
		if image_deps:
			raise ValueError(f'Given source directories for image files do not contain the following required image dependencies:\n{"\n".join(image_deps)}')

		for img in image_src_paths:
			imgname, ext = os.path.splitext(os.path.basename(img))
			parameterized_name = inflection.parameterize(imgname)
			optimize_image(img, idst_dir, parameterized_name)

		# Write updated file
		with open(os.path.join(dst_dir, inflection.parameterize(filename) + ".md"), 'w') as file:
			file.write('---\n' + yaml.dump(header) + '---\n')
			file.write(content)

		print(f"Successfully processed {src_path} and saved to {dst_dir}")
	except Exception as e:
		print(f"Error processing {src_path}: {str(e)}\n")

def main():
	source_files, dst_dir, img_dirs, idst_dir = parse_args()
	for src_path in source_files:
		process_file(src_path, dst_dir, img_dirs, idst_dir)

if __name__ == '__main__':
    main()
