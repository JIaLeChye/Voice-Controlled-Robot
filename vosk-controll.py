import os
import sys
import json
import tkinter as tk
from tkinter import ttk, messagebox
import vosk
import pyaudio
import subprocess
import threading

# from  RPi_Robot_Hat_Lib import RobotController


# Training keywords dictionary with synonyms for robot movements
MOVEMENT_TRAINING_KEYWORDS = {
    "forward": ["forward", "move forward", "go forward", "go straight", "ahead"],
    "backward": ["backward", "back", "reverse", "move back", "go back"],
    "left": ["left", "turn left", "go left", "rotate left"],
    "right": ["right", "turn right", "go right", "rotate right"],
    "horizontal_left": ["slide left", "strafe left", "shift left", "drift left"],
    "horizontal_right": ["slide right", "strafe right", "shift right", "drift right"],
    "stop": ["stop", "halt", "freeze", "brake", "stay"],
    "pause": ["pause", "wait", "hold"],
    "resume": ["resume", "continue", "go"],
}

# Default calibration settings
DEFAULT_CALIBRATION = {
    "motor_speed": {
        "forward": 50,
        "backward": 50,
        "turn_speed": 40,
        "strafe_speed": 45
    },
    "voice_recognition": {
        "confidence_threshold": 0.7,
        "volume_threshold": 0.3
    },
    "movement_duration": {
        "default_duration": 1.0,
        "turn_duration": 0.5
    }
}


class VoskModelChecker:
    """Handles Vosk model verification and downloading."""
    
    def __init__(self):
        self.model = None

    def check_model(self):
        """Check if Vosk model exists, download if necessary, and load it."""
        model_path = "vosk-model-small-en-us-0.15"
        
        if not os.path.exists(model_path):
            print("Model not found.")
            print("Checking internet connection...")
            
            try:
                subprocess.run(["ping", "-c", "1", "google.com"], check=True, capture_output=True)
                print("Internet connection is available.")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("No internet connection. Please check your connection and try again.")
                return False
            
            print("Downloading model...")
            try:
                subprocess.run(["wget", "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip", "-O", "model.zip"], check=True)
                subprocess.run(["unzip", "model.zip", "-d", "model"], check=True)
                subprocess.run(["rm", "model.zip"], check=True)
                print("Model downloaded and unpacked successfully.")
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                print(f"Failed to download or unpack model: {e}")
                return False
            
            # The model path needs to be updated to where unzip places it
            model_path = "model/vosk-model-small-en-us-0.15"
            if not os.path.exists(model_path):
                print(f"Model directory not found at expected path: {model_path}")
                return False

        self.model = vosk.Model(model_path)
        print("Model loaded successfully.")
        return True


class CalibrationManager:
    """Manages robot calibration settings."""
    
    def __init__(self, config_file="robot_calibration.json"):
        self.config_file = config_file
        self.settings = self.load_calibration()
    
    def load_calibration(self):
        """Load calibration settings from file or use defaults."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading calibration: {e}")
                return DEFAULT_CALIBRATION.copy()
        return DEFAULT_CALIBRATION.copy()
    
    def save_calibration(self):
        """Save calibration settings to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            print("Calibration saved successfully")
            return True
        except Exception as e:
            print(f"Error saving calibration: {e}")
            return False
    
    def get_setting(self, category, key):
        """Get a specific calibration setting."""
        return self.settings.get(category, {}).get(key, 0)
    
    def set_setting(self, category, key, value):
        """Set a specific calibration setting."""
        if category not in self.settings:
            self.settings[category] = {}
        self.settings[category][key] = value
    
    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        self.settings = DEFAULT_CALIBRATION.copy()
        self.save_calibration()


class CalibrationWindow:
    """Calibration UI window."""
    
    def __init__(self, parent, calibration_manager, movement_controller):
        self.window = tk.Toplevel(parent)
        self.window.title("Robot Calibration")
        self.window.geometry("600x500")
        self.window.resizable(False, False)
        
        self.calibration = calibration_manager
        self.movement = movement_controller
        
        self._create_ui()
    
    def _create_ui(self):
        """Create calibration UI components."""
        # Title
        title = tk.Label(
            self.window,
            text="Robot Calibration Center",
            font=("Arial", 16, "bold")
        )
        title.pack(pady=10)
        
        # Create notebook (tabs)
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Motor Speed Tab
        motor_frame = ttk.Frame(notebook)
        notebook.add(motor_frame, text="Motor Speed")
        self._create_motor_tab(motor_frame)
        
        # Voice Recognition Tab
        voice_frame = ttk.Frame(notebook)
        notebook.add(voice_frame, text="Voice Recognition")
        self._create_voice_tab(voice_frame)
        
        # Movement Duration Tab
        duration_frame = ttk.Frame(notebook)
        notebook.add(duration_frame, text="Movement Duration")
        self._create_duration_tab(duration_frame)
        
        # Bottom buttons
        button_frame = tk.Frame(self.window)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(
            button_frame,
            text="Save Calibration",
            command=self._save_calibration,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15
        ).pack(side='left', padx=5)
        
        tk.Button(
            button_frame,
            text="Reset to Defaults",
            command=self._reset_calibration,
            bg="#FF9800",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15
        ).pack(side='left', padx=5)
        
        tk.Button(
            button_frame,
            text="Close",
            command=self.window.destroy,
            bg="#f44336",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15
        ).pack(side='right', padx=5)
    
    def _create_motor_tab(self, parent):
        """Create motor speed calibration controls."""
        tk.Label(
            parent,
            text="Adjust motor speeds for different movements",
            font=("Arial", 10)
        ).pack(pady=10)
        
        # Forward speed
        self._create_slider(
            parent,
            "Forward Speed:",
            "motor_speed",
            "forward",
            0, 100,
            lambda v: self.movement.test_forward()
        )
        
        # Backward speed
        self._create_slider(
            parent,
            "Backward Speed:",
            "motor_speed",
            "backward",
            0, 100,
            lambda v: self.movement.test_backward()
        )
        
        # Turn speed
        self._create_slider(
            parent,
            "Turn Speed:",
            "motor_speed",
            "turn_speed",
            0, 100,
            lambda v: self.movement.test_turn()
        )
        
        # Strafe speed
        self._create_slider(
            parent,
            "Strafe Speed:",
            "motor_speed",
            "strafe_speed",
            0, 100,
            lambda v: self.movement.test_strafe()
        )
    
    def _create_voice_tab(self, parent):
        """Create voice recognition calibration controls."""
        tk.Label(
            parent,
            text="Adjust voice recognition sensitivity",
            font=("Arial", 10)
        ).pack(pady=10)
        
        # Confidence threshold
        self._create_slider(
            parent,
            "Confidence Threshold:",
            "voice_recognition",
            "confidence_threshold",
            0.0, 1.0,
            None,
            resolution=0.05
        )
        
        # Volume threshold
        self._create_slider(
            parent,
            "Volume Threshold:",
            "voice_recognition",
            "volume_threshold",
            0.0, 1.0,
            None,
            resolution=0.05
        )
        
        # Info text
        info = tk.Label(
            parent,
            text="Higher confidence = more accurate but less responsive\n"
                 "Lower confidence = more responsive but may have false positives",
            font=("Arial", 9),
            fg="gray",
            justify='left'
        )
        info.pack(pady=20)
    
    def _create_duration_tab(self, parent):
        """Create movement duration calibration controls."""
        tk.Label(
            parent,
            text="Adjust default movement durations (seconds)",
            font=("Arial", 10)
        ).pack(pady=10)
        
        # Default duration
        self._create_slider(
            parent,
            "Default Duration:",
            "movement_duration",
            "default_duration",
            0.1, 5.0,
            None,
            resolution=0.1
        )
        
        # Turn duration
        self._create_slider(
            parent,
            "Turn Duration:",
            "movement_duration",
            "turn_duration",
            0.1, 3.0,
            None,
            resolution=0.1
        )
    
    def _create_slider(self, parent, label, category, key, min_val, max_val, test_callback, resolution=1):
        """Create a labeled slider with value display and test button."""
        frame = tk.Frame(parent)
        frame.pack(fill='x', padx=20, pady=10)
        
        # Label
        tk.Label(frame, text=label, width=20, anchor='w').pack(side='left')
        
        # Current value
        current_value = self.calibration.get_setting(category, key)
        value_var = tk.DoubleVar(value=current_value)
        
        # Value display
        value_label = tk.Label(frame, text=f"{current_value:.2f}", width=8)
        value_label.pack(side='right', padx=5)
        
        # Test button (if callback provided)
        if test_callback:
            test_btn = tk.Button(
                frame,
                text="Test",
                command=test_callback,
                width=6
            )
            test_btn.pack(side='right', padx=5)
        
        # Slider
        slider = tk.Scale(
            frame,
            from_=min_val,
            to=max_val,
            orient='horizontal',
            resolution=resolution,
            variable=value_var,
            showvalue=0,
            command=lambda v: self._update_value(category, key, value_var, value_label)
        )
        slider.pack(side='right', fill='x', expand=True, padx=5)
    
    def _update_value(self, category, key, var, label):
        """Update calibration value when slider changes."""
        value = var.get()
        self.calibration.set_setting(category, key, value)
        label.config(text=f"{value:.2f}")
    
    def _save_calibration(self):
        """Save calibration to file."""
        if self.calibration.save_calibration():
            messagebox.showinfo("Success", "Calibration saved successfully!")
        else:
            messagebox.showerror("Error", "Failed to save calibration")
    
    def _reset_calibration(self):
        """Reset calibration to defaults."""
        if messagebox.askyesno("Confirm Reset", "Reset all calibration to default values?"):
            self.calibration.reset_to_defaults()
            self.window.destroy()
            messagebox.showinfo("Reset Complete", "Calibration reset to defaults. Please reopen calibration window.")


class VoiceRecognition:
    """GUI application for Vosk voice training and robot control."""
    
    def __init__(self, master):
        self.master = master
        self.training_keywords = MOVEMENT_TRAINING_KEYWORDS
        self.is_listening = False
        self.listening_thread = None
        
        # Initialize components
        self.model_checker = VoskModelChecker()
        if not self.model_checker.check_model():
            messagebox.showerror("Error", "Vosk model not available. Exiting.")
            self.master.quit()
            return
            
        self.calibration = CalibrationManager()
        self.robot = RobotController(self.calibration)
        
        # Create a grammar from the training keywords for focused recognition
        all_keywords = [keyword for keywords in self.training_keywords.values() for keyword in keywords]
        grammar = json.dumps(all_keywords)

        # Initialize Vosk recognizer with the specific grammar
        self.recognizer = vosk.KaldiRecognizer(self.model_checker.model, 16000, grammar)
        
        # Initialize PyAudio
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=8192
        )
        
        # Setup window
        self.master.title("Vosk Robot Controller")
        self.master.geometry("400x350")
        
        # Initialize UI components
        self._create_widgets()
        
        # Load and display keywords
        self._display_keywords()

    def _create_widgets(self):
        """Create and layout GUI widgets."""
        # Title
        self.label = tk.Label(
            self.master, 
            text="Vosk Robot Controller",
            font=("Arial", 14, "bold")
        )
        self.label.pack(pady=10)

        # Status Label
        self.status_label = tk.Label(
            self.master, 
            text="Status: Idle",
            font=("Arial", 12)
        )
        self.status_label.pack(pady=5)

        # Recognized Text Label
        self.recognized_text_label = tk.Label(
            self.master, 
            text="",
            font=("Arial", 10, "italic"),
            fg="gray"
        )
        self.recognized_text_label.pack(pady=(0, 10))
        
        # Button frame
        button_frame = tk.Frame(self.master)
        button_frame.pack(pady=10)
        
        # Calibration button
        self.calibration_button = tk.Button(
            button_frame, 
            text="Calibration",
            command=self.open_calibration,
            width=15,
            height=2,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold")
        )
        self.calibration_button.pack(pady=5)
        
        # Start/Stop Recognition button
        self.recognition_button = tk.Button(
            button_frame, 
            text="Start Recognition",
            command=self.toggle_recognition,
            width=15,
            height=2,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold")
        )
        self.recognition_button.pack(pady=5)

        # Quit button
        self.quit_button = tk.Button(
            button_frame, 
            text="Quit", 
            command=self.quit,
            width=15,
            height=2,
            bg="#f44336",
            fg="white",
            font=("Arial", 10, "bold")
        )
        self.quit_button.pack(pady=5)
    
    def open_calibration(self):
        """Open calibration window."""
        if self.is_listening:
            messagebox.showwarning("Warning", "Please stop recognition before opening calibration.")
            return
        CalibrationWindow(self.master, self.calibration, self.robot)

    def toggle_recognition(self):
        """Start or stop voice recognition."""
        if self.is_listening:
            self.stop_recognition()
        else:
            self.start_recognition()

    def start_recognition(self):
        """Start voice recognition in a separate thread."""
        self.is_listening = True
        self.status_label.config(text="Status: Listening...")
        self.recognition_button.config(text="Stop Recognition", bg="#ff9800")
        
        self.listening_thread = threading.Thread(target=self.listen)
        self.listening_thread.daemon = True
        self.listening_thread.start()
        print("Voice recognition started.")

    def stop_recognition(self):
        """Stop voice recognition."""
        self.is_listening = False
        # The thread will stop on its own since the loop condition `self.is_listening` will be false
        print("\nStopping voice recognition...")
        self.status_label.config(text="Status: Idle")
        self.recognition_button.config(text="Start Recognition", bg="#4CAF50")

    def listen(self):
        """Listen for voice commands continuously."""
        self.stream.start_stream()
        while self.is_listening:
            data = self.stream.read(4096, exception_on_overflow=False)
            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                text = result.get('text', '').lower()
                if text:
                    # Update GUI in the main thread
                    self.master.after(0, self.update_recognized_text, text)
                    self.process_command(text)
        self.stream.stop_stream()
        print("Voice recognition stopped.")

    def update_recognized_text(self, text):
        """Update the recognized text label."""
        self.recognized_text_label.config(text=f"Heard: \"{text}\"")

    def process_command(self, text):
        """Process the recognized text and command the robot."""
        for command, keywords in MOVEMENT_TRAINING_KEYWORDS.items():
            if text in keywords:
                print(f"Command recognized: '{text}' -> {command.upper()}")
                if command == "forward":
                    self.robot.forward()
                elif command == "backward":
                    self.robot.backward()
                elif command == "left":
                    self.robot.left()
                elif command == "right":
                    self.robot.right()
                elif command == "horizontal_left":
                    self.robot.horizontal_left()
                elif command == "horizontal_right":
                    self.robot.horizontal_right()
                elif command == "stop":
                    self.robot.stop()
                elif command in ["pause", "resume"]:
                    pass
                return

    def _display_keywords(self):
        """Display training keywords in a formatted way."""
        print("\n" + "="*60)
        print("ROBOT MOVEMENT TRAINING KEYWORDS".center(60))
        print("="*60)
        
        for command, synonyms in self.training_keywords.items():
            print(f"\n{command.upper()}")
            print(f"   Synonyms: {', '.join(synonyms)}")
        
        print("\n" + "="*60)
        print(f"Total movement commands: {len(self.training_keywords)}")
        print("="*60 + "\n")

    def quit(self):
        """Clean up and exit the application."""
        if self.is_listening:
            self.stop_recognition()
        
        # Wait for the listening thread to finish
        if self.listening_thread and self.listening_thread.is_alive():
            self.listening_thread.join(timeout=1.0)

        self.stream.close()
        self.p.terminate()
        self.master.quit()
        self.master.destroy()
        print("Application closed.")


# Placeholder for the actual robot controller library
class RobotController:
    """A placeholder class for the robot's movement controls."""
    def __init__(self, calibration_manager):
        self.calibration = calibration_manager
        print("Initialized placeholder RobotController.")

    def forward(self):
        speed = self.calibration.get_setting("motor_speed", "forward")
        duration = self.calibration.get_setting("movement_duration", "default_duration")
        print(f"Action: Move forward (speed: {speed}, duration: {duration})")

    def backward(self):
        speed = self.calibration.get_setting("motor_speed", "backward")
        duration = self.calibration.get_setting("movement_duration", "default_duration")
        print(f"Action: Move backward (speed: {speed}, duration: {duration})")

    def left(self):
        speed = self.calibration.get_setting("motor_speed", "turn_speed")
        duration = self.calibration.get_setting("movement_duration", "turn_duration")
        print(f"Action: Turn left (speed: {speed}, duration: {duration})")

    def right(self):
        speed = self.calibration.get_setting("motor_speed", "turn_speed")
        duration = self.calibration.get_setting("movement_duration", "turn_duration")
        print(f"Action: Turn right (speed: {speed}, duration: {duration})")

    def horizontal_left(self):
        speed = self.calibration.get_setting("motor_speed", "strafe_speed")
        duration = self.calibration.get_setting("movement_duration", "default_duration")
        print(f"Action: Strafe left (speed: {speed}, duration: {duration})")

    def horizontal_right(self):
        speed = self.calibration.get_setting("motor_speed", "strafe_speed")
        duration = self.calibration.get_setting("movement_duration", "default_duration")
        print(f"Action: Strafe right (speed: {speed}, duration: {duration})")

    def stop(self):
        print("Action: Stop")

    # Test methods for calibration
    def test_forward(self):
        print("Testing forward movement...")
        self.forward()
    
    def test_backward(self):
        print("Testing backward movement...")
        self.backward()
    
    def test_turn(self):
        print("Testing turn movement...")
        self.left()
    
    def test_strafe(self):
        print("Testing strafe movement...")
        self.horizontal_left()

def main():
    """Main entry point for the application."""
    try:
        root = tk.Tk()
        app = VoiceRecognition(root)
        root.mainloop()
        
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        print("Application ended.")


if __name__ == "__main__":
    main()
