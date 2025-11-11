import asyncio
import os
import edge_tts
import langdetect

# Create directories
input_dir = 'input'
output_dir = 'output'
os.makedirs(input_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

# Language to voice mapping
VOICE_MAPPING = {
    'en': {
        'male': 'en-US-GuyNeural',
        'female': 'en-US-JennyNeural'
    },
    'ta': {
        'male': 'ta-IN-ValluvarNeural',
        'female': 'ta-IN-PallaviNeural'
    },
    'hi': {
        'male': 'hi-IN-MadhurNeural',
        'female': 'hi-IN-SwaraNeural'
    },
    # Add more languages as needed
}

# Default voices for unsupported languages
DEFAULT_VOICES = {
    'male': 'en-US-GuyNeural',
    'female': 'en-US-JennyNeural'
}

def detect_language(text):
    try:
        return langdetect.detect(text)
    except:
        return 'en'

async def text_to_speech_edge(input_file, gender='female'):
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    language = detect_language(text)
    print(f"Detected language: {language}")
    
    base_filename = os.path.splitext(os.path.basename(input_file))[0]
    output_file = f"{output_dir}/{base_filename}_{gender}.mp3"
    
    # Select voice
    if language in VOICE_MAPPING and gender in VOICE_MAPPING[language]:
        voice = VOICE_MAPPING[language][gender]
    else:
        voice = DEFAULT_VOICES[gender]
        print(f"No specific {gender} voice found for {language}, using {voice}")
    
    # Generate speech
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)
    
    print(f"Created {gender} voice audio: {output_file}")
    return output_file

async def process_all_input_files_edge():
    input_files = [f for f in os.listdir(input_dir) if f.endswith('test.txt')]
    
    if not input_files:
        print(f"No text files found in {input_dir} folder. Creating a sample...")
        sample_file = f"{input_dir}/sample.txt"
        with open(sample_file, 'w', encoding='utf-8') as f:
            f.write("This is a sample English text.\nதமிழில் ஒரு உதாரணம்.\nहिंदी में एक उदाहरण।")
        print(f"Created sample file: {sample_file}")
        input_files = [os.path.basename(sample_file)]
    
    for input_file in input_files:
        file_path = os.path.join(input_dir, input_file)
        await text_to_speech_edge(file_path, 'male')
        await text_to_speech_edge(file_path, 'female')

# Run with Edge-TTS for actual male voices
if __name__ == "__main__":
    print("Edge TTS Converter - Multi-language with genuine Male & Female voices")
    print("=" * 70)
    
    asyncio.run(process_all_input_files_edge())
    print("Processing complete!")
