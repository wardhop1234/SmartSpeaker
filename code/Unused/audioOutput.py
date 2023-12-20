import pyaudio
import wave
import os

from openai import OpenAI
from dotenv import load_dotenv

api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input="Ladies and gentlemen, distinguished guests, and fellow participants, it is an honor to address you today. In this ever-evolving world, technology continues to push the boundaries of what we can achieve. Artificial intelligence has emerged as a powerful tool, enhancing our lives in countless ways. One remarkable example is Text-to-Speech (TTS) technology, which enables machines to convert written text into natural-sounding speech. TTS has revolutionized accessibility, providing a voice to those who are unable to speak. It has also found applications in entertainment, education, and customer service. Let us embrace this incredible innovation and harness its potential to create a more inclusive and connected society. Together, we can amplify voices and break barriers. Thank you.",
)

response.stream_to_file("output.wav")

# Open the file
wf = wave.open('BabyElephantWalk60.wav', 'rb')

# Create an interface to PortAudio
p = pyaudio.PyAudio()

# Open a .Stream object to write the WAV file to
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)

# Read data
data = wf.readframes(1024)

# Play the sound by writing the audio data to the stream
while data != '':
    stream.write(data)
    data = wf.readframes(1024)

# Close and terminate everything properly
stream.stop_stream()
stream.close()
p.terminate()
