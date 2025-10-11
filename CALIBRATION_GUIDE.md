# Robot Calibration System Guide

## Overview
The calibration system allows you to fine-tune your robot's movement parameters and voice recognition settings.

## Features

### 1. **Motor Speed Calibration**
Adjust the speed for different movement types:
- **Forward Speed** (0-100): Speed when moving forward
- **Backward Speed** (0-100): Speed when moving backward
- **Turn Speed** (0-100): Speed when turning left/right
- **Strafe Speed** (0-100): Speed when sliding horizontally

Each setting includes a **Test** button to immediately test the movement.

### 2. **Voice Recognition Calibration**
Fine-tune voice command detection:
- **Confidence Threshold** (0.0-1.0): How confident the system must be to accept a command
  - Higher = More accurate but less responsive
  - Lower = More responsive but may trigger false positives
  - Default: 0.7
  
- **Volume Threshold** (0.0-1.0): Minimum volume level to trigger recognition
  - Adjust based on your microphone sensitivity
  - Default: 0.3

### 3. **Movement Duration**
Set default movement times:
- **Default Duration** (0.1-5.0 seconds): How long movements last by default
- **Turn Duration** (0.1-3.0 seconds): How long turns last

## How to Use

### Opening Calibration
1. Run the application: `python3 Tester.py`
2. Click the **⚙️ Calibration** button
3. The calibration window will open with three tabs

### Adjusting Settings
1. Navigate between tabs: **Motor Speed**, **Voice Recognition**, **Movement Duration**
2. Use sliders to adjust values
3. Click **Test** buttons to try motor speeds
4. Values update in real-time

### Saving Your Settings
1. Click **💾 Save Calibration** to save settings to `robot_calibration.json`
2. Settings persist between sessions
3. The robot will use these settings for all movements

### Resetting to Defaults
1. Click **🔄 Reset to Defaults**
2. Confirm the reset
3. All settings return to factory defaults
4. Reopen the calibration window to see default values

## Configuration File

Settings are saved to `robot_calibration.json` in the following format:

```json
{
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
```

You can manually edit this file if needed.

## Tips for Best Results

### Motor Speed
- Start with lower speeds (30-40) for indoor use
- Increase gradually while testing
- Different surfaces may require different speeds
- Keep turn speeds slightly lower than forward speed for stability

### Voice Recognition
- Test in your typical operating environment
- Adjust volume threshold based on background noise
- Higher confidence reduces false triggers but may miss soft commands
- Start with defaults and adjust based on performance

### Movement Duration
- Shorter durations (0.5-1.0s) for quick, precise movements
- Longer durations (2.0-3.0s) for covering more distance
- Turn duration should typically be shorter than default duration

## Troubleshooting

**Robot moves too fast/slow:**
- Adjust motor speeds in calibration

**Voice commands not recognized:**
- Lower confidence threshold
- Lower volume threshold
- Speak more clearly and louder

**Too many false voice triggers:**
- Increase confidence threshold
- Increase volume threshold

**Movements too long/short:**
- Adjust movement duration settings

## Default Values

All default values are optimized for:
- Indoor smooth surfaces
- Moderate ambient noise
- Clear voice commands at normal speaking volume

Adjust based on your specific environment and requirements.
