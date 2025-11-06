"""Cleanup utility to delete all Help Center categories

License: CC BY-NC 4.0 (Non-Commercial Use Only)
Copyright (c) 2025 Max Schifferle

This tool is provided "as is" without warranty. Use at your own risk.
See LICENSE file for full terms and conditions.
"""

import click
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from .zendesk_client import ZendeskClient


console = Console()


@click.command()
@click.option('--subdomain', help='Zendesk subdomain to clean')
@click.option('--email', help='Zendesk email')
@click.option('--token', help='Zendesk API token')
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation prompts')
def main(subdomain, email, token, yes):
    """
    Delete all categories from a Zendesk Help Center.
    
    WARNING: This will delete ALL categories, sections, and articles!
    This action cannot be undone.
    """
    console.print(Panel.fit(
        "[bold red]⚠️  Zendesk Help Center Cleanup Tool  ⚠️[/bold red]\n"
        "[yellow]Delete ALL categories, sections, and articles[/yellow]\n\n"
        "[dim]Non-Commercial Use Only | Use at Your Own Risk[/dim]\n"
        "[dim]License: CC BY-NC 4.0 | See LICENSE file[/dim]",
        border_style="red"
    ))
    
    # Load credentials from .env if available
    load_dotenv()
    
    if not subdomain:
        subdomain = os.getenv('DEST_ZENDESK_SUBDOMAIN')
    if not email:
        email = os.getenv('DEST_ZENDESK_EMAIL')
    if not token:
        token = os.getenv('DEST_ZENDESK_API_TOKEN')
    
    # Get credentials interactively if not provided
    if not subdomain:
        subdomain = Prompt.ask("Enter Zendesk subdomain (e.g., 'mycompany' for mycompany.zendesk.com)")
    if not email:
        email = Prompt.ask("Enter email address")
    if not token:
        token = Prompt.ask("Enter API token", password=True)
    
    # Initialize client
    console.print("\n[bold cyan]Connecting to Zendesk...[/bold cyan]")
    try:
        client = ZendeskClient(subdomain, email, token)
    except Exception as e:
        console.print(f"[bold red]Error initializing client: {e}[/bold red]")
        return
    
    # Test connection
    console.print("Testing connection...", end=" ")
    if not client.test_connection():
        console.print("[bold red]✗ Failed[/bold red]")
        console.print("[red]Could not connect to Zendesk. Check credentials and try again.[/red]")
        return
    console.print("[bold green]✓ Connected[/bold green]")
    
    # Get categories to delete
    console.print("\n[bold cyan]Fetching categories...[/bold cyan]")
    try:
        categories = client.get_categories()
    except Exception as e:
        console.print(f"[bold red]Error fetching categories: {e}[/bold red]")
        return
    
    if not categories:
        console.print("[yellow]No categories found. Help Center is already empty.[/yellow]")
        return
    
    console.print(f"[yellow]Found {len(categories)} categories:[/yellow]")
    for cat in categories[:10]:  # Show first 10
        console.print(f"  • {cat['name']}")
    if len(categories) > 10:
        console.print(f"  ... and {len(categories) - 10} more")
    
    # Final confirmation
    if not yes:
        console.print(f"\n[bold red]⚠️  WARNING ⚠️[/bold red]")
        console.print(f"[red]This will PERMANENTLY DELETE all {len(categories)} categories[/red]")
        console.print(f"[red]and ALL their sections and articles from {subdomain}.zendesk.com[/red]")
        console.print(f"[red]This action CANNOT be undone![/red]")
        
        confirm_text = Prompt.ask("\n[yellow]Type 'DELETE' to confirm", default="no")
        if confirm_text != "DELETE":
            console.print("[green]Cancelled. No categories were deleted.[/green]")
            return
    
    # Delete all categories
    console.print("\n[bold red]Deleting all categories...[/bold red]")
    deleted_count = 0
    failed_count = 0
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
    ) as progress:
        task = progress.add_task(f"[red]Deleting {len(categories)} categories...", total=len(categories))
        
        for category in categories:
            try:
                client.delete_category(category['id'])
                deleted_count += 1
                progress.update(task, advance=1, description=f"[red]Deleted {deleted_count}/{len(categories)} categories...")
            except Exception as e:
                console.print(f"[red]✗ Failed to delete '{category['name']}': {e}[/red]")
                failed_count += 1
                progress.update(task, advance=1)
    
    # Summary
    console.print(f"\n[bold green]✓ Cleanup completed![/bold green]")
    console.print(f"  • Deleted: {deleted_count} categories")
    if failed_count > 0:
        console.print(f"  • Failed: {failed_count} categories")


if __name__ == '__main__':
    main()
