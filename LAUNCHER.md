# PseudoPilot Automation - Updated Launcher Guide

## 🚀 New Features

The launcher script has been enhanced with:
- ✅ **Context Database Service** - Singleton background service for aircraft tracking
- ✅ **Aircraft Launch with FlightGear** - Interactive aircraft creation
- ✅ **Separate Lock Files** - Independent singleton management for each service
- ✅ **Socket-based Communication** - Unix socket IPC for database operations

---

## Quick Start

### Interactive Menu

```bash
./main.sh
```

**Menu Options:**
1. Launch PTT Listener (Separate Window)
2. Launch PTT Listener (Current Window)
3. **Start Context Database Service** ← New!
4. **Launch New Aircraft (FlightGear)** ← New!
5. Check Running Processes
6. Stop All Processes

### Command Line

```bash
# Start context database service
./main.sh --start-db

# Launch aircraft (asks for callsign)
./main.sh --launch-aircraft

# Check what's running
./main.sh --status

# Stop everything
./main.sh --kill
```

---

## Context Database Service

The Context Database Service runs as a singleton background daemon that manages aircraft state.

### Features
- **Singleton Pattern**: Only one instance can run at a time
- **Unix Socket Interface**: `/tmp/pseudopilot_context_db.sock`
- **Persistent Process**: Runs in background until stopped
- **Thread-Safe**: Safe for concurrent access
- **JSON API**: Simple request/response protocol

### Lock Files
- Lock: `/tmp/pseudopilot_context_db.lock`
- PID: `/tmp/pseudopilot_context_db.pid`
- Log: `/tmp/context_db_service.log`

### Starting the Service

**Via Menu:**
```bash
./main.sh
# Select option 3
```

**Via Command Line:**
```bash
./main.sh --start-db
```

**Direct:**
```bash
python3 src/piem/context_db_service.py
```

### Checking if Running

```bash
./main.sh --status
```

Output example:
```
Checking running processes...

✓ PTT Listener is running (PID: 12345)
✓ Context Database Service is running (PID: 12346)
```

---

## Launching Aircraft

### Interactive Launch

```bash
./main.sh --launch-aircraft
```

**What happens:**
1. Checks if Context Database Service is running (starts it if not)
2. Asks for aircraft callsign
3. Adds aircraft to context database with default position (KSFO)
4. Launches FlightGear with that callsign

**Example Session:**
```
╔════════════════════════════════════════════════════════╗
║          Launch New Aircraft with FlightGear           ║
╚════════════════════════════════════════════════════════╝

Enter aircraft callsign:
Callsign: N12345

Adding aircraft N12345 to context database...
✓ Aircraft added to database
✓ Aircraft N12345 added to database

Launching FlightGear for N12345...
Starting FlightGear...
(This may take a moment)
✓ FlightGear launched (PID: 67890)
Aircraft: N12345
Airport: KSFO (San Francisco)
Runway: 28L

Log file: /tmp/flightgear_N12345.log
```

### Default Aircraft Parameters

When an aircraft is added:
- **Altitude**: 0 ft (on ground)
- **Heading**: 0° (North)
- **Speed**: 0 kts (stationary)
- **Position**: San Francisco International Airport (KSFO)
  - Latitude: 37.6213°
  - Longitude: -122.3790°

### FlightGear Parameters

Default FlightGear launch settings:
- **Aircraft**: Cessna 172P (c172p)
- **Airport**: KSFO
- **Runway**: 28L
- **Time**: Noon
- **Callsign**: User-specified

---

## Socket Communication

The Context Database Service uses a Unix socket for IPC. Here's how to communicate with it:

### Python Example

```python
import socket
import json

# Connect to service
client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
client.connect('/tmp/pseudopilot_context_db.sock')

# Add aircraft
request = {
    'command': 'add_aircraft',
    'callsign': 'AAL123',
    'altitude': 35000,
    'heading': 270,
    'speed': 450,
    'latitude': 40.7128,
    'longitude': -74.0060
}

client.sendall(json.dumps(request).encode('utf-8'))
response = json.loads(client.recv(4096).decode('utf-8'))
client.close()

print(response)
# {'status': 'ok', 'message': 'Aircraft AAL123 added', 'aircraft': {...}}
```

### Available Commands

**Add Aircraft:**
```json
{
    "command": "add_aircraft",
    "callsign": "AAL123",
    "altitude": 35000,
    "heading": 270,
    "speed": 450,
    "latitude": 40.7128,
    "longitude": -74.0060
}
```

**Get Aircraft:**
```json
{
    "command": "get_aircraft",
    "callsign": "AAL123"
}
```

**Update State:**
```json
{
    "command": "update_state",
    "callsign": "AAL123",
    "altitude": 37000,
    "speed": 460
}
```

**Set Instruction:**
```json
{
    "command": "set_instruction",
    "callsign": "AAL123",
    "instruction": "Climb to FL380",
    "successful": null
}
```

**List All Aircraft:**
```json
{
    "command": "list_aircraft"
}
```

**Get Summary:**
```json
{
    "command": "get_summary"
}
```

**Ping:**
```json
{
    "command": "ping"
}
```

---

## Singleton Pattern

Each service uses its own singleton lock to prevent multiple instances:

### PTT Listener
- Lock: `/tmp/pseudopilot_ptt.lock`
- PID: `/tmp/pseudopilot_ptt.pid`

### Context Database Service
- Lock: `/tmp/pseudopilot_context_db.lock`
- PID: `/tmp/pseudopilot_context_db.pid`

### Benefits

✅ Prevents conflicts  
✅ Easy process management  
✅ Automatic stale lock cleanup  
✅ Clear error messages  

---

## Troubleshooting

### Service Won't Start

```bash
# Check for stale locks
./main.sh --status

# Force cleanup
./main.sh --kill

# Try again
./main.sh --start-db
```

### Check Service Logs

```bash
# Context DB Service log
tail -f /tmp/context_db_service.log

# FlightGear log (replace N12345 with your callsign)
tail -f /tmp/flightgear_N12345.log
```

### FlightGear Not Found

If you get "FlightGear (fgfs) not found in PATH":

**macOS:**
```bash
# If installed via Homebrew
brew install --cask flightgear

# Or add to PATH
export PATH="/Applications/FlightGear.app/Contents/MacOS:$PATH"
```

**Linux:**
```bash
sudo apt install flightgear  # Debian/Ubuntu
sudo dnf install flightgear  # Fedora
```

### Socket Connection Failed

If you can't connect to the database:

1. Check if service is running: `./main.sh --status`
2. Check log file: `cat /tmp/context_db_service.log`
3. Restart service: `./main.sh --kill && ./main.sh --start-db`

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│              main.sh Launcher                   │
│  (Singleton coordinator, menu, CLI)             │
└────────┬────────────────────┬───────────────────┘
         │                    │
         │                    │
         ▼                    ▼
┌──────────────────┐  ┌──────────────────────────┐
│  PTT Listener    │  │  Context DB Service      │
│  (Singleton)     │  │  (Singleton, Unix Socket)│
│                  │  │                          │
│  - Space to talk │  │  - Aircraft tracking     │
│  - Transcription │  │  - State management      │
│  - Audio capture │  │  - Instruction tracking  │
└──────────────────┘  └────────┬─────────────────┘
                               │
                               │ Socket API
                               │
                      ┌────────▼─────────────┐
                      │   FlightGear         │
                      │   (Per aircraft)     │
                      │                      │
                      │   - N12345  PID:123  │
                      │   - AAL456  PID:456  │
                      │   - UAL789  PID:789  │
                      └──────────────────────┘
```

---

## Example Workflow

### 1. Start System

```bash
./main.sh
```

### 2. Start Context Database

```
Select option 3 (Start Context Database Service)
```

### 3. Launch Aircraft #1

```
Select option 4 (Launch New Aircraft)
Enter callsign: N12345
```

FlightGear opens for N12345 at KSFO.

### 4. Launch Aircraft #2

```
Select option 4 (Launch New Aircraft)
Enter callsign: N54321
```

FlightGear opens for N54321 at KSFO.

### 5. Start PTT Listener

```
Select option 1 (Launch PTT Listener in Separate Window)
```

New terminal opens with PTT listener.

### 6. Give Voice Commands

Press SPACE and say: "N12345, taxi to runway 28 Left"

### 7. Check Status

```
Select option 5 (Check Running Processes)
```

Shows:
- PTT Listener running
- Context Database Service running

### 8. Cleanup

```
Select option 6 (Stop All Processes)
```

Stops all services and cleans up.

---

## Future Enhancements

Planned features:
- [ ] FlightGear integration (read aircraft state)
- [ ] Multiple aircraft management UI
- [ ] Custom aircraft parameters (airport, runway, etc.)
- [ ] Aircraft removal from database
- [ ] Database backup/restore
- [ ] Web-based aircraft monitor

---

## Summary

✅ **Singleton Pattern**: All services use lock files  
✅ **Context Database**: Background service for aircraft tracking  
✅ **Aircraft Launch**: Interactive FlightGear integration  
✅ **Socket API**: Easy programmatic access  
✅ **Process Management**: Start, stop, check status  

**See also:**
- `docs/CONTEXT_DATABASE.md` - Full database documentation
- `docs/CONTEXT_DATABASE_QUICK_REF.md` - Quick reference
- `LAUNCHER.md` - Original launcher documentation
