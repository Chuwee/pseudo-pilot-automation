"""
Sistema de logs centralizado
Proporciona logging consistente para todos los módulos del sistema
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


class SystemLogger:
    """Clase centralizada para gestionar el logging del sistema"""
    
    def __init__(self, log_dir: str = "logs", log_level: int = logging.INFO):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.log_level = log_level
        self._setup_logger()
    
    def _setup_logger(self):
        """Configura el logger principal del sistema"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"session_{timestamp}.log"
        
        # Configurar formato
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para archivo
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(formatter)
        
        # Handler para consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(formatter)
        
        # Configurar logger raíz
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Obtiene un logger para un módulo específico"""
        return logging.getLogger(name)


# Instancia global del logger
_system_logger: Optional[SystemLogger] = None


def initialize_logger(log_dir: str = "logs", log_level: int = logging.INFO):
    """Inicializa el sistema de logging"""
    global _system_logger
    _system_logger = SystemLogger(log_dir, log_level)


def get_logger(name: str) -> logging.Logger:
    """Obtiene un logger para un módulo específico"""
    if _system_logger is None:
        initialize_logger()
    return SystemLogger.get_logger(name)
