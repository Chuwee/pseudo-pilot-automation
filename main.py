#!/usr/bin/env python3
"""
PseudoPilot_Automation - Main Entry Point
Orquestador de procesos (Master)

This is the main orchestrator that coordinates the LPIP (Language Parameter & Instruction Parser)
and PIEM (Pseudo-pilot Instruction Execution Module) processes.
"""

import multiprocessing as mp
from multiprocessing import Queue
import logging
from src.common.logger import setup_logger
from src.lpip.worker import lpip_worker
from src.piem.master import piem_master


def main():
    """
    Main entry point - starts both LPIP and PIEM processes
    """
    # Setup logging
    logger = setup_logger(__name__)
    logger.info("Starting PseudoPilot_Automation System")
    
    # Create communication queue between LPIP and PIEM
    instruction_queue = Queue()
    
    # Start LPIP process (Node A: Language Parameter & Instruction Parser)
    lpip_process = mp.Process(
        target=lpip_worker,
        args=(instruction_queue,),
        name="LPIP_Worker"
    )
    
    # Start PIEM process (Node B: Pseudo-pilot Instruction Execution Module)
    piem_process = mp.Process(
        target=piem_master,
        args=(instruction_queue,),
        name="PIEM_Master"
    )
    
    # Launch processes
    lpip_process.start()
    piem_process.start()
    
    logger.info("Both LPIP and PIEM processes started")
    
    # Wait for processes to complete
    try:
        lpip_process.join()
        piem_process.join()
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
        lpip_process.terminate()
        piem_process.terminate()
        lpip_process.join()
        piem_process.join()
    
    logger.info("PseudoPilot_Automation System shut down")


if __name__ == "__main__":
    main()
