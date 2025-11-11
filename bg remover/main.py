# FastAPI Background Remover API

import os
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
from rembg import remove

app = FastAPI(title="Background Remover API")

os.makedirs("uploaded_images", exist_ok=True)
os.makedirs("bgremoved_images", exist_ok=True)

app.mount("/files", StaticFiles(directory="bgremoved_images"), name="files")

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "bmp", "gif", "tiff"}

def is_valid_image(filename: str) -> bool:
    
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.post("/remove-background")
async def remove_background(file: UploadFile = File(...)):

    if not is_valid_image(file.filename):
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "images only"
            }
        )
    
    try:
    
        original_filename = file.filename
        name, ext = os.path.splitext(original_filename)
        unique_id = str(uuid.uuid4())
        
        upload_path = os.path.join("uploaded_images", f"{unique_id}{ext}")
        with open(upload_path, "wb") as buffer:
            buffer.write(await file.read())
        
        input_img = Image.open(upload_path)
        output_img = remove(input_img)
        
        output_filename = f"{unique_id}.png"
        output_path = os.path.join("bgremoved_images", output_filename)
        output_img.save(output_path)
        
        download_link = f"http://127.0.0.1:8000/files/{output_filename}"
        
        return {
            "status": "success",
            "message": "successfully removed the bg!",
            "download_link": download_link
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e)
            }
        )


#  this is the last working file of friday its working well.



