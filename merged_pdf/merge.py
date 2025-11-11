import os
from PyPDF2 import PdfMerger


pdf_folder = r"D:\\v_projects\\pdf project\\merged_pdf"


pdf_files = [
    os.path.join(pdf_folder, f)
    for f in os.listdir(pdf_folder)
    if f.lower().endswith(".pdf")
]

pdf_files.sort()


if not pdf_files:
    print(" No PDF files found in the folder.")
    exit()


output_folder = os.path.join(pdf_folder, "mergedpdf")
os.makedirs(output_folder, exist_ok=True)


output_path = os.path.join(output_folder, "merged_output.pdf")


merger = PdfMerger()

for pdf in pdf_files:
    try:
        print(f"Adding: {pdf}")
        with open(pdf, "rb") as f:
            merger.append(f)
    except Exception as e:
        print(f" Skipping {pdf} due to error: {e}")


merger.write(output_path)
merger.close()

print(f"\n Merged PDF saved successfully at:\n{output_path}")
