"""
Base de datos en memoria (Safety Layer)
Almacena y valida el estado de los aviones para seguridad
"""

from typing import Dict, List, Optional
import time
from src.common.logger import get_logger
from src.common.types import Instruction, AircraftState

logger = get_logger(__name__)


class ContextDatabase:
    """
    Base de datos en memoria que actúa como safety layer
    Almacena estados históricos y valida instrucciones
    """
    
    def __init__(self, max_history: int = 1000):
        """
        Inicializa la base de datos de contexto
        
        Args:
            max_history: Máximo número de estados históricos a mantener por avión
        """
        self.max_history = max_history
        self.current_states: Dict[str, AircraftState] = {}
        self.state_history: Dict[str, List[AircraftState]] = {}
        
        logger.info("ContextDatabase initialized")
    
    def save_state(self, state: AircraftState):
        """
        Guarda el estado actual de un avión
        
        Args:
            state: Estado del avión
        """
        aircraft_id = state.aircraft_id
        
        # Actualizar estado actual
        self.current_states[aircraft_id] = state
        
        # Añadir a historial
        if aircraft_id not in self.state_history:
            self.state_history[aircraft_id] = []
        
        self.state_history[aircraft_id].append(state)
        
        # Limitar tamaño del historial
        if len(self.state_history[aircraft_id]) > self.max_history:
            self.state_history[aircraft_id].pop(0)
        
        logger.debug(f"State saved for {aircraft_id}: alt={state.altitude_ft}ft, spd={state.airspeed_kts}kts")
    
    def get_current_state(self, aircraft_id: str) -> Optional[AircraftState]:
        """
        Obtiene el estado actual de un avión
        
        Args:
            aircraft_id: ID del avión
            
        Returns:
            Estado actual, o None si no existe
        """
        return self.current_states.get(aircraft_id)
    
    def get_history(self, aircraft_id: str, limit: int = 100) -> List[AircraftState]:
        """
        Obtiene el historial de estados de un avión
        
        Args:
            aircraft_id: ID del avión
            limit: Número máximo de estados a retornar
            
        Returns:
            Lista de estados históricos
        """
        history = self.state_history.get(aircraft_id, [])
        return history[-limit:] if limit else history
    
    def is_safe(self, instruction: Instruction, current_state: AircraftState) -> bool:
        """
        Valida si una instrucción es segura de ejecutar
        
        Args:
            instruction: Instrucción a validar
            current_state: Estado actual del avión
            
        Returns:
            True si es segura, False en caso contrario
        """
        # Reglas de seguridad básicas
        
        # 1. No subir tren si está en tierra
        if instruction.instruction_type == "gear" and not instruction.parameters.get("value"):
            if current_state.on_ground:
                logger.warning("Safety check failed: Cannot retract gear while on ground")
                return False
        
        # 2. No retraer flaps a alta velocidad
        if instruction.instruction_type == "flaps":
            max_flaps_speed = 200  # kts (ejemplo)
            if current_state.airspeed_kts > max_flaps_speed and instruction.parameters["value"] > 0:
                logger.warning(f"Safety check failed: Speed too high for flaps ({current_state.airspeed_kts} > {max_flaps_speed} kts)")
                return False
        
        # 3. Validar altitudes razonables
        if instruction.instruction_type == "altitude":
            target_alt = instruction.parameters["value"]
            if target_alt < 0 or target_alt > 60000:
                logger.warning(f"Safety check failed: Unreasonable altitude ({target_alt} ft)")
                return False
        
        # 4. Validar velocidades razonables
        if instruction.instruction_type == "speed":
            target_speed = instruction.parameters["value"]
            if target_speed < 0 or target_speed > 500:
                logger.warning(f"Safety check failed: Unreasonable speed ({target_speed} kts)")
                return False
        
        logger.debug(f"Safety check passed for {instruction.instruction_type}")
        return True
    
    def clear_history(self, aircraft_id: Optional[str] = None):
        """
        Limpia el historial de estados
        
        Args:
            aircraft_id: ID del avión (None para limpiar todos)
        """
        if aircraft_id:
            self.state_history[aircraft_id] = []
            logger.info(f"History cleared for {aircraft_id}")
        else:
            self.state_history.clear()
            logger.info("All history cleared")
