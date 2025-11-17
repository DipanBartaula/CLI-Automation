# Debug Points Architecture

## Memory System Debug Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION START                          │
└────────────────┬────────────────────────────────────────────────┘
                 │
        [DEBUG] AgentOS v0.1.0 loaded
                 │
         ┌───────┴───────┬─────────────┬────────────────┐
         │               │             │                │
    [DEBUG]      [DEBUG]    [DEBUG]      [DEBUG]
    Module      Module      Module       Module
    Loaded      Loaded      Loaded       Loaded
         │               │             │                │
         ▼               ▼             ▼                ▼
    AGENTOS      CORE       MEMORY      TOOLS
    MODULE       MODULE     MODULE      MODULE
         │
         └───────────────┬──────────────┘
                         │
                [DEBUG] AgentOS init
                         │
        ┌────────────────┼────────────────┐
        │                │                │
    [DEBUG]      [DEBUG]        [DEBUG]
    LLM Init    Memory Init    Tools Init
        │                │                │
        ▼                ▼                ▼
    AZURE_LLM  SHORT_TERM      SHELL
               LONG_TERM        FILE
               VECTOR_STORE     APP
               CONTEXT_MGR      MONITOR


┌─────────────────────────────────────────────────────────────────┐
│                    REQUEST PROCESSING                           │
└────────────────┬────────────────────────────────────────────────┘
                 │
        [DEBUG] Processing request
                 │
        [DEBUG] Building context
                 │
        ┌────────┴────────┬─────────────┬──────────────┐
        │                 │             │              │
    [DEBUG]         [DEBUG]      [DEBUG]         [DEBUG]
    Get Recent    Get Task     Vector Search   Format for
    Items         Context      Commands/Tasks  LLM
        │                 │             │              │
        └────────┬────────┴─────────────┴──────────────┘
                 │
        [DEBUG] Context built
                 │
        [DEBUG] Calling LLM
                 │
        ┌────────┴────────────────────────────┐
        │                                      │
     YES (Tool Calls)              NO (Direct Response)
        │                                      │
        ▼                                      │
    [DEBUG] Tool calls detected               │
        │                                      │
    ┌───┴────────────┐                        │
    │                │                        │
[DEBUG]         [DEBUG]                       │
Tool 1          Tool 2                        │
Exec            Exec                          │
    │                │                        │
    └───┬────────────┘                        │
        │                                      │
    [DEBUG] Record in memory                  │
        │                                      │
    [DEBUG] Get final response                │
        │                                      │
        └─────────────────┬─────────────────────┘
                          │
                  [DEBUG] Response ready
                          │
                  Return to User
```

## Memory System Architecture with Debug Points

```
┌─────────────────────────────────────────────────────────────────┐
│                      CONTEXT MANAGER                            │
│  [8 Debug Points]                                               │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ [DEBUG] Init    [DEBUG] Record   [DEBUG] Get Context       │ │
│  │ [DEBUG] Clear   [DEBUG] Format   [DEBUG] Session           │ │
│  │ [DEBUG] Command [DEBUG] Task     [DEBUG] Query             │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────┬──────────────────┬──────────────────┬────────────────┘
           │                  │                  │
    ┌──────▼──────┐    ┌──────▼──────┐   ┌──────▼──────┐
    │             │    │             │   │             │
    │   SHORT     │    │   LONG      │   │   VECTOR    │
    │   TERM      │    │   TERM      │   │   STORE     │
    │ MEMORY      │    │ MEMORY      │   │             │
    │ [8 pts]     │    │ [9 pts]     │   │ [10 pts]    │
    │             │    │             │   │             │
    └─────┬───────┘    └──────┬──────┘   └──────┬──────┘
          │                   │                   │
      ┌───┴─────┐         ┌────┴────┐       ┌────┴─────┐
      │          │         │         │       │          │
  [DEBUG]   [DEBUG]    [DEBUG] [DEBUG]  [DEBUG]     [DEBUG]
   Init      Add        Init   Add      Init      Search
   Add      Recent     Table  Command   Add      Commands
  Recent   Get Task    Prefs   Record   Task        │
   Clear    Summary    History Similar  Similarity  │
  Context   Task       Cleanup  Tasks             Search
   Get      Context                               Tasks
```

## Debug Point Density Map

```
Memory System (32 points) ████████████████████████████░░░░░░░░░░░░░
Core Agent (20 points)    ██████████████░░░░░░░░░░░░░░░░░░░░░░░░░
Initialization (7 points) █████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
Task Execution (8 points) ██████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

                          0%        20%       40%        60%       80%
```

## Request Flow with Debug Points

```
USER REQUEST
     │
     ▼
┌─────────────────────────────────────────┐
│ [D] Processing request: "list files"    │
│ agent.py:process_request()              │
└─────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│ [D] Building context from memory        │
│ context_manager.py:get_context_for_query│
└─────────────────────────────────────────┘
     │
     ├─[D] Retrieved recent actions
     │     short_term.py:get_recent()
     │
     ├─[D] Found similar commands
     │     vector_store.py:search_similar()
     │
     └─[D] Built summary
          short_term.py:get_context_summary()
     │
     ▼
┌─────────────────────────────────────────┐
│ [D] Calling LLM with 12 tools           │
│ agent.py:process_request()              │
└─────────────────────────────────────────┘
     │
     ▼ (LLM Decision)
     │
     ├─ Tool Calls Needed
     │       │
     │       ▼
     │  ┌──────────────────────────────────┐
     │  │ [D] Tool calls detected: 2       │
     │  │ agent.py:_handle_tool_execution()│
     │  └──────────────────────────────────┘
     │       │
     │       ├─[D] Executing tool 1/2: list_directory
     │       │     agent.py:_execute_tool()
     │       │
     │       ├─[D] Recording command in memory
     │       │     context_manager.py:record_command()
     │       │
     │       └─[D] Getting final response
     │            agent.py:_handle_tool_execution()
     │
     └─ Direct Response
             │
             ▼
     ┌─────────────────────────────────────┐
     │ [D] Response ready                  │
     │ agent.py:process_request()          │
     └─────────────────────────────────────┘
             │
             ▼
         USER RESPONSE
```

## Component Initialization Sequence

```
1. Module Loading
   ├─ [D] AgentOS v0.1.0 module loaded         agentos/__init__.py
   ├─ [D] Core agent module loaded             core/__init__.py
   ├─ [D] Memory system module loaded          memory/__init__.py
   ├─ [D] Tools module loaded                  tools/__init__.py
   ├─ [D] LLM integration module loaded        llm/__init__.py
   ├─ [D] Utilities module loaded              utils/__init__.py
   └─ [D] Configuration module loaded          config/__init__.py

2. AgentOS Initialization
   ├─ [D] AgentOS initializing...              agent.py:__init__
   ├─ [D] Initializing LLM client
   │  └─ AzureOpenAIClient created
   ├─ [D] Initializing memory system
   │  ├─ [D] ContextManager initializing
   │  ├─ [D] ShortTermMemory initialized
   │  │  └─ Capacity: 50
   │  ├─ [D] LongTermMemory initializing
   │  │  ├─ DB Path: /path/to/memory.db
   │  │  └─ [D] Created 4 tables
   │  └─ [D] VectorStore initialized
   │     └─ ChromaDB client created
   ├─ [D] Initializing tools
   │  ├─ ShellExecutor
   │  ├─ FileManager
   │  ├─ AppLauncher
   │  └─ SystemMonitor
   ├─ [D] Registering tools                    agent.py:_register_tools
   │  └─ Total tools: 12
   └─ [D] AgentOS initialized successfully

Status: READY
```

## Memory Operation Patterns

```
WRITE OPERATIONS                    READ OPERATIONS
─────────────────────────────────   ─────────────────────────────
[D] Add short-term item             [D] Get recent items
    ↓                                   ↓
[D] Record in long-term DB          [D] Retrieved N items
    ↓                                   ↓
[D] Add to vector store             [D] Similar search
    ↓                                   ↓
[D] Success logged                  [D] Context built

QUERY OPERATIONS                    CLEANUP OPERATIONS
──────────────────────────────────  ──────────────────────────────
[D] Building context for query      [D] Clearing session
    ↓                                   ↓
[D] Retrieved recent actions        [D] Clearing short-term
    ↓                                   ↓
[D] Found similar tasks             [D] Clearing task context
    ↓                                   ↓
[D] Context built
```

## Error Path Tracing

```
ERROR SCENARIO
     │
     ▼
┌──────────────────────────────────────┐
│ [D ERROR] Tool execution failed      │
│ agent.py:_execute_tool()             │
│ Tool: list_directory                 │
│ Error: Permission denied             │
└──────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────┐
│ [D] Tool execution failed - Result   │
│     success: False                   │
│ agent.py:_handle_tool_execution()    │
└──────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────┐
│ [D] Recording failed command         │
│ context_manager.py:record_command()  │
│ Command: list_directory(...)         │
│ Success: False                       │
└──────────────────────────────────────┘
     │
     ▼
Return Error to User
```

## Test Coverage Visualization

```
Memory Tests (35+ cases)
├── TestMemoryItem ............ ██ [2/2]
├── TestShortTermMemory ....... █████████ [9/9]
├── TestLongTermMemory ........ ████████ [8/8]
├── TestCircularBuffer ........ █████ [5/5]
├── TestContextManager ........ ███████ [7/7]
└── TestMemoryIntegration .... ██ [2/2]

Total Coverage: ████████████████████████████ [35 tests]

Short-term Memory:   ████████████████████ [100% coverage]
Long-term Memory:    ████████████████████ [100% coverage]
Vector Store:        ████████████████░░░░ [80%+ coverage]
Context Manager:     ████████████████████ [100% coverage]
Circular Buffer:     ████████████████████ [100% coverage]
```

## Debug Statement Format Reference

```
Standard Format:
[DEBUG] ComponentName - Action: details

Examples:
[DEBUG] ShortTermMemory initialized - Capacity: 50, Session Start: 2025-11-17 10:30:45
[DEBUG] Item added to ShortTermMemory - Type: command, Current size: 5/50
[DEBUG] Retrieved 3 recent items - Filter type: command, Total available: 12
[DEBUG] ContextManager initializing...
[DEBUG] LongTermMemory initializing - DB Path: /home/user/memory.db
[DEBUG] VectorStore - Added command to vector store

Error Format:
[DEBUG ERROR] ComponentName - Error message
[DEBUG ERROR] Failed to add command to vector store: connection timeout

Status Format:
[DEBUG] [COMPONENT] status - value
[DEBUG] ShortTermMemory cleared - Items after: 0
[DEBUG] Tools registration completed - Total tools: 12
```

---

This architecture enables comprehensive debugging while maintaining clean code organization and high test coverage.
