#!/bin/bash
# TextHunter Launch Script for Git Bash on Windows
# This script starts both backend and frontend servers

echo "Starting TextHunter Application..."

# Configuration
BACKEND_PORT=8000
FRONTEND_PORT=3000
BACKEND_URL="http://localhost:${BACKEND_PORT}"
FRONTEND_URL="http://localhost:${FRONTEND_PORT}/"

# Get the script directory (Windows-compatible for Git Bash)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Working directory: ${SCRIPT_DIR}"
cd "${SCRIPT_DIR}" || exit 1

# Convert to Windows path for cmd commands
WIN_SCRIPT_DIR="${SCRIPT_DIR}"

# Start Backend in new window
echo "Starting Backend (FastAPI)..."
start "" "cmd" "/c" "cd /d \"${WIN_SCRIPT_DIR}backend\" && uv run python -m texthunter"

# Wait for backend
echo "Waiting for backend to start (5 seconds)..."
sleep 5

# Start Frontend in new window
echo "Starting Frontend (Vite)..."
start "" "cmd" "/c" "cd /d \"${WIN_SCRIPT_DIR}frontend\" && npm run dev"

# Wait for frontend
echo "Waiting for frontend to start (3 seconds)..."
sleep 3

# Open browser
echo "Opening browser..."
start "" "${FRONTEND_URL}"

echo "Application launched!"
echo "  Backend:  ${BACKEND_URL}"
echo "  Frontend: ${FRONTEND_URL}"
