from collections import deque
from typing import Any, Optional

class CircularBuffer:
    """Circular buffer for fixed-size memory storage."""
    
    def __init__(self, maxsize: int = 100):
        self.buffer = deque(maxlen=maxsize)
        self.maxsize = maxsize
        print(f"[DEBUG] CircularBuffer initialized - Max size: {maxsize}")
    
    def append(self, item: Any) -> None:
        """Add item to buffer."""
        self.buffer.append(item)
        print(f"[DEBUG] Item appended to CircularBuffer - Current size: {len(self.buffer)}/{self.maxsize}")
    
    def get_all(self) -> list:
        """Get all items in buffer."""
        all_items = list(self.buffer)
        print(f"[DEBUG] Retrieved all items from CircularBuffer - Count: {len(all_items)}")
        return all_items
    
    def get_recent(self, n: int) -> list:
        """Get n most recent items."""
        recent_items = list(self.buffer)[-n:]
        print(f"[DEBUG] Retrieved recent items from CircularBuffer - Count: {len(recent_items)}/{n}")
        return recent_items
    
    def clear(self) -> None:
        """Clear buffer."""
        print(f"[DEBUG] Clearing CircularBuffer - Items before clear: {len(self.buffer)}")
        self.buffer.clear()
        print(f"[DEBUG] CircularBuffer cleared - Items after clear: {len(self.buffer)}")
    
    def __len__(self) -> int:
        return len(self.buffer)
