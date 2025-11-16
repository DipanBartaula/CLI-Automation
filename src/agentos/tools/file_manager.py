import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
import structlog

logger = structlog.get_logger()

class FileManager:
    """
    Safe file operations manager.
    
    Capabilities:
    - Read/write files
    - Directory operations
    - Search files
    - File metadata
    """
    
    def read_file(self, path: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """Read file contents."""
        try:
            file_path = Path(path).resolve()
            
            if not file_path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {path}",
                }
            
            if not file_path.is_file():
                return {
                    "success": False,
                    "error": f"Not a file: {path}",
                }
            
            content = file_path.read_text(encoding=encoding)
            
            return {
                "success": True,
                "content": content,
                "size": len(content),
                "lines": content.count("\n") + 1,
            }
            
        except Exception as e:
            logger.error("file_read_failed", path=path, error=str(e))
            return {
                "success": False,
                "error": str(e),
            }
    
    def write_file(
        self,
        path: str,
        content: str,
        encoding: str = "utf-8",
        create_dirs: bool = True,
    ) -> Dict[str, Any]:
        """Write content to file."""
        try:
            file_path = Path(path).resolve()
            
            if create_dirs:
                file_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_path.write_text(content, encoding=encoding)
            
            logger.info("file_written", path=str(file_path))
            
            return {
                "success": True,
                "path": str(file_path),
                "size": len(content),
            }
            
        except Exception as e:
            logger.error("file_write_failed", path=path, error=str(e))
            return {
                "success": False,
                "error": str(e),
            }
    
    def list_directory(self, path: str = ".") -> Dict[str, Any]:
        """List directory contents."""
        try:
            dir_path = Path(path).resolve()
            
            if not dir_path.exists():
                return {
                    "success": False,
                    "error": f"Directory not found: {path}",
                }
            
            if not dir_path.is_dir():
                return {
                    "success": False,
                    "error": f"Not a directory: {path}",
                }
            
            items = []
            for item in dir_path.iterdir():
                items.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None,
                })
            
            return {
                "success": True,
                "path": str(dir_path),
                "items": items,
                "count": len(items),
            }
            
        except Exception as e:
            logger.error("directory_list_failed", path=path, error=str(e))
            return {
                "success": False,
                "error": str(e),
            }
    
    def search_files(
        self,
        directory: str,
        pattern: str,
        recursive: bool = True,
    ) -> Dict[str, Any]:
        """Search for files matching pattern."""
        try:
            dir_path = Path(directory).resolve()
            
            if recursive:
                matches = list(dir_path.rglob(pattern))
            else:
                matches = list(dir_path.glob(pattern))
            
            results = [
                {
                    "path": str(match),
                    "name": match.name,
                    "type": "directory" if match.is_dir() else "file",
                }
                for match in matches
            ]
            
            return {
                "success": True,
                "matches": results,
                "count": len(results),
            }
            
        except Exception as e:
            logger.error("file_search_failed", directory=directory, error=str(e))
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
                    "name": "read_file",
                    "description": "Read the contents of a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Path to the file",
                            },
                        },
                        "required": ["path"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "Write content to a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Path to the file",
                            },
                            "content": {
                                "type": "string",
                                "description": "Content to write",
                            },
                        },
                        "required": ["path", "content"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "list_directory",
                    "description": "List contents of a directory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Directory path (default: current directory)",
                            },
                        },
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "search_files",
                    "description": "Search for files matching a pattern",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "directory": {
                                "type": "string",
                                "description": "Directory to search in",
                            },
                            "pattern": {
                                "type": "string",
                                "description": "File pattern (e.g., '*.py', 'test_*.txt')",
                            },
                            "recursive": {
                                "type": "boolean",
                                "description": "Search recursively in subdirectories",
                            },
                        },
                        "required": ["directory", "pattern"],
                    },
                },
            },
        ]
