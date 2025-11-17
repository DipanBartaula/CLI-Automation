#!/usr/bin/env python
"""
AgentOS Launcher - Choose between CLI and GUI Terminal
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def main():
    parser = argparse.ArgumentParser(
        description="AgentOS - AI-Powered Command Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python launch.py --gui          # Launch GUI terminal (default)
  python launch.py --cli          # Launch command-line interface
  python launch.py --debug        # Launch GUI with debug logging
  python launch.py --cli --debug  # Launch CLI with debug logging
        """
    )
    
    parser.add_argument(
        '--cli',
        action='store_true',
        help='Launch command-line interface instead of GUI'
    )
    parser.add_argument(
        '--gui',
        action='store_true',
        help='Launch GUI terminal (default)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    # Set debug level if requested
    if args.debug:
        os.environ['DEBUG'] = '1'
    
    # Launch CLI if requested, otherwise GUI (default)
    if args.cli:
        print("🚀 Launching AgentOS CLI...")
        from agentos.cli import main as cli_main
        cli_main(['--debug'] if args.debug else [])
    else:
        print("🚀 Launching AgentOS GUI Terminal...")
        from agentos.gui import main as gui_main
        gui_main()


if __name__ == "__main__":
    main()
