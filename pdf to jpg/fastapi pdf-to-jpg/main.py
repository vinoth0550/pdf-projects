
# main.py

# this is a fastapi code to convert pdf to jpg

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import fitz
import os
import uuid
import shutil
from pathlib import Path

app = FastAPI()


UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("output_jpg")
STATIC_FILES_DIR = Path("files")

for directory in [UPLOAD_DIR, OUTPUT_DIR, STATIC_FILES_DIR]:
    directory.mkdir(exist_ok=True)


app.mount("/files", StaticFiles(directory=str(STATIC_FILES_DIR)), name="files")

@app.post("/convert-pdf-to-jpg/")
async def convert_pdf_to_jpg(file: UploadFile = File(...)):
    
    # Validate file is a PDF
    if not file.filename.lower().endswith(".pdf"):
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "pdf files only" 
            }
        )
    
    # Generate unique ID for this conversion
    unique_id = str(uuid.uuid4())
    output_folder = OUTPUT_DIR / unique_id
    output_folder.mkdir(exist_ok=True)
    
    # Save the uploaded file
    file_path = UPLOAD_DIR / f"{unique_id}.pdf"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # try:
    #     # Convert PDF to JPGs
    #     doc = fitz.open(file_path)
    #     for page_number in range(len(doc)):
    #         page = doc.load_page(page_number)
    #         pix = page.get_pixmap(dpi=200)
    #         output_path = output_folder / f"page_{page_number + 1}.jpg"
    #         pix.save(str(output_path))


    try:
    # Convert PDF to JPGs (using context manager)
        with fitz.open(file_path) as doc:
            for page_number in range(len(doc)):
                page = doc.load_page(page_number)
                pix = page.get_pixmap(dpi=200)
                output_path = output_folder / f"page_{page_number + 1}.jpg"
                pix.save(str(output_path))

        
        # Create a zip file with all JPGs (optional - for multiple pages)
        zip_path = STATIC_FILES_DIR / f"{unique_id}.zip"
        shutil.make_archive(str(zip_path.with_suffix("")), 'zip', output_folder)
        
        # For simplicity, also copy the first page as a standalone JPG
        first_jpg = output_folder / "page_1.jpg"
        if first_jpg.exists():
            jpg_download_path = STATIC_FILES_DIR / f"{unique_id}.jpg"
            shutil.copy(first_jpg, jpg_download_path)
            
        return JSONResponse(
            content={
                "status": "success",
                "message": "pdf file converted into jpg successfully!",
                "download_link": f"http://127.0.0.1:8000/files/{unique_id}.zip"
            }
        )
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Error during conversion: {str(e)}"
            }
        )
    finally:
        # Clean up uploaded file
        if file_path.exists():
            file_path.unlink()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
