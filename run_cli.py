#!/usr/bin/env python
"""
Simple runner script for CLI-AUTO application.
Run this to start the CLI.
"""
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Now import and run
from agentos.cli import main

if __name__ == "__main__":
    main()
