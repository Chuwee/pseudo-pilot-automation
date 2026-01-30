#!/usr/bin/env python3
"""
Test script for Supported Instructions feature

This script demonstrates how to query and manage supported instructions
in the Context Database.
"""

import socket
import json
import sys


def send_command(command_dict):
    """Send a command to the context database service"""
    try:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect('/tmp/pseudopilot_context_db.sock')
        
        client.sendall(json.dumps(command_dict).encode('utf-8'))
        response = json.loads(client.recv(4096).decode('utf-8'))
        client.close()
        
        return response
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def print_separator(title=""):
    """Print a visual separator"""
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
    else:
        print(f"{'='*60}\n")


def test_get_supported_instructions():
    """Test getting supported instructions"""
    print_separator("TEST 1: Get Supported Instructions")
    
    response = send_command({'command': 'get_supported_instructions'})
    
    if response and response['status'] == 'ok':
        instructions = response['instructions']
        count = response['count']
        
        print(f"✓ Found {count} supported instruction(s):")
        for instr in instructions:
            print(f"  - {instr}")
    else:
        print(f"✗ Failed: {response.get('message') if response else 'No response'}")


def test_is_instruction_supported():
    """Test checking if specific instructions are supported"""
    print_separator("TEST 2: Check If Instructions Are Supported")
    
    test_instructions = ["CLIMB", "climb", "DESCEND", "TURN", "random"]
    
    for instr in test_instructions:
        response = send_command({
            'command': 'is_instruction_supported',
            'instruction': instr
        })
        
        if response and response['status'] == 'ok':
            supported = response['supported']
            normalized = response['instruction']
            symbol = "✓" if supported else "✗"
            print(f"  {symbol} {normalized}: {'Supported' if supported else 'Not supported'}")
        else:
            print(f"  ✗ Error checking '{instr}'")


def test_add_supported_instruction():
    """Test adding new supported instructions"""
    print_separator("TEST 3: Add New Supported Instructions")
    
    new_instructions = ["DESCEND", "TURN", "TAXI"]
    
    for instr in new_instructions:
        response = send_command({
            'command': 'add_supported_instruction',
            'instruction': instr
        })
        
        if response and response['status'] == 'ok':
            print(f"✓ {response['message']}")
        else:
            print(f"✗ Failed to add '{instr}': {response.get('message') if response else 'No response'}")


def test_final_list():
    """Test getting final list of supported instructions"""
    print_separator("TEST 4: Final List of Supported Instructions")
    
    response = send_command({'command': 'get_supported_instructions'})
    
    if response and response['status'] == 'ok':
        instructions = response['instructions']
        count = response['count']
        
        print(f"✓ Total: {count} supported instruction(s):")
        for i, instr in enumerate(instructions, 1):
            print(f"  {i}. {instr}")
    else:
        print(f"✗ Failed: {response.get('message') if response else 'No response'}")


def main():
    """Run all tests"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     Supported Instructions - Test Suite                   ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    # Check if service is running
    try:
        response = send_command({'command': 'ping'})
        if not response or response.get('message') != 'pong':
            print("\n❌ Context Database Service is not running!")
            print("Start it with: ./main.sh --start-db")
            return 1
    except Exception:
        print("\n❌ Context Database Service is not running!")
        print("Start it with: ./main.sh --start-db")
        return 1
    
    try:
        test_get_supported_instructions()
        test_is_instruction_supported()
        test_add_supported_instruction()
        test_final_list()
        
        print_separator("ALL TESTS COMPLETED ✓")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
