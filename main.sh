#!/bin/bash
################################################################################
# PseudoPilot Automation - Main Launcher Script
# 
# This bash script provides a menu-driven interface to launch various
# components of the PseudoPilot Automation system.
#
# Features:
# - Launch PTT listener in a separate terminal window
# - Singleton pattern to prevent multiple instances
# - Extensible menu system for future options
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Lock files for different services
PTT_LOCK_FILE="/tmp/pseudopilot_ptt.lock"
PTT_PID_FILE="/tmp/pseudopilot_ptt.pid"
DB_LOCK_FILE="/tmp/pseudopilot_context_db.lock"
DB_PID_FILE="/tmp/pseudopilot_context_db.pid"

# For backward compatibility
LOCK_FILE="$PTT_LOCK_FILE"
PID_FILE="$PTT_PID_FILE"

################################################################################
# Singleton Pattern Implementation
################################################################################

check_singleton() {
    local process_name="$1"
    local lock_file="$2"
    local pid_file="$3"
    
    # Check if lock file exists
    if [ -f "$lock_file" ]; then
        # Check if the process is still running
        if [ -f "$pid_file" ]; then
            local old_pid=$(cat "$pid_file")
            if ps -p "$old_pid" > /dev/null 2>&1; then
                echo -e "${RED}Error: $process_name is already running (PID: $old_pid)${NC}"
                echo -e "${YELLOW}If you're sure it's not running, delete: $lock_file and $pid_file${NC}"
                return 1
            else
                # Process died, clean up stale lock
                echo -e "${YELLOW}Cleaning up stale lock file...${NC}"
                rm -f "$lock_file" "$pid_file"
            fi
        fi
    fi
    
    # Create lock file
    touch "$lock_file"
    echo $$ > "$pid_file"
    return 0
}

release_singleton() {
    local lock_file="$1"
    local pid_file="$2"
    rm -f "$lock_file" "$pid_file"
}

################################################################################
# PTT Listener Functions
################################################################################

launch_ptt_listener() {
    echo -e "${BLUE}Launching PTT Listener in separate window...${NC}"
    
    # Check singleton before launching
    if ! check_singleton "PTT Listener" "$PTT_LOCK_FILE" "$PTT_PID_FILE"; then
        return 1
    fi
    
    # Trap to cleanup on exit
    trap "release_singleton '$PTT_LOCK_FILE' '$PTT_PID_FILE'" EXIT INT TERM
    
    # Determine terminal emulator
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS - use osascript to open new Terminal window
        osascript <<EOF
tell application "Terminal"
    activate
    do script "cd '$SCRIPT_DIR' && source venv/bin/activate && python3 src/lpip/ptt_standalone.py"
end tell
EOF
        echo -e "${GREEN}✓ PTT Listener launched in new Terminal window${NC}"
        
    elif command -v gnome-terminal &> /dev/null; then
        # Linux with GNOME Terminal
        gnome-terminal -- bash -c "cd '$SCRIPT_DIR' && source venv/bin/activate && python3 src/lpip/ptt_standalone.py; exec bash"
        echo -e "${GREEN}✓ PTT Listener launched in new terminal window${NC}"
        
    elif command -v xterm &> /dev/null; then
        # Fallback to xterm
        xterm -e "cd '$SCRIPT_DIR' && source venv/bin/activate && python3 src/lpip/ptt_standalone.py" &
        echo -e "${GREEN}✓ PTT Listener launched in xterm${NC}"
        
    else
        echo -e "${RED}Error: No suitable terminal emulator found${NC}"
        release_singleton "$PTT_LOCK_FILE" "$PTT_PID_FILE"
        return 1
    fi
    
    echo -e "${YELLOW}Press Ctrl+C to stop monitoring...${NC}"
    
    # Wait for user to stop
    while true; do
        sleep 1
    done
}

launch_ptt_listener_current_window() {
    echo -e "${BLUE}Launching PTT Listener in current window...${NC}"
    
    # Check singleton
    if ! check_singleton "PTT Listener" "$PTT_LOCK_FILE" "$PTT_PID_FILE"; then
        return 1
    fi
    
    # Trap to cleanup on exit
    trap "release_singleton '$PTT_LOCK_FILE' '$PTT_PID_FILE'" EXIT INT TERM
    
    # Run in current terminal
    python3 "$SCRIPT_DIR/src/lpip/ptt_standalone.py"
}

################################################################################
# Context Database Service Functions
################################################################################

start_context_db_service() {
    echo -e "${BLUE}Starting Context Database Service...${NC}"
    
    # Check singleton
    if ! check_singleton "Context DB Service" "$DB_LOCK_FILE" "$DB_PID_FILE"; then
        return 1
    fi
    
    # Start service in background
    nohup python3 "$SCRIPT_DIR/src/piem/context_db_service.py" > /tmp/context_db_service.log 2>&1 &
    local service_pid=$!
    
    # Update PID file with actual service PID
    echo $service_pid > "$DB_PID_FILE"
    
    echo -e "${GREEN}✓ Context Database Service started (PID: $service_pid)${NC}"
    sleep 1
    
    # Verify it's running
    if ps -p "$service_pid" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Service is running${NC}"
    else
        echo -e "${RED}✗ Service failed to start. Check /tmp/context_db_service.log${NC}"
        release_singleton "$DB_LOCK_FILE" "$DB_PID_FILE"
        return 1
    fi
}

stop_context_db_service() {
    echo -e "${YELLOW}Stopping Context Database Service...${NC}"
    
    if [ -f "$DB_PID_FILE" ]; then
        local pid=$(cat "$DB_PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            kill "$pid" 2>/dev/null || true
            sleep 1
            
            # Force kill if still running
            if ps -p "$pid" > /dev/null 2>&1; then
                kill -9 "$pid" 2>/dev/null || true
            fi
            
            echo -e "${GREEN}✓ Service stopped${NC}"
        fi
    fi
    
    # Clean up lock files
    release_singleton "$DB_LOCK_FILE" "$DB_PID_FILE"
}

is_context_db_running() {
    if [ -f "$DB_PID_FILE" ]; then
        local pid=$(cat "$DB_PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

################################################################################
# Aircraft Launch Functions
################################################################################

launch_aircraft() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║          Launch New Aircraft with FlightGear           ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Ensure context database service is running
    if ! is_context_db_running; then
        echo -e "${YELLOW}Context Database Service is not running. Starting it...${NC}"
        start_context_db_service
        if [ $? -ne 0 ]; then
            echo -e "${RED}Failed to start Context Database Service${NC}"
            read -p "Press Enter to continue..."
            return 1
        fi
        echo ""
    fi
    
    # Ask for callsign
    echo -e "${GREEN}Enter aircraft callsign:${NC}"
    read -p "Callsign: " callsign
    
    if [ -z "$callsign" ]; then
        echo -e "${RED}Error: Callsign cannot be empty${NC}"
        read -p "Press Enter to continue..."
        return 1
    fi
    
    # Normalize callsign
    callsign=$(echo "$callsign" | tr '[:lower:]' '[:upper:]' | tr -d ' ')
    
    echo ""
    echo -e "${BLUE}Adding aircraft $callsign to context database...${NC}"
    
    # Add aircraft to database via socket
    python3 -c "
import socket
import json
import sys

socket_path = '/tmp/pseudopilot_context_db.sock'

try:
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(socket_path)
    
    request = {
        'command': 'add_aircraft',
        'callsign': '$callsign',
        'altitude': 0,
        'heading': 0,
        'speed': 0,
        'latitude': 37.6213,  # Default: San Francisco Airport
        'longitude': -122.3790
    }
    
    client.sendall(json.dumps(request).encode('utf-8'))
    response = json.loads(client.recv(4096).decode('utf-8'))
    client.close()
    
    if response['status'] == 'ok':
        print('✓ Aircraft added to database')
        sys.exit(0)
    else:
        print(f'✗ Error: {response[\"message\"]}')
        sys.exit(1)
except Exception as e:
    print(f'✗ Error connecting to database: {e}')
    sys.exit(1)
"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Aircraft $callsign added to database${NC}"
    else
        echo -e "${RED}✗ Failed to add aircraft to database${NC}"
        read -p "Press Enter to continue..."
        return 1
    fi
    
    echo ""
    echo -e "${BLUE}Launching FlightGear for $callsign...${NC}"
    
    # Check if FlightGear is installed
    if ! command -v fgfs &> /dev/null; then
        echo -e "${RED}✗ FlightGear (fgfs) not found in PATH${NC}"
        echo -e "${YELLOW}Please install FlightGear or add it to your PATH${NC}"
        read -p "Press Enter to continue..."
        return 1
    fi
    
    # Launch FlightGear in background
    echo -e "${GREEN}Starting FlightGear...${NC}"
    echo -e "${YELLOW}(This may take a moment)${NC}"
    
    # Launch FlightGear with basic settings
    # Adjust these parameters as needed
    fgfs \
        --aircraft=c172p \
        --airport=KSFO \
        --runway=28L \
        --callsign="$callsign" \
        --timeofday=noon \
        > /tmp/flightgear_${callsign}.log 2>&1 &
    
    local fg_pid=$!
    
    echo -e "${GREEN}✓ FlightGear launched (PID: $fg_pid)${NC}"
    echo -e "${BLUE}Aircraft: $callsign${NC}"
    echo -e "${BLUE}Airport: KSFO (San Francisco)${NC}"
    echo -e "${BLUE}Runway: 28L${NC}"
    echo ""
    echo -e "${YELLOW}Log file: /tmp/flightgear_${callsign}.log${NC}"
    
    echo ""
    read -p "Press Enter to continue..."
}

################################################################################
# Main Menu
################################################################################

show_menu() {
    clear
    echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║     PseudoPilot Automation - Main Launcher            ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}Available Options:${NC}"
    echo ""
    echo -e "  ${YELLOW}1)${NC} Launch PTT Listener (Separate Window)"
    echo -e "  ${YELLOW}2)${NC} Launch PTT Listener (Current Window)"
    echo -e "  ${YELLOW}3)${NC} Start Context Database Service"
    echo -e "  ${YELLOW}4)${NC} Launch New Aircraft (FlightGear)"
    echo -e "  ${YELLOW}5)${NC} Check Running Processes"
    echo -e "  ${YELLOW}6)${NC} Stop All Processes"
    echo ""
    echo -e "  ${YELLOW}0)${NC} Exit"
    echo ""
    echo -n "Select an option: "
}

check_processes() {
    echo -e "${BLUE}Checking running processes...${NC}"
    echo ""
    
    local found_any=false
    
    # Check PTT Listener
    if [ -f "$PTT_PID_FILE" ]; then
        local pid=$(cat "$PTT_PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ PTT Listener is running (PID: $pid)${NC}"
            found_any=true
        else
            echo -e "${YELLOW}⚠ PTT lock file exists but process is not running${NC}"
            rm -f "$PTT_LOCK_FILE" "$PTT_PID_FILE"
        fi
    fi
    
    # Check Context DB Service
    if [ -f "$DB_PID_FILE" ]; then
        local pid=$(cat "$DB_PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Context Database Service is running (PID: $pid)${NC}"
            found_any=true
        else
            echo -e "${YELLOW}⚠ Context DB lock file exists but process is not running${NC}"
            rm -f "$DB_LOCK_FILE" "$DB_PID_FILE"
        fi
    fi
    
    if [ "$found_any" = false ]; then
        echo -e "${YELLOW}No processes currently running${NC}"
    fi
    
    echo ""
    read -p "Press Enter to continue..."
}

stop_all_processes() {
    echo -e "${RED}Stopping all processes...${NC}"
    echo ""
    
    # Stop PTT Listener
    if [ -f "$PTT_PID_FILE" ]; then
        local pid=$(cat "$PTT_PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo -e "${YELLOW}Stopping PTT Listener ($pid)...${NC}"
            kill "$pid" 2>/dev/null || true
            sleep 1
            if ps -p "$pid" > /dev/null 2>&1; then
                kill -9 "$pid" 2>/dev/null || true
            fi
            echo -e "${GREEN}✓ PTT Listener stopped${NC}"
        fi
    fi
    
    # Stop Context DB Service
    if [ -f "$DB_PID_FILE" ]; then
        local pid=$(cat "$DB_PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo -e "${YELLOW}Stopping Context DB Service ($pid)...${NC}"
            kill "$pid" 2>/dev/null || true
            sleep 1
            if ps -p "$pid" > /dev/null 2>&1; then
                kill -9 "$pid" 2>/dev/null || true
            fi
            echo -e "${GREEN}✓ Context DB Service stopped${NC}"
        fi
    fi
    
    # Clean up all lock files
    rm -f "$PTT_LOCK_FILE" "$PTT_PID_FILE" "$DB_LOCK_FILE" "$DB_PID_FILE"
    echo -e "${GREEN}✓ All lock files cleaned up${NC}"
    
    echo ""
    read -p "Press Enter to continue..."
}

main_menu() {
    while true; do
        show_menu
        read -r choice
        
        case $choice in
            1)
                launch_ptt_listener
                ;;
            2)
                launch_ptt_listener_current_window
                ;;
            3)
                start_context_db_service
                read -p "Press Enter to continue..."
                ;;
            4)
                launch_aircraft
                ;;
            5)
                check_processes
                ;;
            6)
                stop_all_processes
                ;;
            0)
                echo -e "${GREEN}Exiting...${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}Invalid option. Please try again.${NC}"
                sleep 2
                ;;
        esac
    done
}

################################################################################
# Command Line Arguments Support
################################################################################

show_help() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  -l, --launch-ptt         Launch PTT listener in separate window"
    echo "  -c, --launch-ptt-current Launch PTT listener in current window"
    echo "  -d, --start-db           Start Context Database Service"
    echo "  -a, --launch-aircraft    Launch new aircraft with FlightGear"
    echo "  -s, --status             Check running processes"
    echo "  -k, --kill               Stop all processes"
    echo "  -h, --help               Show this help message"
    echo "  (no args)                Show interactive menu"
    echo ""
}

# Parse command line arguments
if [ $# -eq 0 ]; then
    # No arguments - show menu
    main_menu
else
    case "$1" in
        -l|--launch-ptt)
            launch_ptt_listener
            ;;
        -c|--launch-ptt-current)
            launch_ptt_listener_current_window
            ;;
        -d|--start-db)
            start_context_db_service
            ;;
        -a|--launch-aircraft)
            launch_aircraft
            ;;
        -s|--status)
            check_processes
            ;;
        -k|--kill)
            stop_all_processes
            ;;
        -h|--help)
            show_help
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
fi
