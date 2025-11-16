import json
from typing import Dict, Any, List, Optional
import structlog

from ..llm.azure_client import AzureOpenAIClient
from ..memory.context_manager import ContextManager
from ..tools.shell_executor import ShellExecutor
from ..tools.file_manager import FileManager
from ..tools.app_launcher import AppLauncher
from ..tools.system_monitor import SystemMonitor
from config.prompts import load_prompts

logger = structlog.get_logger()

class AgentOS:
    """
    Main agentic system for computer automation.
    
    Capabilities:
    - Natural language command interpretation
    - Tool-based execution
    - Memory-augmented reasoning
    - Safety checks
    """
    
    def __init__(self):
        # LLM client
        self.llm = AzureOpenAIClient()
        
        # Memory system
        self.context_manager = ContextManager()
        
        # Tools
        self.shell = ShellExecutor()
        self.file_manager = FileManager()
        self.app_launcher = AppLauncher()
        self.system_monitor = SystemMonitor()
        
        # Tool registry
        self.tools = self._register_tools()
        
        # System prompt
        self.system_prompt = self._load_system_prompt()
    
    def _register_tools(self) -> List[Dict[str, Any]]:
        """Register all available tools."""
        tools = []
        
        # Shell executor
        tools.append(self.shell.get_tool_definition())
        
        # File manager
        tools.extend(self.file_manager.get_tool_definitions())
        
        # App launcher
        tools.extend(self.app_launcher.get_tool_definitions())
        
        # System monitor
        tools.extend(self.system_monitor.get_tool_definitions())
        
        logger.info("tools_registered", count=len(tools))
        return tools
    
    def _load_system_prompt(self) -> str:
        """Load system prompt from config."""
        # For now, inline prompt
        return """You are AgentOS, an intelligent computer automation assistant.

You can control the user's computer through various tools:
- execute_shell_command: Run shell commands
- read_file/write_file: File operations
- list_directory/search_files: Navigate filesystem
- open_application/open_url: Launch apps and websites
- get_system_info/get_cpu_info: Monitor system

GUIDELINES:
1. Always explain what you're about to do
2. Use the most appropriate tool for each task
3. Handle errors gracefully
4. Remember context from previous commands
5. Ask for confirmation for destructive operations

SAFETY:
- Validate all file paths
- Avoid dangerous commands
- Check command safety before execution"""
    
    async def process_request(self, user_input: str) -> str:
        """
        Process user request and execute actions.
        
        Flow:
        1. Get context from memory
        2. Plan actions with LLM
        3. Execute tools
        4. Update memory
        5. Return response
        """
        logger.info("processing_request", input=user_input[:100])
        
        # Step 1: Build context
        context = self.context_manager.get_context_for_query(user_input)
        context_str = self.context_manager.format_context_for_llm(context)
        
        # Step 2: Call LLM with tools
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"{context_str}\n\nUser Request: {user_input}"},
        ]
        
        response = self.llm.generate(messages=messages, tools=self.tools)
        
        # Step 3: Handle tool calls
        if "tool_calls" in response:
            return await self._handle_tool_execution(
                user_input,
                response["tool_calls"],
                messages,
            )
        
        # Step 4: Direct response (no tools needed)
        return response["content"]
    
    async def _handle_tool_execution(
        self,
        original_request: str,
        tool_calls: List[Dict[str, Any]],
        messages: List[Dict[str, str]],
    ) -> str:
        """Execute tools and get final response."""
        # Execute all tool calls
        tool_results = []
        
        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            arguments = tool_call["arguments"]
            
            logger.info("executing_tool", tool=tool_name, args=arguments)
            
            # Route to appropriate tool
            result = self._execute_tool(tool_name, arguments)
            
            tool_results.append({
                "tool": tool_name,
                "result": result,
            })
            
            # Record in memory
            self.context_manager.record_command(
                command=f"{tool_name}({json.dumps(arguments)})",
                output=json.dumps(result)[:500],
                success=result.get("success", False),
                metadata={"tool": tool_name},
            )
        
        # Add tool calls to messages
        messages.append({
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": call["id"],
                    "type": "function",
                    "function": {
                        "name": call["name"],
                        "arguments": json.dumps(call["arguments"]),
                    },
                }
                for call in tool_calls
            ],
        })
        
        # Add tool results
        for call, result in zip(tool_calls, tool_results):
            messages.append({
                "role": "tool",
                "tool_call_id": call["id"],
                "content": json.dumps(result["result"]),
            })
        
        # Get final response from LLM
        final_response = self.llm.generate(messages=messages, tools=self.tools)
        
        return final_response["content"]
    
    def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Route tool execution to appropriate handler."""
        try:
            # Shell commands
            if tool_name == "execute_shell_command":
                return self.shell.execute(
                    command=arguments["command"],
                    cwd=arguments.get("working_directory"),
                )
            
            # File operations
            elif tool_name == "read_file":
                return self.file_manager.read_file(arguments["path"])
            
            elif tool_name == "write_file":
                return self.file_manager.write_file(
                    path=arguments["path"],
                    content=arguments["content"],
                )
            
            elif tool_name == "list_directory":
                return self.file_manager.list_directory(
                    arguments.get("path", ".")
                )
            
            elif tool_name == "search_files":
                return self.file_manager.search_files(
                    directory=arguments["directory"],
                    pattern=arguments["pattern"],
                    recursive=arguments.get("recursive", True),
                )
            
            # Application control
            elif tool_name == "open_application":
                return self.app_launcher.open_application(
                    app_name=arguments["app_name"],
                    args=arguments.get("args"),
                )
            
            elif tool_name == "open_url":
                return self.app_launcher.open_url(arguments["url"])
            
            elif tool_name == "open_file":
                return self.app_launcher.open_file(arguments["file_path"])
            
            # System monitoring
            elif tool_name == "get_system_info":
                return self.system_monitor.get_system_info()
            
            elif tool_name == "get_cpu_info":
                return self.system_monitor.get_cpu_info()
            
            elif tool_name == "get_memory_info":
                return self.system_monitor.get_memory_info()
            
            elif tool_name == "get_disk_info":
                return self.system_monitor.get_disk_info()
            
            elif tool_name == "list_processes":
                return self.system_monitor.list_processes(
                    limit=arguments.get("limit", 10)
                )
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}",
                }
                
        except Exception as e:
            logger.error("tool_execution_failed", tool=tool_name, error=str(e))
            return {
                "success": False,
                "error": str(e),
            }
