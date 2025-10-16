# Voice Controlled Robot

This project is a Python-based application for controlling a robot using voice commands. It features a graphical user interface (GUI) built with Tkinter, offline speech recognition powered by the Vosk toolkit, and a robust calibration system to fine-tune the robot's behavior.

## Features

- **Offline Voice Control**: Uses the Vosk library for accurate, offline speech recognition. No internet connection is required after the initial model download.
- **High-Accuracy Command Recognition**: Implements a focused grammar built from a keyword list, ensuring the recognizer is optimized to detect specific robot commands.
- **Graphical User Interface (GUI)**: A user-friendly interface to start/stop recognition, view recognized commands in real-time, and access calibration settings.
- **Dynamic Calibration Panel**: A comprehensive calibration window allows for real-time adjustments of:
  - **Motor Speeds**: Forward, backward, turn, and strafe speeds.
  - **Voice Recognition**: Confidence and volume thresholds.
  - **Movement Durations**: Default and turn durations.
- **Automatic Model Downloader**: Automatically checks for the required Vosk speech model and downloads it if not found.
- **Modular and Extendable**: The robot control logic is abstracted into a `RobotController` class, making it easy to replace the placeholder with an actual hardware control library (e.g., for a Raspberry Pi).
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
- `portaudio` library for PyAudio.

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

## Usage

1.  **Run the Application**:
    ```bash
    python3 vosk-controll.py
    ```

2.  **First-Time Run**: On the first run, the application will check for the Vosk speech model. If it's not found, it will attempt to download and unpack it automatically. This requires an internet connection.

3.  **Using the GUI**:
    - **Start/Stop Recognition**: Click the "🎤 Start Recognition" button to begin listening for commands. The button will change to "🛑 Stop Recognition" to allow you to pause.
    - **Calibration**: Click the "⚙️ Calibration" button to open the settings panel. You must stop recognition before opening calibration.
    - **Quit**: Click the "✖ Quit" button to safely close the application.

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

-   `RobotController`:
    -   A **placeholder class** that simulates robot actions by printing them to the console.
    -   This is the primary class to modify when integrating with actual robot hardware. Each method (e.g., `forward()`, `stop()`) should be updated to call the corresponding function from your robot's hardware library.

## Customization

### Adding New Voice Commands

1.  Open `vosk-controll.py`.
2.  Add the new command and its synonyms to the `MOVEMENT_TRAINING_KEYWORDS` dictionary.
3.  Add a corresponding method for the new command in the `RobotController` class.
4.  Add an `elif` condition in the `process_command` method to call your new robot function.

The grammar will be updated automatically when you restart the application.

### Integrating with Robot Hardware

1.  Import your robot's hardware library at the top of the file.
2.  In the `RobotController` class, initialize your robot's library in the `__init__` method.
3.  Replace the `print()` statements in each movement method (e.g., `forward`, `left`, `stop`) with the actual code to drive your robot's motors.
