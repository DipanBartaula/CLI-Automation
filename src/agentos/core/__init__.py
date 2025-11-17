"""
Core agent module - Contains the main AgentOS agent and task executor.

Classes:
    - AgentOS: Main agentic system for computer automation
    - TaskExecutor: Executes multi-step tasks with error handling and retries
"""

from .agent import AgentOS
from .executor import TaskExecutor

__all__ = [
    "AgentOS",
    "TaskExecutor",
]

print(f"[DEBUG] Core agent module loaded")
