

# demo.py

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from docx2pdf import convert
import os
import uuid
import uvicorn

app = FastAPI()

UPLOAD_DIR = "uploaded_docxs"
OUTPUT_DIR = "converted_pdfs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.post("/convert/wordtopdf")
async def convert_docx_to_pdf(file: UploadFile = File(...)):
    try:
        file_id = str(uuid.uuid4())
        input_path = os.path.join(UPLOAD_DIR, f"{file_id}.docx")

       
        with open(input_path, "wb") as f:
            f.write(await file.read())
            
        output_path = os.path.join(OUTPUT_DIR, f"{file_id}.pdf")

    
        convert(input_path, output_path)

      
        download_link = f"https://word-to-pdf-production-6d1c.up.railway.app/files/{file_id}"

        return JSONResponse(content={
            "status": "success",
            "message": "Word file converted successfully!",
            "download_link": download_link
        })

    except Exception as e:
        return JSONResponse(content={
            "status": "error",
            "message": str(e)
        })


@app.get("/files/{file_id}")
def get_converted_file(file_id: str):
    pdf_path = os.path.join(OUTPUT_DIR, f"{file_id}.pdf")
    if os.path.exists(pdf_path):
        return FileResponse(pdf_path, media_type="application/pdf", filename=f"{file_id}.pdf")
    return JSONResponse(content={"error": "File not found"}, status_code=404)



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  
    uvicorn.run("main:app", host="0.0.0.0", port=port)