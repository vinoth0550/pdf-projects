# pdf to excel

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import tabula
import pandas as pd
import os
import shutil



app = FastAPI(
    title="PDF to Excel Converter API",
    description="API for converting PDF files to Excel spreadsheets",
    version="1.0 (Plesk Production)"
)


# step 1 : ALLOWED ORIGINS

ALLOWED_ORIGINS = [
    "https://python.selfietoons.com",
    "https://tsitfilemanager.in",
    "https://www.tsitfilemanager.in",
    "http://localhost:3000",
    "http://localhost:3001"
]

# step 2 : CORS SETUP

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


# Folders

UPLOAD_DIR = "uploads_pdf"
OUTPUT_DIR = "converted_excel"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

app.mount("/excel-downloads", StaticFiles(directory=OUTPUT_DIR), name="excel-downloads")


# step 3 : Filename function

def get_unique_excel_filename(base_name):
    """Generate unique filename for XLSX to avoid overwriting."""
    filename = f"{base_name}.xlsx"
    counter = 1

    while os.path.exists(os.path.join(OUTPUT_DIR, filename)):
        filename = f"{base_name}({counter}).xlsx"
        counter += 1

    return filename



# PDF → Excel Conversion

def pdf_to_excel(pdf_path, output_path):
    try:
        # Read tables from PDF into DataFrame list
        tables = tabula.read_pdf(pdf_path, pages="all", multiple_tables=True)

        if not tables or len(tables) == 0:
            raise Exception("No tables found in the PDF.")

        # Write each table into separate sheets
        with pd.ExcelWriter(output_path) as writer:
            for i, table in enumerate(tables):
                sheet_name = f"Sheet_{i+1}"
                table.to_excel(writer, sheet_name=sheet_name, index=False)

        return output_path

    except Exception as e:
        if os.path.exists(output_path):
            os.remove(output_path)
        raise Exception(f"Conversion failed: {str(e)}")



# step 4 : Main API Route

@app.post("/api/convert/pdftoexcel")
async def convert_pdf_to_excel(file: UploadFile = File(...)):
    try:
        if not file.filename.lower().endswith(".pdf"):
            return {
                "status": "error",
                "message": "pdf file only"
            }

        original_name = os.path.splitext(file.filename)[0]

        input_path = os.path.join(UPLOAD_DIR, file.filename)
        output_filename = get_unique_excel_filename(original_name)
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        pdf_to_excel(input_path, output_path)

        download_link = f"https://python.selfietoons.com/api/filesexcel/{output_filename}"

        return {
            "status": "success",
            "message": "PDF converted to Excel successfully!",
            "download_link": download_link,
            "file_name": output_filename
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Conversion failed: {str(e)}"
        }



# step 5 : File Download

@app.get("/api/filesexcel/{file_name}")
def get_converted_excel(file_name: str):
    excel_path = os.path.join(OUTPUT_DIR, file_name)
    if os.path.exists(excel_path):
        return FileResponse(
            excel_path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=file_name
        )
    
    raise HTTPException(status_code=404, detail="File not found.")



# step 6 : Home route

@app.get("/api/excel/")
def home_excel():
    return {"message": "PDF → Excel API running successfully on Plesk production!"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001)
