import os
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class AzureOpenAIConfig(BaseModel):
    """Azure OpenAI configuration."""
    endpoint: str
    api_key: str
    api_version: str
    deployment: str
    temperature: float = 0.7
    max_tokens: int = 4096

class MemoryConfig(BaseModel):
    """Memory system configuration."""
    db_path: Path
    vector_db_path: Path
    short_term_capacity: int = 50
    long_term_retention_days: int = 30
    embedding_model: str = "all-MiniLM-L6-v2"

class SafetyConfig(BaseModel):
    """Safety and validation configuration."""
    enable_checks: bool = True
    dangerous_commands: List[str]
    max_retries: int = 3
    require_confirmation: bool = True
    sandbox_mode: bool = False

class Settings:
    """Global settings manager."""
    
    def __init__(self):
        self.azure_openai = AzureOpenAIConfig(
            endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        )
        
        self.memory = MemoryConfig(
            db_path=Path(os.getenv("MEMORY_DB_PATH", "./data/memory/agentos.db")),
            vector_db_path=Path(os.getenv("VECTOR_DB_PATH", "./data/memory/embeddings")),
        )
        
        self.safety = SafetyConfig(
            enable_checks=os.getenv("ENABLE_SAFETY_CHECKS", "true").lower() == "true",
            dangerous_commands=os.getenv("DANGEROUS_COMMANDS", "").split(","),
        )
        
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_path = Path(os.getenv("LOG_PATH", "./data/logs/agentos.log"))
        
        # Create necessary directories
        self._setup_directories()
    
    def _setup_directories(self):
        """Create required directories."""
        self.memory.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.memory.vector_db_path.mkdir(parents=True, exist_ok=True)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

settings = Settings()
