from pathlib import Path
from typing import Tuple, Optional
import re

def validate_path(path: str) -> Tuple[bool, Optional[str]]:
    """
    Validate file/directory path.
    
    Returns: (is_valid, error_message)
    """
    try:
        # Check for path traversal attempts
        if ".." in path:
            return False, "Path traversal not allowed"
        
        # Check for suspicious characters
        dangerous_chars = [";", "|", "&", "$", "`"]
        if any(char in path for char in dangerous_chars):
            return False, "Invalid characters in path"
        
        # Try to resolve path
        resolved = Path(path).resolve()
        
        return True, None
        
    except Exception as e:
        return False, str(e)

def validate_command(command: str) -> Tuple[bool, Optional[str]]:
    """
    Validate shell command for safety.
    
    Returns: (is_safe, warning_message)
    """
    dangerous_patterns = [
        r"rm\s+-rf\s+/",
        r"dd\s+if=",
        r"mkfs\.",
        r":\(\)\{.*;\};",  # Fork bomb
        r"chmod\s+-R\s+777",
        r"sudo\s+rm",
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return False, f"Dangerous pattern detected: {pattern}"
    
    return True, None

def sanitize_input(text: str, max_length: int = 10000) -> str:
    """Sanitize user input."""
    # Truncate
    text = text[:max_length]
    
    # Remove null bytes
    text = text.replace("\x00", "")
    
    return text.strip()
