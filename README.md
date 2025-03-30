# Hand Gesture Mouse Control

This application allows you to control your computer's mouse cursor and perform actions using hand gestures through your webcam.

## Features

- Move cursor using your index finger
- Click by raising your pinky finger
- Open Notepad by snapping your thumb and middle finger together
- Switch tabs (Ctrl+Tab) by raising your index and middle fingers

## Requirements

- Python 3.7 or higher
- Webcam
- Required Python packages (listed in requirements.txt)

## Installation

1. Clone or download this repository
2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python app.py
```

2. Position yourself in front of your webcam
3. Use the following gestures:
   - Move cursor: Point with your index finger
   - Click: Raise your pinky finger
   - Open Notepad: Snap your thumb and middle finger together
   - Switch tabs: Raise your index and middle fingers
4. Press 'q' to quit the application

## Notes

- Make sure your hand is well-lit and visible to the camera
- Keep your hand within the camera frame
- The application uses your default webcam (index 0)
- The camera feed is mirrored for easier control 