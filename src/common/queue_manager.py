"""
Wrapper para Multiprocessing.Queue / Redis
Gestiona las colas de comunicación entre procesos
"""

from multiprocessing import Queue
from typing import Any, Optional
import time
from src.common.logger import get_logger

logger = get_logger(__name__)


class QueueManager:
    """
    Gestiona colas de comunicación entre procesos.
    Wrapper que puede usar multiprocessing.Queue o Redis según configuración.
    """
    
    def __init__(self, use_redis: bool = False, maxsize: int = 0):
        """
        Inicializa el gestor de colas
        
        Args:
            use_redis: Si True, usa Redis; si False, usa multiprocessing.Queue
            maxsize: Tamaño máximo de la cola (0 = ilimitado)
        """
        self.use_redis = use_redis
        
        if use_redis:
            # TODO: Implementar wrapper de Redis
            raise NotImplementedError("Redis support not yet implemented")
        else:
            self.queue = Queue(maxsize=maxsize)
        
        logger.info(f"QueueManager initialized (Redis: {use_redis})")
    
    def put(self, item: Any, block: bool = True, timeout: Optional[float] = None):
        """
        Añade un elemento a la cola
        
        Args:
            item: Elemento a añadir
            block: Si True, bloquea hasta que haya espacio
            timeout: Tiempo máximo de espera en segundos
        """
        try:
            self.queue.put(item, block=block, timeout=timeout)
            logger.debug(f"Item added to queue: {type(item).__name__}")
        except Exception as e:
            logger.error(f"Error adding item to queue: {e}")
            raise
    
    def get(self, block: bool = True, timeout: Optional[float] = None) -> Any:
        """
        Obtiene un elemento de la cola
        
        Args:
            block: Si True, bloquea hasta que haya un elemento
            timeout: Tiempo máximo de espera en segundos
            
        Returns:
            Elemento de la cola
        """
        try:
            item = self.queue.get(block=block, timeout=timeout)
            logger.debug(f"Item retrieved from queue: {type(item).__name__}")
            return item
        except Exception as e:
            logger.error(f"Error getting item from queue: {e}")
            raise
    
    def empty(self) -> bool:
        """Verifica si la cola está vacía"""
        return self.queue.empty()
    
    def qsize(self) -> int:
        """Retorna el tamaño aproximado de la cola"""
        try:
            return self.queue.qsize()
        except NotImplementedError:
            # Algunas implementaciones de Queue no soportan qsize
            return -1
    
    def close(self):
        """Cierra la cola"""
        if hasattr(self.queue, 'close'):
            self.queue.close()
            logger.info("Queue closed")
