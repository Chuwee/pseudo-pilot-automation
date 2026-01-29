#!/usr/bin/env python3
"""
PseudoPilot_Automation - Main Entry Point
Orquestador con Push-to-Talk Listener

This orchestrator starts a Push-to-Talk audio listener that captures voice commands
and sends them to the instruction queue for processing.
"""

import multiprocessing as mp
from multiprocessing import Queue
import logging
import time
from dotenv import load_dotenv
from src.lpip.listener import PushToTalkListener
from src.common import SystemLogger

# Cargar variables de entorno
load_dotenv()


def handle_transcription(instruction_queue: Queue, transcription: str):
    """
    Callback para manejar las transcripciones
    
    Args:
        instruction_queue: Cola para enviar comandos al PIEM
        transcription: Texto transcrito desde el audio
    """
    logger = SystemLogger.get_logger()
    logger.info(f"Received transcription: {transcription}")
    
    # Send transcription to PIEM for processing
    instruction_queue.put({
        "type": "voice_command",
        "text": transcription,
        "timestamp": time.time()
    })


def main():
    """
    Main entry point - starts Push-to-Talk listener and PIEM process
    """
    # Setup logging
    logger = logging.getLogger(__name__)
    logger.info("Starting PseudoPilot_Automation System with Push-to-Talk")
    
    # Create communication queue between Listener and PIEM
    instruction_queue = Queue()
    logger.debug("Launching instruction queue")
    
    # Create Push-to-Talk listener
    ptt_listener = PushToTalkListener(
        ptt_key="space",
        sample_rate=16000,
        channels=1
    )
    
    # Register callback to send transcriptions to the queue
    ptt_listener.set_transcription_callback(
        lambda text: handle_transcription(instruction_queue, text)
    )
    
    # Start PIEM process (Pseudo-pilot Instruction Execution Module)
    # piem_process = mp.Process(
    #     target=piem_master,
    #     args=(instruction_queue,),
    #     name="PIEM_Master"
    # )
    
    # Launch PIEM process
    #piem_process.start()
    logger.info("PIEM process started")
    
    # Start Push-to-Talk listener (runs in main thread)
    ptt_listener.start()
    
    logger.info("Push-to-Talk system armed and ready")
    
    # Keep running until interrupted
    try:
        while True:
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
        
        # Stop PTT listener
        ptt_listener.stop()
        
        # Terminate PIEM process
        # piem_process.terminate()
        # piem_process.join()
    
    logger.info("PseudoPilot_Automation System shut down")


if __name__ == "__main__":
    main()

