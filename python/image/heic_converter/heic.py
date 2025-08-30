import argparse
import os
from pathlib import Path
import pyheif
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed


def convert_heic_images(input_dir=".", output_format="JPEG", delete_original=False, parallel=True):
    """
    Convert HEIC images to specified format.

    Args:
        input_dir (str): Directory containing HEIC files (default: current directory)
        output_format (str): Output format - JPEG, PNG, or WEBP (default: JPEG)
        delete_original (bool): Whether to delete original HEIC files after conversion (default: False)
        parallel (bool): Whether to convert images in parallel (default: True)
    """
    input_path = Path(input_dir)

    if not input_path.exists():
        print(f"Error: Directory '{input_dir}' does not exist.")
        return

    if not input_path.is_dir():
        print(f"Error: '{input_dir}' is not a directory.")
        return

    # Map format to file extension
    format_extensions = {
        "JPG": ".jpg",
        "JPEG": ".jpg",
        "PNG": ".png",
        "WEBP": ".webp"
    }

    if output_format.upper() not in format_extensions:
        print(f"Error: Unsupported format '{output_format}'. Supported: {list(format_extensions.keys())}")
        return

    file_extension = format_extensions[output_format.upper()]
    converted_count = 0
    failed_count = 0

    # Find all HEIC files
    heic_files = (list(input_path.glob("*.heic")) +
                  list(input_path.glob("*.HEIC")))

    if not heic_files:
        print("No HEIC files found in the specified directory.")
        return

    def convert_one(heic_file):
        output_name = heic_file.stem + file_extension
        output_path = heic_file.parent / output_name
        try:
            heif_file = pyheif.read(heic_file)
            image = Image.frombytes(heif_file.mode, heif_file.size, heif_file.data, "raw")
            image.save(output_path)
            if delete_original:
                heic_file.unlink()
                action = "Converted and deleted"
            else:
                action = "Converted"
            return (True, f" {action}: {heic_file.name} -> {output_name}")
        except Exception as e:
            return (False, f" Failed to convert {heic_file.name}: {e}")


    if parallel:
        with ThreadPoolExecutor() as executor:
            future_to_file = {executor.submit(convert_one, heic_file): heic_file for heic_file in heic_files}
            for future in as_completed(future_to_file):
                success, msg = future.result()
                print(msg)
                if success:
                    converted_count += 1
                else:
                    failed_count += 1
    else:
        for heic_file in heic_files:
            success, msg = convert_one(heic_file)
            print(msg)
            if success:
                converted_count += 1
            else:
                failed_count += 1

    print("-" * 50)
    print(f"Conversion complete: {converted_count} successful, "
          f"{failed_count} failed")


def main():
    """Main function to handle command-line arguments and run conversion."""
    parser = argparse.ArgumentParser(description="Convert HEIC images to other formats")
    parser.add_argument("-d", "--directory", default=".", help="Directory containing HEIC files (default: current directory)")
    parser.add_argument("-f", "--format", default="JPEG", choices=["JPEG", "JPG", "PNG", "WEBP"], help="Output format (default: JPEG)")
    parser.add_argument("--delete-original", action="store_true", help="Delete original HEIC files after conversion (default: keep them)")
    parser.add_argument("--no-parallel", dest="parallel", action="store_false", help="Process images sequentially (default is parallel)")
    args = parser.parse_args()

    print(f"Converting HEIC files in '{args.directory}' to {args.format.upper()}...")
    print(f"Delete original files: {args.delete_original}")
    print(f"Parallel processing: {args.parallel}")
    print("-" * 50)

    convert_heic_images(input_dir=args.directory, output_format=args.format, delete_original=args.delete_original, parallel=args.parallel)


if __name__ == "__main__":
    main()