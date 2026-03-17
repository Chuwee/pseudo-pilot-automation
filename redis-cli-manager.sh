#!/bin/bash

# Redis CLI Manager - Minimal dashboard for managing Redis container
# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

CONTAINER_NAME="pseudo-pilot-redis"
COMPOSE_FILE="docker-compose.yml"

# Check if Redis container is running
is_redis_running() {
    docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"
    return $?
}

# Display help
show_help() {
    echo "Redis CLI Manager"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  monitor   Monitor Redis in a continuously updating panel (Ctrl+C to exit)"
    echo "  status    Show Redis container status (one-time)"
    echo "  start     Start Redis container"
    echo "  stop      Stop Redis container"
    echo "  info      Show detailed Redis server information"
    echo "  help      Show this help message"
    echo ""
}

# Show status
show_status() {
    echo "================================"
    echo "Redis Container Status"
    echo "================================"
    
    if is_redis_running; then
        echo -e "Status: ${GREEN}●${NC} Running"
        
        # Get container uptime
        uptime=$(docker ps --filter "name=${CONTAINER_NAME}" --format '{{.Status}}')
        echo "Uptime: $uptime"
        
        # Get connection info
        echo ""
        echo "Connection Info:"
        echo "  Host: localhost"
        echo "  Port: 6379"
        echo "  Container: $CONTAINER_NAME"
    else
        echo -e "Status: ${RED}●${NC} Stopped"
        echo ""
        echo "Redis is not running. Use '$0 start' to start it."
    fi
    echo "================================"
}

# Start Redis
start_redis() {
    echo "Starting Redis container..."
    
    if is_redis_running; then
        echo -e "${YELLOW}Redis is already running!${NC}"
        return 0
    fi
    
    if [ ! -f "$COMPOSE_FILE" ]; then
        echo -e "${RED}Error: docker-compose.yml not found!${NC}"
        return 1
    fi
    
    docker-compose up -d redis
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Redis started successfully${NC}"
        
        # Wait a moment for container to be ready
        sleep 2
        
        # Check health
        if docker exec $CONTAINER_NAME redis-cli ping > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Redis is responding to PING${NC}"
        fi
    else
        echo -e "${RED}✗ Failed to start Redis${NC}"
        return 1
    fi
}

# Stop Redis
stop_redis() {
    echo "Stopping Redis container..."
    
    if ! is_redis_running; then
        echo -e "${YELLOW}Redis is not running!${NC}"
        return 0
    fi
    
    docker-compose stop redis
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Redis stopped successfully${NC}"
    else
        echo -e "${RED}✗ Failed to stop Redis${NC}"
        return 1
    fi
}

# Show detailed info
show_info() {
    echo "================================"
    echo "Redis Server Information"
    echo "================================"
    
    if ! is_redis_running; then
        echo -e "${RED}Redis is not running. Start it first with '$0 start'${NC}"
        return 1
    fi
    
    # Get Redis INFO
    info_output=$(docker exec $CONTAINER_NAME redis-cli INFO 2>/dev/null)
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Could not connect to Redis${NC}"
        return 1
    fi
    
    # Parse and display key metrics
    echo ""
    echo -e "${BLUE}Server:${NC}"
    echo "$info_output" | grep "^redis_version:" | sed 's/redis_version:/  Version: /'
    echo "$info_output" | grep "^uptime_in_days:" | sed 's/uptime_in_days:/  Uptime (days): /'
    
    echo ""
    echo -e "${BLUE}Clients:${NC}"
    echo "$info_output" | grep "^connected_clients:" | sed 's/connected_clients:/  Connected: /'
    
    echo ""
    echo -e "${BLUE}Memory:${NC}"
    echo "$info_output" | grep "^used_memory_human:" | sed 's/used_memory_human:/  Used: /'
    echo "$info_output" | grep "^used_memory_peak_human:" | sed 's/used_memory_peak_human:/  Peak: /'
    
    echo ""
    echo -e "${BLUE}Stats:${NC}"
    echo "$info_output" | grep "^total_commands_processed:" | sed 's/total_commands_processed:/  Total commands: /'
    echo "$info_output" | grep "^instantaneous_ops_per_sec:" | sed 's/instantaneous_ops_per_sec:/  Ops\/sec: /'
    
    echo ""
    echo -e "${BLUE}Keyspace:${NC}"
    keys_info=$(echo "$info_output" | grep "^db0:")
    if [ -z "$keys_info" ]; then
        echo "  No keys stored"
    else
        echo "$keys_info" | sed 's/db0:/  DB0: /'
    fi
    
    echo "================================"
}

# Monitor mode - continuous display
monitor_redis() {
    # Setup trap to handle Ctrl+C gracefully
    trap 'echo ""; echo "Monitoring stopped."; exit 0' INT
    
    echo "Redis Monitor Panel (Press Ctrl+C to exit)"
    echo ""
    
    while true; do
        # Clear screen and move cursor to top
        clear
        
        echo "╔════════════════════════════════════════════════════════════╗"
        echo "║           REDIS MANAGEMENT DASHBOARD                       ║"
        echo "╚════════════════════════════════════════════════════════════╝"
        echo ""
        
        # Container Status
        if is_redis_running; then
            echo -e "┌─ ${GREEN}STATUS: ● RUNNING${NC}"
            
            # Get uptime
            uptime=$(docker ps --filter "name=${CONTAINER_NAME}" --format '{{.Status}}')
            echo "│  Uptime: $uptime"
            echo "│  Container: $CONTAINER_NAME"
            echo "└─ Connection: localhost:6379"
            
            echo ""
            
            # Get Redis stats
            info_output=$(docker exec $CONTAINER_NAME redis-cli INFO 2>/dev/null)
            
            if [ $? -eq 0 ]; then
                echo "┌─ SERVER INFO"
                version=$(echo "$info_output" | grep "^redis_version:" | cut -d: -f2 | tr -d '\r')
                uptime_days=$(echo "$info_output" | grep "^uptime_in_days:" | cut -d: -f2 | tr -d '\r')
                echo "│  Redis: v$version"
                echo "└─ Uptime: $uptime_days days"
                
                echo ""
                echo "┌─ PERFORMANCE"
                clients=$(echo "$info_output" | grep "^connected_clients:" | cut -d: -f2 | tr -d '\r')
                ops=$(echo "$info_output" | grep "^instantaneous_ops_per_sec:" | cut -d: -f2 | tr -d '\r')
                commands=$(echo "$info_output" | grep "^total_commands_processed:" | cut -d: -f2 | tr -d '\r')
                echo "│  Connected Clients: $clients"
                echo "│  Operations/sec: $ops"
                echo "└─ Total Commands: $commands"
                
                echo ""
                echo "┌─ MEMORY"
                mem_used=$(echo "$info_output" | grep "^used_memory_human:" | cut -d: -f2 | tr -d '\r')
                mem_peak=$(echo "$info_output" | grep "^used_memory_peak_human:" | cut -d: -f2 | tr -d '\r')
                echo "│  Used: $mem_used"
                echo "└─ Peak: $mem_peak"
                
                echo ""
                echo "┌─ KEYSPACE"
                keys_info=$(echo "$info_output" | grep "^db0:")
                if [ -z "$keys_info" ]; then
                    echo "└─ No keys stored"
                else
                    keys_count=$(echo "$keys_info" | grep -o "keys=[0-9]*" | cut -d= -f2)
                    echo "└─ Keys: $keys_count"
                fi
            fi
        else
            echo -e "┌─ ${RED}STATUS: ● STOPPED${NC}"
            echo "│"
            echo "│  Redis container is not running"
            echo "│  Use './redis-cli-manager.sh start' to start it"
            echo "└─"
        fi
        
        echo ""
        echo "────────────────────────────────────────────────────────────"
        echo -e "${BLUE}Refreshing every 2 seconds... Press Ctrl+C to exit${NC}"
        
        # Wait 2 seconds before refresh
        sleep 2
    done
}

# Main command processor
case "$1" in
    monitor)
        monitor_redis
        ;;
    status)
        show_status
        ;;
    start)
        start_redis
        ;;
    stop)
        stop_redis
        ;;
    info)
        show_info
        ;;
    help|--help|-h|"")
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
