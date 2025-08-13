#!/bin/bash
set -e

# Change to the correct working directory
cd /home/user/app

# Activate the virtual environment
source .venv/bin/activate

# Set Python path
export PYTHONPATH=/home/user/app:$PYTHONPATH

# Run download-files
python worker.py download-files

# Function to cleanup background processes on exit
cleanup() {
    echo "Stopping processes..."
    kill $WORKER_PID 2>/dev/null || true
    exit
}
trap cleanup SIGTERM SIGINT

# Start worker in background and capture PID
python worker.py start &
WORKER_PID=$!

# Start health server in foreground (this will keep the script running)
python health.py
