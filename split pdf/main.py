
# fapi_split.py

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from PyPDF2 import PdfReader, PdfWriter
import os
import tempfile
import uuid
from pydantic import BaseModel

app = FastAPI()

STATIC_DIR = "splitted_pdf"
os.makedirs(STATIC_DIR, exist_ok=True)
#
os.makedirs("uploaded_pdfs", exist_ok=True)
#
app.mount("/files", StaticFiles(directory=STATIC_DIR), name="files")

class ResponseModel(BaseModel):
    status: str
    message: str
    download_link: str = None

@app.post("/split-pdf", response_model=ResponseModel)
async def split_pdf(
    file: UploadFile = File(...),
    start_page: int = Form(...),
    end_page: int = Form(...)
):
    tmp_path = None
    
    # Check if file is a PDF
    if not file.filename.lower().endswith('.pdf'):
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "Only PDF files are allowed"
            }
        )
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Read the PDF
        pdf = PdfReader(tmp_path)
        total_pages = len(pdf.pages)

        # Validate range
        if start_page < 1 or end_page > total_pages or start_page > end_page:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": f"Invalid page range. The PDF has {total_pages} pages."
                }
            )

        # Split pages
        pdf_writer = PdfWriter()
        for page_num in range(start_page - 1, end_page):
            pdf_writer.add_page(pdf.pages[page_num])

        #
        upload_path = os.path.join("uploaded_pdfs", f"{uuid.uuid4()}.pdf")
        with open(upload_path, "wb") as buffer:
            buffer.write(await file.read())
        #
        unique_filename = f"{uuid.uuid4()}.pdf"
        output_path = os.path.join(STATIC_DIR, unique_filename)

        with open(output_path, "wb") as f:
            pdf_writer.write(f)

        base_url = "http://127.0.0.1:8000"  # In production, use request.base_url
        download_link = f"{base_url}/files/{unique_filename}"

        return {
            "status": "success",
            "message": "Successfully split PDF file!",
            "download_link": download_link
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"An error occurred: {str(e)}"
            }
        )
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
