

# fastapi-tts

#  A FastAPI application for text-to-speech conversion with multilingual support


import os
import uuid
from typing import Optional
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from gtts import gTTS
import langdetect
from pydub import AudioSegment
import nltk
from nltk.tokenize import sent_tokenize
from fastapi.middleware.cors import CORSMiddleware
import shutil

# Download necessary NLTK data
nltk.download('punkt', quiet=True)

# Create a FastAPI app
app = FastAPI(title="Text to Speech API", description="Convert text to speech with multilingual support")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories if they don't exist
input_dir = 'input'
output_dir = 'output'
public_dir = 'files'
os.makedirs(input_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)
os.makedirs(public_dir, exist_ok=True)

def detect_language(text):
    """Detect the language of the given text."""
    try:
        return langdetect.detect(text)
    except:
        # Default to English if detection fails
        return 'en'

def adjust_voice(audio, gender='female'):
    """
    Adjust audio to sound more male or female.
    - female: Higher pitch (default gTTS)
    - male: Lower pitch, slowed down slightly
    """
    if gender == 'male':
        # Lower pitch by playing it slower
        octaves = -0.2
        new_sample_rate = int(audio.frame_rate * (2.0 ** octaves))
        male_audio = audio._spawn(audio.raw_data, overrides={'frame_rate': new_sample_rate})
        male_audio = male_audio.set_frame_rate(audio.frame_rate)
        return male_audio
    return audio  # Return unchanged for female voice

def text_to_speech(text, gender='female'):
    """
    Convert text to speech with the specified gender voice.
    Auto-detects the language of the input text.
    Returns the path to the output file.
    """
    # Detect language
    language = detect_language(text)
    
    # Generate a unique filename
    unique_id = str(uuid.uuid4())
    temp_file = f"temp_{unique_id}.mp3"
    output_filename = f"{unique_id}_{gender}.mp3"
    output_file = os.path.join(output_dir, output_filename)
    public_file = os.path.join(public_dir, output_filename)
    
    # Create gTTS object and save to temp file
    tts = gTTS(text=text, lang=language, slow=False)
    tts.save(temp_file)
    
    # Load the audio file with pydub
    audio = AudioSegment.from_mp3(temp_file)
    
    # Adjust for gender
    modified_audio = adjust_voice(audio, gender)
    
    # Save the modified audio to both output and public directories
    modified_audio.export(output_file, format="mp3")
    modified_audio.export(public_file, format="mp3")
    
    # Remove temporary file
    os.remove(temp_file)
    
    return output_filename

class SuccessResponse(BaseModel):
    status: str = "success"
    download_link: str

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str

@app.post("/text-to-speech", response_model=SuccessResponse, responses={400: {"model": ErrorResponse}})
async def api_text_to_speech(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    gender: str = Form("female")
):
    if gender not in ['male', 'female']:
        gender = 'female'  # Default to female if invalid gender
    
    # Check if request contains direct text input
    if text and text.strip():
        # Process direct text input
        output_filename = text_to_speech(text, gender)
        
        # Generate download URL - use request base URL in production
        base_url = "http://127.0.0.1:8000"
        download_link = f"{base_url}/files/{output_filename}"
        
        return SuccessResponse(
            status="success",
            download_link=download_link
        )
    
    elif file and file.filename.endswith('.txt'):
        # Process uploaded file
        try:
            # Save the file temporarily
            temp_file_path = f"temp_{uuid.uuid4()}.txt"
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Read the content
            with open(temp_file_path, "r", encoding="utf-8") as f:
                text_content = f.read()
            
            # Remove temp file
            os.remove(temp_file_path)
            
            # Process the text
            output_filename = text_to_speech(text_content, gender)
            
            # Generate download URL - use request base URL in production
            base_url = "http://127.0.0.1:8000"
            download_link = f"{base_url}/files/{output_filename}"
            
            return SuccessResponse(
                status="success",
                download_link=download_link
            )
        except Exception as e:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": f"Error processing file: {str(e)}"
                }
            )
    
    else:
        # No valid input provided
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "text and text files only"
            }
        )

@app.get("/files/{filename}")
async def download_file(filename: str):
    """Serve the generated audio files."""
    file_path = os.path.join(public_dir, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/mpeg", filename=filename)
    raise HTTPException(status_code=404, detail="File not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


# this is the last working file of tuesday