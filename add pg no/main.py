
# add-pg-no.py

# add-pg-no



from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import fitz 
import os
import uuid
import shutil
from typing import Optional
from pydantic import BaseModel
import uvicorn



app = FastAPI(title="PDF Page Numbering API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


UPLOAD_FOLDER = 'uploads-pdfs'
OUTPUT_FOLDER = 'added-pgno-pdfs'


for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
    os.makedirs(folder, exist_ok=True)


class PageNumberResponse(BaseModel):
    success: bool
    message: str
    download_url: Optional[str] = None

def add_page_numbers(input_path, output_path):
    try:

        doc = fitz.open(input_path)
        
        total_pages = len(doc)
        
        for page_num in range(total_pages):
            page = doc[page_num]
            
            text = f" {page_num + 1} "
        
            text_width = fitz.get_text_length(text, fontname="helv", fontsize=8)
            page_rect = page.rect
            x = (page_rect.width - text_width) / 2

            y = page_rect.height - 15                # 30 points from bottom        # 30
            
            page.insert_text((x, y), text, fontname="helv", fontsize=10)
        
        doc.save(output_path)
        return True
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return False

@app.get("/")
async def root():
    return {"message": "PDF Page Numbering API. Use /add-page-numbers to process a PDF file."}

@app.post("/addpgno", response_model=PageNumberResponse)
async def create_numbered_pdf(
    file: UploadFile = File(...),
    position: str = Form("bottom", description="Position of page numbers (bottom, top, etc.)"),
    custom_text: Optional[str] = Form(None, description="Optional custom text format")
):

    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    

    file_id = str(uuid.uuid4())
    original_filename = file.filename
    base_name = os.path.splitext(original_filename)[0]
    
    input_path = os.path.join(UPLOAD_FOLDER, f"{file_id}_{original_filename}")
    output_filename = f"{base_name}_numbered.pdf"
    output_path = os.path.join(OUTPUT_FOLDER, f"{file_id}_{output_filename}")
    
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Process the PDF

    success = add_page_numbers(input_path, output_path)
    
    if not success:
        # Clean up the input file

        if os.path.exists(input_path):
            os.remove(input_path)
        
        raise HTTPException(status_code=500, detail="Failed to process the PDF")
    
    # if os.path.exists(input_path):
    #     os.remove(input_path)
    
    base_url = "http://localhost:8000"  
    download_url = f"{base_url}/download/{file_id}/{output_filename}"
    
    return PageNumberResponse(
        success=True,
        message="Page numbers added successfully",
        download_url=download_url
    )


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
