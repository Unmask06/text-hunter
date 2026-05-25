@echo off
REM TextHunter Launch Script
REM Installs dependencies (if needed), starts backend + frontend, opens browser

echo ========================================
echo   TextHunter - Starting Application
echo ========================================

set BackendPort=8000
set FrontendPort=3000
set BackendUrl=http://localhost:%BackendPort%
set FrontendUrl=http://localhost:%FrontendPort%

cd /d "%~dp0"

REM -----------------------------------------------------------------------
REM Install dependencies (only if missing)
REM -----------------------------------------------------------------------
if not exist "backend\.venv" (
    echo [1/4] Installing Backend dependencies...
    cd /d "%~dp0backend"
    uv sync || ( echo Backend install failed! & pause & exit /b 1 )
    cd /d "%~dp0"
) else (
    echo [1/4] Backend dependencies already installed - skipping
)

if not exist "frontend\node_modules" (
    echo [2/4] Installing Frontend dependencies...
    cd /d "%~dp0frontend"
    npm install || ( echo Frontend install failed! & pause & exit /b 1 )
    cd /d "%~dp0"
) else (
    echo [2/4] Frontend dependencies already installed - skipping
)

REM -----------------------------------------------------------------------
REM Start Backend (FastAPI)
REM -----------------------------------------------------------------------
echo [3/4] Starting Backend on %BackendUrl%...
start "TextHunter Backend" cmd /k "cd /d "%~dp0backend" && uv run python -m texthunter"

REM Wait for backend to be ready
echo Waiting for backend to start...
:wait-backend
timeout /t 2 /nobreak >nul
>nul 2>&1 curl -s "%BackendUrl%/health" && goto backend-ready
echo   Backend not ready yet, retrying...
goto wait-backend
:backend-ready
echo   Backend is ready!

REM -----------------------------------------------------------------------
REM Start Frontend (Vite)
REM -----------------------------------------------------------------------
echo [4/4] Starting Frontend on %FrontendUrl%...
start "TextHunter Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

REM Wait for frontend then open browser
echo Waiting for frontend to start...
:wait-frontend
timeout /t 2 /nobreak >nul
>nul 2>&1 curl -s "%FrontendUrl%" && goto frontend-ready
echo   Frontend not ready yet, retrying...
goto wait-frontend
:frontend-ready
echo   Frontend is ready!

REM -----------------------------------------------------------------------
REM Open browser
REM -----------------------------------------------------------------------
echo Opening browser at %FrontendUrl%
start "" "%FrontendUrl%"

echo ========================================
echo   Application launched!
echo   Backend:  %BackendUrl%
echo   Frontend: %FrontendUrl%
echo ========================================
