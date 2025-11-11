
# for white background colour

import os
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
from rembg import remove

app = FastAPI(title="Background Remover API")

os.makedirs("uploaded_images", exist_ok=True)
os.makedirs("whitebg_added-images", exist_ok=True)

app.mount("/files", StaticFiles(directory="whitebg_added-images"), name="files")

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "bmp", "gif", "tiff"}

def is_valid_image(filename: str) -> bool:
    
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.post("/white-background")
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

        output_img = output_img.convert("RGBA")

        white_bg = Image.new("RGBA", output_img.size, (255, 255, 255, 255))

        final_img = Image.alpha_composite(white_bg, output_img).convert("RGB")

        output_filename = f"{unique_id}.jpg"
        output_path = os.path.join("whitebg_added-images", output_filename)
        final_img.save(output_path, "JPEG")

        download_link = f"http://127.0.0.1:8000/files/{output_filename}"
        
        return {
            "status": "success",
            "message": "successfully added the white background",
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

