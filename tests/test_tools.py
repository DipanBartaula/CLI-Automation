import pytest
from agentos.tools.shell_executor import ShellExecutor
from agentos.tools.file_manager import FileManager

def test_shell_safety_check():
    """Test shell command safety validation."""
    shell = ShellExecutor()
    
    # Safe command
    is_safe, reason = shell.is_safe_command("ls -la")
    assert is_safe == True
    
    # Dangerous command
    is_safe, reason = shell.is_safe_command("rm -rf /")
    assert is_safe == False
    assert reason is not None

def test_file_read(temp_dir):
    """Test file reading."""
    file_manager = FileManager()
    
    # Create test file
    test_file = temp_dir / "test.txt"
    test_file.write_text("Hello World")
    
    result = file_manager.read_file(str(test_file))
    
    assert result["success"] == True
    assert result["content"] == "Hello World"
