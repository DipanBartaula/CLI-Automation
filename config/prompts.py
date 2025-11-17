import yaml
from pathlib import Path
from typing import Dict, Any

def load_prompts() -> Dict[str, Any]:
    """Load prompts from YAML file."""
    prompts_path = Path(__file__).parent / "prompts.yaml"
    
    if prompts_path.exists():
        with open(prompts_path, 'r') as f:
            return yaml.safe_load(f)
    
    # Return default prompts if file doesn't exist
    return {
        "system_prompts": {
            "main": """You are AgentOS, an intelligent computer automation assistant."""
        }
    }
