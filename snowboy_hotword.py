from snowboy import snowboydecoder
import sys
import os

# Suppress JACK audio server error messages
# JACK is not needed - PyAudio will fall back to ALSA
import warnings
warnings.filterwarnings('ignore')

def detected_callback():
    print("Hotword detected!")



model = "/home/vboxuser/Desktop/snowboy/examples/Python/resources/models/snowboy.umdl"

detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5)
print("Listening... Press Ctrl+C to exit")

try:
    detector.start(detected_callback=detected_callback,
                   interrupt_check=lambda: False,
                   sleep_time=0.03)
except KeyboardInterrupt:
    print("\nStopping...")
finally:
    detector.terminate()