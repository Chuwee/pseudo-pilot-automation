"""
Bucle principal del proceso LPIP
Worker que captura audio, transcribe y parsea instrucciones
"""

import time
from multiprocessing import Process
from typing import Optional
from src.common.logger import get_logger
from src.common.queue_manager import QueueManager
from src.lpip.listener import AudioListener
from src.lpip.parser import InstructionParser

logger = get_logger(__name__)


class LPIPWorker(Process):
    """
    Worker del proceso LPIP (Language Parameter & Instruction Parser)
    Captura audio, transcribe con Whisper, parsea con LLM y envía a cola
    """
    
    def __init__(self, output_queue: QueueManager, config: dict):
        """
        Inicializa el worker LPIP
        
        Args:
            output_queue: Cola para enviar instrucciones parseadas
            config: Configuración del sistema
        """
        super().__init__()
        self.output_queue = output_queue
        self.config = config
        self.should_stop = False
        
        logger.info("LPIPWorker initialized")
    
    def run(self):
        """Ejecuta el bucle principal del worker"""
        logger.info("LPIPWorker started")
        
        # Inicializar componentes
        listener = AudioListener(
            sample_rate=self.config.get("audio_sample_rate", 16000),
            model="base"
        )
        
        parser = InstructionParser(
            api_key=self.config.get("openai_api_key", ""),
            model=self.config.get("llm_model", "gpt-4o-mini"),
            temperature=self.config.get("llm_temperature", 0.7)
        )
        
        listener.start_listening()
        
        try:
            while not self.should_stop:
                # 1. Capturar y transcribir audio
                logger.debug("Listening for audio...")
                transcribed_text = listener.listen_and_transcribe(duration=3.0)
                
                if transcribed_text:
                    logger.info(f"Transcribed: '{transcribed_text}'")
                    
                    # 2. Parsear instrucción con LLM
                    instruction = parser.parse(transcribed_text)
                    
                    if instruction and parser.validate_instruction(instruction):
                        # 3. Enviar a cola de salida
                        logger.info(f"Sending instruction to queue: {instruction.instruction_type}")
                        self.output_queue.put(instruction.to_dict())
                    else:
                        logger.warning("Failed to parse or validate instruction")
                else:
                    logger.debug("No audio transcribed")
                
                # Pequeño delay para no saturar
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            logger.info("LPIPWorker interrupted by user")
        except Exception as e:
            logger.error(f"Error in LPIPWorker: {e}", exc_info=True)
        finally:
            listener.stop_listening()
            logger.info("LPIPWorker stopped")
    
    def stop(self):
        """Detiene el worker"""
        logger.info("Stopping LPIPWorker...")
        self.should_stop = True
