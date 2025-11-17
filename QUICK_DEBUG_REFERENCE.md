# Quick Debug Reference Guide

## Debug Print Locations

### Memory System
| File | Component | Debug Points | Purpose |
|------|-----------|--------------|---------|
| `short_term.py` | ShortTermMemory | 8 | Working memory operations |
| `long_term.py` | LongTermMemory | 9 | Persistent memory & DB ops |
| `context_manager.py` | ContextManager | 8 | Memory coordination |
| `vector_store.py` | VectorStore | 10 | Semantic search operations |
| `buffer.py` | CircularBuffer | 5 | Buffer management |

### Core Agent
| File | Component | Debug Points | Purpose |
|------|-----------|--------------|---------|
| `agent.py` | AgentOS | 12 | Main agent operations |
| `executor.py` | TaskExecutor | 8 | Task execution flow |

### Module Initialization
| File | Component | Status |
|------|-----------|--------|
| `__init__.py` (all modules) | Module loading | Added debug prints |

## Most Useful Debug Points for Troubleshooting

### For Memory Issues
1. **Check short-term memory**: `short_term.py:add()` - shows memory accumulation
2. **Verify database**: `long_term.py:_init_database()` - shows table creation
3. **Track context building**: `context_manager.py:get_context_for_query()` - shows memory retrieval

### For Tool Execution
1. **Monitor agent flow**: `agent.py:process_request()` - shows request routing
2. **Track tool execution**: `agent.py:_execute_tool()` - shows each tool call
3. **Check task execution**: `executor.py:execute_task()` - shows step-by-step progress

### For Integration Issues
1. **Module loading**: Module `__init__.py` files - shows initialization order
2. **Component initialization**: `agent.py:__init__()` - shows component setup sequence
3. **Context manager setup**: `context_manager.py:__init__()` - shows memory system init

## Common Debug Patterns

### Looking for Memory Leaks
```
Watch: short_term.py - "Current size: X/50"
Watch: buffer.py - "Items before clear"
```

### Tracking Tool Calls
```
1. agent.py:process_request() - "Tool calls detected"
2. agent.py:_execute_tool() - "Routing tool execution"
3. agent.py:_handle_tool_execution() - "Tool execution completed"
```

### Monitoring Database Operations
```
1. long_term.py:__init__() - "Initializing database"
2. long_term.py:add_command() - "Recording command"
3. long_term.py:get_command_history() - "Retrieved X entries"
```

## Running with Debug Output

### Terminal 1: Start application with debug
```bash
python -m agentos.cli  # Debug prints will show in console
```

### Terminal 2: Run tests with debug
```bash
pytest tests/test_memory.py -v -s
```

### Pipe output to file for analysis
```bash
python -m agentos.cli > debug.log 2>&1
# Then examine with:
grep "DEBUG ERROR" debug.log  # Find errors
grep "ContextManager" debug.log  # Find context operations
```

## Test Coverage Summary

### Memory Tests (35+ cases)
- MemoryItem: 2 tests
- ShortTermMemory: 9 tests
- LongTermMemory: 8 tests
- CircularBuffer: 5 tests
- ContextManager: 7 tests
- Integration: 2 tests

### Running Specific Tests
```bash
# Test short-term memory
pytest tests/test_memory.py::TestShortTermMemory -v

# Test long-term persistence
pytest tests/test_memory.py::TestLongTermMemory::test_add_command -v

# Test integration
pytest tests/test_memory.py::TestMemoryIntegration -v

# Test with coverage
pytest tests/test_memory.py --cov=src/agentos/memory --cov-report=term-missing
```

## Debug Output Format Reference

```
[DEBUG] ComponentName - Action: specific_info
[DEBUG] ShortTermMemory initialized - Capacity: 50, Session Start: 2025-11-17 10:30:45
[DEBUG] Item added to ShortTermMemory - Type: command, Current size: 5/50
[DEBUG] Retrieved 3 recent items - Filter type: command, Total available: 12

[DEBUG ERROR] Failed operation details
[DEBUG ERROR] Failed to add command to vector store: connection timeout
```

## Filtering Debug Output

### Show only errors
```bash
grep "DEBUG ERROR" output.log
```

### Show only memory operations
```bash
grep "Memory" output.log
```

### Show only tool execution
```bash
grep -E "tool|Tool" output.log
```

### Show initialization sequence
```bash
grep -E "initialized|loading" output.log | head -20
```

### Monitor in real-time
```bash
tail -f debug.log | grep "DEBUG"
```

## Performance Debug Tips

### Check memory accumulation
Look for: "Current size: X/50" in short_term.py prints
- If growing constantly: memory leak
- If cycling: normal operation

### Check database growth
Look for: "Retrieved X command" in long_term.py prints
- Compare with "Recording command" count
- Should be persistent

### Check context building time
Look for gap between:
- "Building context for query"
- "Context built - Length"

## Debugging Checklist

- [ ] Module initialization complete (check all `[DEBUG] ... loaded`)
- [ ] AgentOS initialized successfully
- [ ] Memory systems initialized (short-term, long-term, vector store)
- [ ] Context manager has all three systems
- [ ] Tools registered correctly
- [ ] Request processing started
- [ ] Context retrieved from memory
- [ ] Tool calls detected and routed
- [ ] Results recorded back to memory
- [ ] Response returned to user

## Files for Reference

- **Main Debug Enhancement Doc**: `DEBUG_ENHANCEMENTS.md`
- **Test Suite**: `tests/test_memory.py` (comprehensive examples)
- **Memory System**: `src/agentos/memory/` (core implementation)
- **Agent Core**: `src/agentos/core/agent.py` (main orchestration)

## Next Steps for Debugging

1. Start application: See initialization chain
2. Make a request: See full request flow
3. Check memory: Use test suite to verify state
4. Review logs: Filter for specific components
5. Compare with tests: See expected behavior
