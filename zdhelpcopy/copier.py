"""Core logic for copying Help Center content"""

from typing import Dict, List, Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from .zendesk_client import ZendeskClient


console = Console()


class HelpCenterCopier:
    """Handles the copying of Help Center content between Zendesk instances"""
    
    def __init__(self, source_client: ZendeskClient, dest_client: ZendeskClient):
        """
        Initialize the copier
        
        Args:
            source_client: Client for source Zendesk instance
            dest_client: Client for destination Zendesk instance
        """
        self.source = source_client
        self.dest = dest_client
        self.category_mapping = {}
        self.section_mapping = {}
    
    def copy_categories(self) -> Dict[int, int]:
        """
        Copy all categories from source to destination
        
        Returns:
            Mapping of source category IDs to destination category IDs
        """
        console.print("\n[bold cyan]Fetching categories from source...[/bold cyan]")
        source_categories = self.source.get_categories()
        
        console.print(f"[green]Found {len(source_categories)} categories[/green]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        ) as progress:
            task = progress.add_task("[cyan]Copying categories...", total=len(source_categories))
            
            for category in source_categories:
                category_data = {
                    'name': category['name'],
                    'description': category.get('description', ''),
                    'locale': category.get('locale', 'en-us'),
                    'position': category.get('position', 0)
                }
                
                try:
                    new_category = self.dest.create_category(category_data)
                    self.category_mapping[category['id']] = new_category['id']
                    progress.advance(task)
                except Exception as e:
                    console.print(f"[red]Error copying category '{category['name']}': {e}[/red]")
        
        console.print(f"[green]✓ Copied {len(self.category_mapping)} categories[/green]")
        return self.category_mapping
    
    def copy_sections(self) -> Dict[int, int]:
        """
        Copy all sections from source to destination
        
        Returns:
            Mapping of source section IDs to destination section IDs
        """
        console.print("\n[bold cyan]Fetching sections from source...[/bold cyan]")
        source_sections = self.source.get_sections()
        
        console.print(f"[green]Found {len(source_sections)} sections[/green]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        ) as progress:
            task = progress.add_task("[cyan]Copying sections...", total=len(source_sections))
            
            for section in source_sections:
                source_category_id = section.get('category_id')
                dest_category_id = self.category_mapping.get(source_category_id)
                
                if not dest_category_id:
                    console.print(f"[yellow]Warning: Skipping section '{section['name']}' - category not found[/yellow]")
                    progress.advance(task)
                    continue
                
                section_data = {
                    'name': section['name'],
                    'description': section.get('description', ''),
                    'locale': section.get('locale', 'en-us'),
                    'category_id': dest_category_id,
                    'position': section.get('position', 0)
                }
                
                try:
                    new_section = self.dest.create_section(section_data)
                    self.section_mapping[section['id']] = new_section['id']
                    progress.advance(task)
                except Exception as e:
                    console.print(f"[red]Error copying section '{section['name']}': {e}[/red]")
        
        console.print(f"[green]✓ Copied {len(self.section_mapping)} sections[/green]")
        return self.section_mapping
    
    def copy_articles(self) -> int:
        """
        Copy all articles from source to destination
        
        Returns:
            Number of articles copied
        """
        console.print("\n[bold cyan]Fetching articles from source...[/bold cyan]")
        source_articles = self.source.get_articles()
        
        console.print(f"[green]Found {len(source_articles)} articles[/green]")
        
        copied_count = 0
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        ) as progress:
            task = progress.add_task("[cyan]Copying articles...", total=len(source_articles))
            
            for article in source_articles:
                source_section_id = article.get('section_id')
                dest_section_id = self.section_mapping.get(source_section_id)
                
                if not dest_section_id:
                    console.print(f"[yellow]Warning: Skipping article '{article['title']}' - section not found[/yellow]")
                    progress.advance(task)
                    continue
                
                article_data = {
                    'title': article['title'],
                    'body': article.get('body', ''),
                    'locale': article.get('locale', 'en-us'),
                    'section_id': dest_section_id,
                    'position': article.get('position', 0),
                    'draft': article.get('draft', False),
                    'promoted': article.get('promoted', False)
                }
                
                try:
                    self.dest.create_article(article_data)
                    copied_count += 1
                    progress.advance(task)
                except Exception as e:
                    console.print(f"[red]Error copying article '{article['title']}': {e}[/red]")
        
        console.print(f"[green]✓ Copied {copied_count} articles[/green]")
        return copied_count
    
    def copy_all(self):
        """Copy all Help Center content (categories, sections, articles)"""
        console.print("[bold magenta]Starting Help Center copy process...[/bold magenta]")
        
        self.copy_categories()
        self.copy_sections()
        self.copy_articles()
        
        console.print("\n[bold green]✓ Copy process completed![/bold green]")
