import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import structlog

from config.settings import settings

logger = structlog.get_logger()

class LongTermMemory:
    """
    Persistent memory across sessions.
    
    Stores:
    - Command history
    - Task outcomes
    - User preferences
    - Learned patterns
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or settings.memory.db_path
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize SQLite database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Command history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS command_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command TEXT NOT NULL,
                    output TEXT,
                    success BOOLEAN,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """)
            
            # Task history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS task_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_description TEXT NOT NULL,
                    steps TEXT,
                    outcome TEXT,
                    duration_seconds INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # User preferences
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Learning patterns
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learned_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_type TEXT NOT NULL,
                    pattern_data TEXT NOT NULL,
                    confidence REAL,
                    usage_count INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def add_command(
        self,
        command: str,
        output: str,
        success: bool,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record command execution."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO command_history (command, output, success, metadata)
                VALUES (?, ?, ?, ?)
                """,
                (command, output, success, json.dumps(metadata or {}))
            )
            conn.commit()
    
    def get_command_history(
        self,
        limit: int = 100,
        success_only: bool = False,
    ) -> List[Dict[str, Any]]:
        """Retrieve command history."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM command_history"
            if success_only:
                query += " WHERE success = 1"
            query += " ORDER BY timestamp DESC LIMIT ?"
            
            cursor.execute(query, (limit,))
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def add_task(
        self,
        description: str,
        steps: List[str],
        outcome: str,
        duration_seconds: int,
    ) -> None:
        """Record completed task."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO task_history (task_description, steps, outcome, duration_seconds)
                VALUES (?, ?, ?, ?)
                """,
                (description, json.dumps(steps), outcome, duration_seconds)
            )
            conn.commit()
    
    def get_similar_tasks(self, description: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find similar past tasks (simple keyword matching)."""
        keywords = set(description.lower().split())
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM task_history ORDER BY timestamp DESC LIMIT 100")
            
            columns = [desc[0] for desc in cursor.description]
            all_tasks = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # Simple relevance scoring
            scored_tasks = []
            for task in all_tasks:
                task_keywords = set(task["task_description"].lower().split())
                overlap = len(keywords & task_keywords)
                if overlap > 0:
                    scored_tasks.append((overlap, task))
            
            scored_tasks.sort(reverse=True, key=lambda x: x[0])
            return [task for _, task in scored_tasks[:limit]]
    
    def set_preference(self, key: str, value: Any) -> None:
        """Store user preference."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO preferences (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                """,
                (key, json.dumps(value))
            )
            conn.commit()
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Retrieve user preference."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM preferences WHERE key = ?", (key,))
            result = cursor.fetchone()
            
            if result:
                return json.loads(result[0])
            return default
    
    def cleanup_old_data(self, days: int = 30) -> None:
        """Remove data older than specified days."""
        cutoff = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM command_history WHERE timestamp < ?",
                (cutoff.isoformat(),)
            )
            cursor.execute(
                "DELETE FROM task_history WHERE timestamp < ?",
                (cutoff.isoformat(),)
            )
            conn.commit()
            
        logger.info("old_data_cleaned", cutoff_date=cutoff.isoformat())
