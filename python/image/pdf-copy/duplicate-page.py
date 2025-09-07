import argparse
from PyPDF2 import PdfReader, PdfWriter

def repeat_page(input_pdf, page_num, n_copies, output_pdf):
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    if page_num < 1 or page_num > len(reader.pages):
        raise ValueError(f"Page number {page_num} out of range. PDF has {len(reader.pages)} pages.")

    target_page = reader.pages[page_num - 1]

    for _ in range(n_copies):
        writer.add_page(target_page)

    with open(output_pdf, "wb") as f:
        writer.write(f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Duplicate a specific page from a PDF multiple times")
    parser.add_argument("-i", "--input", required=True, help="Input PDF file path")
    parser.add_argument("-o", "--output", required=True, help="Output PDF file path")
    parser.add_argument("-p", "--page", type=int, required=True, help="Page number to duplicate (1-indexed)")
    parser.add_argument("-n", "--copies", type=int, required=True, help="Number of copies to create")
    args = parser.parse_args()

    repeat_page(args.input, args.page, args.copies, args.output)
    print(f"Generated {args.output} with {args.copies} copies of page {args.page}.")
