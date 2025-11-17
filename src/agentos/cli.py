import asyncio
from typing import Optional
import sys
import os

# Add src and project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
import structlog

from agentos.core.agent import AgentOS
from config.settings import settings

console = Console()
logger = structlog.get_logger()

class CLI:
    """Interactive CLI for AgentOS."""
    
    def __init__(self):
        self.agent = AgentOS()
        self.session = PromptSession(
            history=FileHistory(".agentos_history"),
            auto_suggest=AutoSuggestFromHistory(),
        )
        self.running = True
    
    def print_banner(self):
        """Print welcome banner."""
        banner = """
╔═══════════════════════════════════════════════════════════╗
║                        AgentOS                            ║
║          Intelligent Computer Automation CLI             ║
╚═══════════════════════════════════════════════════════════╝

Available commands:
  - Any natural language request (e.g., "list files", "check CPU usage")
  - /help    - Show help
  - /clear   - Clear conversation history
  - /status  - Show system status
  - /exit    - Exit AgentOS

Type your request to begin...
"""
        console.print(banner, style="cyan bold")
    
    async def run(self):
        """Main CLI loop."""
        self.print_banner()
        
        while self.running:
            try:
                # Get user input
                user_input = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.session.prompt("You: ", style="bold green")
                )
                
                if not user_input.strip():
                    continue
                
                # Handle special commands
                if user_input.startswith("/"):
                    self._handle_special_command(user_input)
                    continue
                
                # Process request
                console.print("\n[bold cyan]AgentOS:[/bold cyan] Processing...\n")
                
                response = await self.agent.process_request(user_input)
                
                # Display response
                self._display_response(response)
                
            except KeyboardInterrupt:
                console.print("\n\n[yellow]Use /exit to quit[/yellow]")
                continue
            except EOFError:
                break
            except Exception as e:
                logger.error("cli_error", error=str(e))
                console.print(f"\n[red]Error: {str(e)}[/red]\n")
        
        console.print("\n[cyan]Goodbye![/cyan]\n")
    
    def _handle_special_command(self, command: str):
        """Handle special CLI commands."""
        cmd = command.lower().strip()
        
        if cmd == "/exit" or cmd == "/quit":
            self.running = False
        
        elif cmd == "/help":
            self._show_help()
        
        elif cmd == "/clear":
            self.agent.context_manager.clear_session()
            console.print("\n[green]✓ Session cleared[/green]\n")
        
        elif cmd == "/status":
            self._show_status()
        
        else:
            console.print(f"\n[red]Unknown command: {command}[/red]\n")
    
    def _show_help(self):
        """Show help information."""
        help_text = """
# AgentOS Help

## Natural Language Commands

AgentOS understands natural language. Just tell it what you want:

**Examples:**
- "List all Python files in this directory"
- "What's my CPU usage?"
- "Create a new file called test.txt with hello world"
- "Open Chrome and go to google.com"
- "Show me the contents of config.py"
- "Search for all .log files"

## Special Commands

- `/help` - Show this help
- `/clear` - Clear conversation memory
- `/status` - Show system status
- `/exit` - Exit AgentOS

## Tips

1. Be specific in your requests
2. AgentOS remembers context from previous commands
3. It will ask for confirmation for dangerous operations
4. Check command output to verify success
"""
        console.print(Markdown(help_text))
    
    def _show_status(self):
        """Show system status."""
        import psutil
        
        status = f"""
[bold cyan]System Status[/bold cyan]

Memory Usage: {psutil.virtual_memory().percent}%
CPU Usage: {psutil.cpu_percent(interval=1)}%
Disk Usage: {psutil.disk_usage('/').percent}%

Session Info:
- Commands executed: {len(self.agent.context_manager.short_term.get_recent(100))}
- Active task: {self.agent.context_manager.short_term.get_task_context().get('name', 'None')}
"""
        console.print(Panel(status, border_style="cyan"))
    
    def _display_response(self, response: str):
        """Display agent response with formatting."""
        console.print(Panel(
            Markdown(response),
            title="[bold cyan]AgentOS Response[/bold cyan]",
            border_style="cyan",
        ))
        console.print()

@click.command()
@click.option('--debug', is_flag=True, help='Enable debug logging')
def main(debug: bool):
    """Launch AgentOS CLI."""
    if debug:
        settings.log_level = "DEBUG"
    
    # Configure logging
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(structlog.stdlib, settings.log_level)
        ),
    )
    
    # Run CLI
    cli = CLI()
    try:
        asyncio.run(cli.run())
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted[/yellow]")

if __name__ == "__main__":
    main()
