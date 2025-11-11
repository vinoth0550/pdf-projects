
# text to speech

from gtts import gTTS
import os

def text_to_speech(text, language='en', output_file='output.mp3'):

    # Create gTTS object

    tts = gTTS(text=text, lang=language, slow=False)
    
    # Save to file
    tts.save(output_file)
    
    # Play the audio file 

    os.system(f"start {output_file}")  # Windows
    # os.system(f"mpg123 {output_file}")  # Linux
    # os.system(f"afplay {output_file}")  # macOS

# Example usage
text_to_speech("பைதான் சமூகத்திற்கு வருக.", language='ta')
text_to_speech("welcome to Python community.", language='en')
text_to_speech("पायथन समुदाय में आपका स्वागत है", language='hi')
