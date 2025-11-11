

# compress pdf project

import os
import fitz 
import uuid
import random
import string
from pathlib import Path

def compress_pdf_with_pymupdf(input_path, output_path, quality_level="Medium"):
    quality_mapping = {
        "Maximum": {"deflate": True, "garbage": 0, "clean": False, "pretty": False},
        "High": {"deflate": True, "garbage": 1, "clean": False, "pretty": False},
        "Medium": {"deflate": True, "garbage": 2, "clean": True, "pretty": False},
        "Low": {"deflate": True, "garbage": 3, "clean": True, "pretty": False},
        "Minimum": {"deflate": True, "garbage": 4, "clean": True, "pretty": False}
    }
    
    if quality_level not in quality_mapping:
        quality_level = "Medium"
    
    params = quality_mapping[quality_level]
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)                                        
    
    try:
        doc = fitz.open(input_path)
        
        # Save with compression options
        
        doc.save(output_path,
                 deflate=params["deflate"],         
                 garbage=params["garbage"],        
                 clean=params["clean"],            
                 pretty=params["pretty"])          
        
        doc.close()
        
        original_size = os.path.getsize(input_path)
        compressed_size = os.path.getsize(output_path)
        
        reduction = (1 - compressed_size / original_size) * 100
        print(f"Compression level: {quality_level}")
        print(f"Original size: {original_size / 1024:.2f} KB")
        print(f"Compressed size: {compressed_size / 1024:.2f} KB")
        print(f"Reduction: {reduction:.2f}%")
        
        return True
    except Exception as e:
        print(f"Error compressing PDF: {e}")
        return False

def generate_custom_id(length=8):

    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))
  

def main():
    input_pdf = "C:/Users/ADMIN/Downloads/mergedpdf-1-10.pdf"
    
    output_folder = "compressed_pdf"
    os.makedirs(output_folder, exist_ok=True)
    

    unique_id = generate_custom_id(length=6)
    
 
    output_filename = f"{Path(input_pdf).stem}_{unique_id}_compressed.pdf"
    output_pdf = os.path.join(output_folder, output_filename)
    
    if compress_pdf_with_pymupdf(input_pdf, output_pdf, quality_level="high"):
        print(f"PDF compressed successfully and saved to {output_pdf}")
    else:
        print("PDF compression failed")

if __name__ == "__main__":
    main()
