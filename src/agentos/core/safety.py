from typing import List, Tuple, Optional
import re
import structlog

logger = structlog.get_logger()

class SafetyChecker:
    """
    Comprehensive safety checking system.
    
    Validates:
    - Commands
    - File paths
    - User inputs
    - System operations
    """
    
    def __init__(self):
        self.dangerous_commands = [
            "rm -rf /",
            "dd if=/dev/zero",
            "mkfs.",
            ":(){ :|:& };:",  # Fork bomb
            "chmod -R 777 /",
            "wget * | sh",
            "curl * | bash",
        ]
        
        self.suspicious_patterns = [
            r"sudo\s+rm",
            r"format\s+[A-Z]:",
            r"del\s+/[FSQ]",
            r"shutdown",
            r"reboot",
        ]
    
    def check_command(self, command: str) -> Tuple[bool, Optional[str]]:
        """
        Check if command is safe to execute.
        
        Returns: (is_safe, reason)
        """
        command_lower = command.lower()
        
        # Check exact dangerous commands
        for dangerous in self.dangerous_commands:
            if dangerous.lower() in command_lower:
                logger.warning("dangerous_command_blocked", command=command[:50])
                return False, f"Blocked dangerous command: {dangerous}"
        
        # Check patterns
        for pattern in self.suspicious_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                logger.warning("suspicious_pattern_detected", pattern=pattern)
                return False, f"Suspicious pattern detected: {pattern}"
        
        return True, None
    
    def check_file_operation(
        self,
        operation: str,
        path: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if file operation is safe.
        
        Args:
            operation: 'read', 'write', 'delete'
            path: File path
        """
        # Prevent system file access
        protected_paths = [
            "/etc/passwd",
            "/etc/shadow",
            "/boot",
            "C:\\Windows\\System32",
        ]
        
        for protected in protected_paths:
            if protected.lower() in path.lower():
                return False, f"Access to protected path denied: {protected}"
        
        # Check for path traversal
        if ".." in path:
            return False, "Path traversal not allowed"
        
        # Extra checks for delete operations
        if operation == "delete":
            if path in ["/", "C:\\"]:
                return False, "Cannot delete root directory"
        
        return True, None
    
    def requires_confirmation(self, command: str) -> bool:
        """Check if command requires user confirmation."""
        confirmation_keywords = [
            "delete", "remove", "rm",
            "format", "wipe",
            "shutdown", "reboot",
        ]
        
        return any(kw in command.lower() for kw in confirmation_keywords)
