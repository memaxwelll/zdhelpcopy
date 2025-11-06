"""Core logic for copying Help Center content"""

from typing import Dict, List, Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from .zendesk_client import ZendeskClient


console = Console()


class HelpCenterCopier:
    """Handles the copying of Help Center content between Zendesk instances"""
    
    def __init__(self, source_client: ZendeskClient, dest_client: ZendeskClient, locale_mapping: Dict[str, str] = None):
        """
        Initialize the copier
        
        Args:
            source_client: Client for source Zendesk instance
            dest_client: Client for destination Zendesk instance
            locale_mapping: Optional mapping of source locales to destination locales (e.g., {"en-us": "en-gb"})
        """
        self.source = source_client
        self.dest = dest_client
        self.category_mapping = {}
        self.section_mapping = {}
        self.article_mapping = {}
        self.locale_mapping = locale_mapping or {}
    
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
        # Get destination permission groups to find a valid one to use
        console.print("\n[bold cyan]Fetching permission groups from destination...[/bold cyan]")
        try:
            dest_permission_groups = self.dest.get_permission_groups()
            # Use the first available permission group, or None if none exist
            default_permission_group_id = dest_permission_groups[0]['id'] if dest_permission_groups else 1
            console.print(f"[green]Using permission group ID: {default_permission_group_id}[/green]")
        except Exception as e:
            console.print(f"[yellow]Could not fetch permission groups, using default (1): {e}[/yellow]")
            default_permission_group_id = 1
        
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
                
                # ONLY the absolute minimum required fields
                # Zendesk API rejects articles with extra fields during creation
                body = article.get('body')
                if not body or body.strip() == '':
                    body = '<p>No content</p>'
                
                # Map locale if locale mapping is provided
                source_locale = article.get('locale', 'en-us')
                dest_locale = self.locale_mapping.get(source_locale, source_locale)
                
                # Use destination's permission group since source IDs don't exist in destination
                # Set user_segment_id to null to make it visible to all users
                article_data = {
                    'title': article['title'],
                    'body': body,
                    'locale': dest_locale,
                    'permission_group_id': default_permission_group_id,
                    'user_segment_id': None
                }
                
                try:
                    new_article = self.dest.create_article({'section_id': dest_section_id, **article_data})
                    # Store article mapping for translations
                    self.article_mapping[article['id']] = new_article['id']
                    copied_count += 1
                    progress.advance(task)
                except Exception as e:
                    # Log detailed error for first failure only
                    if copied_count == 0:
                        console.print(f"\n[red]Article creation failed. Error details:[/red]")
                        console.print(f"[yellow]Article: {article['title']}[/yellow]")
                        console.print(f"[yellow]Source permission_group_id: {article.get('permission_group_id')}[/yellow]")
                        console.print(f"[yellow]Payload sent: {article_data}[/yellow]")
                        if hasattr(e, 'response') and hasattr(e.response, 'text'):
                            console.print(f"[yellow]API Response: {e.response.text}[/yellow]")
                        else:
                            console.print(f"[yellow]Error: {str(e)}[/yellow]")
                    progress.advance(task)
        
        console.print(f"[green]✓ Copied {copied_count} articles[/green]")
        return copied_count
    
    def copy_article_translations(self) -> int:
        """
        Copy all article translations from source to destination
        
        Returns:
            Number of translations copied
        """
        console.print("\n[bold cyan]Fetching article translations from source...[/bold cyan]")
        
        translations_to_copy = []
        for source_article_id, dest_article_id in self.article_mapping.items():
            try:
                translations = self.source.get_article_translations(source_article_id)
                # Skip the source locale (already created with the article)
                for translation in translations:
                    if translation.get('locale') != translation.get('source_locale'):
                        translations_to_copy.append({
                            'dest_article_id': dest_article_id,
                            'translation': translation
                        })
            except Exception as e:
                console.print(f"[yellow]Warning: Could not fetch translations for article {source_article_id}: {e}[/yellow]")
        
        if not translations_to_copy:
            console.print("[yellow]No translations found to copy[/yellow]")
            return 0
        
        console.print(f"[green]Found {len(translations_to_copy)} translations[/green]")
        
        copied_count = 0
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        ) as progress:
            task = progress.add_task("[cyan]Copying translations...", total=len(translations_to_copy))
            
            for item in translations_to_copy:
                dest_article_id = item['dest_article_id']
                translation = item['translation']
                
                # Map locale if locale mapping is provided
                source_locale = translation.get('locale')
                dest_locale = self.locale_mapping.get(source_locale, source_locale)
                
                translation_data = {
                    'locale': dest_locale,
                    'title': translation.get('title'),
                    'body': translation.get('body', '<p>No content</p>')
                }
                
                try:
                    self.dest.create_article_translation(dest_article_id, translation_data)
                    copied_count += 1
                    progress.advance(task)
                except Exception as e:
                    console.print(f"[yellow]Warning: Could not copy translation ({translation.get('locale')}): {e}[/yellow]")
                    progress.advance(task)
        
        console.print(f"[green]✓ Copied {copied_count} translations[/green]")
        return copied_count
    
    def copy_all(self):
        """Copy all Help Center content (categories, sections, articles, translations)"""
        console.print("[bold magenta]Starting Help Center copy process...[/bold magenta]")
        
        self.copy_categories()
        self.copy_sections()
        self.copy_articles()
        self.copy_article_translations()
        
        console.print("\n[bold green]✓ Copy process completed![/bold green]")
