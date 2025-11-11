

# pdf-to-word-fapi

# pdf-to-word-fapi.py

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pdf2docx import Converter
import os
import shutil
from typing import Optional
import uuid
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="PDF to Word Converter API",
    description="An API for converting PDF files to Word documents",
    version="1.0.0"
)

# Add CORS middleware to allow cross-origin requests

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads_pdf")
CONVERTED_DIR = os.path.join(BASE_DIR, "converted_word")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CONVERTED_DIR, exist_ok=True)

app.mount("/downloads", StaticFiles(directory=CONVERTED_DIR), name="downloads")

def pdf_to_word(pdf_path, output_dir):
    """Convert a PDF file to a Word document"""
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    word_file = os.path.join(output_dir, base_name + ".docx")
    
    try:
        cv = Converter(pdf_path)
        cv.convert(word_file)
        cv.close()
        return word_file
    except Exception as e:

        if os.path.exists(word_file):
            os.remove(word_file)
        raise Exception(f"Conversion failed: {str(e)}")

@app.post("/convertpdfword", summary="Convert PDF to Word")
async def convert_pdf_to_word(file: UploadFile = File(...)):

    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    unique_id = str(uuid.uuid4())
    
    try:
        
        original_filename = os.path.splitext(file.filename)[0]
        pdf_filename = f"{original_filename}_{unique_id}.pdf"
        pdf_path = os.path.join(UPLOAD_DIR, pdf_filename)

        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        word_file = pdf_to_word(pdf_path, CONVERTED_DIR)

        word_filename = os.path.basename(word_file)

        file_size = os.path.getsize(word_file)
      
        server_host = "localhost:8000"  
        download_link = f"http://{server_host}/downloads/{word_filename}"
        
        return JSONResponse(
            content={
               
                "message": "PDF converted successfully",
              
                "download_link": download_link
            }
        )

    except Exception as e:
      
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


@app.get("/downloads/{filename}", summary="Download Converted File")
async def download_file(filename: str):
    """Download a specific converted file by filename"""
    file_path = os.path.join(CONVERTED_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path, 
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


@app.get("/", summary="API Status")
async def root():
    """Check if the API is running"""
    return {"status": "API is running", "message": "Upload a PDF file to /convert/ to convert it to Word"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
