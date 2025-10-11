import os 
import sys 
import time 
import json 
import pyaudio 
from vosk import Model, KaldiRecognizer 
 
model = Model("vosk-model-small-en-us-0.15")
recognizer = KaldiRecognizer(model, 16000)


p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
stream.start_stream()

print("Listening...")

while True:
    data = stream.read(4000, exception_on_overflow = False)
    if len(data) == 0:
        break
    if recognizer.AcceptWaveform(data):
        result = recognizer.Result()
        text = json.loads(result).get("text", "")
        if text:
            print(f"Recognized: {text}")
    else:
        partial_result = recognizer.PartialResult()
        partial_text = json.loads(partial_result).get("partial", "")
        if partial_text:
            sys.stdout.write(f"\rPartial: {partial_text}")
            sys.stdout.flush()
