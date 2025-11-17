import json
from typing import Any, Dict, List, Optional
from openai import AzureOpenAI
import structlog

from config.settings import settings

logger = structlog.get_logger()

class AzureOpenAIClient:
    """Azure OpenAI client with function calling."""
    
    def __init__(self):
        self.client = AzureOpenAI(
            azure_endpoint=settings.azure_openai.endpoint,
            api_key=settings.azure_openai.api_key,
            api_version=settings.azure_openai.api_version,
        )
        self.deployment = settings.azure_openai.deployment
        self.temperature = settings.azure_openai.temperature
        self.max_tokens = settings.azure_openai.max_tokens
    
    def generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Generate completion with optional tools."""
        try:
            params = {
                "model": self.deployment,
                "messages": messages,
                "temperature": temperature or self.temperature,
                "max_tokens": self.max_tokens,
            }
            
            if tools:
                params["tools"] = tools
                params["tool_choice"] = "auto"
            
            response = self.client.chat.completions.create(**params)
            message = response.choices[0].message
            
            result = {
                "content": message.content,
                "role": message.role,
                "finish_reason": response.choices[0].finish_reason,
            }
            
            if hasattr(message, "tool_calls") and message.tool_calls:
                result["tool_calls"] = [
                    {
                        "id": call.id,
                        "name": call.function.name,
                        "arguments": json.loads(call.function.arguments),
                    }
                    for call in message.tool_calls
                ]
            
            logger.info("llm_generation_success", finish_reason=result["finish_reason"])
            return result
            
        except Exception as e:
            logger.error("llm_generation_failed", error=str(e))
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embeddings for text."""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=text,
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error("embedding_failed", error=str(e))
            raise
