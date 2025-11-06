"""Zendesk API Client for Help Center operations"""

import requests
from typing import Dict, List, Optional
from requests.auth import HTTPBasicAuth


class ZendeskClient:
    """Client for interacting with Zendesk Help Center API"""
    
    def __init__(self, subdomain: str, email: str, api_token: str):
        """
        Initialize Zendesk client
        
        Args:
            subdomain: Zendesk subdomain (e.g., 'mycompany')
            email: Zendesk account email
            api_token: Zendesk API token
        """
        self.subdomain = subdomain
        self.base_url = f"https://{subdomain}.zendesk.com/api/v2"
        self.auth = HTTPBasicAuth(f"{email}/token", api_token)
        self.session = requests.Session()
        self.session.auth = self.auth
    
    def test_connection(self) -> bool:
        """Test the API connection"""
        try:
            response = self.session.get(f"{self.base_url}/help_center/categories.json")
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException:
            return False
    
    def get_categories(self) -> List[Dict]:
        """Fetch all categories from Help Center"""
        categories = []
        url = f"{self.base_url}/help_center/categories.json"
        
        while url:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            categories.extend(data.get('categories', []))
            url = data.get('next_page')
        
        return categories
    
    def get_sections(self, category_id: Optional[int] = None) -> List[Dict]:
        """Fetch sections, optionally filtered by category"""
        sections = []
        
        if category_id:
            url = f"{self.base_url}/help_center/categories/{category_id}/sections.json"
        else:
            url = f"{self.base_url}/help_center/sections.json"
        
        while url:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            sections.extend(data.get('sections', []))
            url = data.get('next_page')
        
        return sections
    
    def get_articles(self, section_id: Optional[int] = None) -> List[Dict]:
        """Fetch articles, optionally filtered by section"""
        articles = []
        
        if section_id:
            url = f"{self.base_url}/help_center/sections/{section_id}/articles.json"
        else:
            url = f"{self.base_url}/help_center/articles.json"
        
        while url:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            articles.extend(data.get('articles', []))
            url = data.get('next_page')
        
        return articles
    
    def create_category(self, category_data: Dict) -> Dict:
        """Create a new category"""
        url = f"{self.base_url}/help_center/categories.json"
        payload = {"category": category_data}
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()['category']
    
    def create_section(self, section_data: Dict) -> Dict:
        """Create a new section"""
        url = f"{self.base_url}/help_center/sections.json"
        payload = {"section": section_data}
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()['section']
    
    def create_article(self, article_data: Dict) -> Dict:
        """Create a new article"""
        section_id = article_data.get('section_id')
        url = f"{self.base_url}/help_center/sections/{section_id}/articles.json"
        payload = {"article": article_data}
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()['article']
