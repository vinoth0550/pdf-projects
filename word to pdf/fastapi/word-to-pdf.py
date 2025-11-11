

# uvicorn main:app --reload

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from docx2pdf import convert
import os
import uuid

app = FastAPI()

UPLOAD_DIR = "uploads"
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

        download_link = f"http://127.0.0.1:8000/files/{file_id}"

        return JSONResponse(content={
            "status": "success",
            "message": "Word file converted successfully!",
            "pdf_path": output_path,
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