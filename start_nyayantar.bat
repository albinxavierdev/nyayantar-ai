@echo off
echo ========================================
echo    Starting Nyayantar AI Services
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.12+ and try again
    pause
    exit /b 1
)

:: Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 18+ and try again
    pause
    exit /b 1
)

:: Check if .env file exists
if not exist ".env" (
    echo WARNING: .env file not found
    echo Please create .env file with your API keys:
    echo OPENAI_API_KEY=your_key_here
    echo COHERE_API_KEY=your_key_here
    echo.
)

:: Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

:: Get current timestamp for log files
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "timestamp=%dt:~0,8%_%dt:~8,6%"

echo Starting services at %date% %time%...
echo Log files will be saved in logs/ directory
echo.

:: Start Backend API Server in background
echo Starting Backend API Server...
start "Nyayantar Backend" /min cmd /c "python api_server.py > logs/backend_%timestamp%.log 2>&1"

:: Wait a moment for backend to start
timeout /t 3 /nobreak >nul

:: Start Frontend in background
echo Starting Frontend UI...
start "Nyayantar Frontend" /min cmd /c "cd nyayantar-ui && npm start > ../logs/frontend_%timestamp%.log 2>&1"

:: Wait a moment for frontend to start
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo    Services Started Successfully!
echo ========================================
echo.
echo Backend API: http://localhost:8000
echo Frontend UI: http://localhost:3000
echo API Docs:   http://localhost:8000/docs
echo.
echo Services are running in the background
echo Check logs/ directory for output logs
echo.
echo To stop services, run: stop_nyayantar.bat
echo.
pause
