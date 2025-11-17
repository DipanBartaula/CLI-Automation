from typing import Any, Dict, List, Optional
import structlog

from .short_term import ShortTermMemory
from .long_term import LongTermMemory
from .vector_store import VectorStore

logger = structlog.get_logger()

class ContextManager:
    """
    Manages all memory systems and provides unified context.
    
    Coordinates:
    - Short-term (working memory)
    - Long-term (persistent storage)
    - Vector store (semantic search)
    """
    
    def __init__(self):
        print(f"[DEBUG] ContextManager initializing...")
        self.short_term = ShortTermMemory()
        print(f"[DEBUG] ShortTermMemory initialized")
        self.long_term = LongTermMemory()
        print(f"[DEBUG] LongTermMemory initialized")
        self.vector_store = VectorStore()
        print(f"[DEBUG] VectorStore initialized")
        print(f"[DEBUG] ContextManager initialized successfully")
    
    def record_command(
        self,
        command: str,
        output: str,
        success: bool,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record command across all memory systems."""
        print(f"[DEBUG] Recording command across memory systems - Command: {command[:50]}, Success: {success}")
        # Short-term memory
        self.short_term.add(
            content=f"Command: {command}\nOutput: {output[:200]}",
            item_type="command",
            metadata={"success": success, **(metadata or {})},
        )
        
        # Long-term memory
        self.long_term.add_command(command, output, success, metadata)
        
        # Vector store (only successful commands)
        if success:
            print(f"[DEBUG] Adding command to vector store")
            self.vector_store.add_command(command, output, metadata)
        
        logger.info("command_recorded", command=command[:50], success=success)
        print(f"[DEBUG] Command recorded successfully across all memory systems")
    
    def record_task(
        self,
        description: str,
        steps: List[str],
        outcome: str,
        duration_seconds: int,
    ) -> None:
        """Record completed task."""
        print(f"[DEBUG] Recording task - Description: {description[:50]}, Steps: {len(steps)}, Duration: {duration_seconds}s")
        # Short-term
        self.short_term.add(
            content=f"Task: {description}\nOutcome: {outcome}",
            item_type="task",
        )
        
        # Long-term
        self.long_term.add_task(description, steps, outcome, duration_seconds)
        
        # Vector store
        print(f"[DEBUG] Adding task to vector store")
        self.vector_store.add_task(description, steps, outcome)
        
        logger.info("task_recorded", description=description[:50])
        print(f"[DEBUG] Task recorded successfully across all memory systems")
    
    def get_context_for_query(self, query: str) -> Dict[str, Any]:
        """
        Build comprehensive context for a query.
        
        Combines:
        - Recent short-term memory
        - Relevant long-term history
        - Semantically similar past actions
        """
        print(f"[DEBUG] Building context for query: {query[:50]}")
        context = {
            "recent_actions": [],
            "similar_commands": [],
            "similar_tasks": [],
            "current_task": None,
            "summary": "",
        }
        
        # Recent actions from short-term memory
        recent = self.short_term.get_recent(10)
        print(f"[DEBUG] Retrieved {len(recent)} recent actions")
        context["recent_actions"] = [
            {
                "type": item.item_type,
                "content": item.content,
                "timestamp": item.timestamp.isoformat(),
            }
            for item in recent
        ]
        
        # Current task context
        task_ctx = self.short_term.get_task_context()
        if task_ctx:
            print(f"[DEBUG] Found active task: {task_ctx.get('name')}")
            context["current_task"] = task_ctx
        
        # Similar past commands (semantic search)
        similar_cmds = self.vector_store.search_similar_commands(query, n_results=3)
        print(f"[DEBUG] Found {len(similar_cmds)} similar commands")
        context["similar_commands"] = similar_cmds
        
        # Similar past tasks
        similar_tasks = self.vector_store.search_similar_tasks(query, n_results=2)
        print(f"[DEBUG] Found {len(similar_tasks)} similar tasks")
        context["similar_tasks"] = similar_tasks
        
        # Build summary
        context["summary"] = self.short_term.get_context_summary()
        print(f"[DEBUG] Context building completed")
        
        return context
    
    def format_context_for_llm(self, context: Dict[str, Any]) -> str:
        """Format context as prompt for LLM."""
        print(f"[DEBUG] Formatting context for LLM - Context keys: {list(context.keys())}")
        parts = []
        
        # Summary
        if context["summary"]:
            parts.append("=== Session Context ===")
            parts.append(context["summary"])
            parts.append("")
        
        # Current task
        if context["current_task"]:
            parts.append("=== Active Task ===")
            parts.append(f"Task: {context['current_task'].get('name', 'N/A')}")
            parts.append("")
        
        # Similar past commands
        if context["similar_commands"]:
            parts.append("=== Similar Past Commands ===")
            for i, cmd in enumerate(context["similar_commands"], 1):
                parts.append(f"{i}. {cmd['document'][:150]}...")
            parts.append("")
        
        # Similar tasks
        if context["similar_tasks"]:
            parts.append("=== Similar Past Tasks ===")
            for i, task in enumerate(context["similar_tasks"], 1):
                parts.append(f"{i}. {task['document'][:150]}...")
            parts.append("")
        
        result = "\n".join(parts)
        print(f"[DEBUG] Context formatted for LLM - Length: {len(result)} chars")
        return result
    
    def clear_session(self) -> None:
        """Clear short-term memory (start fresh session)."""
        print(f"[DEBUG] Clearing session - Clearing short-term memory")
        self.short_term.clear()
        logger.info("session_cleared")
        print(f"[DEBUG] Session cleared successfully")
