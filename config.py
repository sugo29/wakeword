"""Configuration settings for the STT module."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
PICOVOICE_ACCESS_KEY = os.getenv("PICOVOICE_ACCESS_KEY", "ki9oLbdwFINW406ywWz5RTpMuLj+W42OYqDD7N4ksn/6KydR81xFxA==")

# Audio Settings
SAMPLE_RATE = 16000
CHUNK_SIZE = 512
CHANNELS = 1
FORMAT = "int16"

# Wake/Sleep Words
WAKE_WORD = "hi"  # Custom wake word - you can train custom models with Picovoice
SLEEP_WORD = "bye"

# Whisper Settings (Local Model)
# Options: "tiny", "base", "small", "medium", "large"
# tiny = fastest, least accurate | large = slowest, most accurate
WHISPER_MODEL = "base"  # Good balance of speed and accuracy

# Recording Settings
MAX_RECORDING_DURATION = 30  # seconds per chunk
SILENCE_THRESHOLD = 500  # adjust based on environment
SILENCE_DURATION = 2  # seconds of silence before processing

# Real-time Transcription Settings
REALTIME_CHUNK_DURATION = 2  # Process audio every 2 seconds for real-time feel
MIN_AUDIO_LENGTH = 0.5  # Minimum audio length to transcribe (seconds)
