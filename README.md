# Kestra CLI (Under Development)

A command-line interface for managing Kestra flows, executions, and namespaces.

## Installation

```bash
# Create virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -e .
```

## Quick Setup

Configure your Kestra instance:

```bash
uv run kestra config add default http://localhost:8080 main --token YOUR_TOKEN --default
```

This creates a configuration file at `~/.kestra/config` with your host, tenant, and authentication token.

## Usage

### Get a flow

```bash
uv run kestra flows get <namespace> <flow_id>
```

### Run an execution

```bash
uv run kestra executions run <namespace> <flow_id>
```

### Deploy a flow

```bash
uv run kestra flows deploy path/to/flow.yaml
```

### Additional Options

All commands support `--output json` for JSON output and can override config with `--host`, `--tenant`, and `--token` flags:

```bash
uv run kestra flows get my.namespace my-flow --output json --host http://localhost:8080 --token YOUR_TOKEN
```

## Development

The project structure:

- `src/api_client/`: API client modules
- `src/cli/`: CLI command modules
- `src/main_cli.py`: Main entrypoint

### Setup

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
uv run kestra --help
```

## Requirements

- Python 3.12+
- uv (dependency management)
- typer, httpx, rich
