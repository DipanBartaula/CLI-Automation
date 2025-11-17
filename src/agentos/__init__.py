from .core.agent import AgentOS
from .cli import CLI

__version__ = "0.1.0"
__author__ = "CLI-Automation Team"
__description__ = "Intelligent computer automation assistant"

__all__ = [
    "AgentOS",
    "CLI",
    "__version__",
]

print(f"[DEBUG] AgentOS v{__version__} module loaded")
