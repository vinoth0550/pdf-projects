
# text to speech with multi-language support

import os
from gtts import gTTS
import langdetect
from pydub import AudioSegment
from pydub.effects import speedup
import nltk
from nltk.tokenize import sent_tokenize
import speech_recognition as sr

# Download necessary NLTK data
nltk.download('punkt', quiet=True)

# Create input and output directories if they don't exist
input_dir = 'input'
output_dir = 'output'
os.makedirs(input_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

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
        # Lower pitch by playing it slower (0.9x speed)
        octaves = -0.2
        new_sample_rate = int(audio.frame_rate * (2.0 ** octaves))
        male_audio = audio._spawn(audio.raw_data, overrides={'frame_rate': new_sample_rate})
        male_audio = male_audio.set_frame_rate(audio.frame_rate)
        return male_audio
    return audio  # Return unchanged for female voice

def text_to_speech(input_file, gender='female'):
    """
    Convert text from a file to speech with the specified gender voice.
    Auto-detects the language of the input text.
    """
    # Read the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Detect language
    language = detect_language(text)
    print(f"Detected language: {language}")
    
    # Create base filename from input filename
    base_filename = os.path.splitext(os.path.basename(input_file))[0]
    temp_file = f"temp_{base_filename}.mp3"
    output_file = f"{output_dir}/{base_filename}_{gender}.mp3"
    
    # Create gTTS object and save to temp file
    tts = gTTS(text=text, lang=language, slow=False)
    tts.save(temp_file)
    
    # Load the audio file with pydub
    audio = AudioSegment.from_mp3(temp_file)
    
    # Adjust for gender
    modified_audio = adjust_voice(audio, gender)
    
    # Save the modified audio
    modified_audio.export(output_file, format="mp3")
    
    # Remove temporary file
    os.remove(temp_file)
    
    print(f"Created {gender} voice audio: {output_file}")
    return output_file

def process_all_input_files():
    """Process all text files in the input directory."""
    input_files = [f for f in os.listdir(input_dir) if f.endswith('song.txt')]
    
    if not input_files:
        print(f"No text files found in {input_dir} folder. Please add .txt files.")
        # Create a sample file to demonstrate
        sample_file = f"{input_dir}/sample.txt"
        with open(sample_file, 'w', encoding='utf-8') as f:
            f.write("This is a sample English text.\nதமிழில் ஒரு உதாரணம்.\nहिंदी में एक उदाहरण।")
        print(f"Created a sample file: {sample_file}")
        input_files = [os.path.basename(sample_file)]
    
    for input_file in input_files:
        file_path = os.path.join(input_dir, input_file)
        # Create both male and female versions
        text_to_speech(file_path, 'male')
        text_to_speech(file_path, 'female')

if __name__ == "__main__":
    print("Text-to-Speech Converter - Multi-language with Male/Female voices")
    print("=" * 70)
    print(f"Input files should be placed in the '{input_dir}' folder as .txt files")
    print(f"Output audio files will be saved to the '{output_dir}' folder")
    print("=" * 70)
    
    process_all_input_files()
    print("Processing complete!")
