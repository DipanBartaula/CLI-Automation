import subprocess
import shlex
from typing import Dict, Any, Optional, List
import platform
import structlog

from config.settings import settings

logger = structlog.get_logger()

class ShellExecutor:
    """
    Safe shell command executor.
    
    Features:
    - Command validation
    - Timeout handling
    - Output capturing
    - Cross-platform support
    """
    
    def __init__(self):
        self.os_type = platform.system()
        self.shell = self._get_shell()
        self.dangerous_patterns = settings.safety.dangerous_commands
    
    def _get_shell(self) -> str:
        """Get appropriate shell for OS."""
        if self.os_type == "Windows":
            return "powershell.exe"
        else:
            return "/bin/bash"
    
    def is_safe_command(self, command: str) -> tuple[bool, Optional[str]]:
        """
        Check if command is safe to execute.
        
        Returns: (is_safe, reason)
        """
        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if pattern.lower() in command.lower():
                return False, f"Dangerous pattern detected: {pattern}"
        
        # Check for piped elevated privileges
        if any(p in command.lower() for p in ["sudo", "su -", "runas"]):
            return False, "Elevated privileges not allowed without confirmation"
        
        # Check for recursive operations
        if "rm -r" in command or "del /s" in command:
            return False, "Recursive deletion requires confirmation"
        
        return True, None
    
    def execute(
        self,
        command: str,
        timeout: int = 30,
        cwd: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute shell command safely.
        
        Returns:
        {
            "stdout": str,
            "stderr": str,
            "returncode": int,
            "success": bool,
            "error": Optional[str]
        }
        """
        # Safety check
        is_safe, reason = self.is_safe_command(command)
        if not is_safe:
            logger.warning("unsafe_command_blocked", command=command, reason=reason)
            return {
                "stdout": "",
                "stderr": reason,
                "returncode": -1,
                "success": False,
                "error": reason,
            }
        
        try:
            logger.info("executing_command", command=command, cwd=cwd)
            
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
                executable=self.shell if self.os_type != "Windows" else None,
            )
            
            success = result.returncode == 0
            
            logger.info(
                "command_executed",
                command=command[:50],
                returncode=result.returncode,
                success=success,
            )
            
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "success": success,
                "error": None if success else result.stderr,
            }
            
        except subprocess.TimeoutExpired:
            error = f"Command timed out after {timeout} seconds"
            logger.error("command_timeout", command=command, timeout=timeout)
            return {
                "stdout": "",
                "stderr": error,
                "returncode": -1,
                "success": False,
                "error": error,
            }
        except Exception as e:
            error = str(e)
            logger.error("command_failed", command=command, error=error)
            return {
                "stdout": "",
                "stderr": error,
                "returncode": -1,
                "success": False,
                "error": error,
            }
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get OpenAI function definition for this tool."""
        return {
            "type": "function",
            "function": {
                "name": "execute_shell_command",
                "description": "Execute a shell command on the system. Use for file operations, system queries, running programs, etc.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The shell command to execute (e.g., 'ls -la', 'python script.py', 'git status')",
                        },
                        "explanation": {
                            "type": "string",
                            "description": "Brief explanation of what this command does",
                        },
                        "working_directory": {
                            "type": "string",
                            "description": "Optional working directory for command execution",
                        },
                    },
                    "required": ["command", "explanation"],
                },
            },
        }
