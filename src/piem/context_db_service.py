#!/usr/bin/env python3
"""
Context Database Service - Daemon that manages aircraft context

This service runs as a background daemon and provides a simple socket-based
interface to manage the aircraft context database.
"""

import socket
import json
import logging
import signal
import sys
import os
from pathlib import Path
from typing import Optional

# Setup path for imports - add both paths
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '../..'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src', 'piem', 'core'))

# Direct imports to avoid circular dependencies
import context_db
import aircraft

ContextDatabase = context_db.ContextDatabase
Aircraft = aircraft.Aircraft
AircraftState = aircraft.AircraftState

# Configuration
SOCKET_PATH = "/tmp/pseudopilot_context_db.sock"
PID_FILE = "/tmp/pseudopilot_context_db.pid"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ContextDatabaseService:
    """
    Background service that manages the context database
    
    Provides a Unix socket interface for external processes to interact
    with the aircraft context database.
    """
    
    def __init__(self, socket_path: str = SOCKET_PATH):
        """
        Initialize the context database service
        
        Args:
            socket_path: Path to Unix socket for communication
        """
        self.socket_path = socket_path
        self.db = ContextDatabase()
        self.running = False
        self.server_socket: Optional[socket.socket] = None
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)
    
    def start(self):
        """Start the context database service"""
        # Remove old socket if it exists
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)
        
        # Create Unix socket
        self.server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server_socket.bind(self.socket_path)
        self.server_socket.listen(5)
        
        # Write PID file
        with open(PID_FILE, 'w') as f:
            f.write(str(os.getpid()))
        
        self.running = True
        logger.info(f"Context Database Service started on {self.socket_path}")
        logger.info(f"PID: {os.getpid()}")
        
        # Main service loop
        while self.running:
            try:
                # Accept connection
                client_socket, _ = self.server_socket.accept()
                
                # Handle request
                self._handle_client(client_socket)
                
            except Exception as e:
                if self.running:
                    logger.error(f"Error handling client: {e}")
    
    def _handle_client(self, client_socket: socket.socket):
        """
        Handle a client request
        
        Args:
            client_socket: Client socket connection
        """
        try:
            # Receive request (max 4096 bytes)
            data = client_socket.recv(4096).decode('utf-8')
            
            if not data:
                return
            
            # Parse request
            request = json.loads(data)
            command = request.get('command')
            
            logger.debug(f"Received command: {command}")
            
            # Process command
            response = self._process_command(command, request)
            
            # Send response
            client_socket.sendall(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            response = {'status': 'error', 'message': str(e)}
            client_socket.sendall(json.dumps(response).encode('utf-8'))
        
        finally:
            client_socket.close()
    
    def _process_command(self, command: str, request: dict) -> dict:
        """
        Process a command and return response
        
        Args:
            command: Command to execute
            request: Full request data
            
        Returns:
            Response dictionary
        """
        if command == 'add_aircraft':
            return self._cmd_add_aircraft(request)
        
        elif command == 'get_aircraft':
            return self._cmd_get_aircraft(request)
        
        elif command == 'update_state':
            return self._cmd_update_state(request)
        
        elif command == 'set_instruction':
            return self._cmd_set_instruction(request)
        
        elif command == 'list_aircraft':
            return self._cmd_list_aircraft(request)
        
        elif command == 'remove_aircraft':
            return self._cmd_remove_aircraft(request)
        
        elif command == 'get_summary':
            return self._cmd_get_summary(request)
        
        elif command == 'ping':
            return {'status': 'ok', 'message': 'pong'}
        
        else:
            return {'status': 'error', 'message': f'Unknown command: {command}'}
    
    # Command handlers
    
    def _cmd_add_aircraft(self, request: dict) -> dict:
        """Add a new aircraft"""
        try:
            callsign = request['callsign']
            altitude = request.get('altitude', 0)
            heading = request.get('heading', 0)
            speed = request.get('speed', 0)
            latitude = request.get('latitude', 0)
            longitude = request.get('longitude', 0)
            
            aircraft = self.db.add_aircraft(
                callsign=callsign,
                altitude=altitude,
                heading=heading,
                speed=speed,
                latitude=latitude,
                longitude=longitude
            )
            
            return {
                'status': 'ok',
                'message': f'Aircraft {callsign} added',
                'aircraft': aircraft.to_dict()
            }
        
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _cmd_get_aircraft(self, request: dict) -> dict:
        """Get aircraft by callsign"""
        try:
            callsign = request['callsign']
            aircraft = self.db.get_aircraft(callsign)
            
            if aircraft:
                return {
                    'status': 'ok',
                    'aircraft': aircraft.to_dict()
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Aircraft {callsign} not found'
                }
        
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _cmd_update_state(self, request: dict) -> dict:
        """Update aircraft state"""
        try:
            callsign = request['callsign']
            
            aircraft = self.db.update_aircraft_state(
                callsign,
                altitude=request.get('altitude'),
                heading=request.get('heading'),
                speed=request.get('speed'),
                latitude=request.get('latitude'),
                longitude=request.get('longitude')
            )
            
            return {
                'status': 'ok',
                'message': f'Aircraft {callsign} updated',
                'aircraft': aircraft.to_dict()
            }
        
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _cmd_set_instruction(self, request: dict) -> dict:
        """Set instruction for aircraft"""
        try:
            callsign = request['callsign']
            instruction = request['instruction']
            successful = request.get('successful')
            
            aircraft = self.db.set_instruction(callsign, instruction, successful)
            
            return {
                'status': 'ok',
                'message': f'Instruction set for {callsign}',
                'aircraft': aircraft.to_dict()
            }
        
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _cmd_list_aircraft(self, request: dict) -> dict:
        """List all aircraft"""
        try:
            aircraft_list = [
                aircraft.to_dict()
                for aircraft in self.db.get_all_aircraft()
            ]
            
            return {
                'status': 'ok',
                'count': len(aircraft_list),
                'aircraft': aircraft_list
            }
        
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _cmd_remove_aircraft(self, request: dict) -> dict:
        """Remove aircraft"""
        try:
            callsign = request['callsign']
            removed = self.db.remove_aircraft(callsign)
            
            if removed:
                return {
                    'status': 'ok',
                    'message': f'Aircraft {callsign} removed'
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Aircraft {callsign} not found'
                }
        
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _cmd_get_summary(self, request: dict) -> dict:
        """Get database summary"""
        try:
            summary = self.db.get_summary()
            
            return {
                'status': 'ok',
                'summary': summary,
                'count': len(self.db)
            }
        
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def stop(self):
        """Stop the service"""
        self.running = False
        
        if self.server_socket:
            self.server_socket.close()
        
        # Clean up socket file
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)
        
        # Clean up PID file
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        
        logger.info("Context Database Service stopped")


def main():
    """Main entry point"""
    print("=" * 60)
    print("🗄️  Context Database Service - Starting")
    print("=" * 60)
    print()
    
    service = ContextDatabaseService()
    
    try:
        service.start()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        service.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        service.stop()
        sys.exit(1)


if __name__ == "__main__":
    main()
