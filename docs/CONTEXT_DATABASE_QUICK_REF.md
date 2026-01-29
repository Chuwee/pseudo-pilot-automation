# Context Database Quick Reference

## Import

```python
from src.piem.core import ContextDatabase, Aircraft, AircraftState
```

## Initialize

```python
db = ContextDatabase()
```

## CRUD Operations

### Create/Add Aircraft

```python
db.add_aircraft(
    callsign="AAL123",
    altitude=35000,      # feet
    heading=270,         # degrees (0-360)
    speed=450,           # knots
    latitude=40.7128,    # decimal degrees (-90 to 90)
    longitude=-74.0060,  # decimal degrees (-180 to 180)
    instruction="Climb to FL350",  # optional
    instruction_successful=None    # optional (True/False/None)
)
```

### Read Aircraft

```python
# Get specific aircraft
aircraft = db.get_aircraft("AAL123")

# Check if exists
if db.has_aircraft("AAL123"):
    # or use: if "AAL123" in db:
    pass

# Get all aircraft
all_aircraft = db.get_all_aircraft()

# Get all callsigns
callsigns = db.get_all_callsigns()

# Get count
count = len(db)  # or db.get_aircraft_count()
```

### Update Aircraft

```python
# Update state (any combination of parameters)
db.update_aircraft_state(
    "AAL123",
    altitude=37000,    # optional
    heading=280,       # optional
    speed=460,         # optional
    latitude=41.0,     # optional
    longitude=-75.0    # optional
)

# Set instruction
db.set_instruction("AAL123", "Turn left heading 240")

# Mark instruction result
db.mark_instruction_result("AAL123", successful=True)  # or False
```

### Delete Aircraft

```python
# Remove specific aircraft
removed = db.remove_aircraft("AAL123")  # returns True if removed

# Clear all aircraft
count = db.clear()  # returns number of aircraft removed
```

## Aircraft Object Properties

```python
aircraft = db.get_aircraft("AAL123")

# Properties
aircraft.callsign                           # "AAL123"
aircraft.current_state.altitude             # 35000
aircraft.current_state.heading              # 270
aircraft.current_state.speed                # 450
aircraft.current_state.latitude             # 40.7128
aircraft.current_state.longitude            # -74.0060
aircraft.last_instruction                   # "Climb to FL350" or None
aircraft.last_instruction_successful        # True/False/None
aircraft.last_updated                       # datetime object

# Methods
aircraft.update_state(altitude=38000)
aircraft.set_instruction("Descend to FL300", successful=None)
aircraft.mark_instruction_result(True)
```

## Serialization

```python
# Entire database
data_dict = db.to_dict()                    # → dict
json_str = db.to_json(indent=2)             # → str
summary = db.get_summary()                  # → str (human-readable)

# Individual aircraft
aircraft = db.get_aircraft("AAL123")
aircraft_dict = aircraft.to_dict()          # → dict
aircraft_json = aircraft.to_json()          # → str
str_repr = str(aircraft)                    # → str (one-line summary)
```

## Validation Rules

### AircraftState
- `altitude`: Must be ≥ 0 (feet)
- `heading`: Must be 0-360 (degrees)
- `speed`: Must be ≥ 0 (knots)
- `latitude`: Must be -90 to 90 (decimal degrees)
- `longitude`: Must be -180 to 180 (decimal degrees)

### Aircraft
- `callsign`: Cannot be empty, auto-normalized to uppercase

## Common Patterns

### Pattern 1: Track New Aircraft

```python
# When aircraft appears on radar
db.add_aircraft("N12345", 5000, 360, 120, 37.7749, -122.4194)
```

### Pattern 2: Process ATC Instruction

```python
# ATC gives instruction
db.set_instruction("N12345", "Cleared for takeoff runway 28L")

# Aircraft executes
# ... (aircraft takes off)

# Mark success
db.mark_instruction_result("N12345", successful=True)
```

### Pattern 3: Update Position from Simulator

```python
# Simulator update callback
def on_position_update(callsign, lat, lon, alt, hdg, spd):
    if db.has_aircraft(callsign):
        db.update_aircraft_state(
            callsign,
            latitude=lat,
            longitude=lon,
            altitude=alt,
            heading=hdg,
            speed=spd
        )
```

### Pattern 4: Get All Aircraft in Summary

```python
print(db.get_summary())  # formatted output for debugging
```

### Pattern 5: Safety Check Before Instruction

```python
aircraft = db.get_aircraft("AAL123")
if aircraft:
    if aircraft.last_instruction_successful == False:
        print(f"Warning: Last instruction failed for {aircraft.callsign}")
    # Proceed with new instruction
    db.set_instruction("AAL123", "New instruction...")
```

## Error Handling

```python
try:
    # May raise ValueError for invalid parameters
    db.add_aircraft("TEST", 10000, 400, 250, 40.0, -100.0)
except ValueError as e:
    print(f"Validation error: {e}")

try:
    # May raise KeyError if aircraft not found
    db.update_aircraft_state("NONEXISTENT", altitude=15000)
except KeyError as e:
    print(f"Aircraft not found: {e}")
```

## Thread Safety

✅ All operations are thread-safe  
✅ Uses `threading.RLock` internally  
✅ Safe for multiprocessing environments  

```python
import threading

def worker(db, callsign):
    for i in range(100):
        db.update_aircraft_state(callsign, altitude=10000 + i * 100)

threads = [threading.Thread(target=worker, args=(db, f"AC{i}")) for i in range(5)]
for t in threads: t.start()
for t in threads: t.join()
```

## Performance

| Operation | Complexity | Notes |
|-----------|------------|-------|
| Add aircraft | O(1) | Direct dict insert |
| Get aircraft | O(1) | Direct dict lookup |
| Update state | O(1) | Direct dict lookup |
| Remove aircraft | O(1) | Direct dict delete |
| Get all aircraft | O(n) | Iterates all |
| Serialize | O(n) | Iterates all |

**Memory:** ~1-2 KB per aircraft

## Quick Test

```bash
python3 examples/context_db_example.py
```

Runs comprehensive test suite covering all functionality.

---

**See full documentation:** `docs/CONTEXT_DATABASE.md`
