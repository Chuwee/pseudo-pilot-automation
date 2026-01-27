"""
Dispatcher: Lee Cola -> Distribuye a Workers
Master process que distribuye instrucciones a workers individuales
"""

import time
from multiprocessing import Process
from typing import Dict
from queue import Empty
from src.common.logger import get_logger
from src.common.queue_manager import QueueManager
from src.common.types import Instruction

logger = get_logger(__name__)


class PiemMaster(Process):
    """
    Master del módulo PIEM
    Lee instrucciones de la cola y las distribuye a workers (pilotos virtuales)
    """
    
    def __init__(self, input_queue: QueueManager, config: dict):
        """
        Inicializa el master PIEM
        
        Args:
            input_queue: Cola de entrada con instrucciones
            config: Configuración del sistema
        """
        super().__init__()
        self.input_queue = input_queue
        self.config = config
        self.should_stop = False
        self.workers: Dict[str, 'PilotWorker'] = {}
        
        logger.info("PiemMaster initialized")
    
    def run(self):
        """Ejecuta el bucle principal del dispatcher"""
        logger.info("PiemMaster started")
        
        try:
            while not self.should_stop:
                try:
                    # Leer instrucción de la cola con timeout
                    instruction_dict = self.input_queue.get(block=True, timeout=1.0)
                    
                    # Reconstruir objeto Instruction
                    instruction = Instruction(
                        instruction_type=instruction_dict["instruction_type"],
                        parameters=instruction_dict["parameters"],
                        raw_text=instruction_dict["raw_text"],
                        timestamp=instruction_dict["timestamp"],
                        confidence=instruction_dict.get("confidence", 1.0),
                        aircraft_id=instruction_dict.get("aircraft_id")
                    )
                    
                    logger.info(f"Received instruction: {instruction.instruction_type}")
                    
                    # Distribuir a worker apropiado
                    self._dispatch_instruction(instruction)
                    
                except Empty:
                    # No hay instrucciones, continuar esperando
                    continue
                except Exception as e:
                    logger.error(f"Error processing instruction: {e}", exc_info=True)
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            logger.info("PiemMaster interrupted by user")
        except Exception as e:
            logger.error(f"Error in PiemMaster: {e}", exc_info=True)
        finally:
            self._cleanup_workers()
            logger.info("PiemMaster stopped")
    
    def _dispatch_instruction(self, instruction: Instruction):
        """
        Distribuye una instrucción al worker apropiado
        
        Args:
            instruction: Instrucción a distribuir
        """
        aircraft_id = instruction.aircraft_id or "default_aircraft"
        
        # Por ahora, solo loguear la distribución
        # TODO: Implementar workers reales y distribución
        logger.info(f"Dispatching {instruction.instruction_type} to aircraft {aircraft_id}")
        logger.debug(f"Parameters: {instruction.parameters}")
        
        # TODO: Enviar a worker específico
        # if aircraft_id not in self.workers:
        #     self._create_worker(aircraft_id)
        # self.workers[aircraft_id].send_instruction(instruction)
    
    def _create_worker(self, aircraft_id: str):
        """
        Crea un nuevo worker para un avión
        
        Args:
            aircraft_id: ID del avión
        """
        logger.info(f"Creating worker for aircraft: {aircraft_id}")
        # TODO: Implementar creación de workers
        pass
    
    def _cleanup_workers(self):
        """Limpia y detiene todos los workers"""
        logger.info("Cleaning up workers...")
        for aircraft_id, worker in self.workers.items():
            logger.debug(f"Stopping worker for {aircraft_id}")
            # TODO: Implementar limpieza de workers
            pass
    
    def stop(self):
        """Detiene el master"""
        logger.info("Stopping PiemMaster...")
        self.should_stop = True
