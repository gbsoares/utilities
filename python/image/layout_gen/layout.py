"""
Photo Layout Generator

This script creates a PDF layout from JPEG images in the current directory,
arranging them in a grid format with customizable dimensions and settings.
"""

import argparse
import os
import sys
from PIL import Image, ExifTags
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER, A4, LEGAL
from reportlab.lib.units import inch


# Constants
DEFAULT_IMG_WIDTH_IN = 4.0
DEFAULT_IMG_HEIGHT_IN = 3.0
DEFAULT_MARGIN_IN = 0.125
DEFAULT_COLS = 2
DEFAULT_ROWS = 3
DEFAULT_DPI = 600
DEFAULT_OUTPUT = "layout.pdf"

# Page size mapping
PAGE_SIZES = {
    'letter': LETTER,
    'A4': A4,
    'legal': LEGAL,
}

def crop_to_aspect(img: Image.Image, target_ratio: float) -> Image.Image:
    """
    Crop image to target aspect ratio by removing excess from longer dimension.
    
    Args:
        img: PIL Image object to crop
        target_ratio: Target width/height ratio (default 4:3)
        
    Returns:
        Cropped PIL Image object
    """
    width, height = img.size
    current_ratio = width / height

    if current_ratio > target_ratio:
        # Too wide - crop horizontally
        new_width = int(height * target_ratio)
        left = (width - new_width) // 2
        img = img.crop((left, 0, left + new_width, height))
    elif current_ratio < target_ratio:
        # Too tall - crop vertically
        new_height = int(width / target_ratio)
        top = (height - new_height) // 2
        img = img.crop((0, top, width, top + new_height))
    
    return img


def get_image_files(directory: str) -> list[str]:
    """
    Get list of JPEG files from directory, sorted alphabetically, with full paths.
    
    Args:
        directory: Directory to search for images (default current directory)
        
    Returns:
        List of JPEG filenames with directory prepended
    """
    image_extensions = ('.jpg', '.jpeg')
    images = [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.lower().endswith(image_extensions)
    ]
    return sorted(images)


def process_image(image_path: str, img_width_in: float, img_height_in: float, dpi: int):
    """
    Process a single image: load, rotate if needed, crop and resize.
    
    Args:
        image_path: Path to image file
        img_width_in: Target width in inches
        img_height_in: Target height in inches  
        dpi: Target DPI resolution
        
    Returns:
        Path to temporary processed image file, or None if processing failed
    """
    try:
        img = Image.open(image_path)
        
        # Rotate portrait images to landscape
        if img.width < img.height:
            img = img.rotate(90, expand=True)

        # Calculate target dimensions in pixels
        target_width = int(img_width_in * dpi)
        target_height = int(img_height_in * dpi)
        
        # Crop to aspect ratio and resize
        target_ratio = img_width_in / img_height_in
        img = crop_to_aspect(img, target_ratio)
        img = img.resize((target_width, target_height), Image.LANCZOS)

        # Save to temporary file
        temp_path = f"temp_{os.path.basename(image_path)}.jpg"
        img.save(temp_path, format='JPEG', quality=95)
        
        return temp_path
    
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None


def paginate_images(images, rows, cols):
    """Yield pages of images laid out in a grid of rows x cols."""
    per_page = rows * cols
    for page_start in range(0, len(images), per_page):
        yield images[page_start:page_start + per_page]


def create_photo_layout(img_width_in: float, img_height_in: float,
                       margin_in: float, 
                       page_size: str, 
                       cols: int, rows: int,
                       dpi: int,
                       input_dir: str,
                       output_file: str) -> None:
    """
    Create a PDF layout with images arranged in a grid.
    
    Args:
        img_width_in: Image width in inches
        img_height_in: Image height in inches
        margin_in: Margin between images in inches
        page_size: Page size ('letter', 'A4', 'legal')
        cols: Number of columns
        rows: Number of rows
        dpi: DPI resolution for processed images
        input_dir: Directory containing input images
        output_file: Output PDF filename
    """
    # Get page dimensions
    if page_size not in PAGE_SIZES:
        raise ValueError(f"Invalid page size: {page_size}. Choose from: {', '.join(PAGE_SIZES.keys())}")
    page_width, page_height = PAGE_SIZES[page_size]
    
    # Calculate dimensions in points (1 pt = 1/72 inch)
    box_width = img_width_in * inch
    box_height = img_height_in * inch
    margin = margin_in * inch

    # Check if layout fits on page
    total_width = cols * box_width + (cols + 1) * margin
    total_height = rows * box_height + (rows + 1) * margin
    
    if total_width > page_width or total_height > page_height:
        print(f"Warning: Layout ({total_width:.1f} x {total_height:.1f} pts) may not fit on {page_size} page ({page_width:.1f} x {page_height:.1f} pts)")

    # Get image files
    images = get_image_files(input_dir)
    if not images:
        print(f"No JPEG images found in directory: {input_dir}")
        return

    print(f"Found {len(images)} images")
    print(f"Creating {rows}x{cols} grid on {page_size} page")
    print(f"Image size: {img_width_in}\" x {img_height_in}\" at {dpi} DPI")

    # Create PDF canvas
    pdf_canvas = canvas.Canvas(output_file, pagesize=PAGE_SIZES[page_size])

    for page_num, images_per_page in enumerate(paginate_images(images, rows, cols), 1):
        for idx, img_path in enumerate(images_per_page):
            row = idx // cols
            col = idx % cols
            print(f"  Placing {os.path.basename(img_path)} @ row {row}, col {col} on page {page_num}")

            temp_path = process_image(img_path, img_width_in, img_height_in, dpi)
            if temp_path is None:
                continue

            try:
                # Calculate position on page
                box_x = margin + col * (box_width + margin)
                box_y = page_height - ((row + 1) * (box_height + margin))

                # Center image in box
                img = Image.open(temp_path)
                img_width_pts = img.width * 72 / dpi
                img_height_pts = img.height * 72 / dpi

                x_offset = (box_width - img_width_pts) / 2
                y_offset = (box_height - img_height_pts) / 2

                draw_x = box_x + x_offset
                draw_y = box_y + y_offset

                # Draw image on PDF
                pdf_canvas.drawImage(
                    temp_path, draw_x, draw_y,
                    width=img_width_pts, height=img_height_pts
                )

            except Exception as e:
                print(f"Error placing {img_path}: {e}")
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        # After each page, start a new page if there are more images
        if page_num * rows * cols < len(images):
            pdf_canvas.showPage()

    # Save PDF
    pdf_canvas.save()
    print(f"PDF saved as: {output_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate PDF layout from JPEG images")
    parser.add_argument('-d', '--input-dir', default='.', help='Directory containing input images (default: current directory)')
    parser.add_argument('-w', '--width', type=float, default=DEFAULT_IMG_WIDTH_IN, help=f'Image width in inches (default: {DEFAULT_IMG_WIDTH_IN})')
    parser.add_argument('--height', type=float, default=DEFAULT_IMG_HEIGHT_IN, help=f'Image height in inches (default: {DEFAULT_IMG_HEIGHT_IN})')
    parser.add_argument('-m', '--margin', type=float, default=DEFAULT_MARGIN_IN, help=f'Margin between images in inches (default: {DEFAULT_MARGIN_IN})')
    parser.add_argument('-c', '--cols', type=int, default=DEFAULT_COLS, help=f'Number of columns (default: {DEFAULT_COLS})')
    parser.add_argument('-r', '--rows', type=int, default=DEFAULT_ROWS, help=f'Number of rows (default: {DEFAULT_ROWS})')
    parser.add_argument('--dpi', type=int, default=DEFAULT_DPI, help=f'DPI resolution for processed images (default: {DEFAULT_DPI})')
    parser.add_argument('-p', '--page-size', choices=list(PAGE_SIZES.keys()), default='letter', help='Page size')
    parser.add_argument('-o', '--output', default=DEFAULT_OUTPUT, help='Output PDF filename')
    args = parser.parse_args()

    try:
        create_photo_layout(
            img_width_in=args.width,
            img_height_in=args.height, 
            margin_in=args.margin,
            cols=args.cols,
            rows=args.rows,
            dpi=args.dpi,
            page_size=args.page_size,
            output_file=args.output,
            input_dir=args.input_dir
        )
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
