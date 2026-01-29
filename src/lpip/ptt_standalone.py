#!/usr/bin/env python3
"""
PTT Standalone Listener
Runs the Push-to-Talk listener as a standalone process
"""

import time
import logging
from multiprocessing import Queue
from dotenv import load_dotenv
from listener import PushToTalkListener
from src.common import SystemLogger

# Load environment variables
load_dotenv()


def handle_transcription(transcription: str):
    """
    Callback to handle transcriptions
    
    Args:
        transcription: Transcribed text from audio
    """
    logger = SystemLogger.get_logger()
    logger.info(f"📝 Transcription: {transcription}")
    
    # TODO: Send to instruction queue or processing module
    print(f"\n{'='*60}")
    print(f"🎤 TRANSCRIPTION: {transcription}")
    print(f"{'='*60}\n")


def main():
    """
    Main entry point for standalone PTT listener
    """
    # Setup logging
    logger = logging.getLogger(__name__)
    
    print("=" * 60)
    print("🎙️  Push-to-Talk Listener - Standalone Mode")
    print("=" * 60)
    print()
    print("Press and hold SPACE to record audio")
    print("Release SPACE to stop recording and transcribe")
    print("Press Ctrl+C to exit")
    print()
    print("=" * 60)
    
    logger.info("Starting PTT Listener in standalone mode")
    
    # Create Push-to-Talk listener
    ptt_listener = PushToTalkListener(
        ptt_key="space",
        sample_rate=16000,
        channels=1
    )
    
    # Register callback for transcriptions
    ptt_listener.set_transcription_callback(handle_transcription)
    
    # Start the listener
    ptt_listener.start()
    
    logger.info("PTT Listener armed and ready")
    
    # Keep running until interrupted
    try:
        while True:
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
        logger.info("Shutting down PTT Listener")
        
        # Stop PTT listener
        ptt_listener.stop()
    
    print("PTT Listener stopped")
    logger.info("PTT Listener shut down successfully")


if __name__ == "__main__":
    main()
