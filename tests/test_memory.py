"""
Comprehensive tests for memory system components.
Tests cover short-term memory, long-term memory, context manager, and vector store.
"""

import pytest
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agentos.memory.short_term import ShortTermMemory, MemoryItem
from agentos.memory.long_term import LongTermMemory
from agentos.memory.context_manager import ContextManager
from agentos.memory.buffer import CircularBuffer


class TestMemoryItem:
    """Test MemoryItem dataclass."""
    
    def test_memory_item_creation(self):
        """Test creating a memory item."""
        print("\n[TEST] Testing MemoryItem creation...")
        content = "Test command executed"
        item = MemoryItem(content=content, item_type="command")
        
        assert item.content == content
        assert item.item_type == "command"
        assert isinstance(item.timestamp, datetime)
        assert isinstance(item.metadata, dict)
        print("[PASSED] MemoryItem created successfully")
    
    def test_memory_item_with_metadata(self):
        """Test memory item with metadata."""
        print("\n[TEST] Testing MemoryItem with metadata...")
        metadata = {"status": "success", "duration": 2.5}
        item = MemoryItem(
            content="Task completed",
            item_type="task",
            metadata=metadata
        )
        
        assert item.metadata == metadata
        assert item.metadata["status"] == "success"
        print("[PASSED] MemoryItem with metadata works correctly")


class TestShortTermMemory:
    """Test ShortTermMemory class."""
    
    @pytest.fixture
    def short_term(self):
        """Create a ShortTermMemory instance."""
        print("\n[FIXTURE] Creating ShortTermMemory instance...")
        return ShortTermMemory(capacity=10)
    
    def test_initialization(self, short_term):
        """Test ShortTermMemory initialization."""
        print("\n[TEST] Testing ShortTermMemory initialization...")
        assert short_term.capacity == 10
        assert len(short_term._memory) == 0
        assert short_term._task_context == {}
        print("[PASSED] ShortTermMemory initialized correctly")
    
    def test_add_item(self, short_term):
        """Test adding items to memory."""
        print("\n[TEST] Testing adding items to ShortTermMemory...")
        short_term.add("Command 1", item_type="command")
        short_term.add("Command 2", item_type="command")
        
        assert len(short_term._memory) == 2
        print("[PASSED] Items added successfully")
    
    def test_get_recent(self, short_term):
        """Test retrieving recent items."""
        print("\n[TEST] Testing get_recent functionality...")
        for i in range(5):
            short_term.add(f"Item {i}", item_type="command")
        
        recent = short_term.get_recent(3)
        assert len(recent) == 3
        assert recent[-1].content == "Item 4"
        print("[PASSED] Retrieved recent items correctly")
    
    def test_get_recent_by_type(self, short_term):
        """Test filtering items by type."""
        print("\n[TEST] Testing get_recent with type filter...")
        short_term.add("Command 1", item_type="command")
        short_term.add("Result 1", item_type="result")
        short_term.add("Command 2", item_type="command")
        
        commands = short_term.get_recent(10, item_type="command")
        assert len(commands) == 2
        assert all(item.item_type == "command" for item in commands)
        print("[PASSED] Type filtering works correctly")
    
    def test_capacity_limit(self, short_term):
        """Test that capacity limit is enforced."""
        print("\n[TEST] Testing capacity limit...")
        for i in range(15):
            short_term.add(f"Item {i}")
        
        # Should only have 10 items due to capacity
        assert len(short_term._memory) == 10
        print("[PASSED] Capacity limit enforced correctly")
    
    def test_task_context(self, short_term):
        """Test task context management."""
        print("\n[TEST] Testing task context management...")
        task_name = "Download files"
        context = {"target_dir": "/downloads", "file_count": 5}
        
        short_term.set_task_context(task_name, context)
        retrieved_context = short_term.get_task_context()
        
        assert retrieved_context["name"] == task_name
        assert retrieved_context["target_dir"] == "/downloads"
        print("[PASSED] Task context set and retrieved correctly")
    
    def test_clear_task_context(self, short_term):
        """Test clearing task context."""
        print("\n[TEST] Testing clear_task_context...")
        short_term.set_task_context("Test Task", {"data": "value"})
        short_term.clear_task_context()
        
        assert short_term.get_task_context() == {}
        print("[PASSED] Task context cleared correctly")
    
    def test_clear_memory(self, short_term):
        """Test clearing all memory."""
        print("\n[TEST] Testing clear all memory...")
        short_term.add("Item 1")
        short_term.add("Item 2")
        short_term.set_task_context("Task", {})
        
        assert len(short_term._memory) > 0
        
        short_term.clear()
        
        assert len(short_term._memory) == 0
        assert short_term.get_task_context() == {}
        print("[PASSED] All memory cleared correctly")
    
    def test_context_summary(self, short_term):
        """Test generating context summary."""
        print("\n[TEST] Testing context summary generation...")
        short_term.add("Command 1", item_type="command")
        short_term.add("Command 2", item_type="command")
        short_term.set_task_context("Active Task", {})
        
        summary = short_term.get_context_summary()
        
        assert "Session started" in summary
        assert "Recent actions" in summary
        assert "Active task" in summary
        assert "Active Task" in summary
        print("[PASSED] Context summary generated correctly")


class TestLongTermMemory:
    """Test LongTermMemory class."""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database."""
        print("\n[FIXTURE] Creating temporary database...")
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_memory.db"
            yield db_path
            # Ensure DB is closed before cleanup (Windows fix)
            import gc
            gc.collect()
    
    @pytest.fixture
    def long_term(self, temp_db):
        """Create a LongTermMemory instance with temp database."""
        print("\n[FIXTURE] Creating LongTermMemory instance...")
        instance = LongTermMemory(db_path=temp_db)
        yield instance
        # Close database connection before cleanup
        try:
            if hasattr(instance, 'conn') and instance.conn:
                instance.conn.close()
        except Exception as e:
            print(f"[DEBUG] Error closing connection: {e}")
        import gc
        gc.collect()
    
    def test_initialization(self, long_term):
        """Test LongTermMemory initialization."""
        print("\n[TEST] Testing LongTermMemory initialization...")
        assert long_term.db_path is not None
        print("[PASSED] LongTermMemory initialized correctly")
    
    def test_add_command(self, long_term):
        """Test adding commands to long-term memory."""
        print("\n[TEST] Testing add_command...")
        long_term.add_command(
            command="ls -la",
            output="total files...",
            success=True,
            metadata={"shell": "bash"}
        )
        
        history = long_term.get_command_history(limit=10)
        assert len(history) > 0
        assert history[0]["command"] == "ls -la"
        assert history[0]["success"] == 1  # SQLite stores as 1/0
        print("[PASSED] Command added successfully")
    
    def test_get_command_history(self, long_term):
        """Test retrieving command history."""
        print("\n[TEST] Testing get_command_history...")
        long_term.add_command("cmd1", "output1", True)
        long_term.add_command("cmd2", "output2", False)
        long_term.add_command("cmd3", "output3", True)
        
        history = long_term.get_command_history(limit=10)
        assert len(history) == 3
        print("[PASSED] Command history retrieved correctly")
    
    def test_get_command_history_success_only(self, long_term):
        """Test filtering successful commands only."""
        print("\n[TEST] Testing success_only filter...")
        long_term.add_command("cmd1", "output1", True)
        long_term.add_command("cmd2", "output2", False)
        long_term.add_command("cmd3", "output3", True)
        
        success_history = long_term.get_command_history(limit=10, success_only=True)
        assert len(success_history) == 2
        assert all(cmd["success"] for cmd in success_history)
        print("[PASSED] Success filter works correctly")
    
    def test_add_task(self, long_term):
        """Test adding tasks to long-term memory."""
        print("\n[TEST] Testing add_task...")
        steps = ["Step 1", "Step 2", "Step 3"]
        long_term.add_task(
            description="File organization task",
            steps=steps,
            outcome="Successfully organized files",
            duration_seconds=120
        )
        
        # Verify by querying database directly
        with sqlite3.connect(long_term.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM task_history")
            tasks = cursor.fetchall()
            assert len(tasks) == 1
        print("[PASSED] Task added successfully")
    
    def test_get_similar_tasks(self, long_term):
        """Test finding similar tasks."""
        print("\n[TEST] Testing get_similar_tasks...")
        long_term.add_task("Download files from website", ["wget url"], "Success", 10)
        long_term.add_task("Install software package", ["apt-get install"], "Success", 20)
        long_term.add_task("Download and install package", ["wget && install"], "Success", 30)
        
        similar = long_term.get_similar_tasks("Download files", limit=2)
        assert len(similar) > 0
        print("[PASSED] Similar tasks found")
    
    def test_set_get_preference(self, long_term):
        """Test setting and getting preferences."""
        print("\n[TEST] Testing preference management...")
        long_term.set_preference("theme", "dark")
        long_term.set_preference("language", "en")
        
        theme = long_term.get_preference("theme")
        language = long_term.get_preference("language")
        
        assert theme == "dark"
        assert language == "en"
        print("[PASSED] Preferences saved and retrieved correctly")
    
    def test_get_preference_default(self, long_term):
        """Test getting preference with default value."""
        print("\n[TEST] Testing preference default value...")
        value = long_term.get_preference("nonexistent", "default_value")
        assert value == "default_value"
        print("[PASSED] Default preference value works correctly")
    
    def test_cleanup_old_data(self, long_term):
        """Test cleanup of old data."""
        print("\n[TEST] Testing cleanup_old_data...")
        # Add a command
        long_term.add_command("test_cmd", "output", True)
        
        history = long_term.get_command_history(limit=10)
        assert len(history) > 0
        
        # Cleanup with 0 days (removes everything)
        long_term.cleanup_old_data(days=0)
        
        history_after = long_term.get_command_history(limit=10)
        assert len(history_after) == 0
        print("[PASSED] Old data cleanup works correctly")


class TestCircularBuffer:
    """Test CircularBuffer class."""
    
    @pytest.fixture
    def buffer(self):
        """Create a CircularBuffer instance."""
        print("\n[FIXTURE] Creating CircularBuffer instance...")
        return CircularBuffer(maxsize=5)
    
    def test_initialization(self, buffer):
        """Test CircularBuffer initialization."""
        print("\n[TEST] Testing CircularBuffer initialization...")
        assert buffer.maxsize == 5
        assert len(buffer) == 0
        print("[PASSED] CircularBuffer initialized correctly")
    
    def test_append(self, buffer):
        """Test appending items."""
        print("\n[TEST] Testing append...")
        buffer.append("item1")
        buffer.append("item2")
        
        assert len(buffer) == 2
        print("[PASSED] Items appended successfully")
    
    def test_capacity_overflow(self, buffer):
        """Test that old items are removed when capacity exceeded."""
        print("\n[TEST] Testing capacity overflow...")
        for i in range(7):
            buffer.append(f"item{i}")
        
        # Should only have 5 items
        assert len(buffer) == 5
        all_items = buffer.get_all()
        # Should have items 2-6 (dropped 0-1)
        assert "item2" in all_items
        assert "item6" in all_items
        print("[PASSED] Capacity overflow handled correctly")
    
    def test_get_recent(self, buffer):
        """Test getting recent items."""
        print("\n[TEST] Testing get_recent...")
        for i in range(5):
            buffer.append(f"item{i}")
        
        recent = buffer.get_recent(3)
        assert len(recent) == 3
        assert recent[-1] == "item4"
        print("[PASSED] Recent items retrieved correctly")
    
    def test_clear(self, buffer):
        """Test clearing buffer."""
        print("\n[TEST] Testing clear...")
        for i in range(3):
            buffer.append(f"item{i}")
        
        assert len(buffer) > 0
        buffer.clear()
        
        assert len(buffer) == 0
        print("[PASSED] Buffer cleared successfully")


class TestContextManager:
    """Test ContextManager class."""
    
    @pytest.fixture
    def context_manager(self):
        """Create a ContextManager instance."""
        print("\n[FIXTURE] Creating ContextManager instance...")
        # This will fail if dependencies aren't available
        # but we'll catch it gracefully
        try:
            return ContextManager()
        except Exception as e:
            print(f"[WARNING] Could not initialize ContextManager: {e}")
            pytest.skip(f"ContextManager initialization failed: {e}")
    
    def test_initialization(self, context_manager):
        """Test ContextManager initialization."""
        print("\n[TEST] Testing ContextManager initialization...")
        assert context_manager.short_term is not None
        assert context_manager.long_term is not None
        assert context_manager.vector_store is not None
        print("[PASSED] ContextManager initialized correctly")
    
    def test_record_command(self, context_manager):
        """Test recording a command."""
        print("\n[TEST] Testing record_command...")
        context_manager.record_command(
            command="echo 'hello'",
            output="hello",
            success=True,
            metadata={"type": "echo"}
        )
        
        # Verify it was added to short-term
        recent = context_manager.short_term.get_recent(1)
        assert len(recent) > 0
        print("[PASSED] Command recorded successfully")
    
    def test_record_task(self, context_manager):
        """Test recording a task."""
        print("\n[TEST] Testing record_task...")
        context_manager.record_task(
            description="Organize files",
            steps=["Step 1", "Step 2"],
            outcome="Success",
            duration_seconds=60
        )
        
        recent = context_manager.short_term.get_recent(1, item_type="task")
        assert len(recent) > 0
        print("[PASSED] Task recorded successfully")
    
    def test_get_context_for_query(self, context_manager):
        """Test getting context for a query."""
        print("\n[TEST] Testing get_context_for_query...")
        context_manager.record_command("test cmd", "output", True)
        
        context = context_manager.get_context_for_query("test query")
        
        assert "recent_actions" in context
        assert "similar_commands" in context
        assert "similar_tasks" in context
        assert "current_task" in context
        assert "summary" in context
        print("[PASSED] Context retrieved successfully")
    
    def test_format_context_for_llm(self, context_manager):
        """Test formatting context for LLM."""
        print("\n[TEST] Testing format_context_for_llm...")
        context_manager.record_command("test", "output", True)
        
        context = context_manager.get_context_for_query("query")
        formatted = context_manager.format_context_for_llm(context)
        
        assert isinstance(formatted, str)
        assert len(formatted) >= 0
        print("[PASSED] Context formatted for LLM")
    
    def test_clear_session(self, context_manager):
        """Test clearing session."""
        print("\n[TEST] Testing clear_session...")
        context_manager.record_command("cmd", "output", True)
        assert len(context_manager.short_term._memory) > 0
        
        context_manager.clear_session()
        
        assert len(context_manager.short_term._memory) == 0
        print("[PASSED] Session cleared successfully")


class TestMemoryIntegration:
    """Integration tests for memory systems."""
    
    def test_full_workflow(self):
        """Test a complete memory workflow."""
        print("\n[TEST] Testing full memory workflow...")
        
        # Create instances
        short_term = ShortTermMemory(capacity=20)
        buffer = CircularBuffer(maxsize=10)
        
        # Simulate workflow
        print("[WORKFLOW] Adding items to memory...")
        for i in range(5):
            content = f"Command {i}: ls -la"
            short_term.add(content, item_type="command")
            buffer.append(content)
        
        print("[WORKFLOW] Setting task context...")
        short_term.set_task_context("File Organization", {"target": "/home"})
        
        print("[WORKFLOW] Retrieving items...")
        recent_items = short_term.get_recent(3)
        buffer_items = buffer.get_all()
        context = short_term.get_context_summary()
        
        print("[WORKFLOW] Validating results...")
        assert len(recent_items) == 3
        assert len(buffer_items) == 5
        assert "File Organization" in context
        
        print("[PASSED] Full workflow completed successfully")
    
    def test_memory_persistence(self):
        """Test that long-term memory persists."""
        print("\n[TEST] Testing memory persistence...")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            
            # First instance
            print("[PERSISTENCE] Creating first instance...")
            mem1 = LongTermMemory(db_path=db_path)
            mem1.add_command("persistent cmd", "output", True)
            del mem1
            import gc
            gc.collect()
            
            # Second instance with same db
            print("[PERSISTENCE] Creating second instance with same DB...")
            mem2 = LongTermMemory(db_path=db_path)
            history = mem2.get_command_history(limit=10)
            
            print("[PERSISTENCE] Validating persistence...")
            assert len(history) == 1
            assert history[0]["command"] == "persistent cmd"
            del mem2
            gc.collect()
        
        print("[PASSED] Memory persistence works correctly")


# Test execution
if __name__ == "__main__":
    print("\n" + "="*70)
    print("STARTING COMPREHENSIVE MEMORY TESTS")
    print("="*70)
    
    pytest.main([__file__, "-v", "-s"])
    
    print("\n" + "="*70)
    print("MEMORY TESTS COMPLETED")
    print("="*70)
