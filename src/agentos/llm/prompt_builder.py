from typing import List, Dict, Any

class PromptBuilder:
    """Build prompts with context and formatting."""
    
    @staticmethod
    def build_system_prompt(capabilities: List[str]) -> str:
        """Build system prompt with capabilities list."""
        return f"""You are AgentOS, an intelligent computer automation assistant.

CAPABILITIES:
{chr(10).join(f'- {cap}' for cap in capabilities)}

GUIDELINES:
1. Always explain what you're about to do
2. Use the most appropriate tool for each task
3. Handle errors gracefully
4. Remember context from previous interactions
5. Ask for confirmation for destructive operations

SAFETY:
- Validate all inputs
- Avoid dangerous commands
- Check safety before execution
"""
    
    @staticmethod
    def format_context(context: Dict[str, Any]) -> str:
        """Format context dictionary as readable text."""
        parts = []
        
        if context.get("recent_actions"):
            parts.append("=== Recent Actions ===")
            for action in context["recent_actions"][-5:]:
                parts.append(f"- {action['content'][:100]}")
        
        if context.get("current_task"):
            parts.append(f"\n=== Current Task ===")
            parts.append(context["current_task"].get("name", "N/A"))
        
        return "\n".join(parts)
