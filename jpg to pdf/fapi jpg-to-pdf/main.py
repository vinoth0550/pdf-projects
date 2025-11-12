
# this is the jpg to pdf conversion fastapi

import os
import uuid
import shutil
from pathlib import Path

from PIL import Image
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles


BASE_DIR   = Path(__file__).resolve().parent
INPUT_DIR  = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

app = FastAPI()


app.mount("/files", StaticFiles(directory=OUTPUT_DIR), name="files")


@app.post("/convert-jpg-to-pdf")
async def convert_jpg_to_pdf(file: UploadFile = File(...)):
    
    #  Validate extension

    orig_name = file.filename
    _, ext = os.path.splitext(orig_name)
    if ext.lower() not in (".jpg", ".jpeg"):
        return JSONResponse(
            status_code=400,
            content={
                "status":  "error",
                "message": "jpg format images only"
            }
        )

    unique_id   = str(uuid.uuid4())
    input_path  = INPUT_DIR  / f"{unique_id}{ext.lower()}"
    output_path = OUTPUT_DIR / f"{unique_id}.pdf"

    with input_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        image = Image.open(input_path)
        image.convert("RGB").save(output_path, "PDF")
    except Exception as exc:                  
        return JSONResponse(
            status_code=500,
            content={
                "status":  "error",
                "message": "internal conversion error"
            }
        )
    download_link = f"http://127.0.0.1:8000/files/{output_path.name}"

    return {
        "status":        "success",
        "message":       "jpg file convertedn into pdf successfully!",
        "download_link": download_link
    }
