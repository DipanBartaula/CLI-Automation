from collections import deque
from typing import Any, Optional

class CircularBuffer:
    """Circular buffer for fixed-size memory storage."""
    
    def __init__(self, maxsize: int = 100):
        self.buffer = deque(maxlen=maxsize)
        self.maxsize = maxsize
    
    def append(self, item: Any) -> None:
        """Add item to buffer."""
        self.buffer.append(item)
    
    def get_all(self) -> list:
        """Get all items in buffer."""
        return list(self.buffer)
    
    def get_recent(self, n: int) -> list:
        """Get n most recent items."""
        return list(self.buffer)[-n:]
    
    def clear(self) -> None:
        """Clear buffer."""
        self.buffer.clear()
    
    def __len__(self) -> int:
        return len(self.buffer)
