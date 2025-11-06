"""Interactive CLI for Zendesk Help Center Copy Tool"""

import click
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from .zendesk_client import ZendeskClient
from .copier import HelpCenterCopier


console = Console()


def load_credentials_from_env():
    """Load credentials from .env file if it exists"""
    load_dotenv()
    return {
        'source': {
            'subdomain': os.getenv('SOURCE_ZENDESK_SUBDOMAIN'),
            'email': os.getenv('SOURCE_ZENDESK_EMAIL'),
            'api_token': os.getenv('SOURCE_ZENDESK_API_TOKEN')
        },
        'dest': {
            'subdomain': os.getenv('DEST_ZENDESK_SUBDOMAIN'),
            'email': os.getenv('DEST_ZENDESK_EMAIL'),
            'api_token': os.getenv('DEST_ZENDESK_API_TOKEN')
        }
    }


def prompt_credentials(instance_name: str, existing_creds: dict = None) -> dict:
    """
    Prompt user for Zendesk credentials
    
    Args:
        instance_name: Name of instance (source/destination)
        existing_creds: Existing credentials from .env (optional)
    
    Returns:
        Dictionary with subdomain, email, and api_token
    """
    console.print(f"\n[bold cyan]Configure {instance_name.upper()} Zendesk Instance[/bold cyan]")
    
    subdomain = existing_creds.get('subdomain') if existing_creds else None
    if subdomain:
        use_existing = Confirm.ask(f"Use existing subdomain '{subdomain}'?", default=True)
        if not use_existing:
            subdomain = None
    
    if not subdomain:
        subdomain = Prompt.ask("Enter Zendesk subdomain (e.g., 'mycompany' for mycompany.zendesk.com)")
    
    email = existing_creds.get('email') if existing_creds else None
    if email:
        use_existing = Confirm.ask(f"Use existing email '{email}'?", default=True)
        if not use_existing:
            email = None
    
    if not email:
        email = Prompt.ask("Enter email address")
    
    api_token = existing_creds.get('api_token') if existing_creds else None
    if api_token:
        masked_token = f"{api_token[:4]}...{api_token[-4:]}" if len(api_token) > 8 else "***"
        use_existing = Confirm.ask(f"Use existing API token ({masked_token})?", default=True)
        if not use_existing:
            api_token = None
    
    if not api_token:
        api_token = Prompt.ask("Enter API token", password=True)
    
    return {
        'subdomain': subdomain,
        'email': email,
        'api_token': api_token
    }


@click.command()
@click.option('--source-subdomain', help='Source Zendesk subdomain')
@click.option('--source-email', help='Source Zendesk email')
@click.option('--source-token', help='Source Zendesk API token')
@click.option('--dest-subdomain', help='Destination Zendesk subdomain')
@click.option('--dest-email', help='Destination Zendesk email')
@click.option('--dest-token', help='Destination Zendesk API token')
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation prompts')
def main(source_subdomain, source_email, source_token, 
         dest_subdomain, dest_email, dest_token, yes):
    """
    Interactive CLI tool to copy Zendesk Help Center content from one instance to another.
    
    This tool will copy:
    - Categories
    - Sections
    - Articles
    
    You can provide credentials via command-line options, environment variables (.env file),
    or interactively when prompted.
    """
    console.print(Panel.fit(
        "[bold magenta]Zendesk Help Center Copy Tool[/bold magenta]\n"
        "Copy Help Center content between Zendesk instances",
        border_style="magenta"
    ))
    
    # Load credentials from .env if available
    env_creds = load_credentials_from_env()
    
    # Get source credentials
    if source_subdomain and source_email and source_token:
        source_creds = {
            'subdomain': source_subdomain,
            'email': source_email,
            'api_token': source_token
        }
    else:
        source_creds = prompt_credentials('source', env_creds['source'])
    
    # Get destination credentials
    if dest_subdomain and dest_email and dest_token:
        dest_creds = {
            'subdomain': dest_subdomain,
            'email': dest_email,
            'api_token': dest_token
        }
    else:
        dest_creds = prompt_credentials('destination', env_creds['dest'])
    
    # Initialize clients
    console.print("\n[bold cyan]Connecting to Zendesk instances...[/bold cyan]")
    
    try:
        source_client = ZendeskClient(**source_creds)
        dest_client = ZendeskClient(**dest_creds)
    except Exception as e:
        console.print(f"[bold red]Error initializing clients: {e}[/bold red]")
        return
    
    # Test connections
    console.print("Testing source connection...", end=" ")
    if not source_client.test_connection():
        console.print("[bold red]✗ Failed[/bold red]")
        console.print("[red]Could not connect to source Zendesk. Check credentials and try again.[/red]")
        return
    console.print("[bold green]✓ Connected[/bold green]")
    
    console.print("Testing destination connection...", end=" ")
    if not dest_client.test_connection():
        console.print("[bold red]✗ Failed[/bold red]")
        console.print("[red]Could not connect to destination Zendesk. Check credentials and try again.[/red]")
        return
    console.print("[bold green]✓ Connected[/bold green]")
    
    # Confirmation
    if not yes:
        console.print(f"\n[yellow]Ready to copy from [bold]{source_creds['subdomain']}[/bold] to [bold]{dest_creds['subdomain']}[/bold][/yellow]")
        console.print("[yellow]This will create new categories, sections, and articles in the destination.[/yellow]")
        
        if not Confirm.ask("\nProceed with copy?", default=False):
            console.print("[red]Copy cancelled.[/red]")
            return
    
    # Perform the copy
    try:
        copier = HelpCenterCopier(source_client, dest_client)
        copier.copy_all()
    except KeyboardInterrupt:
        console.print("\n[red]Copy interrupted by user.[/red]")
    except Exception as e:
        console.print(f"\n[bold red]Error during copy: {e}[/bold red]")
        raise


if __name__ == '__main__':
    main()
