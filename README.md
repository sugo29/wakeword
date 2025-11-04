# Speech-to-Text Wake/Sleep Module

A modular speech-to-text application with wake word ("Hi") and sleep word ("Bye") detection.

## Features
- Wake word detection using Porcupine (Picovoice)
- Sleep word detection
- Real-time speech transcription using OpenAI Whisper API
- Simple Streamlit UI for demo
- Modular design for React Native integration

## Tech Stack
- **Audio Capture**: PyAudio
- **Speech-to-Text**: OpenAI Whisper (Local/Open-Source) - **100% FREE!**
- **Wake Word Detection**: Porcupine (Picovoice)
- **UI**: Streamlit

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
# Create .env file
OPENAI_API_KEY=your_openai_api_key_here
PICOVOICE_ACCESS_KEY=your_picovoice_key_here
```

3. Run the app:
```bash
streamlit run app.py
```

## Project Structure
```
python-stt-app/
├── test_cli.py           # CLI application (main entry)
├── stt_module.py         # Core STT logic (modular)
├── config.py             # Configuration
├── requirements.txt      # Dependencies
├── .env                  # Environment variables (not in git)
└── README.md            # This file
```

## Usage

1. Launch the app with `streamlit run app.py`
2. Say "Hi" to activate listening
3. Speak - your words will be transcribed in real-time
4. Say "Bye" to deactivate listening

## React Native Integration

The `stt_module.py` is fully modular and ready for React Native integration via:
- Python backend API (FastAPI)
- WebSocket streaming for real-time transcription
- REST endpoints for control

To create an API server for React Native:
1. Install: `pip install fastapi uvicorn websockets`
2. Create a FastAPI server with WebSocket endpoint
3. Stream audio from React Native to Python backend
4. Receive real-time transcriptions via WebSocket

Example server structure available on request.
