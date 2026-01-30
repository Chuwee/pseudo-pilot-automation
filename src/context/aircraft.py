class Aircraft:
    def __init__(self, callsign: str) -> None:
        self.callsign = callsign
        self.last_instruction_was_succesful = False
        self.last_known_instruction = None
        self.altitude = None
        self.heading = None
        self.speed = None
        self.latitude = None
        self.longitude = None

    def to_string(self) -> str:
        """
        Method to convert the aircraft to a string.
        
        :param self: self
        :return: The string representation of the aircraft
        :rtype: str
        """
        return str(self.__dict__)

    def __str__(self) -> str:
        """
        Method to convert the aircraft to a string.
        
        :param self: self
        :return: The string representation of the aircraft
        :rtype: str
        """
        return self.to_string()

    def to_dict(self) -> dict:
        """
        Serialize aircraft to dictionary for Redis storage.
        
        :param self: self
        :return: Dictionary representation of the aircraft
        :rtype: dict
        """
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict) -> 'Aircraft':
        """
        Deserialize aircraft from dictionary.
        
        :param data: Dictionary containing aircraft data
        :return: Aircraft instance
        :rtype: Aircraft
        """
        aircraft = cls(data['callsign'])
        for key, value in data.items():
            if key != 'callsign':  # callsign already set in __init__
                setattr(aircraft, key, value)
        return aircraft