# Shared Context Database - Quick Start Guide

## Overview

The context database now supports **multi-process sharing** using Redis as a backend. Multiple listener processes can now access and modify the same aircraft context transparently.

## Setup

### 1. Start Redis

Using Docker (recommended):
```bash
docker-compose up -d redis
```

Or install Redis locally:
```bash
# macOS
brew install redis
redis-server

# Ubuntu
sudo apt-get install redis-server
sudo systemctl start redis
```

### 2. Update Your .env File

Copy the new settings from `.env.example`:
```bash
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
USE_REDIS=true
```

## Usage

### Basic Usage (Single Process)

```python
from src.context.context_database import get_context_database

# Get database instance (automatically uses Redis if configured)
db = get_context_database()

# Add aircraft
aircraft = db.add_aircraft("AFR123")
aircraft.altitude = 35000
aircraft.speed = 450

# IMPORTANT: Update aircraft in database after modifying
if hasattr(db, 'update_aircraft'):
    db.update_aircraft(aircraft)

# Retrieve aircraft
retrieved = db.get_aircraft("AFR123")
print(f"Altitude: {retrieved.altitude}")  # 35000

# List all aircraft
callsigns = db.get_callsign_list()
print(callsigns)  # ['AFR123']
```

### Multi-Process Shared Access

The magic happens when multiple processes access the same database:

**Process 1 (listener):**
```python
from src.context.context_database import get_context_database

db = get_context_database()
aircraft = db.add_aircraft("BAW456")
aircraft.altitude = 38000
db.update_aircraft(aircraft)  # Save to Redis
```

**Process 2 (another listener or orchestrator):**
```python
from src.context.context_database import get_context_database

db = get_context_database()  # Connects to SAME Redis
aircraft = db.get_aircraft("BAW456")  # Sees aircraft from Process 1!
print(aircraft.altitude)  # 38000
```

### Updating Your Listener Code

Replace this:
```python
from src.context.context_database import ContextDatabase

context_database = ContextDatabase()
```

With this:
```python
from src.context.context_database import get_context_database

context_database = get_context_database()
```

**Important:** When modifying aircraft properties, call `update_aircraft()`:

```python
# Get aircraft
aircraft = db.get_aircraft("AFR123")

# Modify properties
aircraft.altitude = 40000
aircraft.speed = 460

# Save changes back to Redis
db.update_aircraft(aircraft)  # Don't forget this!
```

## Testing

### Verify Redis Connection

```bash
python examples/context_database_usage.py
```

### Test Multi-Process Sharing

Terminal 1:
```bash
python examples/context_database_usage.py A
```

Terminal 2:
```bash
python examples/context_database_usage.py B
```

### Check Redis Data Directly

```bash
# Connect to Redis CLI
docker exec -it pseudo-pilot-redis redis-cli

# View all keys
KEYS *

# Get aircraft data
GET aircraft:AFR123

# View active aircraft set
SMEMBERS aircraft:active
```

## Switching Between In-Memory and Redis

Set `USE_REDIS=false` in `.env` to use the original in-memory database (useful for testing or when Redis isn't available).

## API Reference

All methods remain the same as the original `ContextDatabase`:

- `add_aircraft(callsign)` - Add new aircraft
- `get_aircraft(callsign)` - Retrieve aircraft
- `update_aircraft(aircraft)` - **[NEW]** Save modified aircraft to Redis
- `remove_aircraft(callsign)` - Remove aircraft
- `get_all_aircrafts()` - Get list of all aircraft
- `get_callsign_list()` - Get list of callsigns
- `get_instructions_supported()` - Get supported instructions
- `clear_all()` - **[NEW]** Remove all aircraft (useful for testing)

## Troubleshooting

**Redis connection failed:**
- Ensure Redis is running: `docker-compose ps`
- Check Redis host/port in `.env`
- Test connection: `redis-cli ping` (should return `PONG`)

**Changes not visible in other processes:**
- Make sure you're calling `db.update_aircraft(aircraft)` after modifying
- Verify all processes have `USE_REDIS=true`

**For testing without Redis:**
- Set `USE_REDIS=false` in `.env`
- Database will work in single-process mode only
