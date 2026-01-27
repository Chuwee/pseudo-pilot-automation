"""
Máquina de Estados (Takeoff, Approach, Flare)
FSM para gestionar las fases de vuelo
"""

from enum import Enum
from typing import Optional, Callable, Dict
from src.common.logger import get_logger
from src.common.types import FlightPhase, AircraftState

logger = get_logger(__name__)


class FlightStateMachine:
    """
    Máquina de estados finitos para gestionar las fases de vuelo
    Transiciona automáticamente entre fases según el estado del avión
    """
    
    def __init__(self, aircraft_id: str):
        """
        Inicializa la máquina de estados
        
        Args:
            aircraft_id: ID del avión
        """
        self.aircraft_id = aircraft_id
        self.current_phase = FlightPhase.IDLE
        self.previous_phase = FlightPhase.IDLE
        
        logger.info(f"FlightStateMachine initialized for {aircraft_id}")
    
    def update(self, state: AircraftState):
        """
        Actualiza la fase de vuelo según el estado actual
        
        Args:
            state: Estado actual del avión
        """
        old_phase = self.current_phase
        new_phase = self._determine_phase(state)
        
        if new_phase != old_phase:
            logger.info(f"[{self.aircraft_id}] Phase transition: {old_phase.value} -> {new_phase.value}")
            self.previous_phase = old_phase
            self.current_phase = new_phase
            self._on_phase_change(old_phase, new_phase, state)
    
    def _determine_phase(self, state: AircraftState) -> FlightPhase:
        """
        Determina la fase de vuelo basándose en el estado
        
        Args:
            state: Estado del avión
            
        Returns:
            Fase de vuelo determinada
        """
        # En tierra
        if state.on_ground:
            if state.airspeed_kts < 5:
                return FlightPhase.IDLE
            elif state.airspeed_kts < 80:
                return FlightPhase.TAXI
            else:
                return FlightPhase.TAKEOFF
        
        # En el aire
        if state.altitude_ft < 1000:
            if state.vertical_speed_fpm < -500:
                return FlightPhase.FLARE
            elif state.vertical_speed_fpm < -200:
                return FlightPhase.APPROACH
            else:
                return FlightPhase.CLIMB
        elif state.altitude_ft < 10000:
            if state.vertical_speed_fpm > 100:
                return FlightPhase.CLIMB
            elif state.vertical_speed_fpm < -100:
                return FlightPhase.DESCENT
            else:
                return FlightPhase.CRUISE
        else:
            if state.vertical_speed_fpm > 100:
                return FlightPhase.CLIMB
            elif state.vertical_speed_fpm < -100:
                return FlightPhase.DESCENT
            else:
                return FlightPhase.CRUISE
    
    def _on_phase_change(self, old_phase: FlightPhase, new_phase: FlightPhase, state: AircraftState):
        """
        Callback cuando cambia la fase de vuelo
        
        Args:
            old_phase: Fase anterior
            new_phase: Nueva fase
            state: Estado actual
        """
        logger.info(f"[{self.aircraft_id}] Entering {new_phase.value} phase")
        
        # Ejecutar acciones específicas de cada transición
        if new_phase == FlightPhase.TAKEOFF:
            self._on_takeoff(state)
        elif new_phase == FlightPhase.APPROACH:
            self._on_approach(state)
        elif new_phase == FlightPhase.FLARE:
            self._on_flare(state)
        elif new_phase == FlightPhase.LANDING and old_phase == FlightPhase.FLARE:
            self._on_landing(state)
    
    def _on_takeoff(self, state: AircraftState):
        """Acciones al iniciar despegue"""
        logger.info(f"[{self.aircraft_id}] Takeoff initiated")
        # TODO: Configurar parámetros de despegue
    
    def _on_approach(self, state: AircraftState):
        """Acciones al iniciar aproximación"""
        logger.info(f"[{self.aircraft_id}] Approach initiated")
        # TODO: Configurar ILS, verificar tren abajo, etc.
    
    def _on_flare(self, state: AircraftState):
        """Acciones al iniciar flare"""
        logger.info(f"[{self.aircraft_id}] Flare initiated at {state.altitude_ft} ft")
        # TODO: Reducir throttle, pitch up suave
    
    def _on_landing(self, state: AircraftState):
        """Acciones al completar aterrizaje"""
        logger.info(f"[{self.aircraft_id}] Landing completed")
        # TODO: Activar reversores, frenos
    
    def get_current_phase(self) -> FlightPhase:
        """Retorna la fase actual"""
        return self.current_phase
    
    def can_execute_instruction(self, instruction_type: str) -> bool:
        """
        Verifica si una instrucción puede ejecutarse en la fase actual
        
        Args:
            instruction_type: Tipo de instrucción
            
        Returns:
            True si puede ejecutarse, False en caso contrario
        """
        # Restricciones por fase
        if self.current_phase == FlightPhase.FLARE:
            # Durante flare, solo permitir ajustes menores
            allowed = ["throttle"]
            return instruction_type in allowed
        
        if self.current_phase == FlightPhase.TAKEOFF:
            # Durante despegue, no permitir ciertos cambios
            forbidden = ["gear", "flaps"]
            return instruction_type not in forbidden
        
        return True
