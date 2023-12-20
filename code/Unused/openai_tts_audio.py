"""
import base64
import requests
import openai
# OpenAI API Key
api_key = ""

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Path to your image
image_path = "dejavu.jpeg"

# Getting the base64 string
base64_image = encode_image(image_path)

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

payload = {
    "model": "gpt-4-vision-preview",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "Provide a description of this image. So when I describe the image in Google Search, it can determine what it is based on my location"
          },
          {
            "type": "image_url",
            "image_url": {
              "url": f"data:image/jpeg;base64,{base64_image}"
            }
          }
        ]
      }
    ],
    "max_tokens": 300
}

response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

print(response.json())
"""
#import pyaudio
import wave
from openai import OpenAI


api_key = "{openai_api_key}"
client = OpenAI(api_key=api_key)
string = """Ladies and gentlemen, distinguished guests, and fellow participants, it is an honor to address you today. In this ever-evolving world, technology continues to push the boundaries of what we can achieve. Artificial intelligence has emerged as a powerful tool, enhancing our lives in countless ways. One remarkable example is Text-to-Speech (TTS) technology, which enables machines to convert written text into natural-sounding speech. TTS has revolutionized accessibility, providing a voice to those who are unable to speak. It has also found applications in entertainment, education, and customer service. Let us embrace this incredible innovation and harness its potential to create a more inclusive and connected society. Together, we can amplify voices and break barriers. Thank you."""



response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input=string[:20]
)


response.stream_to_file("audio.mp3")

#opus_file = "audio.opus"
#audio = AudioSegment.from_file(opus_file, format="opus")

# Play the audio
#play(audio)
import subprocess 
import os

import ffmpeg
# convert mp3 to wav file 
subprocess.call(['ffmpeg', '-i', 'audio.mp3', 
                 'audio.wav'])
#sound = AudioSegment.from_mp3("audio.mp3")
#sound.export("output.wav", format="wav")
import vlc
instance = vlc.Instance('--aout=alsa')
p = instance.media_player_new()
m = instance.media_new('something.mp3') 
p.set_media(m)
p.play() 
p.pause() 
wf = wave.open('audio.wav', 'rb')




