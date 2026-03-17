import socket
import time

class FlightGearConnection:

    def __init__(self, host: str = "localhost", port: int = 5500):
        self.host = host
        self.port = port

    def connect(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.host, self.port))
        self.sock = sock

    def disconnect(self) -> None:
        self.sock.close()

    def _receive(self) -> str:
        data, addr = self.sock.recvfrom(1024)
        return data.decode("utf-8")

    def _send(self, data: str) -> None:
        self.sock.sendto(data.encode("utf-8"), (self.host, self.port))

    def get_property(self, property_name: str) -> str:
        self._send(f"get {property_name}")
        return self._receive()

    def set_property(self, property_name: str, value: str) -> None:
        self._send(f"set {property_name} {value}")

    def get_properties(self, property_names: list[str]) -> list[str]:
        return [self.get_property(property_name) for property_name in property_names]

    def set_properties(self, property_names: list[str], values: list[str]) -> None:
        for property_name, value in zip(property_names, values):
            self.set_property(property_name, value)

    def get_properties_with_delay(self, property_names: list[str], delay: float) -> list[str]:
        return [self.get_property(property_name) for property_name in property_names]
        