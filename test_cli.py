"""Simple CLI test for the STT module."""
import sys
from stt_module import STTModule
import config


def on_transcript(text):
    """Callback for transcriptions - prints in real-time."""
    # Print without newline for continuous feel
    print(f"{text} ", end='', flush=True)


def main():
    print("=" * 50)
    print("🎤 Speech-to-Text CLI Test")
    print("=" * 50)
    print()
    print("Instructions:")
    print("1. Say 'Porcupine' (wake word) to activate")
    print("2. Speak normally - text appears in REAL-TIME!")
    print("3. Say 'Bye' (sleep word) to deactivate")
    print("4. Press Ctrl+C to exit")
    print()
    print("💡 TIP: Transcription appears every ~2 seconds as you speak")
    print("-" * 50)
    
    try:
        # Initialize STT module
        print("\n⏳ Initializing STT module...")
        stt = STTModule(
            picovoice_key=config.PICOVOICE_ACCESS_KEY,
            whisper_model="base",
            on_transcript=on_transcript
        )
        
        print("✅ Initialization complete!")
        print("\n👂 Listening for wake word 'Porcupine'...")
        print("-" * 50)
        
        # Run the STT module
        stt.run()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'stt' in locals():
            stt.cleanup()
        print("\n👋 Goodbye!")


if __name__ == "__main__":
    main()
