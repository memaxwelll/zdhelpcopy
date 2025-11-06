"""Check what content exists in destination Help Center"""
import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv

load_dotenv()

email = os.getenv('DEST_ZENDESK_EMAIL')
token = os.getenv('DEST_ZENDESK_API_TOKEN')
subdomain = os.getenv('DEST_ZENDESK_SUBDOMAIN')

auth = HTTPBasicAuth(f'{email}/token', token)
base_url = f'https://{subdomain}.zendesk.com/api/v2'

print(f"Checking {subdomain}.zendesk.com Help Center...\n")

# Check categories
resp = requests.get(f'{base_url}/help_center/categories.json', auth=auth)
categories = resp.json()['categories']
print(f"Categories: {len(categories)}")

# Check one category's translations
if categories:
    cat_id = categories[0]['id']
    resp = requests.get(f'{base_url}/help_center/categories/{cat_id}/translations.json', auth=auth)
    cat_trans = resp.json()['translations']
    print(f"  First category '{categories[0]['name']}' has {len(cat_trans)} translations:")
    for t in cat_trans:
        print(f"    - {t['locale']}: {t['title']}")

# Check sections
resp = requests.get(f'{base_url}/help_center/sections.json', auth=auth)
sections = resp.json()['sections']
print(f"\nSections: {len(sections)}")

if sections:
    sec_id = sections[0]['id']
    resp = requests.get(f'{base_url}/help_center/sections/{sec_id}/translations.json', auth=auth)
    sec_trans = resp.json()['translations']
    print(f"  First section '{sections[0]['name']}' has {len(sec_trans)} translations:")
    for t in sec_trans:
        print(f"    - {t['locale']}: {t['title']}")

# Check articles
resp = requests.get(f'{base_url}/help_center/articles.json', auth=auth)
articles = resp.json()['articles']
print(f"\nArticles: {len(articles)}")

if articles:
    art_id = articles[0]['id']
    resp = requests.get(f'{base_url}/help_center/articles/{art_id}/translations.json', auth=auth)
    art_trans = resp.json()['translations']
    print(f"  First article '{articles[0]['title']}' has {len(art_trans)} translations:")
    for t in art_trans:
        print(f"    - {t['locale']}: {t['title'][:50]}")

# Check available locales
resp = requests.get(f'{base_url}/help_center/locales.json', auth=auth)
locales = resp.json()['locales']
print(f"\nEnabled locales in Help Center: {locales}")

# Check French content specifically
print("\n--- French (fr) Content ---")
resp = requests.get(f'{base_url}/help_center/fr/categories.json', auth=auth)
fr_categories = resp.json()['categories']
print(f"French categories visible: {len(fr_categories)}")

resp = requests.get(f'{base_url}/help_center/fr/sections.json', auth=auth)
fr_sections = resp.json()['sections']
print(f"French sections visible: {len(fr_sections)}")

resp = requests.get(f'{base_url}/help_center/fr/articles.json', auth=auth)
fr_articles = resp.json()['articles']
print(f"French articles visible: {len(fr_articles)}")
