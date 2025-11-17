#!/usr/bin/env python
"""
Direct GUI Terminal Launcher for AgentOS
Simple one-command startup for the GUI terminal
"""

import sys
import os

# Add src and project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

if __name__ == "__main__":
    from agentos.gui.gui_new import main
    main()
