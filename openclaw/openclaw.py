#!/usr/bin/env python3
"""
🦀 OpenClaw - Open Source AI Coding Assistant

Usage:
    python openclaw.py                    # Interactive mode
    python openclaw.py code "add login"   # Single command
    python openclaw.py --help             # Help
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import Optional
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich import print as rprint

# Add parent directory to path to import framework
sys.path.insert(0, str(Path(__file__).parent.parent))

from framework import AgentRegistry
from openclaw.agents.coder_agent import CoderAgent
from core import AIClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

console = Console()


class OpenClaw:
    """Main OpenClaw application"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenClaw.

        Args:
            api_key: OpenRouter API key (or set OPENROUTER_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key required. Set OPENROUTER_API_KEY env var "
                "or pass api_key parameter"
            )

        # Initialize agent registry
        self.registry = AgentRegistry()

        # Register agents
        self._register_agents()

        console.print(Panel.fit(
            "🦀 [bold cyan]OpenClaw[/bold cyan] - Open Source AI Coding Assistant\n"
            f"Registered agents: {', '.join(self.registry.list_agents())}",
            border_style="cyan"
        ))

    def _register_agents(self):
        """Register all available agents"""
        # Coder agent
        coder = CoderAgent(
            model="openrouter/qwen/qwen-2.5-7b-instruct",
            temperature=0.3
        )
        self.registry.register(coder)

        console.print("[green]✓[/green] Registered CoderAgent")

        # TODO: Add more agents (Debugger, Tester, Reviewer, etc.)

    async def execute_command(self, command: str, args: str = "") -> None:
        """
        Execute a command.

        Args:
            command: Command name (code, debug, test, etc.)
            args: Command arguments
        """
        if command == "code":
            await self._code_command(args)
        elif command == "help":
            self._help_command()
        elif command == "list":
            self._list_agents()
        elif command == "stats":
            self._show_stats()
        elif command == "exit" or command == "quit":
            console.print("[yellow]Goodbye! 👋[/yellow]")
            sys.exit(0)
        else:
            console.print(f"[red]Unknown command: {command}[/red]")
            console.print("Type [cyan]help[/cyan] for available commands")

    async def _code_command(self, description: str):
        """Generate code"""
        if not description:
            description = Prompt.ask("[cyan]What do you want to code?[/cyan]")

        console.print(f"\n[yellow]🤔 Thinking about: {description}[/yellow]\n")

        # Get coder agent
        coder = self.registry.get("coder")
        if not coder:
            console.print("[red]Error: Coder agent not found[/red]")
            return

        # Execute task
        result = await coder.run(task={
            "description": description,
            "language": "python"  # TODO: Auto-detect or ask
        })

        if result.success:
            # Display result
            console.print(Panel(
                Markdown(result.result.get("explanation", "")),
                title="💡 Explanation",
                border_style="green"
            ))

            console.print("\n[bold cyan]Generated Code:[/bold cyan]\n")
            code = result.result.get("code", "")
            console.print(Panel(code, border_style="cyan"))

            # Ask if user wants to save
            save = Prompt.ask(
                "\n[cyan]Save to file?[/cyan]",
                choices=["y", "n"],
                default="n"
            )

            if save == "y":
                filename = Prompt.ask("[cyan]Filename[/cyan]")
                with open(filename, "w") as f:
                    f.write(code)
                console.print(f"[green]✓[/green] Saved to {filename}")

        else:
            console.print(f"[red]❌ Error: {result.error}[/red]")

    def _help_command(self):
        """Show help"""
        help_text = """
# OpenClaw Commands

## Coding
- `code <description>` - Generate code based on description
- `refactor <file>` - Refactor code in a file
- `explain <file>` - Explain what code does

## Debugging
- `debug <error>` - Help debug an error (coming soon)
- `fix <file>` - Suggest fixes for bugs (coming soon)

## Testing
- `test <file>` - Generate tests for code (coming soon)

## Other
- `list` - List all available agents
- `stats` - Show agent statistics
- `help` - Show this help message
- `exit` - Exit OpenClaw

## Examples
```
> code "create a FastAPI endpoint for user login"
> code "implement binary search in Python"
> list
> stats
```
"""
        console.print(Markdown(help_text))

    def _list_agents(self):
        """List all registered agents"""
        agents = self.registry.list_agents()
        console.print("\n[bold cyan]Registered Agents:[/bold cyan]\n")

        for agent_name in agents:
            agent = self.registry.get(agent_name)
            console.print(f"  • [green]{agent_name}[/green]: {agent.metadata.description}")

        console.print()

    def _show_stats(self):
        """Show agent statistics"""
        stats = self.registry.get_stats()

        console.print("\n[bold cyan]Agent Statistics:[/bold cyan]\n")

        for agent_data in stats["agents"]:
            name = agent_data["name"]
            agent_stats = agent_data["stats"]

            console.print(f"\n[green]{name}[/green]:")
            console.print(f"  Executions: {agent_stats['total_executions']}")
            console.print(f"  Successes: {agent_stats['successes']}")
            console.print(f"  Failures: {agent_stats['failures']}")
            console.print(f"  Success Rate: {agent_stats['success_rate']:.1%}")

        console.print()

    async def interactive_mode(self):
        """Run in interactive mode"""
        console.print("\n[cyan]Type 'help' for available commands or 'exit' to quit[/cyan]\n")

        while True:
            try:
                # Get user input
                user_input = Prompt.ask("[bold cyan]openclaw>[/bold cyan]")

                if not user_input.strip():
                    continue

                # Parse command
                parts = user_input.strip().split(maxsplit=1)
                command = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""

                # Execute
                await self.execute_command(command, args)

            except KeyboardInterrupt:
                console.print("\n[yellow]Use 'exit' to quit[/yellow]")
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="OpenClaw - Open Source AI Coding Assistant"
    )
    parser.add_argument("command", nargs="?", help="Command to execute")
    parser.add_argument("args", nargs="*", help="Command arguments")
    parser.add_argument("--api-key", help="OpenRouter API key")

    args = parser.parse_args()

    try:
        # Initialize OpenClaw
        claw = OpenClaw(api_key=args.api_key)

        if args.command:
            # Single command mode
            command_args = " ".join(args.args) if args.args else ""
            await claw.execute_command(args.command, command_args)
        else:
            # Interactive mode
            await claw.interactive_mode()

    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
