```markdown
# AgentOS - Agentic Computer Automation System

An intelligent CLI agent that controls your computer through natural language commands.

## Features

- 🤖 **Natural Language Control**: Tell your computer what to do in plain English
- 🧠 **Memory System**: Remembers context and learns from past actions
- 🛠️ **Multi-Tool Support**: File operations, app launching, system monitoring, and more
- 🔒 **Safety First**: Built-in safety checks for dangerous operations
- 📊 **Rich CLI**: Beautiful terminal interface with syntax highlighting

## Installation

```bash
# Clone repository
git clone https://github.com/yourusername/agentos.git
cd agentos

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

## Configuration

1. Copy `.env.example` to `.env` (already provided with Azure credentials)
2. Ensure all environment variables are set correctly

## Usage

```bash
# Start AgentOS CLI
agentos

# With debug logging
agentos --debug
```

### Example Commands

```
You: List all Python files in the current directory
You: What's my CPU and memory usage?
You: Create a file called notes.txt with "Hello World"
You: Open Chrome and navigate to github.com
You: Search for all .log files in /var/log
You: Show me running processes using more than 50% CPU
```

### Special Commands

- `/help` - Show help information
- `/clear` - Clear conversation memory
- `/status` - Show system status
- `/exit` - Exit AgentOS

## Architecture

```
┌─────────────────────────────────────────┐
│         CLI Interface (Rich)            │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│      AgentOS Core (LLM + Tools)         │
│  - Azure OpenAI GPT-4o                  │
│  - Function calling orchestration       │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│        Memory System                     │
│  - Short-term (session context)         │
│  - Long-term (SQLite persistence)       │
│  - Vector store (ChromaDB)              │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│          Tool Ecosystem                  │
│  - Shell executor                        │
│  - File manager                          │
│  - App launcher                          │
│  - System monitor                        │
└─────────────────────────────────────────┘
```

## Memory System

### Short-Term Memory
- Stores recent commands and results
- Maintains conversation context
- Limited to 50 items (configurable)

### Long-Term Memory
- Persists command history across sessions
- Stores task outcomes
- SQLite-based storage

### Vector Store
- Semantic search for similar past commands
- ChromaDB for embedding storage
- Helps agent learn from experience

## Safety Features

1. **Command Validation**: Checks for dangerous patterns
2. **Confirmation Prompts**: Asks before destructive operations
3. **Sandboxing Options**: Can run in read-only mode
4. **Audit Logging**: All actions logged to file

## Development

```bash
# Run tests
pytest tests/ -v

# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

## Project Structure

```
agentos/
├── src/agentos/          # Main package
│   ├── core/             # Agent logic
│   ├── llm/              # LLM client
│   ├── memory/           # Memory systems
│   ├── tools/            # Tool implementations
│   └── utils/            # Utilities
├── config/               # Configuration
├── data/                 # Data storage
│   ├── memory/           # Memory databases
│   └── logs/             # Log files
└── tests/                # Test suite
```

## How It Works

### 1. Request Processing

```
User Input → Context Retrieval → LLM Planning → Tool Execution → Response
```

### 2. Function Calling Flow

```python
# User: "List all Python files"
# 
# LLM receives:
# - System prompt (capabilities, guidelines)
# - User query
# - Available tools (as OpenAI function definitions)
# - Recent context from memory
#
# LLM responds with tool call:
# {
#   "tool_calls": [{
#     "name": "search_files",
#     "arguments": {
#       "directory": ".",
#       "pattern": "*.py",
#       "recursive": true
#     }
#   }]
# }
#
# AgentOS executes tool → Returns results → LLM formats response
```

### 3. Memory Integration

Every action is recorded in three places:
1. **Short-term**: Immediate context for current session
2. **Long-term**: Persistent SQL database for history
3. **Vector store**: Embeddings for semantic search

When processing new requests, the agent retrieves:
- Recent actions (last 10)
- Similar past commands (top 3)
- Related tasks (top 2)

This context helps the agent make better decisions.

## Advanced Usage

### Custom Tools

Add your own tools by extending the base classes:

```python
# In src/agentos/tools/my_tool.py
class MyTool:
    def execute(self, param: str) -> Dict[str, Any]:
        # Your logic here
        return {"success": True, "result": "..."}
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "my_tool",
                "description": "What it does",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "param": {"type": "string"}
                    }
                }
            }
        }

# Register in agent.py
self.my_tool = MyTool()
tools.append(self.my_tool.get_tool_definition())
```

### Browser Automation (Optional)

Install Playwright for web automation:

```bash
pip install playwright
playwright install
```

### API Mode

Use AgentOS programmatically:

```python
from agentos import AgentOS
import asyncio

async def main():
    agent = AgentOS()
    response = await agent.process_request("List files in current directory")
    print(response)

asyncio.run(main())
```

## Troubleshooting

**Issue**: "Module not found" errors
```bash
pip install -e .
```

**Issue**: Memory database locked
```bash
rm data/memory/agentos.db
# Will be recreated on next run
```

**Issue**: Azure OpenAI connection errors
- Verify credentials in `.env`
- Check network connectivity
- Ensure deployment name is correct

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file

## Acknowledgments

- Built with Azure OpenAI GPT-4o
- Uses ChromaDB for vector storage
- CLI powered by Rich and Click
```

## Installation & Running Instructions

```bash
# 1. Create project directory
mkdir agentos && cd agentos

# 2. Create all directories
mkdir -p src/agentos/{core,llm,memory,tools,utils}
mkdir -p config data/{memory,logs} tests

# 3. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 4. Create and copy all the files above into their respective locations

# 5. Install dependencies
pip install -r requirements.txt

# 6. Install in development mode
pip install -e .

# 7. Run AgentOS
agentos

# Or run directly
python -m agentos.main
```

## Key Technical Highlights

### 1. **Memory Architecture**
- **Short-term**: In-memory deque for current session
- **Long-term**: SQLite for persistent history
- **Vector store**: ChromaDB for semantic retrieval
- All three work together to provide rich context

### 2. **Function Calling Flow**
```
User Query → Context Enrichment → LLM (with tools) → Tool Calls → 
Execution → Results → LLM (final response) → User
```

### 3. **Safety Layers**
- Command validation before execution
- Dangerous pattern detection
- Sandboxing options
- Full audit trail

### 4. **State Management**
- Conversation state in short-term memory
- Task context tracking
- Automatic cleanup of old data
- Graceful error recovery