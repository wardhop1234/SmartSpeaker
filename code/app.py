import pyaudio, sounddevice, wave, vlc
import os, subprocess, threading, time, json
import openai, requests

from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
from pydub import AudioSegment
from pydub.playback import play

import RPi.GPIO as GPIO

# files we created
from db import getPinEnabled, aliasPin, addLogEntry
from prompts import full_memory_response, process_prompt, pin_setup, pin_cleanup

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)
openai.api_key = api_key

# function that returns a list indicating if there was sound in each second of the audio file
def find_silence_seconds(filepath, chunk_size=10):
  path = Path(filepath)
  directory = path.parent
  filename = path.name
  sound = AudioSegment.from_file(filepath, format="wav")
  trim_ms = 0
  intervals = [] #For every second 1 if audio was silence and 0 if there was no silence
  i = 0
  assert chunk_size > 0  # to avoid infinite loop
  while trim_ms + chunk_size < len(sound):
    # print(abs(sound[trim_ms:trim_ms+chunk_size].dBFS))
    if (abs(sound[trim_ms:trim_ms+chunk_size].dBFS) >20
        and abs(sound[trim_ms:trim_ms+chunk_size].dBFS) <80):
      intervals.append(0)
    else:
      intervals.append(1)
    trim_ms += chunk_size
    i = i +1
  silence_seconds = []
  i = 0
  while(i<len(intervals)-100):
      if sum(intervals[i:i+100]) < 10:
        silence_seconds.append("silence")
      else:
        silence_seconds.append("sound")
      i = i + 100
  
  return silence_seconds

# function used for playing .wav files
def play_audio(filepath):
  chunk = 1024

  wf = wave.open(filepath, 'rb')

  p = pyaudio.PyAudio()

  stream = p.open(format =
                  p.get_format_from_width(wf.getsampwidth()),
                  channels = wf.getnchannels(),
                  rate = wf.getframerate(),
                  output = True)

  # read data (based on the chunk size)
  data = wf.readframes(chunk)

  # play stream (looping from beginning of file to the end)
  while data != b'':
      # writing to the stream is what *actually* plays the sound.
      stream.write(data)
      data = wf.readframes(chunk)

  # cleanup stuff.
  stream.close()    
  p.terminate()

# function used for recording .wav files
def record_audio(filepath):
  # Set the duration and parameters
  duration = 5.1  # seconds, add 0.1 to deal with rounding errors when detecting seconds of silence
  chunk = 1024
  sample_format = pyaudio.paInt16
  channels = int(os.getenv('CHANNELS'))
  fs = 44100 

  p = pyaudio.PyAudio()  

  print('Recording')

  stream = p.open(format=sample_format,
                  channels=channels,
                  rate=fs,
                  frames_per_buffer=chunk,
                  input=True)

  frames = []  # Initialize array to store frames

  # Store data in chunks for duration
  for i in range(0, int(fs / chunk * duration)):
      data = stream.read(chunk)
      frames.append(data)

  # Stop and close the stream 
  stream.stop_stream()
  stream.close()

  # Terminate the PortAudio interface
  p.terminate()

  print('Finished recording')

  # Save the recorded data as a WAV file
  wf = wave.open(filepath, 'wb')
  wf.setnchannels(channels)
  wf.setsampwidth(p.get_sample_size(sample_format))
  wf.setframerate(fs)
  wf.writeframes(b''.join(frames))
  wf.close()

# speech to text function for checking user input (this version is slightly slower but more accurate)
def retrieve_text(filepath):
  audio_file = open(filepath, "rb")
  transcript = client.audio.transcriptions.create(model = "whisper-1", file = audio_file)
  return transcript.text

# speech to text function for checking for activation word (this version is less accurate but faster)
def get_text(filepath):
  trans_key = os.getenv('TRANSCRIPTION')
  headers = {
      'Authorization': f'Token {trans_key}',
      'Content-Type': 'audio/wav',
  }
  
  t = time.time()
  with open(filepath, 'rb') as f:
      data = f.read()


  response = requests.post('https://api.deepgram.com/v1/listen', headers=headers, data=data)

  return response.json()["results"]["channels"][0]["alternatives"][0]["transcript"]

# convert the audio input into an audio response (stored in Audio Files/output.mp3) from the device
def speechToAnswer(filepath=r"Audio Files/input.wav"):
  print("before stt")
  t = time.time()
  # convert the audio file to text
  output = retrieve_text(filepath)
  print(f"after stt {time.time() - t}")
  print(output)

  t = time.time()
  print("before chat")
  # list to store the output
  result = []
  # we make 2 calls to the ChatGPT API, one for the individual message and one that incorporates memory
  t1 = threading.Thread(target = full_memory_response, args = (result, output))
  t1.start()
  chatResult , default = process_prompt(output)
  while t1.is_alive():
    if not default:
      break
  print(f"after chat {time.time() - t}")
  # memory is only used for default prompts, so if it is a default prompt, we load the result of full_memory_response into chatResult
  if (default):
    chatResult = result[0]
    addLogEntry({"role" : "user" , "content" : output})
    addLogEntry({"role" : "assistant" , "content" : chatResult})


  t = time.time()
  print("before tts")
  response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input=chatResult
  )

  response.stream_to_file(r"Audio Files/output.mp3")
  print(f"after tts {time.time() - t}")

# the device in "active" mode, where it records user input and responds to an answer
def active():
  while (1):
    chunk = 1024
    # beeps help let the user know when the device is recording
    play_audio(r"Audio Files/beep-01a.wav")

    # record user input
    record_audio(r"Audio Files/input.wav")

    # beep to signify that the device has stopped recording
    play_audio(r"Audio Files/beep-02.wav")

    time.sleep(1)

    # check if anything was actually recorded
    total = find_silence_seconds(r"Audio Files/input.wav").count("silence")
    print(total, "seconds of silence detected")
    if total > 4:
      print("returning to passive mode")
      play_audio(r"Audio Files/switch.wav")
      return

    # Now we process the recorded file in a thread while also playing audio at the same time
    t1 = threading.Thread(target = speechToAnswer)
    t1.start()

    # waiting.wav contains the generic "please wait while I process your request" speech
    play_audio(r"Audio Files/waiting.wav")

    time.sleep(1)

    # music file that is played while the user waits for a response
    wf = wave.open(r"Audio Files/BabyElephantWalk60.wav", 'rb')

    p = pyaudio.PyAudio()

    stream = p.open(format =
                    p.get_format_from_width(wf.getsampwidth()),
                    channels = wf.getnchannels(),
                    rate = wf.getframerate(),
                    output = True)

    # read data (based on the chunk size)
    data = wf.readframes(chunk)

    # while the thread is active, continue playing music
    while t1.is_alive():
      stream.write(data)
      data = wf.readframes(chunk)
    
    # cleanup stuff.
    stream.close()    
    p.terminate()

    time.sleep(1)

    print('Playing back')
    starttime = time.time()
    print("before playback")
    # use vlc media player to play audio in mp3 format w/o the need to convert back to wav
    os.system("cvlc --play-and-exit Audio\ Files/output.mp3")
    print(f"after playback {time.time() - starttime}")

# check if the activation command was spoken
def check_active(filepath):
  text = get_text(filepath)
  print(f"text checked: {text}")
  if "activate" in text.lower():
    return 1
  elif "exit" in text.lower():
    return 2
  return 0


# MAIN FUNCTION STARTS HERE

print("powering on")

# Run GPIO setup for voice commands
pin_setup()
t = time.time()

play_audio(r"Audio Files/on.wav")

# this is the main loop for passive mode
while (1):
  # record 5 seconds of audio and check it for noise
  record_audio(r"Audio Files/activate.wav")
  t = time.time()
  total = find_silence_seconds(r"Audio Files/activate.wav").count("silence")
  if total < 5:
    # check if "activate" was spoken
    print("check active")
    # power on indicator light
    GPIO.output(22, True)
    status = check_active(r"Audio Files/activate.wav")
    if status == 1:
      # in this case activate was found, so enter active mode
      print("entering active mode")
      active()
    elif status == 2:
      # in this case exit was found, so power down
      play_audio(r"Audio Files/off.wav")
      GPIO.output(22, False)
      print("powering off")
      break
    GPIO.output(22, False)
pin_cleanup()