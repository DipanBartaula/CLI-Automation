import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional
import structlog

from config.settings import settings

logger = structlog.get_logger()

class VectorStore:
    """
    Vector database for semantic memory retrieval.
    
    Uses ChromaDB for embedding storage and similarity search.
    """
    
    def __init__(self):
        print(f"[DEBUG] VectorStore initializing - Path: {settings.memory.vector_db_path}")
        self.client = chromadb.PersistentClient(
            path=str(settings.memory.vector_db_path),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        print(f"[DEBUG] ChromaDB client created")
        
        # Create collections
        self.commands_collection = self.client.get_or_create_collection(
            name="commands",
            metadata={"description": "Command execution history"},
        )
        print(f"[DEBUG] Commands collection initialized")
        
        self.tasks_collection = self.client.get_or_create_collection(
            name="tasks",
            metadata={"description": "Task completion history"},
        )
        print(f"[DEBUG] Tasks collection initialized")
        print(f"[DEBUG] VectorStore initialized successfully")
    
    def add_command(
        self,
        command: str,
        output: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add command to vector store."""
        print(f"[DEBUG] Adding command to vector store - Command: {command[:50]}")
        try:
            doc_id = f"cmd_{len(self.commands_collection.get()['ids'])}"
            print(f"[DEBUG] Generated doc_id: {doc_id}")
            
            self.commands_collection.add(
                documents=[f"{command}\n{output}"],
                metadatas=[metadata or {}],
                ids=[doc_id],
            )
            print(f"[DEBUG] Command added successfully to vector store")
        except Exception as e:
            logger.error("vector_add_failed", error=str(e))
            print(f"[DEBUG ERROR] Failed to add command to vector store: {str(e)}")
    
    def search_similar_commands(
        self,
        query: str,
        n_results: int = 5,
    ) -> List[Dict[str, Any]]:
        """Find semantically similar past commands."""
        print(f"[DEBUG] Searching for similar commands - Query: {query[:50]}, n_results: {n_results}")
        try:
            results = self.commands_collection.query(
                query_texts=[query],
                n_results=n_results,
            )
            
            if not results["ids"] or not results["ids"][0]:
                print(f"[DEBUG] No similar commands found")
                return []
            
            similar = [
                {
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                }
                for i in range(len(results["ids"][0]))
            ]
            print(f"[DEBUG] Found {len(similar)} similar commands")
            return similar
        except Exception as e:
            logger.error("vector_search_failed", error=str(e))
            print(f"[DEBUG ERROR] Failed to search similar commands: {str(e)}")
            return []
    
    def add_task(
        self,
        description: str,
        steps: List[str],
        outcome: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add task to vector store."""
        print(f"[DEBUG] Adding task to vector store - Description: {description[:50]}, Steps: {len(steps)}")
        try:
            doc_id = f"task_{len(self.tasks_collection.get()['ids'])}"
            print(f"[DEBUG] Generated doc_id: {doc_id}")
            
            task_doc = f"{description}\nSteps: {'; '.join(steps)}\nOutcome: {outcome}"
            
            self.tasks_collection.add(
                documents=[task_doc],
                metadatas=[metadata or {}],
                ids=[doc_id],
            )
            print(f"[DEBUG] Task added successfully to vector store")
        except Exception as e:
            logger.error("vector_add_task_failed", error=str(e))
            print(f"[DEBUG ERROR] Failed to add task to vector store: {str(e)}")
    
    def search_similar_tasks(
        self,
        query: str,
        n_results: int = 3,
    ) -> List[Dict[str, Any]]:
        """Find semantically similar past tasks."""
        print(f"[DEBUG] Searching for similar tasks - Query: {query[:50]}, n_results: {n_results}")
        try:
            results = self.tasks_collection.query(
                query_texts=[query],
                n_results=n_results,
            )
            
            if not results["ids"] or not results["ids"][0]:
                print(f"[DEBUG] No similar tasks found")
                return []
            
            similar = [
                {
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                }
                for i in range(len(results["ids"][0]))
            ]
            print(f"[DEBUG] Found {len(similar)} similar tasks")
            return similar
        except Exception as e:
            logger.error("vector_search_tasks_failed", error=str(e))
            print(f"[DEBUG ERROR] Failed to search similar tasks: {str(e)}")
            return []
