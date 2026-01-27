"""
Wrapper Telnet (set/get/subscribe)
Cliente para comunicación con FlightGear via Telnet
"""

import socket
from typing import Optional, Any
from src.common.logger import get_logger

logger = get_logger(__name__)


class FlightGearClient:
    """Cliente Telnet para comunicación con FlightGear"""
    
    def __init__(self, host: str = "localhost", port: int = 5401, timeout: int = 5):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.socket: Optional[socket.socket] = None
        self.connected = False
        logger.info(f"FlightGearClient initialized ({host}:{port})")
    
    def connect(self) -> bool:
        """Establece conexión con FlightGear"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.host, self.port))
            self.connected = True
            self._read_response()
            logger.info(f"Connected to FlightGear at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to FlightGear: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Cierra la conexión"""
        if self.socket:
            try:
                self.socket.close()
                logger.info("Disconnected from FlightGear")
            except Exception as e:
                logger.error(f"Error disconnecting: {e}")
            finally:
                self.connected = False
                self.socket = None
    
    def get_property(self, prop_path: str) -> Optional[str]:
        """Obtiene el valor de una propiedad"""
        if not self.connected:
            return None
        try:
            command = f"get {prop_path}\r\n"
            self.socket.send(command.encode())
            response = self._read_response()
            return response
        except Exception as e:
            logger.error(f"Error getting property {prop_path}: {e}")
            return None
    
    def set_property(self, prop_path: str, value: Any) -> bool:
        """Establece el valor de una propiedad"""
        if not self.connected:
            return False
        try:
            command = f"set {prop_path} {value}\r\n"
            self.socket.send(command.encode())
            self._read_response()
            return True
        except Exception as e:
            logger.error(f"Error setting property {prop_path}: {e}")
            return False
    
    def _read_response(self, buffer_size: int = 1024) -> str:
        """Lee la respuesta del servidor"""
        try:
            data = self.socket.recv(buffer_size)
            return data.decode().strip()
        except Exception as e:
            logger.error(f"Error reading response: {e}")
            return ""
