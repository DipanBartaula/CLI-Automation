#!/usr/bin/env python
"""Test script to interactively test the CLI with sample commands."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agentos.cli import CLI
from agentos.core.agent import AgentOS
import asyncio

async def test_cli():
    """Test CLI functionality with sample commands."""
    
    print("\n" + "="*70)
    print("     🤖 AGENTOS CLI - INTERACTIVE TEST")
    print("="*70 + "\n")
    
    cli = CLI()
    
    # Test commands
    test_commands = [
        "What are the contents of requirements.txt?",
        "List Python files in the src directory",
        "Get current directory path",
        "/help",
        "/status",
    ]
    
    print("[INFO] Starting interactive CLI test session...\n")
    
    for i, cmd in enumerate(test_commands, 1):
        print(f"\n{'─'*70}")
        print(f"[TEST {i}] Command: {cmd}")
        print('─'*70)
        
        try:
            # Process the command through the agent
            if cmd.startswith('/'):
                # Special command
                result = cli._handle_special_command(cmd)
                if result:
                    print(f"[RESULT] {result}")
            else:
                # Regular command - process through agent
                print(f"[PROCESSING] Sending to AgentOS...")
                response = await cli.agent.process_request(cmd)
                print(f"[RESPONSE] {response[:200]}..." if len(response) > 200 else f"[RESPONSE] {response}")
                
        except Exception as e:
            print(f"[ERROR] {str(e)}")
    
    print(f"\n{'─'*70}")
    print("[INFO] Test session completed!")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        asyncio.run(test_cli())
    except KeyboardInterrupt:
        print("\n[INFO] Test interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
