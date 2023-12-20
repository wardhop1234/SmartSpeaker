
from os import path                                                 

from pydub import AudioSegment

def m2w(src, dest):
  sound = AudioSegment.from_mp3(src)
  sound.export(dest, format="wav")

def w2m(src, dest):
  sound = AudioSegment.from_wav(src)
  sound.export(dest, format="mp3")
