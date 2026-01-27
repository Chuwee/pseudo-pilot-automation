"""PIEM Interfaces - Communication with FlightGear simulator"""

from .fg_client import FlightGearClient
from .properties import FlightGearProperties

__all__ = ['FlightGearClient', 'FlightGearProperties']
