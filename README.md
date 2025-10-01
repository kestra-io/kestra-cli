# Kestra CLI

A command-line interface for managing Kestra flows.

## Installation

### Development Setup

1. Create a virtual environment with `uv`:
```bash
uv venv
source .venv/bin/activate
```

2. Install dependencies:
```bash
uv pip install -e .
```

3. Setup authentication (optional - you can also use CLI flags):
```bash
uv run kestra config add default http://localhost:8080 main --token YOUR_TOKEN --default
```

## Usage

### Basic Commands

#### Flows
```bash
# List flows in a namespace
uv run kestra flows list <namespace>

# Get a specific flow
uv run kestra flows get <namespace> <flow_id>
```

### Authentication

You can authenticate in several ways:

1. **Using CLI flags** (recommended for testing):
```bash
uv run kestra flows list <namespace> --host http://localhost:8080 --token YOUR_TOKEN
```

2. **Using configuration file** (after running `uv run kestra config add`):
```bash
uv run kestra flows list <namespace>
```

### Output Formats

All commands support two output formats:

- **Table format** (default): Human-readable tables
- **JSON format**: Machine-readable JSON output

Use the `--output json` flag to get JSON output:
```bash
uv run kestra flows list <namespace> --output json
```

### Examples

```bash
# List flows in the 'company.team' namespace
uv run kestra flows list company.team --host http://localhost:8080 --token YOUR_TOKEN

# Get a specific flow in JSON format
uv run kestra flows get company.team concurrency_limits_demo --host http://localhost:8080 --token YOUR_TOKEN --output json

# Show version information
uv run kestra version
```

## Configuration

The CLI stores authentication information in `~/.kestra/config`. You can manage multiple contexts and switch between them.

### Config Commands

```bash
# Show current configuration
uv run kestra config show

# Add a new authentication context
uv run kestra config add <name> <host> <tenant> --token <token> [--default]

# Remove a context
uv run kestra config remove <name>

# Set a context as default
uv run kestra config use <name>
```

### Examples

```bash
# Add a context and set it as default
uv run kestra config add default http://localhost:8080 main --token YOUR_TOKEN --default

# Add another context
uv run kestra config add production https://kestra.company.com main --token PROD_TOKEN

# Switch to production context
uv run kestra config use production

# Show all contexts
uv run kestra config show
```

## Development

The project follows a modular structure:

- `src/api_client/`: API client modules for different endpoints
- `src/cli/`: CLI command modules
- `src/main_cli.py`: Main CLI entrypoint

### Development Setup

1. Create virtual environment:
```bash
uv venv
source .venv/bin/activate
```

2. Install dependencies:
```bash
uv pip install -e .
```

3. Run the CLI:
```bash
uv run kestra --help
```

## Requirements

- Python 3.12+
- uv (for dependency management)
- typer
- httpx
- rich
