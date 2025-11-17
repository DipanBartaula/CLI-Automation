from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import json

@dataclass
class MemoryItem:
    """Single memory item."""
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    item_type: str = "general"  # command, result, conversation, etc.
    
    def __post_init__(self):
        """Debug logging after initialization."""
        print(f"[DEBUG] MemoryItem created - Type: {self.item_type}, Content length: {len(self.content)}, Timestamp: {self.timestamp}")

class ShortTermMemory:
    """
    Working memory for current session.
    
    Stores:
    - Recent commands and results
    - Current conversation context
    - Active task state
    """
    
    def __init__(self, capacity: int = 50):
        self.capacity = capacity
        self._memory: deque = deque(maxlen=capacity)
        self._session_start = datetime.now()
        self._task_context: Dict[str, Any] = {}
        print(f"[DEBUG] ShortTermMemory initialized - Capacity: {capacity}, Session Start: {self._session_start}")
    
    def add(
        self,
        content: str,
        item_type: str = "general",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add item to short-term memory."""
        item = MemoryItem(
            content=content,
            item_type=item_type,
            metadata=metadata or {},
        )
        self._memory.append(item)
        print(f"[DEBUG] Item added to ShortTermMemory - Type: {item_type}, Current size: {len(self._memory)}/{self.capacity}")
    
    def get_recent(self, n: int = 10, item_type: Optional[str] = None) -> List[MemoryItem]:
        """Get n most recent items, optionally filtered by type."""
        items = list(self._memory)
        
        if item_type:
            items = [item for item in items if item.item_type == item_type]
        
        result = items[-n:]
        print(f"[DEBUG] Retrieved {len(result)} recent items - Filter type: {item_type}, Total available: {len(items)}")
        return result
    
    def get_context_summary(self) -> str:
        """Generate summary of recent context."""
        recent_items = self.get_recent(10)
        
        summary_parts = [
            f"Session started: {self._session_start.strftime('%Y-%m-%d %H:%M')}",
            f"Recent actions ({len(recent_items)}):",
        ]
        
        for item in recent_items:
            summary_parts.append(
                f"  [{item.item_type}] {item.content[:100]}"
            )
        
        if self._task_context:
            summary_parts.append(f"Active task: {self._task_context.get('name', 'None')}")
        
        return "\n".join(summary_parts)
    
    def set_task_context(self, task_name: str, context: Dict[str, Any]) -> None:
        """Set context for current task."""
        self._task_context = {
            "name": task_name,
            "started": datetime.now(),
            **context,
        }
        print(f"[DEBUG] Task context set - Task: {task_name}, Context keys: {list(context.keys())}")
    
    def clear_task_context(self) -> None:
        """Clear current task context."""
        self._task_context = {}
        print(f"[DEBUG] Task context cleared")
    
    def get_task_context(self) -> Dict[str, Any]:
        """Get current task context."""
        return self._task_context.copy()
    
    def clear(self) -> None:
        """Clear all short-term memory."""
        print(f"[DEBUG] Clearing all ShortTermMemory - Items before: {len(self._memory)}")
        self._memory.clear()
        self._task_context = {}
        print(f"[DEBUG] ShortTermMemory cleared - Items after: {len(self._memory)}")
