# Voice Controlled Robot

This project is a Python-based application for controlling a robot using voice commands. It features a graphical user interface (GUI) built with Tkinter, offline speech recognition powered by the Vosk toolkit, and a robust calibration system to fine-tune the robot's behavior.

**Latest Update (October 2025)**: Added support for specific USB audio devices to resolve ALSA errors, enhanced calibration system with real-time testing, and created a Robot Controller (RC) version with full hardware integration.

## Features

- **Offline Voice Control**: Uses the Vosk library for accurate, offline speech recognition. No internet connection is required after the initial model download.
- **High-Accuracy Command Recognition**: Implements a focused grammar built from a keyword list, ensuring the recognizer is optimized to detect specific robot commands.
- **Graphical User Interface (GUI)**: A user-friendly interface to start/stop recognition, view recognized commands in real-time, and access calibration settings.
- **Dynamic Calibration Panel**: A comprehensive calibration window allows for real-time adjustments of:
  - **Motor Speeds**: Forward, backward, turn, and strafe speeds with live testing capabilities.
  - **Voice Recognition**: Confidence and volume thresholds with precision controls.
  - **Movement Durations**: Default and turn durations for fine-tuned control.
- **Automatic Model Downloader**: Automatically checks for the required Vosk speech model and downloads it if not found.
- **Audio Device Selection**: Automatically detects and uses USB audio devices (e.g., "USB PnP Sound Device") to avoid ALSA configuration errors on Raspberry Pi and Linux systems.
- **ALSA Error Suppression**: Clean terminal output with suppressed ALSA warnings that don't affect functionality.
- **Two Versions Available**:
  - `vosk-controll.py`: Simulation version with placeholder robot controls for testing.
  - `vosk-controll(RC).py`: Robot Controller version with full RPi_Robot_Hat_Lib integration for actual hardware control.
- **Modular and Extendable**: The robot control logic is abstracted into a `MovementController` class, making it easy to adapt to different hardware configurations.
- **Robust and Modern Code**: Uses the `subprocess` module for secure external command execution and `threading` to keep the GUI responsive during voice recognition.

## How It Works

The application operates in a continuous loop managed by the main `VoiceRecognition` class:

1.  **Audio Input**: `pyaudio` captures audio from the default microphone.
2.  **Speech-to-Text**: The audio stream is fed into the `Vosk` recognizer, which is pre-configured with a grammar containing all valid commands (e.g., "forward", "turn left").
3.  **Command Processing**: When a valid command is recognized, the `process_command` method is triggered.
4.  **Robot Action**: The method maps the recognized text to a function in the `RobotController` class, which executes the corresponding movement.
5.  **GUI Feedback**: The recognized text is displayed in the GUI, and the status is updated.

## Installation and Setup

### Prerequisites

- Python 3.x
- `portaudio` library for PyAudio
- USB microphone (recommended for best results on Raspberry Pi)

On Debian/Ubuntu-based systems, you can install `portaudio` with:
```bash
sudo apt-get update
sudo apt-get install portaudio19-dev python3-pyaudio
```

### Dependencies

Install the required Python packages using pip:

```bash
pip install vosk pyaudio
```

For the Robot Controller (RC) version, you'll also need:
```bash
pip install RPi_Robot_Hat_Lib
```

### Audio Device Setup

To check available audio devices on your system:
```bash
arecord -l
```

The application will automatically detect and use USB audio devices. If you encounter ALSA errors, they are typically harmless and have been suppressed in the latest version.

## Usage

### Running the Simulation Version

For testing without hardware:
```bash
python3 vosk-controll.py
```

### Running the Robot Controller Version

For actual robot hardware control:
```bash
python3 vosk-controll\(RC\).py
```

### First-Time Setup

On the first run, the application will check for the Vosk speech model. If it's not found, it will attempt to download and unpack it automatically. This requires an internet connection.

### Using the GUI

- **Start/Stop Recognition**: Click the "Start Recognition" button to begin listening for commands. The button will change to "Stop Recognition" to allow you to pause.
- **Calibration**: Click the "Calibration" button to open the settings panel. You must stop recognition before opening calibration.
  - Adjust motor speeds and test them in real-time using the "Test" buttons
  - Fine-tune voice recognition sensitivity (0.0 - 1.0 range with 0.05 precision)
  - Set movement durations for precise control
  - Save your settings for persistent configuration
- **Quit**: Click the "Quit" button to safely close the application.

### Voice Commands

The following commands are recognized (with variations):
- **Forward**: "forward", "move forward", "go forward", "go straight", "ahead"
- **Backward**: "backward", "back", "reverse", "move back", "go back"
- **Left**: "left", "turn left", "go left", "rotate left"
- **Right**: "right", "turn right", "go right", "rotate right"
- **Strafe Left**: "slide left", "strafe left", "shift left", "drift left", "horizontal left"
- **Strafe Right**: "slide right", "strafe right", "shift right", "drift right", "horizontal right"
- **Stop**: "stop", "halt", "freeze", "brake", "stay"

## Code Overview

The entire logic is contained within `vosk-controll.py` and is structured into several key classes:

-   `VoskModelChecker`:
    -   Responsible for checking if the Vosk model exists.
    -   If the model is missing, it uses `subprocess` to run `wget` and `unzip` to download and set it up.

-   `CalibrationManager`:
    -   Manages loading and saving settings from the `robot_calibration.json` file.
    -   If the file doesn't exist, it creates one with default values.

-   `CalibrationWindow`:
    -   The Tkinter GUI for the calibration panel. It contains tabs for adjusting motor speeds, voice sensitivity, and movement durations.
    -   Allows for real-time testing of movement commands.

-   `VoiceRecognition`:
    -   The main class that orchestrates the entire application.
    -   Initializes all components (Vosk, PyAudio, GUI).
    -   Builds the recognition grammar from `MOVEMENT_TRAINING_KEYWORDS`.
    -   Manages the main GUI window, including buttons and status labels.
    -   Runs the voice listening loop in a separate thread (`threading`) to prevent the GUI from freezing.
    -   Handles starting, stopping, and gracefully quitting the application.

-   `MovementController` (in RC version) / `RobotController` (in simulation version):
    -   In the simulation version: A **placeholder class** that simulates robot actions by printing them to the console.
    -   In the RC version: Fully integrated with RPi_Robot_Hat_Lib for actual hardware control, including:
        - Real-time speed and duration control from calibration settings
        - Automatic motor stopping after movement duration
        - Test methods for calibration verification

## Customization

### Adding New Voice Commands

1.  Open `vosk-controll.py`.
2.  Add the new command and its synonyms to the `MOVEMENT_TRAINING_KEYWORDS` dictionary.
3.  Add a corresponding method for the new command in the `RobotController` class.
4.  Add an `elif` condition in the `process_command` method to call your new robot function.

The grammar will be updated automatically when you restart the application.

### Integrating with Robot Hardware

**Option 1**: Use the existing RC version (`vosk-controll(RC).py`) which already has full RPi_Robot_Hat_Lib integration.

**Option 2**: Customize for your own hardware:
1.  Import your robot's hardware library at the top of the file.
2.  In the `MovementController` class, initialize your robot's library in the `__init__` method.
3.  Update each movement method (e.g., `forward`, `left`, `stop`) to:
    - Get the calibrated speed and duration from `self.calibration`
    - Control your robot's motors
    - Use `time.sleep(duration)` for timed movements
    - Call `self.Robot.stop()` after each movement

## Troubleshooting

### ALSA Errors
If you see numerous ALSA error messages, they are typically harmless. The latest version suppresses these messages while maintaining full functionality. Ensure you're using a USB microphone for best results.

### Audio Device Not Found
Run `arecord -l` to list available capture devices. The application looks for "USB PnP Sound Device" by default. You may need to modify the device name in the code if using a different microphone.

### Calibration Not Working
- Ensure recognition is stopped before opening the calibration window
- Test buttons will execute movements using current calibration values
- Remember to click "Save Calibration" to persist your changes

## Project Structure

```
Voice-Controlled-Robot/
├── vosk-controll.py          # Simulation version (placeholder controls)
├── vosk-controll(RC).py      # Robot Controller version (hardware integration)
├── robot_calibration.json    # Auto-generated calibration settings
├── model/
│   └── vosk-model-small-en-us-0.15/  # Vosk speech recognition model
└── README.md                 # This file
```

## License

This project is open source and available for educational and personal use.

## Credits

- **Vosk**: Offline speech recognition toolkit
- **RPi_Robot_Hat_Lib**: Custom library for Raspberry Pi robot control (contact Cyton.io)
- **PyAudio**: Python audio I/O library

## Changelog

### October 2025
- Added automatic USB audio device detection
- Suppressed ALSA error messages for cleaner output
- Fixed calibration slider resolution for voice recognition settings
- Created Robot Controller (RC) version with full hardware integration
- Enhanced movement controller with calibrated speed and duration control
- Added real-time testing in calibration window
- Improved error handling and type safety
