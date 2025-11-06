# Zendesk Help Center Copy Tool

## Project Setup Checklist

- [x] Verify that the copilot-instructions.md file in the .github directory is created.
- [x] Clarify Project Requirements
- [x] Scaffold the Project
- [x] Customize the Project
- [x] Install Required Extensions (None required)
- [x] Compile the Project
- [x] Create and Run Task (Not needed for CLI tool)
- [x] Launch the Project
- [x] Ensure Documentation is Complete

## Project Details
- **Type**: Python CLI Tool
- **Purpose**: Interactive tool to copy Zendesk Help Center content between Zendesk instances
- **Framework**: Click (CLI), requests (API calls), rich (terminal UI)
- **Features**: Interactive prompts, progress indicators, error handling, flexible authentication

## Usage
Run the tool with:
```powershell
python -m zdhelpcopy.cli
```

Or with credentials:
```powershell
python -m zdhelpcopy.cli --source-subdomain "source" --source-email "email@example.com" --source-token "token" --dest-subdomain "dest" --dest-email "email@example.com" --dest-token "token"
```

## Development Setup Complete
- Virtual environment created and activated
- All dependencies installed (click, requests, python-dotenv, rich)
- Project structure created with modular components
- Configuration via .env file supported
- Comprehensive README.md with usage instructions
