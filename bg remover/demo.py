import os
import shutil
import uuid
from typing import List

import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from PIL import Image
from rembg import remove

# Create the FastAPI app
app = FastAPI(title="Background Remover API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create folders if they don't exist
os.makedirs("upload_images", exist_ok=True)
os.makedirs("bgremoved_images", exist_ok=True)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/results", StaticFiles(directory="bgremoved_images"), name="results")
app.mount("/uploads", StaticFiles(directory="upload_images"), name="uploads")

# Templates
templates = Jinja2Templates(directory="templates")

# Create templates directory and HTML file
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Create index.html template
with open("templates/index.html", "w") as f:
    f.write("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Background Remover</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            text-align: center;
            color: #333;
        }
        .container {
            display: flex;
            justify-content: space-between;
            margin-top: 30px;
        }
        .image-container {
            flex: 1;
            margin: 0 10px;
            text-align: center;
        }
        .image-box {
            background-color: #f0f0f0;
            height: 300px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 10px;
            border-radius: 5px;
            overflow: hidden;
        }
        .image-box img {
            max-width: 100%;
            max-height: 300px;
        }
        .controls {
            text-align: center;
            margin-top: 20px;
        }
        button, label {
            background-color: #4CAF50;
            border: none;
            color: white;
            padding: 10px 20px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 5px;
        }
        button:disabled {
            background-color: #cccccc;
            cursor: not-allowed;
        }
        input[type="file"] {
            display: none;
        }
        #status {
            margin-top: 20px;
            padding: 10px;
            border-radius: 5px;
            background-color: #f0f0f0;
        }
        .download-btn {
            background-color: #2196F3;
        }
    </style>
</head>
<body>
    <h1>Background Remover</h1>
    
    <div class="container">
        <div class="image-container">
            <h3>Original Image</h3>
            <div class="image-box" id="original-image">
                <p>No image selected</p>
            </div>
        </div>
        <div class="image-container">
            <h3>Processed Image</h3>
            <div class="image-box" id="processed-image">
                <p>No processed image yet</p>
            </div>
        </div>
    </div>
    
    <div class="controls">
        <label for="file-upload" class="upload-btn">Upload Image</label>
        <input id="file-upload" type="file" accept="image/*" onchange="previewImage(this)">
        
        <button id="process-btn" onclick="processImage()" disabled>Remove Background</button>
        <button id="download-btn" class="download-btn" style="display: none;" onclick="downloadImage()">Download Image</button>
    </div>
    
    <div id="status">Ready</div>
    
    <script>
        let uploadedFile = null;
        let processedImagePath = null;
        
        function previewImage(input) {
            const originalImage = document.getElementById('original-image');
            const processBtn = document.getElementById('process-btn');
            const status = document.getElementById('status');
            
            if (input.files && input.files[0]) {
                uploadedFile = input.files[0];
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    originalImage.innerHTML = `<img src="${e.target.result}" alt="Original Image">`;
                    processBtn.disabled = false;
                    status.textContent = `Image loaded: ${uploadedFile.name}`;
                };
                
                reader.readAsDataURL(input.files[0]);
            }
        }
        
        async function processImage() {
            if (!uploadedFile) {
                return;
            }
            
            const processBtn = document.getElementById('process-btn');
            const status = document.getElementById('status');
            const downloadBtn = document.getElementById('download-btn');
            const processedImage = document.getElementById('processed-image');
            
            processBtn.disabled = true;
            status.textContent = 'Processing image...';
            
            const formData = new FormData();
            formData.append('file', uploadedFile);
            
            try {
                const response = await fetch('/remove-bg', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    throw new Error('Failed to process image');
                }
                
                const result = await response.json();
                processedImagePath = result.processed_image_url;
                
                processedImage.innerHTML = `<img src="${processedImagePath}" alt="Processed Image">`;
                status.textContent = 'Background removed successfully!';
                downloadBtn.style.display = 'inline-block';
            } catch (error) {
                status.textContent = `Error: ${error.message}`;
                processBtn.disabled = false;
            }
        }
        
        function downloadImage() {
            if (processedImagePath) {
                const a = document.createElement('a');
                a.href = processedImagePath;
                a.download = processedImagePath.split('/').pop();
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            }
        }
    </script>
</body>
</html>
    """)

# Create a simple CSS file
with open("static/style.css", "w") as f:
    f.write("""
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 20px;
    background-color: #f5f5f5;
}
.container {
    max-width: 1000px;
    margin: 0 auto;
    background-color: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
h1 {
    text-align: center;
    color: #333;
}
    """)

# Routes
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/remove-bg")
async def remove_background(file: UploadFile = File(...)):
    try:
        # Generate unique filename
        filename = file.filename
        name, ext = os.path.splitext(filename)
        unique_id = str(uuid.uuid4())[:8]
        
        # Save paths
        upload_path = os.path.join("upload_images", f"{name}_{unique_id}{ext}")
        output_filename = f"{name}_{unique_id}_nobg.png"
        output_path = os.path.join("bgremoved_images", output_filename)
        
        # Save the uploaded file
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process the image
        input_img = Image.open(upload_path)
        output_img = remove(input_img)
        output_img.save(output_path)
        
        # Return the paths for the client
        return {
            "original_image_url": f"/uploads/{os.path.basename(upload_path)}",
            "processed_image_url": f"/results/{output_filename}",
            "message": "Background removed successfully!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.get("/images")
async def list_processed_images():
    try:
        processed_images = os.listdir("bgremoved_images")
        return {"processed_images": [f"/results/{img}" for img in processed_images]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing images: {str(e)}")

@app.get("/download/{filename}")
async def download_image(filename: str):
    try:
        file_path = os.path.join("bgremoved_images", filename)
        if os.path.exists(file_path):
            return FileResponse(file_path, filename=filename)
        else:
            raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
