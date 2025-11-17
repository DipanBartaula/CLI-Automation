"""
Utilities module - Helper functions for logging, validation, and formatting.

Functions:
    - setup_logging: Configure logging system
    - validate_path: Validate file paths for safety
    - validate_command: Validate shell commands
    - format_bytes: Format byte sizes (KB, MB, GB, etc.)
    - format_duration: Format time durations
"""

from .logger import setup_logging
from .validators import validate_path, validate_command
from .formatters import format_bytes, format_duration

__all__ = [
    "setup_logging",
    "validate_path",
    "validate_command",
    "format_bytes",
    "format_duration",
]

print(f"[DEBUG] Utilities module loaded")
