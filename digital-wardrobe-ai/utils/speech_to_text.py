from openai import OpenAI
from dotenv import load_dotenv  # load environment variables from .env file
load_dotenv()

def get_text_from_speech(input_file):
    client = OpenAI()
    audio_file= open(input_file, "rb")
    transcription = client.audio.transcriptions.create(
        model="gpt-4o-transcribe", 
        file=audio_file
    )
    print(transcription.text)

    return transcription.text