from src.piem.core.flight_gear_connection import FlightGearConnection

class PIEMMonolith:

    METHOD_MAP = {
        "autopilot_on": self._run_instruction_set_autopilot_on,
        "altitude": self._run_instruction_set_altitude,
    }

    def __init__(self, flight_gear_connection: FlightGearConnection):
        self.flight_gear_connection = flight_gear_connection
    
    def _run_instruction_set_autopilot_on(self) -> None:
        """
        Enable the autopilot in FlightGear.
        Sets the autopilot master switch property to true.
        """
        self.flight_gear_connection.set_property("/autopilot/locks/master", "true")

    def _run_instruction_set_altitude(self, altitude: int) -> None:
        """
        Set the altitude in FlightGear.
        Sets the autopilot altitude property to the given altitude.
        """
        self.flight_gear_connection.set_property("/autopilot/settings/target-altitude", str(altitude))

    def run_instruction(self, instruction: dict) -> str:
        """
        Run a single instruction in FlightGear.

        Instruction format:
        {
            "callsign": str,
            "command": str,
            "value": int,
            "success_msg": str,
            "error_msg": str
        }
        """
        callsign = instruction["callsign"]
        command = instruction["command"]
        value = instruction["value"]
        success_msg = instruction["success_msg"]
        error_msg = instruction["error_msg"]

        method = self.METHOD_MAP.get(command)
        if method:
            method(value)
        else:
            return error_msg
        return success_msg
    
    def run(self):
        pass