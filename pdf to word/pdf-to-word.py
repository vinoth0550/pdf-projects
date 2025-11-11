
# pdf to word

from pdf2docx import Converter
from tkinter import Tk, filedialog
import os
import shutil

def pdf_to_word(pdf_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    word_file = os.path.join(output_dir, base_name + ".docx")
    
    cv = Converter(pdf_path)
    cv.convert(word_file)
    cv.close()
    
    print(f"Converted file saved successfully: {word_file}")

def main():
    # Hide the main tkinter window
    Tk().withdraw()

    # Let user choose a PDF file
    pdf_path = filedialog.askopenfilename(
        title="Select PDF file to convert",
        filetypes=[("PDF files", "*.pdf")]
    )

    if not pdf_path:
        print(" No file selected. Exiting.")
        return

    # Define project folder paths
    project_dir = os.path.dirname(os.path.abspath(__file__))
    upload_dir = os.path.join(project_dir, "uploads")
    converted_dir = os.path.join(project_dir, "converted")

    # Make sure folders exist
    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs(converted_dir, exist_ok=True)

    # Copy selected PDF into uploads folder
    uploaded_pdf_path = os.path.join(upload_dir, os.path.basename(pdf_path))
    shutil.copy(pdf_path, uploaded_pdf_path)
    print(f"📁 File copied to uploads folder: {uploaded_pdf_path}")

    # Convert the uploaded file to Word in converted folder
    pdf_to_word(uploaded_pdf_path, converted_dir)

if __name__ == "__main__":
    main()
