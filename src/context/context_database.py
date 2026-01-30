from src.context.aircraft import Aircraft

class ContextDatabase:

    def __init__(self) -> None:
        self.aircrafts : dict[str, Aircraft] = dict()
        self.instructions_supported = ["ALTITUDE", "SPEED"]

    def get_instructions_supported(self) -> str:
        """
        Method to get the list of instructions supported by the context database.
        
        :param self: self
        :return: The list of instructions supported
        :rtype: list[str]
        """
        return ", ".join(self.instructions_supported)

    def to_string(self) -> str:
        """
        Method to convert the context database to a string.
        
        :param self: self
        :return: The string representation of the context database
        :rtype: str
        """
        return str(self.aircrafts)

    def get_callsign_list(self) -> list[str]:
        """
        Method to get the list of callsigns from the context database.
        
        :param self: self
        :return: The list of callsigns
        :rtype: list[str]
        """
        return list(self.aircrafts.keys())

    def add_aircraft(self, callsign) -> Aircraft:
        """
        Method to add an aircraft to the context database.
        
        :param self: self
        :param callsign: The aircraft's callsign
        :return: The created aircraft
        :rtype: Aircraft
        """
        if callsign in self.aircrafts:
            return self.aircrafts[callsign]
        
        aircraft = Aircraft(callsign)

        self.aircrafts[callsign] = aircraft

        return aircraft

    def get_aircraft(self, callsign) -> Aircraft:
        """
        Method to get an aircraft from the context database.
        
        :param self: self
        :param callsign: The aircraft's callsign
        :return: The aircraft
        :rtype: Aircraft
        """
        return self.aircrafts.get(callsign)

    def remove_aircraft(self, callsign) -> None:
        """
        Method to remove an aircraft from the context database.
        
        :param self: self
        :param callsign: The aircraft's callsign
        :return: None
        :rtype: None
        """
        if callsign in self.aircrafts:
            del self.aircrafts[callsign]

    def get_all_aircrafts(self) -> list[Aircraft]:
        """
        Method to get all aircrafts from the context database.
        
        :param self: self
        :return: The list of aircrafts
        :rtype: list[Aircraft]
        """
        return list(self.aircrafts.values())


def get_context_database():
    """
    Factory function to get the appropriate context database instance.
    
    Returns Redis-backed database if USE_REDIS is True in config,
    otherwise returns in-memory database.
    
    Returns:
        ContextDatabase or ContextDatabaseRedis instance
    """
    import src.common.config as config
    
    if config.USE_REDIS:
        from src.context.context_database_redis import ContextDatabaseRedis
        return ContextDatabaseRedis()
    else:
        return ContextDatabase()