import psutil
import platform
from datetime import datetime
from typing import Dict, Any, List
import structlog

logger = structlog.get_logger()

class SystemMonitor:
    """
    System information and monitoring.
    
    Provides:
    - CPU/Memory usage
    - Disk information
    - Network stats
    - Process information
    """
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get general system information."""
        try:
            return {
                "success": True,
                "os": platform.system(),
                "os_version": platform.version(),
                "architecture": platform.machine(),
                "processor": platform.processor(),
                "hostname": platform.node(),
                "python_version": platform.python_version(),
            }
        except Exception as e:
            logger.error("system_info_failed", error=str(e))
            return {"success": False, "error": str(e)}
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """Get CPU usage information."""
        try:
            return {
                "success": True,
                "cpu_percent": psutil.cpu_percent(interval=1),
                "cpu_count": psutil.cpu_count(),
                "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
            }
        except Exception as e:
            logger.error("cpu_info_failed", error=str(e))
            return {"success": False, "error": str(e)}
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Get memory usage information."""
        try:
            mem = psutil.virtual_memory()
            return {
                "success": True,
                "total_gb": round(mem.total / (1024**3), 2),
                "available_gb": round(mem.available / (1024**3), 2),
                "used_gb": round(mem.used / (1024**3), 2),
                "percent": mem.percent,
            }
        except Exception as e:
            logger.error("memory_info_failed", error=str(e))
            return {"success": False, "error": str(e)}
    
    def get_disk_info(self) -> Dict[str, Any]:
        """Get disk usage information."""
        try:
            partitions = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    partitions.append({
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total_gb": round(usage.total / (1024**3), 2),
                        "used_gb": round(usage.used / (1024**3), 2),
                        "free_gb": round(usage.free / (1024**3), 2),
                        "percent": usage.percent,
                    })
                except PermissionError:
                    continue
            
            return {
                "success": True,
                "partitions": partitions,
            }
        except Exception as e:
            logger.error("disk_info_failed", error=str(e))
            return {"success": False, "error": str(e)}
    
    def list_processes(self, limit: int = 10) -> Dict[str, Any]:
        """List running processes."""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
            
            return {
                "success": True,
                "processes": processes[:limit],
                "total_count": len(processes),
            }
        except Exception as e:
            logger.error("process_list_failed", error=str(e))
            return {"success": False, "error": str(e)}
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get OpenAI function definitions."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_system_info",
                    "description": "Get general system information (OS, architecture, etc.)",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_cpu_info",
                    "description": "Get CPU usage and information",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_memory_info",
                    "description": "Get memory usage information",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_disk_info",
                    "description": "Get disk usage information",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "list_processes",
                    "description": "List running processes with resource usage",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of processes to return (default: 10)",
                            },
                        },
                    },
                },
            },
        ]
