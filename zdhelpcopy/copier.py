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
        
        # Get existing categories in destination
        console.print("[cyan]Checking for existing categories in destination...[/cyan]")
        dest_categories = self.dest.get_categories()
        dest_categories_by_name = {cat['name']: cat for cat in dest_categories}
        
        created_count = 0
        skipped_count = 0
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        ) as progress:
            task = progress.add_task("[cyan]Processing categories...", total=len(source_categories))
            
            for category in source_categories:
                category_name = category['name']
                
                # Check if category already exists
                if category_name in dest_categories_by_name:
                    existing_category = dest_categories_by_name[category_name]
                    self.category_mapping[category['id']] = existing_category['id']
                    skipped_count += 1
                    progress.advance(task)
                    continue
                
                category_data = {
                    'name': category_name,
                    'description': category.get('description', ''),
                    'locale': category.get('locale', 'en-us'),
                    'position': category.get('position', 0)
                }
                
                try:
                    new_category = self.dest.create_category(category_data)
                    self.category_mapping[category['id']] = new_category['id']
                    created_count += 1
                    progress.advance(task)
                except Exception as e:
                    console.print(f"[red]Error copying category '{category_name}': {e}[/red]")
        
        console.print(f"[green]✓ Created {created_count} categories, skipped {skipped_count} existing[/green]")
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
        
        # Get existing sections in destination
        console.print("[cyan]Checking for existing sections in destination...[/cyan]")
        dest_sections = self.dest.get_sections()
        # Group by category_id and name for lookup
        dest_sections_by_key = {(sec['category_id'], sec['name']): sec for sec in dest_sections}
        
        created_count = 0
        skipped_count = 0
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        ) as progress:
            task = progress.add_task("[cyan]Processing sections...", total=len(source_sections))
            
            for section in source_sections:
                source_category_id = section.get('category_id')
                dest_category_id = self.category_mapping.get(source_category_id)
                
                if not dest_category_id:
                    console.print(f"[yellow]Warning: Skipping section '{section['name']}' - category not found[/yellow]")
                    progress.advance(task)
                    continue
                
                section_name = section['name']
                section_key = (dest_category_id, section_name)
                
                # Check if section already exists in this category
                if section_key in dest_sections_by_key:
                    existing_section = dest_sections_by_key[section_key]
                    self.section_mapping[section['id']] = existing_section['id']
                    skipped_count += 1
                    progress.advance(task)
                    continue
                
                section_data = {
                    'name': section_name,
                    'description': section.get('description', ''),
                    'locale': section.get('locale', 'en-us'),
                    'category_id': dest_category_id,
                    'position': section.get('position', 0)
                }
                
                try:
                    new_section = self.dest.create_section(section_data)
                    self.section_mapping[section['id']] = new_section['id']
                    created_count += 1
                    progress.advance(task)
                except Exception as e:
                    console.print(f"[red]Error copying section '{section_name}': {e}[/red]")
        
        console.print(f"[green]✓ Created {created_count} sections, skipped {skipped_count} existing[/green]")
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
        
        # Get existing articles in destination
        console.print("[cyan]Checking for existing articles in destination...[/cyan]")
        dest_articles = self.dest.get_articles()
        # Group by section_id and title for lookup
        dest_articles_by_key = {(art['section_id'], art['title']): art for art in dest_articles}
        
        copied_count = 0
        skipped_count = 0
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        ) as progress:
            task = progress.add_task("[cyan]Processing articles...", total=len(source_articles))
            
            for article in source_articles:
                source_section_id = article.get('section_id')
                dest_section_id = self.section_mapping.get(source_section_id)
                
                if not dest_section_id:
                    console.print(f"[yellow]Warning: Skipping article '{article['title']}' - section not found[/yellow]")
                    progress.advance(task)
                    continue
                
                article_title = article['title']
                article_key = (dest_section_id, article_title)
                
                # Check if article already exists in this section
                if article_key in dest_articles_by_key:
                    existing_article = dest_articles_by_key[article_key]
                    self.article_mapping[article['id']] = existing_article['id']
                    skipped_count += 1
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
                    'title': article_title,
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
                        console.print(f"[yellow]Article: {article_title}[/yellow]")
                        console.print(f"[yellow]Source permission_group_id: {article.get('permission_group_id')}[/yellow]")
                        console.print(f"[yellow]Payload sent: {article_data}[/yellow]")
                        if hasattr(e, 'response') and hasattr(e.response, 'text'):
                            console.print(f"[yellow]API Response: {e.response.text}[/yellow]")
                        else:
                            console.print(f"[yellow]Error: {str(e)}[/yellow]")
                    progress.advance(task)
        
        console.print(f"[green]✓ Created {copied_count} articles, skipped {skipped_count} existing[/green]")
        return copied_count
    
    def copy_category_translations(self) -> int:
        """
        Copy all category translations from source to destination
        
        Returns:
            Number of translations copied
        """
        console.print("\n[bold cyan]Copying category translations...[/bold cyan]")
        
        copied_count = 0
        skipped_count = 0
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        ) as progress:
            task = progress.add_task("[cyan]Processing category translations...", total=len(self.category_mapping))
            
            for source_cat_id, dest_cat_id in self.category_mapping.items():
                try:
                    # Get source translations
                    source_translations = self.source.get_category_translations(source_cat_id)
                    
                    # Get existing destination translations
                    dest_translations = self.dest.get_category_translations(dest_cat_id)
                    existing_locales = {t['locale'] for t in dest_translations}
                    
                    # Copy missing translations
                    for translation in source_translations:
                        source_locale = translation['locale']
                        dest_locale = self.locale_mapping.get(source_locale, source_locale)
                        
                        if dest_locale not in existing_locales:
                            translation_data = {
                                'locale': dest_locale,
                                'title': translation['title'],
                                'body': translation.get('body', '')
                            }
                            try:
                                self.dest.create_category_translation(dest_cat_id, translation_data)
                                copied_count += 1
                            except Exception as e:
                                console.print(f"[yellow]Warning: Could not copy category translation ({dest_locale}): {e}[/yellow]")
                                skipped_count += 1
                        else:
                            skipped_count += 1
                except Exception as e:
                    console.print(f"[yellow]Warning: Could not process category {source_cat_id}: {e}[/yellow]")
                
                progress.advance(task)
        
        console.print(f"[green]✓ Copied {copied_count} category translations, skipped {skipped_count} existing[/green]")
        return copied_count
    
    def copy_section_translations(self) -> int:
        """
        Copy all section translations from source to destination
        
        Returns:
            Number of translations copied
        """
        console.print("\n[bold cyan]Copying section translations...[/bold cyan]")
        
        copied_count = 0
        skipped_count = 0
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        ) as progress:
            task = progress.add_task("[cyan]Processing section translations...", total=len(self.section_mapping))
            
            for source_sec_id, dest_sec_id in self.section_mapping.items():
                try:
                    # Get source translations
                    source_translations = self.source.get_section_translations(source_sec_id)
                    
                    # Get existing destination translations
                    dest_translations = self.dest.get_section_translations(dest_sec_id)
                    existing_locales = {t['locale'] for t in dest_translations}
                    
                    # Copy missing translations
                    for translation in source_translations:
                        source_locale = translation['locale']
                        dest_locale = self.locale_mapping.get(source_locale, source_locale)
                        
                        if dest_locale not in existing_locales:
                            translation_data = {
                                'locale': dest_locale,
                                'title': translation['title'],
                                'body': translation.get('body', '')
                            }
                            try:
                                self.dest.create_section_translation(dest_sec_id, translation_data)
                                copied_count += 1
                            except Exception as e:
                                console.print(f"[yellow]Warning: Could not copy section translation ({dest_locale}): {e}[/yellow]")
                                skipped_count += 1
                        else:
                            skipped_count += 1
                except Exception as e:
                    console.print(f"[yellow]Warning: Could not process section {source_sec_id}: {e}[/yellow]")
                
                progress.advance(task)
        
        console.print(f"[green]✓ Copied {copied_count} section translations, skipped {skipped_count} existing[/green]")
        return copied_count
    
    def copy_article_translations(self) -> int:
        """
        Copy all article translations from source to destination
        
        Returns:
            Number of translations copied
        """
        console.print("\n[bold cyan]Fetching article translations from source...[/bold cyan]")
        
        translations_to_copy = []
        existing_translations = {}
        
        # Get existing translations for all destination articles
        console.print("[cyan]Checking for existing translations in destination...[/cyan]")
        for source_article_id, dest_article_id in self.article_mapping.items():
            try:
                dest_translations = self.dest.get_article_translations(dest_article_id)
                existing_translations[dest_article_id] = {t['locale'] for t in dest_translations}
            except:
                existing_translations[dest_article_id] = set()
        
        # Collect translations to copy
        for source_article_id, dest_article_id in self.article_mapping.items():
            try:
                translations = self.source.get_article_translations(source_article_id)
                # Skip the source locale (already created with the article)
                for translation in translations:
                    source_locale = translation.get('locale')
                    if source_locale != translation.get('source_locale'):
                        # Apply locale mapping
                        dest_locale = self.locale_mapping.get(source_locale, source_locale)
                        
                        # Skip if translation already exists
                        if dest_locale not in existing_translations.get(dest_article_id, set()):
                            translations_to_copy.append({
                                'dest_article_id': dest_article_id,
                                'translation': translation,
                                'dest_locale': dest_locale
                            })
            except Exception as e:
                console.print(f"[yellow]Warning: Could not fetch translations for article {source_article_id}: {e}[/yellow]")
        
        if not translations_to_copy:
            console.print("[yellow]No new translations to copy (all already exist)[/yellow]")
            return 0
        
        console.print(f"[green]Found {len(translations_to_copy)} new translations to copy[/green]")
        
        copied_count = 0
        skipped_count = 0
        failed_locales = {}
        
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
                dest_locale = item['dest_locale']
                
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
                    # Track failed locales
                    error_str = str(e)
                    if '400' in error_str:
                        failed_locales[dest_locale] = failed_locales.get(dest_locale, 0) + 1
                    skipped_count += 1
                    progress.advance(task)
        
        console.print(f"[green]✓ Copied {copied_count} translations[/green]")
        
        if failed_locales:
            console.print(f"\n[yellow]⚠️  Translation warnings:[/yellow]")
            for locale, count in failed_locales.items():
                console.print(f"[yellow]  • {count} translations failed for locale '{locale}' - ensure this language is enabled in destination[/yellow]")
            console.print(f"\n[cyan]To enable missing languages:[/cyan]")
            console.print(f"[cyan]  1. Go to Admin → Guide → Guide admin[/cyan]")
            console.print(f"[cyan]  2. Navigate to Languages/Settings[/cyan]")
            console.print(f"[cyan]  3. Click 'Add language' and enable: {', '.join(failed_locales.keys())}[/cyan]")
        
        return copied_count
    
    def copy_all(self):
        """Copy all Help Center content (categories, sections, articles, translations)"""
        console.print("[bold magenta]Starting Help Center copy process...[/bold magenta]")
        
        self.copy_categories()
        self.copy_category_translations()
        self.copy_sections()
        self.copy_section_translations()
        self.copy_articles()
        self.copy_article_translations()
        
        console.print("\n[bold green]✓ Copy process completed![/bold green]")
