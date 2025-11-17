import subprocess
import platform
from typing import Dict, Any, List, Optional
import structlog

logger = structlog.get_logger()

class AppLauncher:
    """
    Launch and control desktop applications.
    
    Supports:
    - Opening applications
    - Opening URLs in browser
    - Opening files with default apps
    - Process management
    """
    
    def __init__(self):
        self.os_type = platform.system()
    
    def open_application(self, app_name: str, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Launch an application."""
        try:
            command = self._build_open_command(app_name, args or [])
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            
            logger.info("application_launched", app=app_name, pid=process.pid)
            
            return {
                "success": True,
                "pid": process.pid,
                "message": f"Launched {app_name}",
            }
            
        except Exception as e:
            logger.error("app_launch_failed", app=app_name, error=str(e))
            return {
                "success": False,
                "error": str(e),
            }
    
    def _build_open_command(self, app_name: str, args: List[str]) -> List[str]:
        """Build platform-specific open command."""
        if self.os_type == "Darwin":  # macOS
            return ["open", "-a", app_name] + args
        elif self.os_type == "Windows":
            return ["start", app_name] + args
        else:  # Linux
            return [app_name] + args
    
    def open_url(self, url: str) -> Dict[str, Any]:
        """Open URL in default browser."""
        try:
            if self.os_type == "Darwin":
                subprocess.run(["open", url])
            elif self.os_type == "Windows":
                subprocess.run(["start", url], shell=True)
            else:
                subprocess.run(["xdg-open", url])
            
            logger.info("url_opened", url=url)
            
            return {
                "success": True,
                "message": f"Opened {url}",
            }
            
        except Exception as e:
            logger.error("url_open_failed", url=url, error=str(e))
            return {
                "success": False,
                "error": str(e),
            }
    
    def open_file(self, file_path: str) -> Dict[str, Any]:
        """Open file with default application."""
        try:
            if self.os_type == "Darwin":
                subprocess.run(["open", file_path])
            elif self.os_type == "Windows":
                subprocess.run(["start", "", file_path], shell=True)
            else:
                subprocess.run(["xdg-open", file_path])
            
            logger.info("file_opened", path=file_path)
            
            return {
                "success": True,
                "message": f"Opened {file_path}",
            }
            
        except Exception as e:
            logger.error("file_open_failed", path=file_path, error=str(e))
            return {
                "success": False,
                "error": str(e),
            }
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get OpenAI function definitions."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "open_application",
                    "description": "Launch a desktop application",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "app_name": {
                                "type": "string",
                                "description": "Name of the application (e.g., 'chrome', 'vscode', 'terminal')",
                            },
                            "args": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Optional command-line arguments",
                            },
                        },
                        "required": ["app_name"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "open_url",
                    "description": "Open a URL in the default browser",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL to open",
                            },
                        },
                        "required": ["url"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "open_file",
                    "description": "Open a file with its default application",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file",
                            },
                        },
                        "required": ["file_path"],
                    },
                },
            },
        ]
