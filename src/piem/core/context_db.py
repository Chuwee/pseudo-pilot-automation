#!/usr/bin/env python3
"""
Context Database - In-memory database for aircraft tracking

This module provides a lightweight, thread-safe in-memory database for tracking
aircraft states and instructions in the pseudo-pilot system.
"""

import threading
from typing import Dict, List, Optional
import logging
from datetime import datetime
import json

try:
    from .aircraft import Aircraft, AircraftState
except ImportError:
    from aircraft import Aircraft, AircraftState


class ContextDatabase:
    """
    In-memory context database for aircraft tracking
    
    This database uses a Python dictionary to store Aircraft objects, keyed by
    their callsigns. It provides thread-safe operations for storing and retrieving
    aircraft information.
    
    Features:
    - Fast reads and writes using Python dict
    - Thread-safe operations using locks
    - Serializable to JSON for debugging/logging
    - No persistence (in-memory only)
    """
    
    def __init__(self):
        """Initialize the context database"""
        self._aircraft: Dict[str, Aircraft] = {}
        self._lock = threading.RLock()  # Reentrant lock for nested operations
        self._logger = logging.getLogger(__name__)
        self._logger.info("Context Database initialized")
    
    # ========================================================================
    # CREATE / UPDATE Operations
    # ========================================================================
    
    def add_aircraft(
        self,
        callsign: str,
        altitude: float,
        heading: float,
        speed: float,
        latitude: float,
        longitude: float,
        instruction: Optional[str] = None,
        instruction_successful: Optional[bool] = None
    ) -> Aircraft:
        """
        Add a new aircraft to the database or update if exists
        
        Args:
            callsign: Aircraft callsign (unique identifier)
            altitude: Aircraft altitude in feet
            heading: Aircraft heading in degrees
            speed: Aircraft speed in knots
            latitude: Aircraft latitude in decimal degrees
            longitude: Aircraft longitude in decimal degrees
            instruction: Optional initial instruction
            instruction_successful: Optional instruction result
            
        Returns:
            The created/updated Aircraft object
            
        Raises:
            ValueError: If any parameter is invalid
        """
        with self._lock:
            callsign = callsign.upper().strip()
            
            # Create aircraft state
            state = AircraftState(
                altitude=altitude,
                heading=heading,
                speed=speed,
                latitude=latitude,
                longitude=longitude
            )
            
            # Create aircraft
            aircraft = Aircraft(
                callsign=callsign,
                current_state=state,
                last_instruction=instruction,
                last_instruction_successful=instruction_successful
            )
            
            # Store in database
            self._aircraft[callsign] = aircraft
            
            self._logger.info(f"Added aircraft {callsign} to context database")
            return aircraft
    
    def update_aircraft_state(
        self,
        callsign: str,
        altitude: Optional[float] = None,
        heading: Optional[float] = None,
        speed: Optional[float] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
    ) -> Aircraft:
        """
        Update the state of an existing aircraft
        
        Args:
            callsign: Aircraft callsign
            altitude: New altitude (optional)
            heading: New heading (optional)
            speed: New speed (optional)
            latitude: New latitude (optional)
            longitude: New longitude (optional)
            
        Returns:
            The updated Aircraft object
            
        Raises:
            KeyError: If aircraft not found
        """
        with self._lock:
            callsign = callsign.upper().strip()
            
            if callsign not in self._aircraft:
                raise KeyError(f"Aircraft {callsign} not found in database")
            
            aircraft = self._aircraft[callsign]
            aircraft.update_state(
                altitude=altitude,
                heading=heading,
                speed=speed,
                latitude=latitude,
                longitude=longitude
            )
            
            self._logger.debug(f"Updated state for aircraft {callsign}")
            return aircraft
    
    def set_instruction(
        self,
        callsign: str,
        instruction: str,
        successful: Optional[bool] = None
    ) -> Aircraft:
        """
        Set an instruction for an aircraft
        
        Args:
            callsign: Aircraft callsign
            instruction: Instruction text
            successful: Whether instruction was successful (None if pending)
            
        Returns:
            The updated Aircraft object
            
        Raises:
            KeyError: If aircraft not found
        """
        with self._lock:
            callsign = callsign.upper().strip()
            
            if callsign not in self._aircraft:
                raise KeyError(f"Aircraft {callsign} not found in database")
            
            aircraft = self._aircraft[callsign]
            aircraft.set_instruction(instruction, successful)
            
            self._logger.info(
                f"Set instruction for {callsign}: '{instruction}' "
                f"(success={successful})"
            )
            return aircraft
    
    def mark_instruction_result(self, callsign: str, successful: bool) -> Aircraft:
        """
        Mark the result of the last instruction for an aircraft
        
        Args:
            callsign: Aircraft callsign
            successful: Whether the instruction was successful
            
        Returns:
            The updated Aircraft object
            
        Raises:
            KeyError: If aircraft not found
            ValueError: If no instruction has been set
        """
        with self._lock:
            callsign = callsign.upper().strip()
            
            if callsign not in self._aircraft:
                raise KeyError(f"Aircraft {callsign} not found in database")
            
            aircraft = self._aircraft[callsign]
            aircraft.mark_instruction_result(successful)
            
            self._logger.info(
                f"Marked instruction result for {callsign}: {successful}"
            )
            return aircraft
    
    # ========================================================================
    # READ Operations
    # ========================================================================
    
    def get_aircraft(self, callsign: str) -> Optional[Aircraft]:
        """
        Get an aircraft by callsign
        
        Args:
            callsign: Aircraft callsign
            
        Returns:
            Aircraft object or None if not found
        """
        with self._lock:
            callsign = callsign.upper().strip()
            return self._aircraft.get(callsign)
    
    def has_aircraft(self, callsign: str) -> bool:
        """
        Check if an aircraft exists in the database
        
        Args:
            callsign: Aircraft callsign
            
        Returns:
            True if aircraft exists, False otherwise
        """
        with self._lock:
            callsign = callsign.upper().strip()
            return callsign in self._aircraft
    
    def get_all_aircraft(self) -> List[Aircraft]:
        """
        Get all aircraft in the database
        
        Returns:
            List of all Aircraft objects
        """
        with self._lock:
            return list(self._aircraft.values())
    
    def get_aircraft_count(self) -> int:
        """
        Get the total number of aircraft in the database
        
        Returns:
            Number of aircraft
        """
        with self._lock:
            return len(self._aircraft)
    
    def get_all_callsigns(self) -> List[str]:
        """
        Get all callsigns currently in the database
        
        Returns:
            List of callsigns
        """
        with self._lock:
            return list(self._aircraft.keys())
    
    # ========================================================================
    # DELETE Operations
    # ========================================================================
    
    def remove_aircraft(self, callsign: str) -> bool:
        """
        Remove an aircraft from the database
        
        Args:
            callsign: Aircraft callsign
            
        Returns:
            True if aircraft was removed, False if not found
        """
        with self._lock:
            callsign = callsign.upper().strip()
            
            if callsign in self._aircraft:
                del self._aircraft[callsign]
                self._logger.info(f"Removed aircraft {callsign} from database")
                return True
            
            return False
    
    def clear(self) -> int:
        """
        Clear all aircraft from the database
        
        Returns:
            Number of aircraft that were removed
        """
        with self._lock:
            count = len(self._aircraft)
            self._aircraft.clear()
            self._logger.info(f"Cleared all {count} aircraft from database")
            return count
    
    # ========================================================================
    # Utility / Serialization Methods
    # ========================================================================
    
    def to_dict(self) -> Dict[str, dict]:
        """
        Convert entire database to dictionary
        
        Returns:
            Dictionary mapping callsigns to aircraft data
        """
        with self._lock:
            return {
                callsign: aircraft.to_dict()
                for callsign, aircraft in self._aircraft.items()
            }
    
    def to_json(self, indent: int = 2) -> str:
        """
        Convert entire database to JSON string
        
        Args:
            indent: JSON indentation level
            
        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict(), indent=indent)
    
    def get_summary(self) -> str:
        """
        Get a human-readable summary of the database
        
        Returns:
            Summary string
        """
        with self._lock:
            count = len(self._aircraft)
            
            if count == 0:
                return "Context Database: Empty (no aircraft tracked)"
            
            lines = [
                f"Context Database Summary ({count} aircraft):",
                "=" * 60
            ]
            
            for aircraft in self._aircraft.values():
                lines.append(str(aircraft))
                if aircraft.last_instruction:
                    success_str = (
                        "✓" if aircraft.last_instruction_successful
                        else "✗" if aircraft.last_instruction_successful is False
                        else "?"
                    )
                    lines.append(
                        f"  └─ Last instruction [{success_str}]: "
                        f"{aircraft.last_instruction}"
                    )
            
            lines.append("=" * 60)
            return "\n".join(lines)
    
    def __len__(self) -> int:
        """Return the number of aircraft in the database"""
        return self.get_aircraft_count()
    
    def __contains__(self, callsign: str) -> bool:
        """Check if a callsign exists in the database"""
        return self.has_aircraft(callsign)
    
    def __repr__(self) -> str:
        """String representation of database"""
        return f"<ContextDatabase: {len(self._aircraft)} aircraft>"
