"""
Mapeo de comandos a props (/controls/...)
Proporciona mapeo de comandos a rutas de propiedades de FlightGear
"""

from typing import Dict


class FlightGearProperties:
    """Mapeo de propiedades de FlightGear"""
    
    # Controles de vuelo
    AILERON = "/controls/flight/aileron"
    ELEVATOR = "/controls/flight/elevator"
    RUDDER = "/controls/flight/rudder"
    THROTTLE = "/controls/engines/engine/throttle"
    FLAPS = "/controls/flight/flaps"
    GEAR = "/controls/gear/gear-down"
    
    # Autopilot
    AP_HEADING = "/autopilot/settings/heading-bug-deg"
    AP_ALTITUDE = "/autopilot/settings/target-altitude-ft"
    AP_SPEED = "/autopilot/settings/target-speed-kt"
    AP_VERTICAL_SPEED = "/autopilot/settings/vertical-speed-fpm"
    
    # Posición y orientación
    LATITUDE = "/position/latitude-deg"
    LONGITUDE = "/position/longitude-deg"
    ALTITUDE = "/position/altitude-ft"
    HEADING = "/orientation/heading-deg"
    PITCH = "/orientation/pitch-deg"
    ROLL = "/orientation/roll-deg"
    
    # Velocidades
    AIRSPEED = "/velocities/airspeed-kt"
    GROUNDSPEED = "/velocities/groundspeed-kt"
    VERTICAL_SPEED = "/velocities/vertical-speed-fps"
    
    # Estado
    ON_GROUND = "/gear/gear[0]/wow"
    
    @staticmethod
    def get_command_mapping() -> Dict[str, str]:
        """Retorna mapeo de comandos a propiedades"""
        return {
            "heading": FlightGearProperties.AP_HEADING,
            "altitude": FlightGearProperties.AP_ALTITUDE,
            "speed": FlightGearProperties.AP_SPEED,
            "flaps": FlightGearProperties.FLAPS,
            "gear": FlightGearProperties.GEAR,
            "throttle": FlightGearProperties.THROTTLE,
        }
