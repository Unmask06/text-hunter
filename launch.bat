@echo off
REM TextHunter Launch Script
REM This script installs dependencies and starts both backend and frontend servers

echo Starting TextHunter Application...

REM Configuration
set BackendPort=8000
set FrontendPort=3000
set BackendUrl=http://localhost:%BackendPort%
set FrontendUrl=http://localhost:%FrontendPort%/

REM Get the script directory
set ScriptDir=%~dp0
echo Working directory: %ScriptDir%
cd /d "%ScriptDir%"

REM Install Backend Dependencies
echo Installing Backend dependencies...
cd /d "%ScriptDir%backend"
uv sync
if errorlevel 1 (
    echo Backend dependency installation failed!
    pause
    exit /b 1
)
cd /d "%ScriptDir%"

REM Install Frontend Dependencies
echo Installing Frontend dependencies...
cd /d "%ScriptDir%frontend"
npm install
if errorlevel 1 (
    echo Frontend dependency installation failed!
    pause
    exit /b 1
)
cd /d "%ScriptDir%"

REM Start Backend
echo Starting Backend (FastAPI)...
start "TextHunter Backend" cmd /k "cd /d "%ScriptDir%backend" && uv run python -m texthunter"

REM Wait for backend
echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

REM Start Frontend
echo Starting Frontend (Vite)...
start "TextHunter Frontend" cmd /k "cd /d "%ScriptDir%frontend" && npm run dev"

REM Wait for frontend
timeout /t 3 /nobreak >nul

REM Open browser
echo Opening browser...
start "" "%FrontendUrl%"

echo Application launched!
echo   Backend:  %BackendUrl%
echo   Frontend: %FrontendUrl%