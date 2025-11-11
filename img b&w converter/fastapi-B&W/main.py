import os
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
import shutil
from typing import Optional

# Create directories

os.makedirs("uploaded", exist_ok=True)
os.makedirs("converted", exist_ok=True)

app = FastAPI(title="Image Converter API")


app.mount("/files", StaticFiles(directory="converted"), name="files")


VALID_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"]

@app.post("/convert-b&w", response_class=JSONResponse)
async def convert_image(img: UploadFile = File(...)):
 
    file_extension = os.path.splitext(img.filename)[1].lower()
    if file_extension not in VALID_EXTENSIONS:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "images only"
            }
        )
    
    try:
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        upload_path = os.path.join("uploaded", unique_filename)
        
        # Save the uploaded file

        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(img.file, buffer)
        
        # Convert image to black and white

        img = Image.open(upload_path)
        bw_img = img.convert('1')        # '1'- this makes the images full b&w format without grey
        
        # Save the converted image

        converted_path = os.path.join("converted", unique_filename)
        bw_img.save(converted_path)
        
        # Generate download link

        base_url = "http://127.0.0.1:8000"
        download_link = f"{base_url}/files/{unique_filename}"
        
        return JSONResponse(
            content={
                "status": "success",
                "message": "successfully converted image into B&W format",
                "download_link": download_link
            }
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"An error occurred: {str(e)}"
            }
        )

# Root endpoint

@app.get("/")
def read_root():
    return {"message": "Image Conversion API - Upload an image to /convert/ endpoint"}
