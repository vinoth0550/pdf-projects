
# compress fastapi

import os
import fitz
import uuid
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIRECTORY = os.path.join(BASE_DIR, "compressed_files")
os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
#
os.makedirs("uploaded_pdfs", exist_ok=True)
#

# Mount static directory

app.mount("/files", StaticFiles(directory=OUTPUT_DIRECTORY), name="files")

def compress_pdf_with_pymupdf(input_path, output_path, quality_level="Medium"):
    quality_mapping = {
        "Maximum": {"deflate": True, "garbage": 0, "clean": False, "pretty": False},
        "High": {"deflate": True, "garbage": 1, "clean": False, "pretty": False},
        "Medium": {"deflate": True, "garbage": 2, "clean": True, "pretty": False},
        "Low": {"deflate": True, "garbage": 3, "clean": True, "pretty": False},
        "Minimum": {"deflate": True, "garbage": 4, "clean": True, "pretty": False},
    }
    params = quality_mapping.get(quality_level, quality_mapping["Medium"])

    doc = fitz.open(input_path)
    doc.save(output_path, **params)
    doc.close()

    original_size = os.path.getsize(input_path)
    compressed_size = os.path.getsize(output_path)
    reduction = (1 - compressed_size / original_size) * 100

    return {
        "original_size": round(original_size / 1024, 2),
        "compressed_size": round(compressed_size / 1024, 2),
        "reduction_percentage": round(reduction, 2),
    }

@app.post("/compress-pdf")
async def compress_pdf(file: UploadFile = File(...), quality_level: Optional[str] = Form("Medium")):
    if not file.filename.endswith(".pdf"):
        return JSONResponse(status_code=400, content={"status": "error", "message": "Only PDF files are allowed"})

   
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)

    temp_file = os.path.join(OUTPUT_DIRECTORY, f"temp_{file.filename}")

    try:

        with open(temp_file, "wb") as f:
            content = await file.read()
            f.write(content)

        output_filename = f"{uuid.uuid4()}.pdf"
        output_path = os.path.join(OUTPUT_DIRECTORY, output_filename)

        #
        upload_path = os.path.join("uploaded_pdfs", f"{uuid.uuid4()}.pdf")
        with open(upload_path, "wb") as buffer:
            buffer.write(await file.read())
        #

        compression_stats = compress_pdf_with_pymupdf(temp_file, output_path, quality_level)
        os.remove(temp_file)

        base_url = "http://127.0.0.1:8000"
        download_link = f"{base_url}/files/{output_filename}"

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Successfully compressed PDF file!",
                "download_link": download_link,
                "compression_stats": compression_stats,
            },
        )

    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
