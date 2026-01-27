"""
Definiciones de Dataclasses (Instruction, State)
Tipos de datos compartidos entre módulos
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from enum import Enum


class FlightPhase(Enum):
    """Fases de vuelo para la FSM"""
    IDLE = "idle"
    TAXI = "taxi"
    TAKEOFF = "takeoff"
    CLIMB = "climb"
    CRUISE = "cruise"
    DESCENT = "descent"
    APPROACH = "approach"
    FLARE = "flare"
    LANDING = "landing"
    ROLLOUT = "rollout"


@dataclass
class Instruction:
    """Instrucción parseada desde lenguaje natural"""
    instruction_type: str
    parameters: Dict[str, Any]
    raw_text: str
    timestamp: float
    confidence: float = 1.0
    aircraft_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la instrucción a diccionario"""
        return {
            "instruction_type": self.instruction_type,
            "parameters": self.parameters,
            "raw_text": self.raw_text,
            "timestamp": self.timestamp,
            "confidence": self.confidence,
            "aircraft_id": self.aircraft_id
        }


@dataclass
class AircraftState:
    """Estado actual de una aeronave"""
    aircraft_id: str
    phase: FlightPhase = FlightPhase.IDLE
    altitude_ft: float = 0.0
    airspeed_kts: float = 0.0
    heading_deg: float = 0.0
    vertical_speed_fpm: float = 0.0
    latitude: float = 0.0
    longitude: float = 0.0
    on_ground: bool = True
    gear_down: bool = True
    flaps_position: float = 0.0
    throttle_position: float = 0.0
    timestamp: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el estado a diccionario"""
        return {
            "aircraft_id": self.aircraft_id,
            "phase": self.phase.value,
            "altitude_ft": self.altitude_ft,
            "airspeed_kts": self.airspeed_kts,
            "heading_deg": self.heading_deg,
            "vertical_speed_fpm": self.vertical_speed_fpm,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "on_ground": self.on_ground,
            "gear_down": self.gear_down,
            "flaps_position": self.flaps_position,
            "throttle_position": self.throttle_position,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }


@dataclass
class SystemConfig:
    """Configuración del sistema cargada desde settings.yaml"""
    openai_api_key: str
    flightgear_host: str
    flightgear_port: int
    flightgear_timeout: int
    audio_sample_rate: int
    llm_model: str
    llm_temperature: float
    log_level: str = "INFO"
