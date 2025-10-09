# Kestra CLI (Under Development)

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

# Deploy a flow from a YAML file (creates new or updates existing)
uv run kestra flows deploy <path/to/flow.yaml>

# Deploy a flow with override (skip existence check)
uv run kestra flows deploy <path/to/flow.yaml> --override
```

#### Namespaces
```bash
# List all namespaces (uses tenant from default context)
uv run kestra namespaces list

# List all namespaces with specific tenant
uv run kestra namespaces list --tenant main

# Search for specific namespaces
uv run kestra namespaces list --query "myproject"
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
# List all namespaces for the 'main' tenant
uv run kestra namespaces list --host http://localhost:8080 --token YOUR_TOKEN --tenant main

# List all namespaces in JSON format
uv run kestra namespaces list --host http://localhost:8080 --token YOUR_TOKEN --tenant main --output json

# Search for namespaces matching a query
uv run kestra namespaces list --query "company" --host http://localhost:8080 --token YOUR_TOKEN --tenant main

# List flows in the 'company.team' namespace
uv run kestra flows list company.team --host http://localhost:8080 --token YOUR_TOKEN

# Get a specific flow in JSON format
uv run kestra flows get company.team concurrency_limits_demo --host http://localhost:8080 --token YOUR_TOKEN --output json

# Deploy a flow from a YAML file
uv run kestra flows deploy examples/my-flow.yaml --host http://localhost:8080 --token YOUR_TOKEN

# Deploy a flow with override
uv run kestra flows deploy examples/my-flow.yaml --host http://localhost:8080 --token YOUR_TOKEN --override

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
