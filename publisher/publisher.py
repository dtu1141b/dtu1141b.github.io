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
		header['title'] = titlecase.titlecase(filename)
		header['author'] = 'Kishore Kumar'

		# Parse & construct updated contents
		def handle_wikilink(name):
			return f'[{name}](/blog/{inflection.parameterize(name)})'

		def handle_image(name, deps):
			deps.add(name)
			basename, ext = os.path.splitext(os.path.basename(name))
			return f'![{basename}](/images/{inflection.parameterize(basename) + ext})\n'

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
			shutil.copy2(img, os.path.join(idst_dir, inflection.parameterize(imgname) + ext))

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
