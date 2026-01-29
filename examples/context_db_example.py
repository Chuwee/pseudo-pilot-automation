#!/usr/bin/env python3
"""
Context Database - Standalone Test Script

This script directly imports and tests the context database modules
without going through package initialization.
"""

import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Direct import of the modules
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, os.path.join(project_root, 'src', 'piem', 'core'))

# Import the modules directly
import aircraft
import context_db

Aircraft = aircraft.Aircraft
AircraftState = aircraft.AircraftState
ContextDatabase = context_db.ContextDatabase


def print_separator(title: str = ""):
    """Print a visual separator"""
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
    else:
        print(f"{'='*60}\n")


def test_basic_usage():
    """Test basic CRUD operations"""
    print_separator("TEST 1: Basic Usage")
    
    # Initialize the database
    db = ContextDatabase()
    print("✓ Context Database initialized")
    print(f"  Current count: {len(db)} aircraft\n")
    
    # Add first aircraft
    print("Adding aircraft AAL123...")
    aircraft1 = db.add_aircraft(
        callsign="AAL123",
        altitude=35000,
        heading=270,
        speed=450,
        latitude=40.7128,
        longitude=-74.0060
    )
    print(f"✓ Added: {aircraft1}\n")
    
    # Add second aircraft
    print("Adding aircraft UAL456...")
    aircraft2 = db.add_aircraft(
        callsign="UAL456",
        altitude=28000,
        heading=90,
        speed=380,
        latitude=34.0522,
        longitude=-118.2437,
        instruction="Climb to FL350",
        instruction_successful=None  # Pending
    )
    print(f"✓ Added: {aircraft2}\n")
    
    # Show database summary
    print(db.get_summary())
    print(f"\nTotal aircraft in database: {len(db)}")
    
    return db


def test_updating_state(db):
    """Test updating aircraft state"""
    print_separator("TEST 2: Updating Aircraft State")
    
    # Add an aircraft
    db.add_aircraft(
        callsign="DAL789",
        altitude=10000,
        heading=180,
        speed=250,
        latitude=33.9416,
        longitude=-118.4085
    )
    
    print("Initial state:")
    aircraft_obj = db.get_aircraft("DAL789")
    print(f"  {aircraft_obj}\n")
    
    # Update altitude and speed
    print("Updating altitude to 15000ft and speed to 280kts...")
    db.update_aircraft_state("DAL789", altitude=15000, speed=280)
    
    aircraft_obj = db.get_aircraft("DAL789")
    print(f"  {aircraft_obj}\n")
    
    # Update position
    print("Updating position...")
    db.update_aircraft_state(
        "DAL789",
        latitude=34.0000,
        longitude=-118.0000
    )
    
    aircraft_obj = db.get_aircraft("DAL789")
    print(f"  {aircraft_obj}")


def test_instructions(db):
    """Test instruction tracking"""
    print_separator("TEST 3: Tracking Instructions")
    
    # Add aircraft
    db.add_aircraft(
        callsign="SWA321",
        altitude=12000,
        heading=45,
        speed=320,
        latitude=29.7604,
        longitude=-95.3698
    )
    
    print("Aircraft added without instruction")
    aircraft_obj = db.get_aircraft("SWA321")
    print(f"  Instruction: {aircraft_obj.last_instruction}")
    print(f"  Success: {aircraft_obj.last_instruction_successful}\n")
    
    # Set an instruction
    print("Setting instruction: 'Turn left heading 030'...")
    db.set_instruction("SWA321", "Turn left heading 030")
    
    aircraft_obj = db.get_aircraft("SWA321")
    print(f"  Instruction: {aircraft_obj.last_instruction}")
    print(f"  Success: {aircraft_obj.last_instruction_successful} (pending)\n")
    
    # Mark as successful
    print("Marking instruction as successful...")
    db.mark_instruction_result("SWA321", successful=True)
    
    aircraft_obj = db.get_aircraft("SWA321")
    print(f"  Instruction: {aircraft_obj.last_instruction}")
    print(f"  Success: {aircraft_obj.last_instruction_successful} ✓\n")
    
    # Set another instruction that fails
    print("Setting new instruction: 'Climb to FL450'...")
    db.set_instruction("SWA321", "Climb to FL450")
    print("Marking instruction as failed...")
    db.mark_instruction_result("SWA321", successful=False)
    
    aircraft_obj = db.get_aircraft("SWA321")
    print(f"  Instruction: {aircraft_obj.last_instruction}")
    print(f"  Success: {aircraft_obj.last_instruction_successful} ✗")


def test_serialization(db):
    """Test serialization"""
    print_separator("TEST 4: Serialization")
    
    # Add some aircraft
    db.add_aircraft(
        callsign="N12345",
        altitude=5000,
        heading=360,
        speed=120,
        latitude=37.7749,
        longitude=-122.4194,
        instruction="Cleared for takeoff runway 28L",
        instruction_successful=True
    )
    
    # Convert to JSON
    print("Database as JSON (truncated):")
    json_str = db.to_json()
    print(json_str[:300] + "..." if len(json_str) > 300 else json_str)
    
    # Individual aircraft serialization
    aircraft_obj = db.get_aircraft("N12345")
    print("\nIndividual aircraft as JSON:")
    print(aircraft_obj.to_json())


def test_validation():
    """Test validation of aircraft parameters"""
    print_separator("TEST 5: Validation")
    
    db = ContextDatabase()
    
    # Test valid aircraft
    print("Creating valid aircraft...")
    try:
        aircraft_obj = db.add_aircraft(
            callsign="TEST001",
            altitude=10000,
            heading=180,
            speed=250,
            latitude=40.0,
            longitude=-100.0
        )
        print(f"✓ Success: {aircraft_obj.callsign}")
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    # Test invalid heading
    print("\nTrying to create aircraft with invalid heading (400°)...")
    try:
        aircraft_obj = db.add_aircraft(
            callsign="TEST002",
            altitude=10000,
            heading=400,  # Invalid!
            speed=250,
            latitude=40.0,
            longitude=-100.0
        )
        print(f"✗ Should have failed but didn't")
    except ValueError as e:
        print(f"✓ Correctly rejected: {e}")
    
    # Test invalid latitude
    print("\nTrying to create aircraft with invalid latitude (100°)...")
    try:
        aircraft_obj = db.add_aircraft(
            callsign="TEST003",
            altitude=10000,
            heading=180,
            speed=250,
            latitude=100,  # Invalid!
            longitude=-100.0
        )
        print(f"✗ Should have failed but didn't")
    except ValueError as e:
        print(f"✓ Correctly rejected: {e}")


def test_querying(db):
    """Test querying operations"""
    print_separator("TEST 6: Querying")
    
    print(f"Current aircraft count: {len(db)}\n")
    
    # Check if aircraft exists
    print(f"Does 'AAL123' exist? {db.has_aircraft('AAL123')}")
    print(f"Does 'XXX999' exist? {db.has_aircraft('XXX999')}")
    
    # Using 'in' operator
    print(f"\n'UAL456' in db: {'UAL456' in db}")
    print(f"'YYY888' in db: {'YYY888' in db}")
    
    # Get all callsigns
    print(f"\nAll callsigns in database:")
    for cs in sorted(db.get_all_callsigns()):
        print(f"  - {cs}")


def main():
    """Run all tests"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║          Context Database - Test Suite                    ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    try:
        db = test_basic_usage()
        test_updating_state(db)
        test_instructions(db)
        test_serialization(db)
        test_validation()
        test_querying(db)
        
        print_separator("ALL TESTS PASSED ✓")
        print(f"\nFinal database summary:")
        print(db.get_summary())
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
