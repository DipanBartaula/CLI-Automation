import pytest
from agentos.core.agent import AgentOS

@pytest.mark.asyncio
async def test_agent_initialization():
    """Test agent initializes correctly."""
    agent = AgentOS()
    assert agent.llm is not None
    assert agent.context_manager is not None
    assert len(agent.tools) > 0

@pytest.mark.asyncio  
async def test_tool_execution():
    """Test tool execution routing."""
    agent = AgentOS()
    
    result = agent._execute_tool(
        "get_system_info",
        {}
    )
    
    assert result["success"] == True
    assert "os" in result
```

## File 37: tests/unit/test_memory.py

```python
"""Unit tests for memory system."""
import pytest
from agentos.memory.short_term import ShortTermMemory
from agentos.memory.long_term import LongTermMemory

def test_short_term_memory():
    """Test short-term memory operations."""
    memory = ShortTermMemory(capacity=10)
    
    memory.add("Test command", item_type="command")
    recent = memory.get_recent(1)
    
    assert len(recent) == 1
    assert recent[0].content == "Test command"

def test_long_term_memory(temp_dir):
    """Test long-term memory persistence."""
    db_path = temp_dir / "test.db"
    memory = LongTermMemory(db_path=db_path)
    
    memory.add_command("ls", "output", True)
    
    history = memory.get_command_history(limit=1)
    assert len(history) == 1
    assert history[0]["command"] == "ls"
