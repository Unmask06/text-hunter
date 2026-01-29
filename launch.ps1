# TextHunter Launch Script
# This script starts both backend and frontend servers

Write-Host "Starting TextHunter Application..." -ForegroundColor Cyan

# Configuration
$BackendPort = 8000
$FrontendPort = 5173
$BackendUrl = "http://localhost:$BackendPort"
$FrontendUrl = "http://localhost:$FrontendPort"

# Get the script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Write-Host "Working directory: $ScriptDir" -ForegroundColor DarkGray
Set-Location $ScriptDir

# Start Backend
Write-Host "Starting Backend (FastAPI)..." -ForegroundColor Cyan
$backendArgs = "-NoExit", "-Command", "cd '$ScriptDir\backend'; uv run python -m texthunter"
Start-Process powershell -ArgumentList $backendArgs

# Wait for backend
Write-Host "Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Start Frontend
Write-Host "Starting Frontend (Vite)..." -ForegroundColor Cyan
$frontendArgs = "-NoExit", "-Command", "cd '$ScriptDir\frontend'; npm run dev"
Start-Process powershell -ArgumentList $frontendArgs

# Wait for frontend
Start-Sleep -Seconds 3

# Open browser
Write-Host "Opening browser..." -ForegroundColor Cyan
Start-Process $FrontendUrl

Write-Host "Application launched!" -ForegroundColor Green
Write-Host "  Backend:  $BackendUrl" -ForegroundColor White
Write-Host "  Frontend: $FrontendUrl" -ForegroundColor White
