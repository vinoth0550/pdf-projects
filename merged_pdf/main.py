

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import uuid
from typing import List
import pypdf

app = FastAPI()


UPLOAD_DIR = "uploaded"
MERGED_DIR = "merged"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(MERGED_DIR, exist_ok=True)


app.mount("/files", StaticFiles(directory=MERGED_DIR), name="files")

@app.post("/merge-pdf")
async def merge_pdfs(files: List[UploadFile] = File(...)):
   
    if not files:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "No files provided"
            }
        )
    
    
    for file in files:
        if not file.filename.lower().endswith('.pdf'):
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Only PDF files are allowed"
                }
            )
    
    
    unique_id = str(uuid.uuid4())
    merged_filename = f"{unique_id}.pdf"
    
    
    saved_paths = []
    try:
        for file in files:
            
            safe_filename = f"{uuid.uuid4()}_{os.path.basename(file.filename)}"
            file_path = os.path.join(UPLOAD_DIR, safe_filename)
            
          
            file_content = await file.read()
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            saved_paths.append(file_path)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Error saving files: {str(e)}"
            }
        )
    
 
    try:
        pdf_writer = pypdf.PdfWriter()
        
        for pdf_path in saved_paths:
            try:
          
                with open(pdf_path, 'rb') as pdf_file:
                    pdf_reader = pypdf.PdfReader(pdf_file)
                
                    for page_num in range(len(pdf_reader.pages)):
                        pdf_writer.add_page(pdf_reader.pages[page_num])
            except Exception as e:
                return JSONResponse(
                    status_code=400,
                    content={
                        "status": "error",
                        "message": f"Error with PDF file '{os.path.basename(pdf_path)}': {str(e)}"
                    }
                )

        merged_path = os.path.join(MERGED_DIR, merged_filename)
        with open(merged_path, "wb") as output_file:
            pdf_writer.write(output_file)
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Error merging PDFs: {str(e)}"
            }
        )
    

    base_url = "http://127.0.0.1:8000"  
    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "message": "Successfully merged PDF files!",
            "download_link": f"{base_url}/files/{merged_filename}"
        }
    )

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "PDF Merger API - Upload PDFs to /merge-pdfs/ endpoint"}


# its a merging pdf files project its working well.