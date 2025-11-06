# Zendesk Help Center Copy Tool

An interactive CLI tool to copy Zendesk Help Center content (categories, sections, and articles) from one Zendesk instance to another.

## Features

- 🔄 **Complete Copy**: Copies categories, sections, and articles
- 🎯 **Interactive**: Guided prompts for easy configuration
- 📊 **Progress Tracking**: Real-time progress bars and status updates
- 🔐 **Flexible Authentication**: Support for CLI args, environment variables, or interactive input
- ✨ **Rich Output**: Beautiful terminal output with colors and formatting
- 🛡️ **Error Handling**: Graceful error handling with detailed feedback

## Installation

### Prerequisites

- Python 3.7 or higher
- Zendesk account with API access
- API tokens for both source and destination Zendesk instances

### Setup

1. Clone or download this repository
2. Create a virtual environment (recommended):
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

4. (Optional) Install in editable mode:
   ```powershell
   pip install -e .
   ```

## Configuration

### Option 1: Environment Variables (Recommended)

1. Copy `.env.example` to `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```

2. Edit `.env` and fill in your credentials:
   ```
   SOURCE_ZENDESK_SUBDOMAIN=your-source-subdomain
   SOURCE_ZENDESK_EMAIL=your-email@example.com
   SOURCE_ZENDESK_API_TOKEN=your-source-api-token

   DEST_ZENDESK_SUBDOMAIN=your-destination-subdomain
   DEST_ZENDESK_EMAIL=your-email@example.com
   DEST_ZENDESK_API_TOKEN=your-destination-api-token
   ```

### Option 2: Command-Line Arguments

Pass credentials directly when running the tool (see Usage section).

### Option 3: Interactive Prompts

Simply run the tool without credentials, and it will prompt you for the necessary information.

## Getting Zendesk API Tokens

1. Log in to your Zendesk instance
2. Navigate to **Admin** → **Apps and integrations** → **APIs** → **Zendesk API**
3. Click **Settings** tab
4. Enable **Token Access**
5. Click **Add API token**
6. Copy the generated token (you won't be able to see it again!)

## Usage

### Basic Usage (Interactive)

```powershell
python -m zdhelpcopy.cli
```

The tool will guide you through the process with interactive prompts.

### With Environment Variables

If you have a `.env` file configured:

```powershell
python -m zdhelpcopy.cli --yes
```

The `--yes` flag skips confirmation prompts.

### With Command-Line Arguments

```powershell
python -m zdhelpcopy.cli `
  --source-subdomain "source-company" `
  --source-email "user@example.com" `
  --source-token "your-source-token" `
  --dest-subdomain "dest-company" `
  --dest-email "user@example.com" `
  --dest-token "your-dest-token" `
  --yes
```

### If Installed via pip

After running `pip install -e .`, you can use the CLI command directly:

```powershell
zdhelpcopy
```

## What Gets Copied

The tool copies the following Help Center content:

### Categories
- Name
- Description
- Locale
- Position

### Sections
- Name
- Description
- Locale
- Category association
- Position

### Articles
- Title
- Body (HTML content)
- Locale
- Section association
- Position
- Draft status
- Promoted status

## Important Notes

⚠️ **Warning**: This tool creates NEW content in the destination. It does not:
- Delete existing content
- Update existing content
- Check for duplicates

🔒 **Permissions**: Your API tokens must have permission to:
- Read from source Help Center
- Write to destination Help Center

🌍 **Locales**: The tool copies content for the default locale only. Multi-locale content requires additional handling.

📝 **Attachments**: Article attachments and images are not currently copied.

## Troubleshooting

### Connection Errors

If you get connection errors:
1. Verify your subdomain is correct (without `.zendesk.com`)
2. Check that your email and API token are correct
3. Ensure your API token has the necessary permissions

### Import Errors

If you see "Import could not be resolved" errors in VS Code:
1. Make sure the virtual environment is activated
2. Select the correct Python interpreter in VS Code (Ctrl+Shift+P → "Python: Select Interpreter")
3. Restart VS Code if needed

### Rate Limiting

Zendesk API has rate limits. If you hit them:
- The tool will show error messages
- Wait a few minutes and try again
- Consider copying in smaller batches

## Development

### Project Structure

```
zdhelpcopy/
├── .github/
│   └── copilot-instructions.md
├── zdhelpcopy/
│   ├── __init__.py
│   ├── cli.py              # Interactive CLI interface
│   ├── copier.py           # Core copy logic
│   └── zendesk_client.py   # Zendesk API client
├── .env.example
├── .gitignore
├── requirements.txt
├── setup.py
└── README.md
```

### Running Tests

(Tests to be added in future versions)

## Future Enhancements

- [ ] Support for multi-locale content
- [ ] Copy article attachments and images
- [ ] Update existing content instead of only creating new
- [ ] Selective copying (specific categories/sections)
- [ ] Dry-run mode
- [ ] Export to JSON/import from JSON
- [ ] Copy article translations
- [ ] Copy user segments and permissions

## License

MIT License - feel free to use and modify as needed.

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review Zendesk API documentation: https://developer.zendesk.com/api-reference/
3. Open an issue in this repository

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.
