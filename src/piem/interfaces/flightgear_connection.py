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

    def receive(self) -> str:
        data, addr = self.sock.recvfrom(1024)
        return data.decode("utf-8")

    def send(self, data: str) -> None:
        self.sock.sendto(data.encode("utf-8"), (self.host, self.port))
