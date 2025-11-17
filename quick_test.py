#!/usr/bin/env python
"""Quick test of agent responses"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agentos.core.agent import AgentOS

async def main():
    print("Testing AgentOS Agent Response Handling")
    print("=" * 60)
    
    agent = AgentOS()
    
    # Test 1: Create directory
    print("\n[TEST 1] Create directory")
    cmd = "create a directory named ankit_bro in A: drive"
    print(f"Command: {cmd}")
    
    try:
        response = await agent.process_request(cmd)
        print(f"Response type: {type(response)}")
        print(f"Response is None: {response is None}")
        print(f"Response length: {len(str(response)) if response else 0}")
        print(f"Response: {response}")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Test complete!")

if __name__ == "__main__":
    asyncio.run(main())
