#!/bin/bash

# Pseudo-Pilot Automation Dashboard - Main Entry Point
# Modular dashboard for managing all system components

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source all library modules
source "$SCRIPT_DIR/lib/common.sh"
source "$SCRIPT_DIR/lib/redis.sh"
source "$SCRIPT_DIR/lib/flightgear.sh"
source "$SCRIPT_DIR/lib/system.sh"
source "$SCRIPT_DIR/lib/help.sh"

#===============================================================================
# MAIN
#===============================================================================

COMPONENT=$1
ACTION=$2

# Handle no arguments or help
if [ -z "$COMPONENT" ] || [ "$COMPONENT" = "help" ] || [ "$COMPONENT" = "--help" ] || [ "$COMPONENT" = "-h" ]; then
    show_help
    exit 0
fi

# Route to component handler
route_component "$COMPONENT" "$ACTION"
