"""
Tools module - Provides various tools for system automation.

Classes:
    - ShellExecutor: Execute shell commands with safety checks
    - FileManager: File operations (read, write, search, list)
    - AppLauncher: Launch applications and open URLs/files
    - SystemMonitor: Monitor system resources and processes
    - BrowserControl: Browser automation and control
"""

from .shell_executor import ShellExecutor
from .file_manager import FileManager
from .app_launcher import AppLauncher
from .system_monitor import SystemMonitor
from .browser_control import BrowserControl

__all__ = [
    "ShellExecutor",
    "FileManager",
    "AppLauncher",
    "SystemMonitor",
    "BrowserControl",
]

print(f"[DEBUG] Tools module loaded")
