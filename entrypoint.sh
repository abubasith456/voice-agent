#!/bin/bash

set -e

# Activate the virtual environment
source /app/.venv/bin/activate

# Start the uvicorn server
uv run worker.py download-files && uv run worker.py start
