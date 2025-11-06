"""Core Speech-to-Text module with wake/sleep word detection."""
import pyaudio
import numpy as np
import pvporcupine
import whisper
import wave
import io
import time
from typing import Optional, Callable
import config


class STTModule:
    """Speech-to-Text module with wake/sleep word detection."""
    
    def __init__(self, 
                 picovoice_key: str = None,
                 whisper_model: str = None,
                 on_transcript: Callable[[str], None] = None):
        
        self.picovoice_key = picovoice_key or config.PICOVOICE_ACCESS_KEY
        self.whisper_model_name = whisper_model or config.WHISPER_MODEL
        self.on_transcript = on_transcript
        
        # Load Whisper model
        self.whisper_model = whisper.load_model(self.whisper_model_name)

        
        # Audio setup
        self.audio = pyaudio.PyAudio()
        self.stream = None
        
        # State
        self.is_active = False
        self.is_listening = False
        self.audio_buffer = []
        
        # Porcupine wake word detector
        self.porcupine = None
        self._init_porcupine()
    
    def _init_porcupine(self):
        """Initialize Porcupine wake word detector."""
        try:
            # Using built-in keywords - "porcupine" or you can use custom trained models
            # For custom wake words, you need to train them on Picovoice Console
            self.porcupine = pvporcupine.create(
                access_key=self.picovoice_key,
                keywords=["porcupine"]  # Built-in keyword, change to custom model path for "hi"
            )
        except Exception as e:
            print(f"Warning: Could not initialize Porcupine: {e}")
            print("Wake word detection will be disabled. Use manual activation.")
            self.porcupine = None
    
    def start_listening(self):
        """Start the audio stream for listening."""
        if self.stream is None:
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=config.CHANNELS,
                rate=config.SAMPLE_RATE,
                input=True,
                frames_per_buffer=config.CHUNK_SIZE
            )
        self.is_listening = True
    
    def stop_listening(self):
        """Stop the audio stream."""
        self.is_listening = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
    
    def activate(self):
        """Activate STT (wake word detected)."""
        self.is_active = True
        self.audio_buffer = []
        print("🎤 STT Activated - Start speaking...")
    
    def deactivate(self):
        """Deactivate STT (sleep word detected)."""
        self.is_active = False
        self.audio_buffer = []
        print("💤 STT Deactivated")
    
    def detect_wake_word(self, audio_chunk: bytes) -> bool:
        """
        Detect wake word in audio chunk.
        
        Args:
            audio_chunk: Raw audio bytes
            
        Returns:
            True if wake word detected
        """
        if self.porcupine is None:
            return False
        
        try:
            # Convert bytes to int16 array
            pcm = np.frombuffer(audio_chunk, dtype=np.int16)
            
            # Porcupine expects specific frame length
            if len(pcm) >= self.porcupine.frame_length:
                pcm = pcm[:self.porcupine.frame_length]
                keyword_index = self.porcupine.process(pcm)
                return keyword_index >= 0
        except Exception as e:
            print(f"Wake word detection error: {e}")
        
        return False
    
    def detect_sleep_word(self, text: str) -> bool:
        """
        Detect sleep word in transcribed text.
        
        Args:
            text: Transcribed text
            
        Returns:
            True if sleep word detected
        """
        return config.SLEEP_WORD.lower() in text.lower()
    
    def transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        """
        Transcribe audio using local Whisper model.
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            Transcribed text or None
        """
        try:
            # Convert bytes to numpy array
            audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            
            # Transcribe using local Whisper
            result = self.whisper_model.transcribe(
                audio_np,
                language="en",  # You can change or remove this for auto-detection
                fp16=False  # Set to True if you have CUDA GPU
            )
            
            text = result["text"].strip()
            return text if text else None
        
        except Exception as e:
            print(f"Transcription error: {e}")
            return None
    
    def process_audio_chunk(self, audio_chunk: bytes):
        """
        Process incoming audio chunk.
        
        Args:
            audio_chunk: Raw audio bytes
        """
        # Check for wake word if not active
        if not self.is_active:
            if self.detect_wake_word(audio_chunk):
                self.activate()
            return
        
        # If active, accumulate audio
        self.audio_buffer.append(audio_chunk)
        
        # Process buffer when it reaches a certain size (real-time: every 2 seconds)
        buffer_duration = len(self.audio_buffer) * config.CHUNK_SIZE / config.SAMPLE_RATE
        
        if buffer_duration >= config.REALTIME_CHUNK_DURATION:
            self._process_buffer()
    
    def _process_buffer(self):
        """Process accumulated audio buffer."""
        if not self.audio_buffer:
            return
        
        # Combine audio chunks
        audio_data = b''.join(self.audio_buffer)
        self.audio_buffer = []
        
        # Check if audio is long enough
        duration = len(audio_data) / (config.SAMPLE_RATE * 2)  # 2 bytes per sample (int16)
        if duration < config.MIN_AUDIO_LENGTH:
            return
        
        # Transcribe
        text = self.transcribe_audio(audio_data)
        
        if text:
            # Check for sleep word
            if self.detect_sleep_word(text):
                self.deactivate()
            
            # Callback with transcription (real-time!)
            if self.on_transcript:
                self.on_transcript(text)
    
    def run(self, duration: Optional[int] = None):
        """
        Run the STT module.
        
        Args:
            duration: Optional duration in seconds (None for infinite)
        """
        self.start_listening()
        start_time = time.time()
        
        print("Listening for wake word...")
        
        try:
            while self.is_listening:
                # Check duration
                if duration and (time.time() - start_time) > duration:
                    break
                
                # Read audio chunk
                if self.stream:
                    audio_chunk = self.stream.read(config.CHUNK_SIZE, exception_on_overflow=False)
                    self.process_audio_chunk(audio_chunk)
        
        except KeyboardInterrupt:
            print("\n⚠️ Interrupted by user")
        
        finally:
            self.stop_listening()
    
    def cleanup(self):
        """Clean up resources."""
        self.stop_listening()
        if self.porcupine:
            self.porcupine.delete()
        self.audio.terminate()
