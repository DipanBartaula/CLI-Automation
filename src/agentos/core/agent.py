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
        print(f"[DEBUG] AgentOS initializing...")
        # LLM client
        print(f"[DEBUG] Initializing LLM client...")
        self.llm = AzureOpenAIClient()
        print(f"[DEBUG] LLM client initialized")
        
        # Memory system
        print(f"[DEBUG] Initializing memory system...")
        self.context_manager = ContextManager()
        print(f"[DEBUG] Memory system initialized")
        
        # Tools
        print(f"[DEBUG] Initializing tools...")
        self.shell = ShellExecutor()
        self.file_manager = FileManager()
        self.app_launcher = AppLauncher()
        self.system_monitor = SystemMonitor()
        print(f"[DEBUG] All tools initialized")
        
        # Tool registry
        self.tools = self._register_tools()
        
        # System prompt
        self.system_prompt = self._load_system_prompt()
        print(f"[DEBUG] AgentOS initialized successfully")
    
    def _register_tools(self) -> List[Dict[str, Any]]:
        """Register all available tools."""
        print(f"[DEBUG] Registering tools...")
        tools = []
        
        # Shell executor
        shell_tools = self.shell.get_tool_definition()
        tools.append(shell_tools)
        print(f"[DEBUG] Shell executor tool registered")
        
        # File manager
        file_tools = self.file_manager.get_tool_definitions()
        tools.extend(file_tools)
        print(f"[DEBUG] File manager tools registered - Count: {len(file_tools)}")
        
        # App launcher
        app_tools = self.app_launcher.get_tool_definitions()
        tools.extend(app_tools)
        print(f"[DEBUG] App launcher tools registered - Count: {len(app_tools)}")
        
        # System monitor
        monitor_tools = self.system_monitor.get_tool_definitions()
        tools.extend(monitor_tools)
        print(f"[DEBUG] System monitor tools registered - Count: {len(monitor_tools)}")
        
        logger.info("tools_registered", count=len(tools))
        print(f"[DEBUG] Tools registration completed - Total tools: {len(tools)}")
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
        print(f"[DEBUG] Processing request - Input: {user_input[:80]}")
        logger.info("processing_request", input=user_input[:100])
        
        # Step 1: Build context
        print(f"[DEBUG] Step 1: Building context from memory...")
        context = self.context_manager.get_context_for_query(user_input)
        context_str = self.context_manager.format_context_for_llm(context)
        print(f"[DEBUG] Context built - Length: {len(context_str)} chars")
        
        # Step 2: Call LLM with tools
        print(f"[DEBUG] Step 2: Calling LLM with {len(self.tools)} available tools...")
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"{context_str}\n\nUser Request: {user_input}"},
        ]
        
        response = self.llm.generate(messages=messages, tools=self.tools)
        print(f"[DEBUG] LLM response received")
        
        # Step 3: Handle tool calls
        if "tool_calls" in response:
            print(f"[DEBUG] Tool calls detected - Count: {len(response['tool_calls'])}")
            return await self._handle_tool_execution(
                user_input,
                response["tool_calls"],
                messages,
            )
        
        # Step 4: Direct response (no tools needed)
        print(f"[DEBUG] Direct response from LLM (no tool calls)")
        return response["content"]
    
    async def _handle_tool_execution(
        self,
        original_request: str,
        tool_calls: List[Dict[str, Any]],
        messages: List[Dict[str, str]],
    ) -> str:
        """Execute tools and get final response."""
        print(f"[DEBUG] Handling tool execution - Tool calls: {len(tool_calls)}")
        # Execute all tool calls
        tool_results = []
        
        for i, tool_call in enumerate(tool_calls):
            tool_name = tool_call["name"]
            arguments = tool_call["arguments"]
            
            print(f"[DEBUG] Executing tool {i+1}/{len(tool_calls)} - Tool: {tool_name}, Args: {arguments}")
            logger.info("executing_tool", tool=tool_name, args=arguments)
            
            # Route to appropriate tool
            result = self._execute_tool(tool_name, arguments)
            print(f"[DEBUG] Tool execution completed - Result success: {result.get('success', False)}")
            
            tool_results.append({
                "tool": tool_name,
                "result": result,
            })
            
            # Record in memory
            print(f"[DEBUG] Recording command in memory...")
            self.context_manager.record_command(
                command=f"{tool_name}({json.dumps(arguments)})",
                output=json.dumps(result)[:500],
                success=result.get("success", False),
                metadata={"tool": tool_name},
            )
        
        # Add tool calls to messages
        print(f"[DEBUG] Adding tool calls to message history...")
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
        print(f"[DEBUG] Getting final response from LLM...")
        final_response = self.llm.generate(messages=messages, tools=self.tools)
        print(f"[DEBUG] Final response received")
        
        return final_response["content"]
    
    def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Route tool execution to appropriate handler."""
        print(f"[DEBUG] Routing tool execution - Tool: {tool_name}")
        try:
            # Shell commands
            if tool_name == "execute_shell_command":
                print(f"[DEBUG] Executing shell command...")
                return self.shell.execute(
                    command=arguments["command"],
                    cwd=arguments.get("working_directory"),
                )
            
            # File operations
            elif tool_name == "read_file":
                print(f"[DEBUG] Reading file - Path: {arguments['path']}")
                return self.file_manager.read_file(arguments["path"])
            
            elif tool_name == "write_file":
                print(f"[DEBUG] Writing file - Path: {arguments['path']}")
                return self.file_manager.write_file(
                    path=arguments["path"],
                    content=arguments["content"],
                )
            
            elif tool_name == "list_directory":
                print(f"[DEBUG] Listing directory - Path: {arguments.get('path', '.')}")
                return self.file_manager.list_directory(
                    arguments.get("path", ".")
                )
            
            elif tool_name == "search_files":
                print(f"[DEBUG] Searching files - Pattern: {arguments['pattern']}")
                return self.file_manager.search_files(
                    directory=arguments["directory"],
                    pattern=arguments["pattern"],
                    recursive=arguments.get("recursive", True),
                )
            
            # Application control
            elif tool_name == "open_application":
                print(f"[DEBUG] Opening application - App: {arguments['app_name']}")
                return self.app_launcher.open_application(
                    app_name=arguments["app_name"],
                    args=arguments.get("args"),
                )
            
            elif tool_name == "open_url":
                print(f"[DEBUG] Opening URL - URL: {arguments['url']}")
                return self.app_launcher.open_url(arguments["url"])
            
            elif tool_name == "open_file":
                print(f"[DEBUG] Opening file - Path: {arguments['file_path']}")
                return self.app_launcher.open_file(arguments["file_path"])
            
            # System monitoring
            elif tool_name == "get_system_info":
                print(f"[DEBUG] Getting system info...")
                return self.system_monitor.get_system_info()
            
            elif tool_name == "get_cpu_info":
                print(f"[DEBUG] Getting CPU info...")
                return self.system_monitor.get_cpu_info()
            
            elif tool_name == "get_memory_info":
                print(f"[DEBUG] Getting memory info...")
                return self.system_monitor.get_memory_info()
            
            elif tool_name == "get_disk_info":
                print(f"[DEBUG] Getting disk info...")
                return self.system_monitor.get_disk_info()
            
            elif tool_name == "list_processes":
                print(f"[DEBUG] Listing processes...")
                return self.system_monitor.list_processes(
                    limit=arguments.get("limit", 10)
                )
            
            else:
                print(f"[DEBUG ERROR] Unknown tool - Tool: {tool_name}")
                return {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}",
                }
                
        except Exception as e:
            logger.error("tool_execution_failed", tool=tool_name, error=str(e))
            print(f"[DEBUG ERROR] Tool execution failed - Tool: {tool_name}, Error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
            }
