"""
El piloto individual (Thread por avión)
Worker que ejecuta instrucciones para un avión específico
"""

from threading import Thread
import time
from typing import Optional
from src.common.logger import get_logger
from src.common.types import Instruction, AircraftState, FlightPhase

logger = get_logger(__name__)


class PilotWorker(Thread):
    """
    Worker de piloto individual
    Ejecuta instrucciones para un avión específico en su propio thread
    """
    
    def __init__(self, aircraft_id: str, fg_client, context_db, fsm):
        """
        Inicializa el worker del piloto
        
        Args:
            aircraft_id: ID único del avión
            fg_client: Cliente de FlightGear
            context_db: Base de datos de contexto (safety layer)
            fsm: Máquina de estados de vuelo
        """
        super().__init__()
        self.aircraft_id = aircraft_id
        self.fg_client = fg_client
        self.context_db = context_db
        self.fsm = fsm
        self.should_stop = False
        self.current_state = AircraftState(aircraft_id=aircraft_id)
        
        logger.info(f"PilotWorker initialized for aircraft: {aircraft_id}")
    
    def run(self):
        """Ejecuta el bucle principal del piloto"""
        logger.info(f"PilotWorker started for {self.aircraft_id}")
        
        try:
            while not self.should_stop:
                # 1. Actualizar estado del avión
                self._update_aircraft_state()
                
                # 2. Actualizar FSM
                self.fsm.update(self.current_state)
                
                # 3. Guardar estado en context_db
                self.context_db.save_state(self.current_state)
                
                # 4. Ejecutar acciones de la FSM
                self._execute_fsm_actions()
                
                time.sleep(0.1)  # 10 Hz update rate
                
        except Exception as e:
            logger.error(f"Error in PilotWorker {self.aircraft_id}: {e}", exc_info=True)
        finally:
            logger.info(f"PilotWorker stopped for {self.aircraft_id}")
    
    def execute_instruction(self, instruction: Instruction):
        """
        Ejecuta una instrucción recibida
        
        Args:
            instruction: Instrucción a ejecutar
        """
        logger.info(f"[{self.aircraft_id}] Executing: {instruction.instruction_type}")
        
        # Verificar seguridad con context_db
        if not self.context_db.is_safe(instruction, self.current_state):
            logger.warning(f"Instruction rejected by safety layer: {instruction.instruction_type}")
            return
        
        # Ejecutar según tipo de instrucción
        if instruction.instruction_type == "heading":
            self._execute_heading(instruction.parameters["value"])
        elif instruction.instruction_type == "altitude":
            self._execute_altitude(instruction.parameters["value"])
        elif instruction.instruction_type == "speed":
            self._execute_speed(instruction.parameters["value"])
        elif instruction.instruction_type == "flaps":
            self._execute_flaps(instruction.parameters["value"])
        elif instruction.instruction_type == "gear":
            self._execute_gear(instruction.parameters["value"])
        else:
            logger.warning(f"Unknown instruction type: {instruction.instruction_type}")
    
    def _update_aircraft_state(self):
        """Actualiza el estado actual del avión desde FlightGear"""
        # TODO: Obtener datos reales de FlightGear
        pass
    
    def _execute_fsm_actions(self):
        """Ejecuta las acciones de la máquina de estados"""
        # TODO: Implementar ejecución de acciones FSM
        pass
    
    def _execute_heading(self, heading: float):
        """Ejecuta comando de rumbo"""
        logger.info(f"[{self.aircraft_id}] Setting heading to {heading}°")
        # TODO: Enviar comando a FlightGear
        # self.fg_client.set_property("/autopilot/settings/heading-bug-deg", heading)
    
    def _execute_altitude(self, altitude: float):
        """Ejecuta comando de altitud"""
        logger.info(f"[{self.aircraft_id}] Setting altitude to {altitude} ft")
        # TODO: Enviar comando a FlightGear
    
    def _execute_speed(self, speed: float):
        """Ejecuta comando de velocidad"""
        logger.info(f"[{self.aircraft_id}] Setting speed to {speed} kts")
        # TODO: Enviar comando a FlightGear
    
    def _execute_flaps(self, position: float):
        """Ejecuta comando de flaps"""
        logger.info(f"[{self.aircraft_id}] Setting flaps to {position}")
        # TODO: Enviar comando a FlightGear
    
    def _execute_gear(self, down: bool):
        """Ejecuta comando de tren de aterrizaje"""
        logger.info(f"[{self.aircraft_id}] Setting gear {'down' if down else 'up'}")
        # TODO: Enviar comando a FlightGear
    
    def stop(self):
        """Detiene el worker"""
        logger.info(f"Stopping PilotWorker for {self.aircraft_id}")
        self.should_stop = True
