# pdf to jpg using PyMuPDF
# this is the raw py file to convert pdf to jpg

import fitz 
import os

def pdf_to_jpg_pymupdf(input_path):
    output_folder = 'output_jpg'
    os.makedirs(output_folder, exist_ok=True)

    doc = fitz.open(input_path)
    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        pix = page.get_pixmap(dpi=200)  # increase DPI for higher quality
        output_path = os.path.join(output_folder, f"page_{page_number + 1}.jpg")
        pix.save(output_path)

    print(f" Conversion complete! {len(doc)} pages saved in '{output_folder}'.")

pdf_to_jpg_pymupdf("C:\\Users\\ADMIN\\Documents\\word-convereted-pdf.pdf")
