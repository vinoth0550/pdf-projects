from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import subprocess
import os
import shutil
import uuid

app = FastAPI(
    title="PDF to PowerPoint Converter API",
    description="An API for converting PDF documents to PowerPoint files (PPTX) using LibreOffice",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)

# Directory setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploadedpdf")
CONVERTED_DIR = os.path.join(BASE_DIR, "convertedppt")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CONVERTED_DIR, exist_ok=True)

# Serve converted files
app.mount("/convertedppt", StaticFiles(directory=CONVERTED_DIR), name="convertedppt")

def pdf_to_ppt(input_path, output_dir):
    """Convert a PDF document to PowerPoint presentation using LibreOffice"""
    os.makedirs(output_dir, exist_ok=True)
    try:
        # Find LibreOffice executable
        soffice_path = shutil.which("soffice")
        if not soffice_path:
            # Default path on Windows
            soffice_path = r"C:\Program Files\LibreOffice\program\soffice.exe"
            if not os.path.exists(soffice_path):
                # Try another common location
                soffice_path = r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"
        
        if not os.path.exists(soffice_path):
            raise Exception(f"LibreOffice not found at {soffice_path}. Please make sure LibreOffice is installed.")
        
        print(f"Using LibreOffice at: {soffice_path}")
        print(f"Input file exists: {os.path.exists(input_path)}")
        
        subprocess.run([
            soffice_path,
            "--headless",
            "--convert-to", "pptx",  # Convert to PPTX format
            "--outdir", output_dir,
            input_path
        ], check=True)

        base_name = os.path.splitext(os.path.basename(input_path))[0]
        pptx_path = os.path.join(output_dir, base_name + ".pptx")

        if not os.path.exists(pptx_path):
            raise Exception("PowerPoint conversion failed — output file not found.")
        return pptx_path

    except subprocess.CalledProcessError as e:
        raise Exception(f"LibreOffice conversion error: {str(e)}")
    except Exception as e:
        raise Exception(f"Conversion error: {str(e)}")


@app.post("/convert/pdftoppt", summary="Convert PDF to PowerPoint")
async def convert_pdf_to_ppt(file: UploadFile = File(...)):
    """Upload a PDF file and convert it to PowerPoint (PPTX)"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    unique_id = str(uuid.uuid4())

    try:
        original_filename = os.path.splitext(file.filename)[0]
        pdf_filename = f"{original_filename}_{unique_id}{os.path.splitext(file.filename)[1]}"
        pdf_path = os.path.join(UPLOAD_DIR, pdf_filename)

        # Save uploaded file
        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Convert using LibreOffice
        ppt_file = pdf_to_ppt(pdf_path, CONVERTED_DIR)
        ppt_filename = os.path.basename(ppt_file)

        server_host = "localhost:8000"  # Change this to match your actual server
        download_link = f"http://{server_host}/convertedppt/{ppt_filename}"

        return JSONResponse(
            content={
                "message": "PDF converted successfully to PowerPoint",
                "download_link": download_link
            }
        )

    except Exception as e:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


@app.get("/convertedppt/{filename}", summary="Download Converted PPT File")
async def download_file(filename: str):
    """Download a specific converted PPT file by filename"""
    file_path = os.path.join(CONVERTED_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )


@app.get("/", summary="API Status")
async def root():
    """Check if the API is running"""
    return {"status": "API is running", "message": "Upload a PDF file to /convert/pdftoppt to convert it to PowerPoint"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)  # Note: Using port 8001 to avoid conflict with your original API






# the above cord is using libreoffice for conversion it not working well 