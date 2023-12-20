import torch
from TTS.api import TTS

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"

# List available 🐸TTS models
print(TTS().list_models())

# Init TTS
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v1").to(device)

wav = tts.tts(text="Hello world!", speaker_wav="my/cloning/audio.wav", language="en")
