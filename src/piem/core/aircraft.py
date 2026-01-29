#!/usr/bin/env python3
"""
Aircraft Model - Represents an aircraft in the pseudo-pilot system

This module defines the Aircraft dataclass that holds all relevant information
about an aircraft being tracked by the system.
"""

from dataclasses import dataclass, asdict, field
from typing import Optional
from datetime import datetime
import json


@dataclass
class AircraftState:
    """
    Represents the current state of an aircraft
    
    Attributes:
        altitude: Aircraft altitude in feet
        heading: Aircraft heading in degrees (0-360)
        speed: Aircraft speed in knots
        latitude: Aircraft latitude in decimal degrees
        longitude: Aircraft longitude in decimal degrees
    """
    altitude: float  # feet
    heading: float   # degrees (0-360)
    speed: float     # knots
    latitude: float  # decimal degrees
    longitude: float # decimal degrees
    
    def __post_init__(self):
        """Validate aircraft state values"""
        if not 0 <= self.heading <= 360:
            raise ValueError(f"Heading must be between 0 and 360, got {self.heading}")
        if self.altitude < 0:
            raise ValueError(f"Altitude cannot be negative, got {self.altitude}")
        if self.speed < 0:
            raise ValueError(f"Speed cannot be negative, got {self.speed}")
        if not -90 <= self.latitude <= 90:
            raise ValueError(f"Latitude must be between -90 and 90, got {self.latitude}")
        if not -180 <= self.longitude <= 180:
            raise ValueError(f"Longitude must be between -180 and 180, got {self.longitude}")


@dataclass
class Aircraft:
    """
    Represents an aircraft being tracked by the pseudo-pilot system
    
    Attributes:
        callsign: Aircraft callsign (unique identifier)
        current_state: Current state of the aircraft (position, heading, etc.)
        last_instruction: Last instruction sent to this aircraft
        last_instruction_successful: Whether the last instruction was successful
        last_updated: Timestamp of last update
    """
    callsign: str
    current_state: AircraftState
    last_instruction: Optional[str] = None
    last_instruction_successful: Optional[bool] = None
    last_updated: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate callsign"""
        if not self.callsign or not self.callsign.strip():
            raise ValueError("Callsign cannot be empty")
        # Normalize callsign to uppercase
        self.callsign = self.callsign.upper().strip()
    
    def update_state(
        self,
        altitude: Optional[float] = None,
        heading: Optional[float] = None,
        speed: Optional[float] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
    ) -> None:
        """
        Update aircraft state with new values
        
        Args:
            altitude: New altitude in feet
            heading: New heading in degrees
            speed: New speed in knots
            latitude: New latitude in decimal degrees
            longitude: New longitude in decimal degrees
        """
        if altitude is not None:
            self.current_state.altitude = altitude
        if heading is not None:
            self.current_state.heading = heading
        if speed is not None:
            self.current_state.speed = speed
        if latitude is not None:
            self.current_state.latitude = latitude
        if longitude is not None:
            self.current_state.longitude = longitude
        
        self.last_updated = datetime.now()
    
    def set_instruction(self, instruction: str, successful: Optional[bool] = None) -> None:
        """
        Set the last instruction for this aircraft
        
        Args:
            instruction: The instruction text
            successful: Whether the instruction was successful (None if pending)
        """
        self.last_instruction = instruction
        self.last_instruction_successful = successful
        self.last_updated = datetime.now()
    
    def mark_instruction_result(self, successful: bool) -> None:
        """
        Mark the result of the last instruction
        
        Args:
            successful: Whether the instruction was successful
        """
        if self.last_instruction is None:
            raise ValueError("Cannot mark instruction result: no instruction has been set")
        
        self.last_instruction_successful = successful
        self.last_updated = datetime.now()
    
    def to_dict(self) -> dict:
        """
        Convert aircraft to dictionary for serialization
        
        Returns:
            Dictionary representation of the aircraft
        """
        data = asdict(self)
        # Convert datetime to ISO format string
        data['last_updated'] = self.last_updated.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Aircraft':
        """
        Create an aircraft from a dictionary
        
        Args:
            data: Dictionary containing aircraft data
            
        Returns:
            Aircraft instance
        """
        # Convert state dict to AircraftState object
        state_data = data.pop('current_state')
        state = AircraftState(**state_data)
        
        # Convert ISO format string to datetime
        if 'last_updated' in data and isinstance(data['last_updated'], str):
            data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        
        return cls(current_state=state, **data)
    
    def to_json(self) -> str:
        """
        Convert aircraft to JSON string
        
        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Aircraft':
        """
        Create an aircraft from a JSON string
        
        Args:
            json_str: JSON string containing aircraft data
            
        Returns:
            Aircraft instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def __str__(self) -> str:
        """String representation of aircraft"""
        return (
            f"Aircraft {self.callsign}: "
            f"Alt={self.current_state.altitude}ft, "
            f"Hdg={self.current_state.heading}°, "
            f"Spd={self.current_state.speed}kts, "
            f"Pos=({self.current_state.latitude:.4f}, {self.current_state.longitude:.4f})"
        )
    
    def __repr__(self) -> str:
        """Detailed representation of aircraft"""
        return (
            f"Aircraft(callsign='{self.callsign}', "
            f"state={self.current_state}, "
            f"last_instruction='{self.last_instruction}', "
            f"success={self.last_instruction_successful})"
        )
