"""Interactive CLI client for the inventory MCP server (remote-capable)."""
from __future__ import annotations

import asyncio

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from client.llm_agent import InventoryAgent
from client.mcp_session import list_tools, mcp_session
from shared.config import settings

console = Console()
app = typer.Typer(add_completion=False)


async def _interactive_loop(server_url: str, model: str, api_key: str) -> None:
    console.print(Panel.fit(
        f"[bold green]Inventory Assistant[/bold green]\n"
        f"[dim]Server: {server_url}[/dim]\n"
        f"Type 'exit' to quit, 'reset' to clear history."
    ))

    async with mcp_session(url=server_url) as session:
        tools = await list_tools(session)
        console.print(f"[dim]Connected — {len(tools)} MCP tools available[/dim]\n")

        agent = InventoryAgent(session, tools, model=model, api_key=api_key)

        while True:
            try:
                user_input = Prompt.ask("[bold cyan]You[/bold cyan]")
            except (EOFError, KeyboardInterrupt):
                break

            cmd = user_input.strip().lower()
            if cmd in {"exit", "quit", "bye"}:
                break
            if cmd == "reset":
                agent.reset()
                console.print("[dim]Conversation reset.[/dim]")
                continue

            try:
                reply = await agent.chat(user_input)
                console.print(Panel(Markdown(reply), title="[bold]Assistant[/bold]", border_style="green"))
            except Exception as exc:  # noqa: BLE001
                console.print(f"[red]Error:[/red] {exc}")

    console.print("[dim]Goodbye.[/dim]")


@app.command()
def run(
    server_url: str = typer.Option(
        settings.mcp_server_url,
        "--server-url", "-s",
        envvar="MCP_SERVER_URL",
        help="Full URL of the MCP server endpoint, e.g. http://192.168.1.10:8765/mcp",
    ),
    model: str = typer.Option(settings.openai_model, "--model", "-m", help="OpenAI model"),
    api_key: str = typer.Option(settings.openai_api_key, "--api-key", envvar="OPENAI_API_KEY"),
) -> None:
    """Start the interactive inventory assistant (connects to a remote MCP server)."""
    if not api_key:
        console.print("[red]Error:[/red] OPENAI_API_KEY is not set.")
        raise typer.Exit(1)
    asyncio.run(_interactive_loop(server_url=server_url, model=model, api_key=api_key))


if __name__ == "__main__":
    app()
