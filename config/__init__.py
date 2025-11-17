"""
Configuration module - Settings and prompts for AgentOS.

Classes:
    - Settings: Application configuration from environment and files
"""

from .settings import settings
from .prompts import load_prompts

__all__ = [
    "settings",
    "load_prompts",
]

print(f"[DEBUG] Configuration module loaded")
