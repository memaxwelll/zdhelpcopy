# Zendesk Help Center Copy Tool

<div align="center">

🔄 **Copy Help Center content between Zendesk instances with ease**

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)
[![Non-Commercial](https://img.shields.io/badge/usage-non--commercial-red.svg)](LICENSE)

[Features](#features) • [Quick Start](#quick-start) • [Usage](#usage) • [Documentation](#documentation)

</div>

---

## Overview

An interactive Python CLI tool that copies Help Center content (categories, sections, and articles) from one Zendesk instance to another. Perfect for migrating content, setting up test environments, or duplicating Help Centers.

> ⚠️ **IMPORTANT**: This tool is licensed for **NON-COMMERCIAL USE ONLY**. Commercial use is strictly prohibited. See [License](#license) section for details.
> 
> ⚠️ **DISCLAIMER**: Use at your own risk. Always backup your data and test in a non-production environment first. See [Disclaimer](#haftungsausschluss--disclaimer) section.

## Features

- ✅ **Complete Content Copy** - Categories, sections, and articles
- 🎯 **Smart ID Mapping** - Automatically maintains relationships between content
- 📊 **Progress Tracking** - Real-time progress bars and status updates
- 🔐 **Flexible Authentication** - Environment variables, CLI args, or interactive prompts
- 🎨 **Rich Terminal UI** - Beautiful, colorful output with progress indicators
- 🧹 **Cleanup Utility** - Easily delete all Help Center content
- ⚡ **Pagination Support** - Handles large Help Centers efficiently
- 🛡️ **Error Handling** - Detailed error messages and logging

## Quick Start

### 1. Install

```bash
# Clone the repository
git clone https://github.com/memaxwelll/zdhelpcopy.git
cd zdhelpcopy

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On Windows CMD:
.venv\Scripts\activate.bat
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure

Create a `.env` file with your Zendesk credentials:

```env
# Source Zendesk instance (where to copy FROM)
SOURCE_ZENDESK_SUBDOMAIN=your-source-subdomain
SOURCE_ZENDESK_EMAIL=your-email@example.com
SOURCE_ZENDESK_API_TOKEN=your-source-api-token

# Destination Zendesk instance (where to copy TO)
DEST_ZENDESK_SUBDOMAIN=your-dest-subdomain
DEST_ZENDESK_EMAIL=your-email@example.com
DEST_ZENDESK_API_TOKEN=your-dest-api-token
```

> 💡 **Tip:** Copy `.env.example` to `.env` and fill in your credentials

### 3. Run

```bash
python -m zdhelpcopy.cli
```

That's it! The tool will copy all your Help Center content.

## Usage

### Basic Copy

Copy all Help Center content with interactive prompts:

```bash
python -m zdhelpcopy.cli
```

### Auto-confirm Mode

Skip all confirmation prompts (useful for automation):

```bash
python -m zdhelpcopy.cli --yes
```

### Command-Line Arguments

Provide credentials directly (overrides `.env` file):

```bash
python -m zdhelpcopy.cli \
  --source-subdomain "source" \
  --source-email "email@example.com" \
  --source-token "your-token" \
  --dest-subdomain "dest" \
  --dest-email "email@example.com" \
  --dest-token "your-token"
```

### Cleanup Utility

Delete all Help Center content from an instance:

```bash
# Interactive mode (asks for confirmation)
python -m zdhelpcopy.cleanup

# Auto-confirm mode (dangerous!)
python -m zdhelpcopy.cleanup --yes
```

> ⚠️ **Warning:** The cleanup utility permanently deletes ALL categories, sections, and articles. This action cannot be undone!

## Documentation

### Getting API Tokens

1. Log in to your Zendesk instance (e.g., `https://yoursubdomain.zendesk.com`)
2. Navigate to **Admin** (⚙️) → **Apps and integrations** → **APIs** → **Zendesk API**
3. Under **Settings**, click **Add API token**
4. Enter a description (e.g., "Help Center Copy Tool")
5. Click **Save**
6. **Copy the token immediately** (you won't be able to see it again!)
7. Use the token in your `.env` file or command-line arguments

### Authentication Methods

The tool supports three authentication methods (in order of precedence):

1. **Command-line arguments** - Highest priority
2. **Environment variables** (`.env` file) - Medium priority
3. **Interactive prompts** - Lowest priority (fallback)

### What Gets Copied

| Content Type | Copied Attributes |
|-------------|-------------------|
| **Categories** | Name, Description, Locale, Position |
| **Sections** | Name, Description, Locale, Position, Category relationship |
| **Articles** | Title, Body, Locale, Permission group, User segment |

### ID Mapping

The tool maintains relationships between content:

1. **Categories** are copied first, creating a mapping of source IDs → destination IDs
2. **Sections** use the category mapping to maintain correct parent relationships
3. **Articles** use the section mapping to ensure they're placed in the correct sections

### Permission Groups

Articles require a `permission_group_id` in Zendesk. The tool:
- Fetches available permission groups from the destination instance
- Uses the first available group (typically the default public group)
- Sets `user_segment_id` to `null` to make articles visible to all users

### Error Handling

The tool provides detailed error messages:
- Connection test failures show credential issues
- API errors display the full response for debugging
- First article creation failure shows detailed payload for troubleshooting

## Project Structure

```
zdhelpcopy/
├── zdhelpcopy/
│   ├── __init__.py
│   ├── cli.py              # Main CLI interface with interactive prompts
│   ├── zendesk_client.py   # Zendesk API wrapper (v2 Help Center API)
│   ├── copier.py           # Core copy logic with ID mapping
│   └── cleanup.py          # Utility to delete all Help Center content
├── .env                     # Your credentials (gitignored)
├── .env.example            # Template for credentials
├── requirements.txt        # Python dependencies
├── setup.py               # Package configuration
└── README.md              # This file
```

## Requirements

- **Python:** 3.7 or higher
- **Dependencies:**
  - `click` (8.0+) - CLI framework
  - `requests` (2.25+) - HTTP library
  - `python-dotenv` (0.19+) - Environment variable management
  - `rich` (10.0+) - Rich terminal output

Install all dependencies with:
```bash
pip install -r requirements.txt
```

## Examples

### Example 1: First-Time Setup

```bash
# Clone and setup
git clone https://github.com/memaxwelll/zdhelpcopy.git
cd zdhelpcopy
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your credentials

# Run
python -m zdhelpcopy.cli
```

### Example 2: One-Time Copy

```bash
python -m zdhelpcopy.cli \
  --source-subdomain "production" \
  --source-email "admin@company.com" \
  --source-token "abc123..." \
  --dest-subdomain "staging" \
  --dest-email "admin@company.com" \
  --dest-token "xyz789..." \
  --yes
```

### Example 3: Clean and Copy

```bash
# Delete existing content
python -m zdhelpcopy.cleanup --yes

# Copy fresh content
python -m zdhelpcopy.cli --yes
```

## Troubleshooting

### Authentication Errors

**Problem:** `Could not connect to Zendesk`

**Solutions:**
- Verify your subdomain is correct (don't include `.zendesk.com`)
- Check your email address is correct
- Ensure your API token is valid and not expired
- Make sure you're using `/token` format (handled automatically by the tool)

### Article Creation Failures

**Problem:** Articles fail to copy with 400 errors

**Solutions:**
- Check that permission groups exist in destination
- Verify user segments are configured
- Ensure article content doesn't have destination-specific restrictions

### Rate Limiting

**Problem:** Too many requests error

**Solutions:**
- The tool automatically handles pagination
- For very large Help Centers, consider running during off-peak hours
- Zendesk rate limits vary by plan tier

### Network Issues

**Problem:** Connection timeouts or network errors

**Solutions:**
- Check your internet connection
- Verify firewall isn't blocking Zendesk API
- Try again later if Zendesk is experiencing issues

## FAQ

**Q: Can I copy between different Zendesk plan tiers?**  
A: Yes, as long as both instances have Help Center enabled.

**Q: Will this copy user data or tickets?**  
A: No, only Help Center content (categories, sections, articles).

**Q: Can I copy to multiple destinations?**  
A: Run the tool multiple times with different destination credentials.

**Q: What happens if I interrupt the copy process?**  
A: Partially copied content will remain in the destination. Use the cleanup utility to start fresh.

**Q: Does this copy images and attachments?**  
A: Yes, article body HTML is copied as-is, including image URLs. However, images must be publicly accessible.

## Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

Please ensure your code:
- Follows Python best practices (PEP 8)
- Includes docstrings for new functions
- Works with Python 3.7+

## License

This project is licensed under the **Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0)**.

### You are free to:
- ✅ **Share** — copy and redistribute the material in any medium or format
- ✅ **Adapt** — remix, transform, and build upon the material

### Under the following terms:
- 📝 **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made
- 🚫 **NonCommercial** — You may NOT use the material for commercial purposes

**Commercial use is strictly prohibited.** If you wish to use this tool commercially, please contact the author for licensing options.

For the full license text, see the [LICENSE](LICENSE) file or visit:
https://creativecommons.org/licenses/by-nc/4.0/

## Haftungsausschluss / Disclaimer

### 🇩🇪 Deutsch

⚠️ **WICHTIGER HINWEIS**: Dieses Tool wird "wie besehen" zur Verfügung gestellt, **ohne jegliche Gewährleistung**.

**Der Autor übernimmt keine Haftung für:**
- Datenverlust oder -beschädigung
- Unterbrechungen des Geschäftsbetriebs
- Fehler oder Ausfälle bei der Datenübertragung
- Schäden an Zendesk-Instanzen
- Verlust von Produktivität oder Geschäftsmöglichkeiten

**Sie sind selbst verantwortlich für:**
- ✓ Erstellen von Backups Ihrer Daten vor der Nutzung
- ✓ Testen der Funktionalität in einer Testumgebung
- ✓ Sicherstellen, dass Sie über die erforderlichen Berechtigungen verfügen
- ✓ Einhaltung der Zendesk-Nutzungsbedingungen

**Die Verwendung dieses Tools erfolgt auf eigene Gefahr!**

### 🇬🇧 English

⚠️ **IMPORTANT NOTICE**: This tool is provided "as is", **without warranty of any kind**.

**The author assumes no liability for:**
- Data loss or corruption
- Business interruptions
- Errors or failures in data transmission
- Damage to Zendesk instances
- Loss of productivity or business opportunities

**You are responsible for:**
- ✓ Creating backups of your data before use
- ✓ Testing functionality in a test environment
- ✓ Ensuring you have the necessary permissions
- ✓ Compliance with Zendesk terms of service

**Use of this tool is at your own risk!**

### Best Practices

Before using this tool in production:

1. **🧪 Test First**: Always test in a sandbox or staging environment
2. **💾 Backup**: Create full backups of both source and destination Help Centers
3. **🔐 Permissions**: Verify you have proper API access and permissions
4. **📋 Review**: Check Zendesk API rate limits and terms of service
5. **🔍 Validate**: Review copied content before publishing
6. **📊 Monitor**: Watch for errors during the copy process

## Support

- 📖 [Zendesk API Documentation](https://developer.zendesk.com/api-reference/help_center/help-center-api/introduction/)
- 🐛 [Report Issues](https://github.com/memaxwelll/zdhelpcopy/issues)
- 💬 [Discussions](https://github.com/memaxwelll/zdhelpcopy/discussions)

## Acknowledgments

Built with:
- [Click](https://click.palletsprojects.com/) - Command-line interface framework
- [Rich](https://rich.readthedocs.io/) - Beautiful terminal formatting
- [Requests](https://requests.readthedocs.io/) - HTTP library
- [python-dotenv](https://github.com/theskumar/python-dotenv) - Environment variable management

---

<div align="center">

Made with ❤️ for the Zendesk community

⭐ Star this repo if you find it helpful!

</div>
