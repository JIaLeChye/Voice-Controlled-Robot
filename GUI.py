#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox 
from snowboy import snowboydecoder
import os
import threading
import pyaudio 
import wave 
import sys
import time 
import subprocess 


class GUI:
    def __init__(self, master):
        self.voicerecognition = voicerecognition()
        self.master = master
        master.title("Voice Controlled Robot")

        self.label = tk.Label(master, text="Voice Controlled Robot", font=("Helvetica", 16))
        self.label.pack(pady=10)

        self.status_label = tk.Label(master, text="Status: Idle", font=("Helvetica", 12))
        self.status_label.pack(pady=5)

        self.start_button = tk.Button(master, text="Start Listening", command=self.start_listening)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(master, text="Stop Listening", command=self.stop_listening)
        self.stop_button.pack(pady=5)

        self.quit_button = tk.Button(master, text="Quit", command=self.quit_app)
        self.quit_button.pack(pady=20)

        self.listening_thread = None
        self.is_listening = False

    def start_listening(self):
        if self.is_listening:
            messagebox.showinfo("Info", "Already listening.")
            return

        self.is_listening = True
        self.status_label.config(text="Status: Listening...")
        
        self.listening_thread = threading.Thread(target=self.voicerecognition.start)
        self.listening_thread.daemon = True
        self.listening_thread.start()
        
        messagebox.showinfo("Info", "Started listening for wake word.")

    def stop_listening(self):
        if not self.is_listening:
            messagebox.showinfo("Info", "Not currently listening.")
            return
            
        self.is_listening = False
        self.status_label.config(text="Status: Idle")
        self.voicerecognition.stop()
        messagebox.showinfo("Info", "Stopped listening.")
    
    def train_model(self):
        messagebox.showinfo("Info", "Training model... ")
        self.voicerecognition.train()

    def quit_app(self):
        if self.is_listening:
            self.stop_listening()
        self.master.quit()

class voicerecognition:
    def __init__(self):
        model = os.path.join("models", "snowboy.umdl")
            # Ensure the model file exists in the specified path
        if not os.path.isfile(model):
            raise FileNotFoundError(f"Model file not found: {model}")
        
        else: 
            self.detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5)

    def start(self):
        print("Voice recognition started.")
        self.detector.start(detected_callback=self.on_wake_word, sleep_time=0.03)

    def on_wake_word(self):
        print("Wake word detected!")

    def stop(self):
        print("Voice recognition stopped.")
        self.detector.terminate()

class ModelTraining:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.OUTPUT_DIR = "resources/samples/"
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.CHUNK = 1024
        self.RECORDING_TIME = 3.0  # 3 seconds
        self.HOTWORD_NAME = None 
        if self.HOTWORD_NAME is None:
            self.HOTWORD_NAME = input("Please enter a hotword name (default is 'PiRobot'): ") or "PiRobot"
            print(f"Hotword name set to: {self.HOTWORD_NAME}")
        if not os.path.exists(self.OUTPUT_DIR):
           os.makedirs(self.OUTPUT_DIR)
           print("Defined directory not found - creating...")
           print(f"Created directory: {self.OUTPUT_DIR}")
        else:
           print(f"Directory already exists: {self.OUTPUT_DIR}")

    def record_samples(self):
       print("Recording new samples...")
       ## Record 3 audio samples for training

       for i in range(3):
           print(f"Recording sample {i + 1}...")
           input("Press Enter to start recording...",i)
           stream = self.audio.open(format=self.FORMAT, channels=self.CHANNELS,
                               rate=self.RATE, input=True,
                               frames_per_buffer=self.CHUNK)
           frames = []
           for j in range(0, int(self.RATE / self.CHUNK * self.RECORDING_TIME)):
               try: 
                   data = stream.read(self.CHUNK)
                   frames.append(data)
               except (Exception, IOError) as e:
                   print(f"Error occurred while recording: {e}\n")
                   print("Please check your microphone settings and try again.")
           stream.stop_stream()
           stream.close()
           # Save the recorded audio to a WAV file
           os.makedirs(self.OUTPUT_DIR, exist_ok=True)
           with wave.open(os.path.join(self.OUTPUT_DIR, f"sample_{i + 1}.wav"), 'wb') as wf:
               wf.setnchannels(self.CHANNELS)
               wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
               wf.setframerate(self.RATE)
               wf.writeframes(b''.join(frames))
           print(f"Sample {i + 1} saved.")
           time.sleep(1)  # Short pause between recordings
       self.audio.terminate()

    def train_model(self):
        self.record_samples()
        print("Start Training hotword model...")
        enrol_path = os.path.join("tools", "enroll.py")
        subprocess.run()
if __name__ == "__main__":
    root = tk.Tk()
    gui = GUI(root)
    root.mainloop()