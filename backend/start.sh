#!/bin/bash
set -e

# Debug: Environment variables
echo "=== Environment Debug ==="
echo "PORT environment variable: ${PORT}"
echo "All environment variables:"
env | grep -i port || echo "No PORT variables found"
echo "========================="

# Render otomatik olarak PORT environment variable'ını set eder
PORT=${PORT:-10000}

echo "Starting PhotoID API on port $PORT"
echo "Application will be available at: http://0.0.0.0:$PORT"

# Start the application with more verbose logging
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port $PORT \
    --log-level info \
    --access-log