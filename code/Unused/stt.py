import openai
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)
openai.api_key = api_key

# def retrieve_text(filepath):
#   audio_file = open(filepath, "rb")
#   transcript = client.audio.transcriptions.create(model = "whisper-1", file = audio_file)
#   print(transcript)
#   return transcript.text

# print(retrieve_text(r"Audio Files/input.wav"))

response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input="Switching to passive mode."
)

response.stream_to_file(r"Audio Files/switch.mp3")