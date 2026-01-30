"""
Example demonstrating multi-process shared context database usage.

This script shows how multiple processes can access and modify
the same shared aircraft context using Redis backend.
"""

from src.context.context_database import get_context_database
import time


def example_basic_usage():
    """Basic usage example - works identically for in-memory or Redis backend."""
    print("=== Basic Usage Example ===\n")
    
    # Get context database (automatically chooses Redis or in-memory based on config)
    db = get_context_database()
    
    # Add aircraft
    print("Adding aircraft AFR123...")
    aircraft = db.add_aircraft("AFR123")
    aircraft.altitude = 35000
    aircraft.speed = 450
    aircraft.heading = 180
    
    # IMPORTANT: For Redis backend, you must update after modifying
    if hasattr(db, 'update_aircraft'):
        db.update_aircraft(aircraft)
    
    # Retrieve aircraft
    print("Retrieving aircraft AFR123...")
    retrieved = db.get_aircraft("AFR123")
    print(f"  Callsign: {retrieved.callsign}")
    print(f"  Altitude: {retrieved.altitude}")
    print(f"  Speed: {retrieved.speed}")
    print(f"  Heading: {retrieved.heading}")
    
    # List all aircraft
    print(f"\nAll callsigns: {db.get_callsign_list()}")
    
    # Get supported instructions
    print(f"Supported instructions: {db.get_instructions_supported()}")
    
    # Remove aircraft
    print("\nRemoving aircraft AFR123...")
    db.remove_aircraft("AFR123")
    print(f"Remaining callsigns: {db.get_callsign_list()}")


def example_multi_process():
    """
    Example showing multi-process sharing.
    
    Run this script in two separate terminals simultaneously to see
    how Process A's changes are visible to Process B.
    """
    print("\n=== Multi-Process Example ===")
    print("Run this script in two terminals simultaneously!\n")
    
    db = get_context_database()
    
    import sys
    process_name = sys.argv[1] if len(sys.argv) > 1 else "A"
    
    if process_name == "A":
        print("[Process A] Adding aircraft BAW456...")
        aircraft = db.add_aircraft("BAW456")
        aircraft.altitude = 38000
        aircraft.speed = 480
        if hasattr(db, 'update_aircraft'):
            db.update_aircraft(aircraft)
        print("[Process A] Aircraft added!")
        
    else:
        print("[Process B] Waiting 2 seconds for Process A to add aircraft...")
        time.sleep(2)
        print(f"[Process B] Checking for aircraft: {db.get_callsign_list()}")
        baw456 = db.get_aircraft("BAW456")
        if baw456:
            print(f"[Process B] Found BAW456! Altitude: {baw456.altitude}")
        else:
            print("[Process B] BAW456 not found (Process A may not have run yet)")


def example_listener_pattern():
    """
    Example showing typical listener usage pattern.
    
    This is how you would use the context database in your
    actual listener process.
    """
    print("\n=== Listener Pattern Example ===\n")
    
    db = get_context_database()
    
    # Simulating receiving a radio call
    callsign = "UAL789"
    instruction = "ALTITUDE"
    target_altitude = 32000
    
    print(f"Received instruction: {callsign} {instruction} {target_altitude}")
    
    # Get or create aircraft
    aircraft = db.get_aircraft(callsign)
    if not aircraft:
        print(f"  Creating new aircraft: {callsign}")
        aircraft = db.add_aircraft(callsign)
    
    # Update aircraft state
    print(f"  Updating altitude to {target_altitude}...")
    aircraft.altitude = target_altitude
    aircraft.last_known_instruction = f"{instruction} {target_altitude}"
    aircraft.last_instruction_was_succesful = True
    
    # CRITICAL: Save changes back to database
    if hasattr(db, 'update_aircraft'):
        db.update_aircraft(aircraft)
    
    print(f"  ✓ Aircraft {callsign} updated successfully")
    
    # Verify update
    verified = db.get_aircraft(callsign)
    print(f"  Verified altitude: {verified.altitude}")


if __name__ == "__main__":
    print("Shared Context Database Examples")
    print("=" * 50)
    
    # Run basic example
    example_basic_usage()
    
    # Run listener pattern example
    example_listener_pattern()
    
    # Uncomment to test multi-process:
    # example_multi_process()
