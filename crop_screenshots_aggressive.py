#!/usr/bin/env python3
"""
Aggressively crop white space from screenshots with better edge detection.
"""
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np
from pathlib import Path

def find_content_bbox(img, threshold=245):
    """
    Find bounding box of content using a more sophisticated approach.
    """
    # Convert to grayscale
    gray = img.convert('L')
    pixels = np.array(gray)
    
    # Find rows and columns that have content
    # A row/column has content if it has pixels darker than threshold
    height, width = pixels.shape
    
    # Find top (first row with content)
    top = 0
    for y in range(height):
        if np.any(pixels[y, :] < threshold):
            top = max(0, y - 5)  # Small buffer
            break
    
    # Find bottom (last row with content)
    bottom = height - 1
    for y in range(height - 1, -1, -1):
        if np.any(pixels[y, :] < threshold):
            bottom = min(height - 1, y + 5)  # Small buffer
            break
    
    # Find left (first column with content)
    left = 0
    for x in range(width):
        if np.any(pixels[:, x] < threshold):
            left = max(0, x - 5)  # Small buffer
            break
    
    # Find right (last column with content)
    right = width - 1
    for x in range(width - 1, -1, -1):
        if np.any(pixels[:, x] < threshold):
            right = min(width - 1, x + 5)  # Small buffer
            break
    
    return left, top, right, bottom

def crop_screenshot(image_path, output_path, padding=15):
    """Crop screenshot aggressively."""
    # Open image
    img = Image.open(image_path)
    
    # Convert to RGB if necessary
    if img.mode != 'RGB':
        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'RGBA':
            rgb_img.paste(img, mask=img.split()[3])
        else:
            rgb_img.paste(img)
        img = rgb_img
    
    # Find content bounding box
    left, top, right, bottom = find_content_bbox(img, threshold=245)
    
    # Ensure valid bbox
    if right > left and bottom > top:
        # Add padding
        width, height = img.size
        left = max(0, left - padding)
        top = max(0, top - padding)
        right = min(width, right + padding)
        bottom = min(height, bottom + padding)
        
        # Crop
        cropped = img.crop((left, top, right, bottom))
    else:
        # Fallback: use getbbox
        bbox = img.convert('L').getbbox()
        if bbox:
            left, top, right, bottom = bbox
            left = max(0, left - padding)
            top = max(0, top - padding)
            right = min(img.size[0], right + padding)
            bottom = min(img.size[1], bottom + padding)
            cropped = img.crop((left, top, right, bottom))
        else:
            cropped = img
    
    # Enhance sharpness
    cropped = cropped.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
    
    # Save with high quality
    cropped.save(output_path, 'PNG', optimize=False)
    
    return cropped.size

def process_all():
    """Process all screenshots."""
    screenshots_dir = Path('docs/screenshots')
    png_files = list(screenshots_dir.glob('*.png'))
    
    print(f"Processing {len(png_files)} screenshots with aggressive cropping...")
    
    for png_file in png_files:
        print(f"  Processing {png_file.name}...")
        old_size = Image.open(png_file).size
        new_size = crop_screenshot(png_file, png_file, padding=15)
        print(f"    {old_size[0]}x{old_size[1]} -> {new_size[0]}x{new_size[1]}")
    
    print("\n✓ All screenshots processed!")

if __name__ == '__main__':
    try:
        import numpy as np
    except ImportError:
        print("Installing numpy...")
        import subprocess
        subprocess.check_call(['pip', 'install', 'numpy', '--quiet'])
        import numpy as np
    
    process_all()

