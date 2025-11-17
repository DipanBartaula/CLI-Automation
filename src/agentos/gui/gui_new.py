#!/usr/bin/env python
"""
AgentOS GUI Terminal - Modern Linux-style interface
Beautiful green-on-black terminal with full functionality
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import asyncio
import sys
import os
from datetime import datetime
import queue
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from agentos.core.agent import AgentOS


class TerminalEmulator:
    """Modern Linux-style terminal GUI for AgentOS"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("AgentOS Terminal")
        self.root.geometry("1200x750")
        self.root.configure(bg="#0a0e27")
        
        # Initialize agent
        self.agent = None
        self.agent_ready = False
        self.response_queue = queue.Queue()
        
        # Create GUI components
        self._create_widgets()
        self._setup_styles()
        
        # Create data directories
        Path("data/memory").mkdir(parents=True, exist_ok=True)
        Path("data/logs").mkdir(parents=True, exist_ok=True)
        
        # Write initial message
        self.write_output("╔════════════════════════════════════════════════════════════╗", "info")
        self.write_output("║  🤖 AgentOS Terminal - AI-Powered Computer Automation     ║", "success")
        self.write_output("╚════════════════════════════════════════════════════════════╝", "info")
        self.write_output("", "info")
        self.write_output("Initializing AgentOS Backend...", "warning")
        self.root.update()
        
        # Initialize agent in background thread
        self._init_agent_thread()
        
        # Start checking queue
        self.check_response_queue()
        
        # Command history
        self.history = []
        self.history_index = -1
        self.conversation_memory = []
    
    def _create_widgets(self):
        """Create all GUI components"""
        
        # Header panel
        header = tk.Frame(self.root, bg="#0f1440", height=50)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)
        
        # Status indicator
        self.status_frame = tk.Frame(self.root, bg="#0a0e27", height=25)
        self.status_frame.pack(fill=tk.X, padx=10, pady=5)
        self.status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            self.status_frame,
            text="⏳ Initializing...",
            font=("Courier New", 9),
            bg="#0a0e27",
            fg="#ffaa00"
        )
        self.status_label.pack(side=tk.LEFT)
        
        self.memory_label = tk.Label(
            self.status_frame,
            text="Memory: 0 items",
            font=("Courier New", 9),
            bg="#0a0e27",
            fg="#00aaff"
        )
        self.memory_label.pack(side=tk.RIGHT)
        
        # Output area
        output_frame = tk.Frame(self.root, bg="#0a0e27")
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.output = scrolledtext.ScrolledText(
            output_frame,
            font=("Courier New", 10),
            bg="#0a0e27",
            fg="#00dd00",
            insertbackground="#00dd00",
            relief=tk.FLAT,
            borderwidth=0,
            wrap=tk.WORD
        )
        self.output.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags
        self._setup_text_tags()
        
        # Input frame
        input_frame = tk.Frame(self.root, bg="#0a0e27")
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            input_frame,
            text="root@agentos:~$",
            font=("Courier New", 10, "bold"),
            bg="#0a0e27",
            fg="#00ff00"
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        self.input_field = tk.Entry(
            input_frame,
            font=("Courier New", 10),
            bg="#1a1f3a",
            fg="#00dd00",
            insertbackground="#00dd00",
            relief=tk.FLAT,
            borderwidth=2
        )
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.input_field.bind("<Return>", self.on_send)
        self.input_field.bind("<Up>", self.on_history_up)
        self.input_field.bind("<Down>", self.on_history_down)
        self.input_field.bind("<Control-l>", lambda e: self.on_clear())
        self.input_field.bind("<Control-h>", lambda e: self.on_help())
        
        # Button frame
        button_frame = tk.Frame(self.root, bg="#0a0e27")
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        buttons = [
            ("▶ Send", self.on_send, "#00aa00"),
            ("✓ Status", self.on_status, "#0099ff"),
            ("? Help", self.on_help, "#aa00ff"),
            ("✕ Clear", self.on_clear, "#ff6600"),
            ("⊗ Exit", self.on_exit, "#ff0000"),
        ]
        
        for text, cmd, color in buttons:
            btn = tk.Button(
                button_frame,
                text=text,
                command=cmd,
                font=("Courier New", 9, "bold"),
                bg=color,
                fg="#000000",
                activebackground=color,
                activeforeground="#ffffff",
                relief=tk.FLAT,
                padx=12,
                pady=6,
                cursor="hand2"
            )
            btn.pack(side=tk.LEFT, padx=3)
    
    def _setup_text_tags(self):
        """Configure text formatting tags"""
        self.output.tag_config("info", foreground="#00dd00")
        self.output.tag_config("success", foreground="#00ff00")
        self.output.tag_config("error", foreground="#ff3333")
        self.output.tag_config("warning", foreground="#ffaa00")
        self.output.tag_config("user", foreground="#00aaff", font=("Courier New", 10, "bold"))
        self.output.tag_config("system", foreground="#aaaaff")
        self.output.tag_config("input", foreground="#00ff00", font=("Courier New", 10, "bold"))
    
    def _setup_styles(self):
        """Setup color scheme"""
        self.colors = {
            "bg": "#0a0e27",
            "fg": "#00dd00",
            "accent": "#00ff00",
            "success": "#00ff00",
            "error": "#ff3333",
            "warning": "#ffaa00",
        }
    
    def _init_agent_thread(self):
        """Initialize agent in background thread"""
        def init():
            try:
                print("[DEBUG] Initializing AgentOS Agent...")
                self.agent = AgentOS()
                self.agent_ready = True
                print("[DEBUG] AgentOS Agent initialized successfully")
                self.write_output("✓ AgentOS Ready!", "success")
                self.status_label.config(text="✓ Ready", fg="#00ff00")
                self.response_queue.put(("system", "Agent initialized successfully"))
            except Exception as e:
                print(f"[ERROR] Failed to initialize agent: {e}")
                self.write_output(f"✗ Error: {str(e)}", "error")
                self.status_label.config(text="✗ Error", fg="#ff3333")
                self.response_queue.put(("error", str(e)))
        
        thread = threading.Thread(target=init, daemon=True)
        thread.start()
    
    def write_output(self, text, tag="info"):
        """Write text to output area"""
        self.output.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        output_text = f"[{timestamp}] {text}\n"
        self.output.insert(tk.END, output_text, tag)
        self.output.see(tk.END)
        self.output.config(state=tk.DISABLED)
    
    def on_send(self, event=None):
        """Send command to backend"""
        if not self.agent_ready:
            self.write_output("Agent still initializing... Please wait", "warning")
            return
        
        command = self.input_field.get().strip()
        
        if not command:
            return
        
        # Add to history
        self.history.append(command)
        self.history_index = -1
        
        # Add to conversation memory
        self.conversation_memory.append({
            "type": "user",
            "content": command,
            "timestamp": datetime.now()
        })
        
        # Update memory label
        self.memory_label.config(text=f"Memory: {len(self.conversation_memory)} items")
        
        # Clear input
        self.input_field.delete(0, tk.END)
        
        # Display command
        self.write_output(f"> {command}", "input")
        
        # Update status
        self.status_label.config(text="🔄 Processing...", fg="#ffaa00")
        self.root.update()
        
        # Process in thread
        thread = threading.Thread(target=self._process_command, args=(command,), daemon=True)
        thread.start()
    
    def _process_command(self, command):
        """Process command in background"""
        try:
            # Handle special commands
            if command.startswith("/"):
                response = self._handle_special_command(command)
                self.response_queue.put(("success", response))
                return
            
            # Process with agent
            print(f"[DEBUG] Processing command: {command}")
            
            # Create async loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                print(f"[DEBUG] Calling agent.process_request...")
                result = loop.run_until_complete(self.agent.process_request(command))
                print(f"[DEBUG] Agent returned: {repr(result)}")
                print(f"[DEBUG] Type: {type(result)}")
                print(f"[DEBUG] Is None: {result is None}")
                print(f"[DEBUG] Is empty: {result == ''}")
                
                # Always send response, even if it's empty
                if result is not None:
                    print(f"[DEBUG] Queuing response: {result[:100]}")
                    # Add to conversation memory
                    self.conversation_memory.append({
                        "type": "assistant",
                        "content": result,
                        "timestamp": datetime.now()
                    })
                    self.response_queue.put(("success", result))
                else:
                    print(f"[DEBUG] Result is None, sending error")
                    self.response_queue.put(("error", "Agent returned None"))
            except Exception as e2:
                print(f"[DEBUG] Exception in agent call: {str(e2)}")
                import traceback
                traceback.print_exc()
                self.response_queue.put(("error", f"Agent error: {str(e2)}"))
            finally:
                loop.close()
        
        except Exception as e:
            print(f"[ERROR] {str(e)}")
            import traceback
            traceback.print_exc()
            self.response_queue.put(("error", f"Error: {str(e)}"))
    
    def _handle_special_command(self, cmd):
        """Handle special commands"""
        cmd_lower = cmd.lower().strip()
        
        if cmd_lower == "/help":
            return """
╔═══════════════════════════════════════════════════════════════╗
║                    AVAILABLE COMMANDS                         ║
╚═══════════════════════════════════════════════════════════════╝

SPECIAL COMMANDS:
  /help              - Show this help message
  /status            - Show system status
  /memory            - Show conversation memory
  /clear             - Clear output (Ctrl+L)
  /exit              - Exit terminal

EXAMPLES:
  ✓ "Create file ankit_bro.txt in A: drive"
  ✓ "Write about Uzumaki Naruto in test.txt"
  ✓ "What is my CPU usage?"
  ✓ "List files in Desktop"
  ✓ "Open notepad"
"""
        
        elif cmd_lower == "/status":
            try:
                import psutil
                cpu = psutil.cpu_percent(interval=1)
                mem = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                return f"""SYSTEM STATUS:
  CPU: {cpu}%
  Memory: {mem.percent}% ({mem.used // (1024**3)}GB / {mem.total // (1024**3)}GB)
  Disk: {disk.percent}%
"""
            except Exception as e:
                return f"Error: {str(e)}"
        
        elif cmd_lower == "/memory":
            if not self.conversation_memory:
                return "No conversation memory yet."
            
            response = "CONVERSATION MEMORY:\n"
            for i, item in enumerate(self.conversation_memory[-5:], 1):
                content = item['content'][:80]
                if len(item['content']) > 80:
                    content += "..."
                response += f"  [{i}] {item['type'].upper()}: {content}\n"
            return response
        
        elif cmd_lower == "/clear":
            self.output.config(state=tk.NORMAL)
            self.output.delete(1.0, tk.END)
            self.output.config(state=tk.DISABLED)
            return ""
        
        elif cmd_lower == "/exit":
            self.on_exit()
            return ""
        
        else:
            return f"Unknown command: {cmd}. Type /help for available commands."
    
    def check_response_queue(self):
        """Check for responses from background thread"""
        try:
            status, response = self.response_queue.get_nowait()
            print(f"[DEBUG GUI] Got response from queue - Status: {status}, Response type: {type(response)}")
            
            if response is not None:
                print(f"[DEBUG GUI] Response is not None, length: {len(str(response))}")
                if status == "success":
                    print(f"[DEBUG GUI] Displaying success response")
                    self.write_output(response, "success")
                    self.status_label.config(text="✓ Ready", fg="#00ff00")
                elif status == "error":
                    print(f"[DEBUG GUI] Displaying error response")
                    self.write_output(response, "error")
                    self.status_label.config(text="✗ Error", fg="#ff3333")
                else:
                    print(f"[DEBUG GUI] Displaying system response")
                    self.write_output(response, "system")
            else:
                print(f"[DEBUG GUI] Response is None!")
            
            # Update memory label
            self.memory_label.config(text=f"Memory: {len(self.conversation_memory)} items")
        
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.check_response_queue)
    
    def on_history_up(self, event):
        """Navigate history up"""
        if self.history and self.history_index < len(self.history) - 1:
            self.history_index += 1
            cmd = self.history[-(self.history_index + 1)]
            self.input_field.delete(0, tk.END)
            self.input_field.insert(0, cmd)
        return "break"
    
    def on_history_down(self, event):
        """Navigate history down"""
        if self.history_index > 0:
            self.history_index -= 1
            cmd = self.history[-(self.history_index + 1)]
            self.input_field.delete(0, tk.END)
            self.input_field.insert(0, cmd)
        elif self.history_index == 0:
            self.history_index = -1
            self.input_field.delete(0, tk.END)
        return "break"
    
    def on_clear(self):
        """Clear output"""
        self.output.config(state=tk.NORMAL)
        self.output.delete(1.0, tk.END)
        self.output.config(state=tk.DISABLED)
        self.write_output("Output cleared", "info")
    
    def on_status(self):
        """Show status"""
        self.input_field.delete(0, tk.END)
        self.input_field.insert(0, "/status")
        self.on_send()
    
    def on_help(self):
        """Show help"""
        self.input_field.delete(0, tk.END)
        self.input_field.insert(0, "/help")
        self.on_send()
    
    def on_exit(self):
        """Exit application"""
        if messagebox.askokcancel("Exit", "Exit AgentOS Terminal?"):
            self.root.quit()
    
    def run(self):
        """Start the GUI"""
        self.root.mainloop()


def main():
    """Main entry point"""
    root = tk.Tk()
    terminal = TerminalEmulator(root)
    terminal.run()


if __name__ == "__main__":
    main()
