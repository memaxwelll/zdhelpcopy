"""Check French Help Center content"""
import requests
from requests.auth import HTTPBasicAuth

auth = HTTPBasicAuth('max.schifferle@epostservice.ch/token', 'rjEjwmSfW6MDnYHuFCjmGadjczm2CCli7UkuuZGt')

# Check categories in French
resp = requests.get('https://epostgk.zendesk.com/api/v2/help_center/fr/categories.json', auth=auth)
categories = resp.json()['categories']
print(f"French categories: {len(categories)}")
for cat in categories[:3]:
    print(f"  - {cat['name']} (id: {cat['id']})")

# Check sections in French
resp = requests.get('https://epostgk.zendesk.com/api/v2/help_center/fr/sections.json', auth=auth)
sections = resp.json()['sections']
print(f"\nFrench sections: {len(sections)}")
for sec in sections[:3]:
    print(f"  - {sec['name']} (id: {sec['id']})")

# Check articles in French
resp = requests.get('https://epostgk.zendesk.com/api/v2/help_center/fr/articles.json', auth=auth)
articles = resp.json()['articles']
print(f"\nFrench articles: {len(articles)}")
for art in articles[:3]:
    print(f"  - {art['title']} (id: {art['id']}, locale: {art['locale']})")
