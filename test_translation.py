"""Test translation creation to debug the 400 error"""
from zdhelpcopy.zendesk_client import ZendeskClient

# Initialize client
client = ZendeskClient('epostgk', 'max.wehner@klara.de', 'rjEjwmSfW6MDnYHuFCjmGadjczm2CCli7UkuuZGt')

# Get first article
articles = client.get_articles()
article = articles[0]

print(f"Testing with article: {article['id']} - {article['title']}")
print(f"Source locale: {article['source_locale']}")

# Check existing translations
translations = client.get_article_translations(article['id'])
print(f"Existing translations: {[t['locale'] for t in translations]}")

# Try to create a translation for a DIFFERENT locale than source
print("\nAttempting to create 'en-150' translation (different from source)...")
try:
    result = client.create_article_translation(
        article['id'], 
        {
            'locale': 'en-150',
            'title': 'Test Title',
            'body': '<p>Test Content</p>'
        }
    )
    print("✓ Success!", result)
except Exception as e:
    print(f"✗ Error: {e}")
    print(f"Error type: {type(e)}")
    if hasattr(e, 'response'):
        print(f"Response status: {e.response.status_code}")
        print(f"Response body: {e.response.text}")
