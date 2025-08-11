#!/bin/bash
set -e

# Change to the correct working directory
cd /home/user/app

# Activate the virtual environment (correct path for HF user setup)
source .venv/bin/activate

# Set Python path
export PYTHONPATH=/home/user/app:$PYTHONPATH

# Run your worker commands (use python directly, not uv run)
python worker.py download-files && python worker.py start
