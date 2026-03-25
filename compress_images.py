"""
AROS Design - Image Compression Script
Compresses all images for optimal web performance
"""

import os
from pathlib import Path
from PIL import Image
import shutil

# Configuration
MAX_WIDTH = 1920          # Max width for large images
MAX_HEIGHT = 1920         # Max height for large images
JPEG_QUALITY = 82         # Quality for JPEG (80-85 is good for web)
PNG_COMPRESS = 6          # PNG compression level (0-9)
THUMB_SIZE = (800, 800)   # Thumbnail size for gallery previews

# Paths
BASE_DIR = Path(__file__).parent
PHOTOS_DIR = BASE_DIR / "Photos"
OUTPUT_DIR = BASE_DIR / "Photos_Optimized"
THUMBS_DIR = BASE_DIR / "Photos_Thumbnails"

def get_file_size_mb(filepath):
    """Get file size in MB"""
    return os.path.getsize(filepath) / (1024 * 1024)

def compress_image(input_path, output_path, max_size=(MAX_WIDTH, MAX_HEIGHT), quality=JPEG_QUALITY):
    """Compress and resize a single image"""
    try:
        with Image.open(input_path) as img:
            # Convert to RGB if necessary (for PNG with transparency, etc.)
            if img.mode in ('RGBA', 'P'):
                # Keep PNG as PNG to preserve transparency
                if input_path.suffix.lower() == '.png':
                    # Resize if needed
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    img.save(output_path, 'PNG', optimize=True, compress_level=PNG_COMPRESS)
                    return True
                else:
                    img = img.convert('RGB')
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            # Resize if larger than max dimensions
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Save with optimization
            if output_path.suffix.lower() in ['.jpg', '.jpeg']:
                img.save(output_path, 'JPEG', quality=quality, optimize=True, progressive=True)
            elif output_path.suffix.lower() == '.png':
                img.save(output_path, 'PNG', optimize=True, compress_level=PNG_COMPRESS)
            else:
                # Default to JPEG for other formats
                output_path = output_path.with_suffix('.jpg')
                img.save(output_path, 'JPEG', quality=quality, optimize=True, progressive=True)

            return True
    except Exception as e:
        print(f"  Error processing {input_path.name}: {e}")
        return False

def create_thumbnail(input_path, output_path, size=THUMB_SIZE):
    """Create a thumbnail version of an image"""
    try:
        with Image.open(input_path) as img:
            if img.mode in ('RGBA', 'P') and input_path.suffix.lower() != '.png':
                img = img.convert('RGB')
            elif img.mode not in ('RGB', 'RGBA', 'P'):
                img = img.convert('RGB')

            img.thumbnail(size, Image.Resampling.LANCZOS)

            if output_path.suffix.lower() in ['.jpg', '.jpeg']:
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                img.save(output_path, 'JPEG', quality=75, optimize=True, progressive=True)
            else:
                img.save(output_path, optimize=True)

            return True
    except Exception as e:
        print(f"  Error creating thumbnail for {input_path.name}: {e}")
        return False

def process_folder(input_folder, output_folder, thumb_folder, stats):
    """Process all images in a folder"""
    input_folder = Path(input_folder)
    output_folder = Path(output_folder)
    thumb_folder = Path(thumb_folder)

    # Create output directories
    output_folder.mkdir(parents=True, exist_ok=True)
    thumb_folder.mkdir(parents=True, exist_ok=True)

    # Supported image extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff'}

    for item in input_folder.iterdir():
        if item.is_dir():
            # Recurse into subdirectories
            sub_output = output_folder / item.name
            sub_thumb = thumb_folder / item.name
            process_folder(item, sub_output, sub_thumb, stats)
        elif item.suffix.lower() in image_extensions:
            # Process image
            output_path = output_folder / item.name
            thumb_path = thumb_folder / item.name

            # Convert non-standard extensions to jpg
            if item.suffix.lower() not in ['.jpg', '.jpeg', '.png']:
                output_path = output_path.with_suffix('.jpg')
                thumb_path = thumb_path.with_suffix('.jpg')

            original_size = get_file_size_mb(item)
            stats['original_total'] += original_size
            stats['count'] += 1

            print(f"  Processing: {item.name} ({original_size:.2f} MB)")

            # Compress main image
            if compress_image(item, output_path):
                new_size = get_file_size_mb(output_path)
                stats['compressed_total'] += new_size
                savings = ((original_size - new_size) / original_size) * 100 if original_size > 0 else 0
                print(f"    -> {new_size:.2f} MB ({savings:.1f}% smaller)")

            # Create thumbnail
            create_thumbnail(item, thumb_path)

def main():
    print("=" * 60)
    print("AROS Design - Image Compression Tool")
    print("=" * 60)
    print()

    if not PHOTOS_DIR.exists():
        print(f"Error: Photos directory not found at {PHOTOS_DIR}")
        return

    print(f"Source:      {PHOTOS_DIR}")
    print(f"Optimized:   {OUTPUT_DIR}")
    print(f"Thumbnails:  {THUMBS_DIR}")
    print(f"Max Size:    {MAX_WIDTH}x{MAX_HEIGHT}px")
    print(f"JPEG Quality: {JPEG_QUALITY}%")
    print()

    # Initialize stats
    stats = {
        'count': 0,
        'original_total': 0,
        'compressed_total': 0
    }

    # Process all images
    print("Processing images...")
    print("-" * 60)

    process_folder(PHOTOS_DIR, OUTPUT_DIR, THUMBS_DIR, stats)

    # Print summary
    print()
    print("=" * 60)
    print("COMPRESSION COMPLETE")
    print("=" * 60)
    print(f"Images processed:    {stats['count']}")
    print(f"Original size:       {stats['original_total']:.2f} MB")
    print(f"Compressed size:     {stats['compressed_total']:.2f} MB")

    if stats['original_total'] > 0:
        total_savings = stats['original_total'] - stats['compressed_total']
        savings_percent = (total_savings / stats['original_total']) * 100
        print(f"Space saved:         {total_savings:.2f} MB ({savings_percent:.1f}%)")

    print()
    print("Optimized images saved to: Photos_Optimized/")
    print("Thumbnail images saved to: Photos_Thumbnails/")
    print()
    print("To use optimized images on your website, update image paths")
    print("from 'Photos/' to 'Photos_Optimized/'")
    print()

if __name__ == "__main__":
    main()
