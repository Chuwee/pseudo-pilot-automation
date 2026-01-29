# Context Database Documentation

## Overview

The Context Database is a lightweight, thread-safe, in-memory database designed for tracking aircraft states and instructions in the PseudoPilot Automation system. It provides fast read and write operations without the overhead of a traditional database system.

## Design Philosophy

### Why Not Redis or SQL?

- **Lightweight**: No external dependencies or services required
- **Fast**: Direct memory access via Python dictionaries
- **Simple**: No need for database management, schemas, or migrations
- **No Persistence Needed**: Aircraft state is transient; it only matters during active sessions
- **Thread-Safe**: Built-in locking for multiprocessing environments

### Key Features

✅ **In-memory storage** using Python dictionaries  
✅ **Thread-safe operations** with RLock  
✅ **Fast CRUD operations** (Create, Read, Update, Delete)  
✅ **Serializable** to JSON for debugging  
✅ **Comprehensive validation** of aircraft parameters  
✅ **Instruction tracking** with success/failure states  

## Architecture

```
┌─────────────────────────────────────────────┐
│         ContextDatabase                     │
│  (Thread-safe, In-memory)                   │
├─────────────────────────────────────────────┤
│  _aircraft: Dict[callsign → Aircraft]       │
│  _lock: RLock                               │
└─────────────────────────────────────────────┘
                  │
                  │ manages
                  ▼
         ┌─────────────────┐
         │    Aircraft     │
         ├─────────────────┤
         │ - callsign      │
         │ - current_state │──┐
         │ - last_instr    │  │
         │ - instr_success │  │
         │ - last_updated  │  │
         └─────────────────┘  │
                              │
                              ▼
                    ┌──────────────────┐
                    │  AircraftState   │
                    ├──────────────────┤
                    │ - altitude       │
                    │ - heading        │
                    │ - speed          │
                    │ - latitude       │
                    │ - longitude      │
                    └──────────────────┘
```

## Data Models

### AircraftState

Represents the current physical state of an aircraft.

**Attributes:**
- `altitude` (float): Altitude in feet
- `heading` (float): Heading in degrees (0-360)
- `speed` (float): Speed in knots
- `latitude` (float): Latitude in decimal degrees (-90 to 90)
- `longitude` (float): Longitude in decimal degrees (-180 to 180)

**Validation:**
- Heading must be between 0 and 360
- Altitude cannot be negative
- Speed cannot be negative
- Latitude must be between -90 and 90
- Longitude must be between -180 and 180

### Aircraft

Represents an aircraft being tracked by the system.

**Attributes:**
- `callsign` (str): Aircraft callsign (unique identifier, auto-normalized to uppercase)
- `current_state` (AircraftState): Current state of the aircraft
- `last_instruction` (str | None): Last instruction sent to this aircraft
- `last_instruction_successful` (bool | None): Whether the last instruction was successful
  - `True`: Instruction executed successfully
  - `False`: Instruction failed
  - `None`: Instruction pending or no instruction yet
- `last_updated` (datetime): Timestamp of last update

**Methods:**
- `update_state()`: Update one or more state parameters
- `set_instruction()`: Set a new instruction
- `mark_instruction_result()`: Mark the result of the last instruction
- `to_dict()`, `to_json()`: Serialization methods

### ContextDatabase

Main database class for managing all aircraft.

**Thread Safety:**
- Uses `threading.RLock` (reentrant lock) for nested operations
- All public methods are automatically thread-safe

## API Reference

### Creating the Database

```python
from src.piem.core import ContextDatabase

# Initialize database
db = ContextDatabase()
```

### Adding Aircraft

```python
# Add a new aircraft
aircraft = db.add_aircraft(
    callsign="AAL123",
    altitude=35000,      # feet
    heading=270,         # degrees
    speed=450,           # knots
    latitude=40.7128,    # decimal degrees
    longitude=-74.0060,  # decimal degrees
    instruction="Climb to FL350",  # optional
    instruction_successful=None    # optional (None=pending)
)
```

### Updating Aircraft State

```python
# Update one or more state parameters
db.update_aircraft_state(
    "AAL123",
    altitude=37000,  # update altitude only
    speed=460        # update speed only
)

# Update position
db.update_aircraft_state(
    "AAL123",
    latitude=41.0,
    longitude=-75.0
)
```

### Managing Instructions

```python
# Set a new instruction
db.set_instruction("AAL123", "Turn left heading 240")

# Mark instruction as successful
db.mark_instruction_result("AAL123", successful=True)

# Mark instruction as failed
db.mark_instruction_result("AAL123", successful=False)
```

### Querying Aircraft

```python
# Get a specific aircraft
aircraft = db.get_aircraft("AAL123")
if aircraft:
    print(f"Altitude: {aircraft.current_state.altitude}")

# Check if aircraft exists
if db.has_aircraft("AAL123"):
    print("Aircraft exists")

# Using 'in' operator
if "AAL123" in db:
    print("Aircraft exists")

# Get all aircraft
all_aircraft = db.get_all_aircraft()
for aircraft in all_aircraft:
    print(aircraft)

# Get all callsigns
callsigns = db.get_all_callsigns()
print(f"Tracking {len(callsigns)} aircraft: {callsigns}")

# Get aircraft count
count = len(db)  # or db.get_aircraft_count()
```

### Removing Aircraft

```python
# Remove a specific aircraft
removed = db.remove_aircraft("AAL123")
if removed:
    print("Aircraft removed")

# Clear all aircraft
count = db.clear()
print(f"Removed {count} aircraft")
```

### Serialization

```python
# Convert entire database to dictionary
data = db.to_dict()

# Convert to JSON string
json_str = db.to_json(indent=2)
print(json_str)

# Get human-readable summary
summary = db.get_summary()
print(summary)

# Individual aircraft serialization
aircraft = db.get_aircraft("AAL123")
aircraft_json = aircraft.to_json()
```

## Usage Examples

### Example 1: Basic Aircraft Tracking

```python
from src.piem.core import ContextDatabase

# Initialize database
db = ContextDatabase()

# Add aircraft
db.add_aircraft(
    callsign="UAL456",
    altitude=28000,
    heading=90,
    speed=380,
    latitude=34.0522,
    longitude=-118.2437
)

# Update state as aircraft moves
db.update_aircraft_state("UAL456", altitude=30000, speed=400)

# Check current state
aircraft = db.get_aircraft("UAL456")
print(f"{aircraft.callsign} is at {aircraft.current_state.altitude}ft")
```

### Example 2: Instruction Tracking

```python
# Add aircraft
db.add_aircraft("DAL789", 10000, 180, 250, 33.9416, -118.4085)

# ATC gives instruction
db.set_instruction("DAL789", "Climb and maintain FL200")

# Aircraft executes instruction
aircraft = db.get_aircraft("DAL789")
print(f"Current instruction: {aircraft.last_instruction}")

# Update altitude
db.update_aircraft_state("DAL789", altitude=20000)

# Mark instruction as successful
db.mark_instruction_result("DAL789", successful=True)
```

### Example 3: Multi-Aircraft Management

```python
# Track multiple aircraft
aircraft_list = [
    ("AAL100", 35000, 270, 450, 40.7, -74.0),
    ("UAL200", 28000, 90, 380, 34.0, -118.2),
    ("DAL300", 31000, 180, 420, 33.9, -118.4),
]

for cs, alt, hdg, spd, lat, lon in aircraft_list:
    db.add_aircraft(cs, alt, hdg, spd, lat, lon)

# Query all aircraft
print(f"Tracking {len(db)} aircraft:")
for aircraft in db.get_all_aircraft():
    print(f"  - {aircraft}")

# Get summary
print("\n" + db.get_summary())
```

### Example 4: Error Handling

```python
try:
    # Try to add aircraft with invalid heading
    db.add_aircraft("TEST001", 10000, 400, 250, 40.0, -100.0)
except ValueError as e:
    print(f"Validation error: {e}")

try:
    # Try to update non-existent aircraft
    db.update_aircraft_state("NONEXISTENT", altitude=15000)
except KeyError as e:
    print(f"Aircraft not found: {e}")
```

## Threading and Multiprocessing

The ContextDatabase is thread-safe and can be safely used in multiprocessing environments:

```python
import threading

def update_worker(db, callsign):
    """Worker thread that updates aircraft"""
    for i in range(100):
        db.update_aircraft_state(
            callsign,
            altitude=10000 + i * 100
        )

# Create threads
threads = []
for i in range(5):
    t = threading.Thread(
        target=update_worker,
        args=(db, f"AC{i}")
    )
    threads.append(t)
    t.start()

# Wait for completion
for t in threads:
    t.join()
```

## Integration with PIEM

The Context Database integrates seamlessly with the PIEM (Pseudo-pilot Instruction Execution Module):

```python
from src.piem.core import ContextDatabase

class PseudoPilotSystem:
    def __init__(self):
        self.context_db = ContextDatabase()
    
    def process_voice_command(self, transcription):
        """Process voice command and update database"""
        # Parse command...
        callsign = extract_callsign(transcription)
        instruction = extract_instruction(transcription)
        
        # Store instruction in database
        if self.context_db.has_aircraft(callsign):
            self.context_db.set_instruction(callsign, instruction)
        else:
            print(f"Unknown aircraft: {callsign}")
    
    def update_aircraft_position(self, callsign, lat, lon, alt, hdg, spd):
        """Update aircraft position from simulator"""
        if self.context_db.has_aircraft(callsign):
            self.context_db.update_aircraft_state(
                callsign,
                altitude=alt,
                heading=hdg,
                speed=spd,
                latitude=lat,
                longitude=lon
            )
```

## Performance Characteristics

- **Add Aircraft**: O(1) - direct dictionary insertion
- **Update State**: O(1) - direct dictionary lookup
- **Get Aircraft**: O(1) - direct dictionary lookup
- **Remove Aircraft**: O(1) - direct dictionary deletion
- **Get All Aircraft**: O(n) - iterates all aircraft
- **Serialization**: O(n) - iterates all aircraft

**Memory Usage:**
- ~1-2 KB per aircraft (depending on instruction length)
- 1000 aircraft ≈ 1-2 MB

## Best Practices

1. **Normalize Callsigns**: Callsigns are automatically converted to uppercase
2. **Check Existence**: Use `has_aircraft()` or `in` before accessing
3. **Handle Exceptions**: Wrap operations in try-except blocks
4. **Thread Safety**: The database handles locking internally
5. **Validation**: Let the database validate parameters - don't bypass
6. **Logging**: The database logs all operations for debugging

## Testing

Run the comprehensive test suite:

```bash
python3 examples/context_db_example.py
```

This will test:
- Basic CRUD operations
- State updates
- Instruction tracking
- Serialization
- Validation
- Querying
- Thread safety

## Future Enhancements

Potential improvements for future iterations:

- [ ] Historical state tracking (breadcrumbs)
- [ ] Conflict detection (aircraft too close)
- [ ] Export/import from JSON files
- [ ] Query by position (find aircraft in area)
- [ ] Performance metrics (average speed, etc.)
- [ ] Event callbacks (notify on state change)

## License

Part of the PseudoPilot Automation project.
