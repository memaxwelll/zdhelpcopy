"""Check translation status"""
import requests
from requests.auth import HTTPBasicAuth

auth = HTTPBasicAuth('max.schifferle@epostservice.ch/token', 'rjEjwmSfW6MDnYHuFCjmGadjczm2CCli7UkuuZGt')

# Get all articles
resp = requests.get('https://epostgk.zendesk.com/api/v2/help_center/articles.json', auth=auth, params={'per_page': 5})
articles = resp.json()['articles']

print(f"Checking first {len(articles)} articles...\n")

for article in articles:
    print(f"Article: {article['title']}")
    print(f"  ID: {article['id']}")
    print(f"  Source locale: {article['source_locale']}")
    print(f"  Draft: {article['draft']}")
    
    # Get translations
    resp = requests.get(f"https://epostgk.zendesk.com/api/v2/help_center/articles/{article['id']}/translations.json", auth=auth)
    translations = resp.json()['translations']
    
    print(f"  Translations ({len(translations)}):")
    for t in translations:
        status = []
        if t['draft']:
            status.append('DRAFT')
        if t['hidden']:
            status.append('HIDDEN')
        if t['outdated']:
            status.append('OUTDATED')
        status_str = ', '.join(status) if status else 'Published'
        print(f"    - {t['locale']}: {status_str}")
    print()
