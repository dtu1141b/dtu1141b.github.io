#!/usr/bin/env python3
"""
Batch optimize all existing images in the Hugo static/images directory.
This script processes existing images to WebP format with PNG fallback.
"""

import os
import shutil
from pathlib import Path
from PIL import Image
from datetime import datetime


def optimize_image(src_path, dst_dir, base_name, max_width=1920, webp_quality=85, png_optimize=True):
    """
    Optimize an image for web display:
    - Resize if width > max_width (default 1920px for retina displays)
    - Convert to WebP at specified quality (default 85%)
    - Also save optimized PNG as fallback
    - Maintains aspect ratio

    Returns: tuple of (webp_path, png_path, stats_dict)
    """
    try:
        with Image.open(src_path) as img:
            original_mode = img.mode
            width, height = img.size
            original_size = os.path.getsize(src_path)

            resized = False
            if width > max_width:
                ratio = max_width / width
                new_width = max_width
                new_height = int(height * ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                resized = True
                resize_info = f"{width}x{height} → {new_width}x{new_height}"
            else:
                resize_info = f"{width}x{height} (no resize)"

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

            webp_size = os.path.getsize(webp_path)
            png_size = os.path.getsize(png_path)
            savings = ((original_size - webp_size) / original_size) * 100

            stats = {
                'original_size': original_size,
                'webp_size': webp_size,
                'png_size': png_size,
                'savings_percent': savings,
                'resized': resized,
                'resize_info': resize_info
            }

            return webp_path, png_path, stats

    except Exception as e:
        print(f"  ❌ Error optimizing {src_path}: {str(e)}")
        return None, None, None


def main():
    # Configuration
    images_dir = Path('/home/akcube/akcube.github.io/static/images')
    backup_dir = images_dir / 'backup'

    print("=" * 80)
    print("Batch Image Optimization Script")
    print("=" * 80)
    print(f"\nSource directory: {images_dir}")
    print(f"Backup directory: {backup_dir}")

    # Create backup directory
    if not backup_dir.exists():
        backup_dir.mkdir(parents=True)
        print(f"\n✓ Created backup directory: {backup_dir}")
    else:
        print(f"\n✓ Backup directory exists: {backup_dir}")

    # Find all image files
    image_extensions = {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp'}
    image_files = []

    for file in images_dir.iterdir():
        if file.is_file() and file.suffix.lower() in image_extensions:
            # Skip if it's in the backup directory
            if 'backup' not in str(file):
                image_files.append(file)

    print(f"\n✓ Found {len(image_files)} images to process")

    # Confirm before proceeding
    print("\n" + "=" * 80)
    print("WARNING: This will:")
    print("  1. Backup original images to static/images/backup/")
    print("  2. Replace originals with optimized WebP + PNG versions")
    print("  3. Images already optimized will be processed again")
    print("=" * 80)

    response = input("\nDo you want to proceed? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("\n❌ Operation cancelled by user")
        return

    # Process images
    print("\n" + "=" * 80)
    print("Processing Images")
    print("=" * 80 + "\n")

    total_stats = {
        'processed': 0,
        'failed': 0,
        'total_original_size': 0,
        'total_webp_size': 0,
        'total_png_size': 0,
        'resized_count': 0
    }

    for idx, img_file in enumerate(image_files, 1):
        print(f"[{idx}/{len(image_files)}] Processing: {img_file.name}")

        # Backup original
        backup_path = backup_dir / img_file.name
        if not backup_path.exists():
            shutil.copy2(img_file, backup_path)
            print(f"  ✓ Backed up to: {backup_path.name}")
        else:
            print(f"  ℹ Already backed up: {backup_path.name}")

        # Get base name without extension
        base_name = img_file.stem

        # Optimize
        webp_path, png_path, stats = optimize_image(
            str(img_file),
            str(images_dir),
            base_name
        )

        if stats:
            print(f"  ✓ Original: {stats['original_size']//1024}KB")
            print(f"  ✓ WebP: {stats['webp_size']//1024}KB ({stats['savings_percent']:.1f}% savings)")
            print(f"  ✓ PNG: {stats['png_size']//1024}KB")
            print(f"  ✓ Dimensions: {stats['resize_info']}")

            # Delete original file only if it's not one of our newly created files
            # The newly created files are: base_name.webp and base_name.png
            newly_created = {f"{base_name}.webp", f"{base_name}.png"}
            if img_file.name not in newly_created:
                # This is the original file with a different extension (e.g., .jpg)
                # Delete it since we've created optimized versions
                try:
                    img_file.unlink()
                    print(f"  ✓ Removed original: {img_file.name}")
                except FileNotFoundError:
                    pass  # Already deleted or never existed

            total_stats['processed'] += 1
            total_stats['total_original_size'] += stats['original_size']
            total_stats['total_webp_size'] += stats['webp_size']
            total_stats['total_png_size'] += stats['png_size']
            if stats['resized']:
                total_stats['resized_count'] += 1
        else:
            total_stats['failed'] += 1

        print()

    # Print summary
    print("=" * 80)
    print("Optimization Summary")
    print("=" * 80)
    print(f"\n✓ Successfully processed: {total_stats['processed']} images")
    print(f"✗ Failed: {total_stats['failed']} images")
    print(f"↕ Resized: {total_stats['resized_count']} images")
    print(f"\nStorage:")
    print(f"  Original total: {total_stats['total_original_size']//1024//1024}MB ({total_stats['total_original_size']//1024}KB)")
    print(f"  WebP total: {total_stats['total_webp_size']//1024//1024}MB ({total_stats['total_webp_size']//1024}KB)")
    print(f"  PNG total: {total_stats['total_png_size']//1024//1024}MB ({total_stats['total_png_size']//1024}KB)")

    if total_stats['total_original_size'] > 0:
        webp_savings = ((total_stats['total_original_size'] - total_stats['total_webp_size']) / total_stats['total_original_size']) * 100
        png_savings = ((total_stats['total_original_size'] - total_stats['total_png_size']) / total_stats['total_original_size']) * 100
        print(f"\nSavings:")
        print(f"  WebP: {webp_savings:.1f}% reduction")
        print(f"  PNG: {png_savings:.1f}% reduction")

    print("\n" + "=" * 80)
    print("✓ Optimization complete!")
    print("=" * 80)
    print(f"\nBackup location: {backup_dir}")
    print("To revert changes, restore files from the backup directory.")


if __name__ == '__main__':
    main()
