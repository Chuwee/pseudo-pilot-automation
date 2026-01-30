"""
Redis-backed Context Database for multi-process shared state.

This module provides a Redis-backed implementation of ContextDatabase
that allows multiple processes to share aircraft context transparently.
"""

import json
import redis
from typing import Optional, List
from src.context.aircraft import Aircraft
from src.common.logger import get_logger
import src.common.config as config

logger = get_logger(__name__)


class ContextDatabaseRedis:
    """
    Redis-backed context database enabling multi-process data sharing.
    
    This class maintains the same interface as the in-memory ContextDatabase
    but stores all data in Redis, allowing multiple processes to access
    and modify the same shared state.
    """
    
    def __init__(self, redis_client: Optional[redis.Redis] = None) -> None:
        """
        Initialize Redis-backed context database.
        
        Args:
            redis_client: Optional Redis client instance. If not provided,
                         creates a new connection using config settings.
        """
        if redis_client:
            self.redis = redis_client
        else:
            self.redis = redis.Redis(
                host=config.REDIS_HOST,
                port=config.REDIS_PORT,
                db=config.REDIS_DB,
                password=config.REDIS_PASSWORD,
                decode_responses=True,  # Automatically decode bytes to strings
                socket_connect_timeout=5,
                socket_timeout=5
            )
        
        # Test connection
        try:
            self.redis.ping()
            logger.info(f"Connected to Redis at {config.REDIS_HOST}:{config.REDIS_PORT}")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
        
        # Initialize supported instructions if not already set
        if not self.redis.exists("instructions:supported"):
            self.redis.delete("instructions:supported")
            self.redis.rpush("instructions:supported", "ALTITUDE", "SPEED")
            logger.info("Initialized supported instructions in Redis")

    def get_instructions_supported(self) -> str:
        """
        Get the list of instructions supported by the context database.
        
        Returns:
            Comma-separated string of supported instructions
        """
        instructions = self.redis.lrange("instructions:supported", 0, -1)
        return ", ".join(instructions)

    def to_string(self) -> str:
        """
        Convert the context database to a string representation.
        
        Returns:Ok
            String representation of all aircraft
        """
        callsigns = self.get_callsign_list()
        aircrafts = {cs: self.get_aircraft(cs).to_dict() for cs in callsigns}
        return str(aircrafts)

    def get_callsign_list(self) -> list[str]:
        """
        Get the list of callsigns from the context database.
        
        Returns:
            List of active aircraft callsigns
        """
        callsigns = self.redis.smembers("aircraft:active")
        return list(callsigns) if callsigns else []

    def add_aircraft(self, callsign: str) -> Aircraft:
        """
        Add an aircraft to the context database.
        
        Args:
            callsign: The aircraft's callsign
            
        Returns:
            The created or existing Aircraft instance
        """
        # Check if aircraft already exists
        if self.redis.exists(f"aircraft:{callsign}"):
            logger.info(f"Aircraft {callsign} already exists, returning existing")
            return self.get_aircraft(callsign)
        
        # Create new aircraft
        aircraft = Aircraft(callsign)
        
        # Store in Redis as JSON
        self.redis.set(
            f"aircraft:{callsign}",
            json.dumps(aircraft.to_dict())
        )
        
        # Add to active set
        self.redis.sadd("aircraft:active", callsign)
        
        logger.info(f"Added aircraft {callsign} to context database")
        return aircraft

    def get_aircraft(self, callsign: str) -> Optional[Aircraft]:
        """
        Get an aircraft from the context database.
        
        Args:
            callsign: The aircraft's callsign
            
        Returns:
            Aircraft instance or None if not found
        """
        data = self.redis.get(f"aircraft:{callsign}")
        
        if data is None:
            return None
        
        try:
            aircraft_dict = json.loads(data)
            return Aircraft.from_dict(aircraft_dict)
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to deserialize aircraft {callsign}: {e}")
            return None

    def update_aircraft(self, aircraft: Aircraft) -> None:
        """
        Update an existing aircraft in the database.
        
        This method is useful when you've modified an Aircraft object
        and want to persist the changes back to Redis.
        
        Args:
            aircraft: The Aircraft instance to update
        """
        callsign = aircraft.callsign
        
        if not self.redis.sismember("aircraft:active", callsign):
            logger.warning(f"Attempting to update non-existent aircraft {callsign}")
            return
        
        self.redis.set(
            f"aircraft:{callsign}",
            json.dumps(aircraft.to_dict())
        )
        logger.debug(f"Updated aircraft {callsign}")

    def remove_aircraft(self, callsign: str) -> None:
        """
        Remove an aircraft from the context database.
        
        Args:
            callsign: The aircraft's callsign
        """
        if self.redis.sismember("aircraft:active", callsign):
            self.redis.delete(f"aircraft:{callsign}")
            self.redis.srem("aircraft:active", callsign)
            logger.info(f"Removed aircraft {callsign} from context database")

    def get_all_aircrafts(self) -> list[Aircraft]:
        """
        Get all aircrafts from the context database.
        
        Returns:
            List of all Aircraft instances
        """
        callsigns = self.get_callsign_list()
        aircrafts = []
        
        for callsign in callsigns:
            aircraft = self.get_aircraft(callsign)
            if aircraft:
                aircrafts.append(aircraft)
        
        return aircrafts

    def clear_all(self) -> None:
        """
        Clear all aircraft data from the database.
        Useful for testing or resetting state.
        """
        callsigns = self.get_callsign_list()
        for callsign in callsigns:
            self.remove_aircraft(callsign)
        logger.info("Cleared all aircraft from context database")

    def close(self) -> None:
        """
        Close the Redis connection.
        """
        self.redis.close()
        logger.info("Closed Redis connection")
