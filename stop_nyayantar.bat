@echo off
echo ========================================
echo    Stopping Nyayantar AI Services
echo ========================================
echo.

:: Kill Python processes running api_server.py
echo Stopping Backend API Server...
taskkill /f /im python.exe /fi "WINDOWTITLE eq Nyayantar Backend*" >nul 2>&1
taskkill /f /im python.exe /fi "WINDOWTITLE eq *api_server.py*" >nul 2>&1

:: Kill Node.js processes running npm start
echo Stopping Frontend UI...
taskkill /f /im node.exe /fi "WINDOWTITLE eq Nyayantar Frontend*" >nul 2>&1
taskkill /f /im node.exe /fi "WINDOWTITLE eq *npm start*" >nul 2>&1

:: Kill any remaining processes on ports 8000 and 3000
echo Stopping processes on ports 8000 and 3000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000') do taskkill /f /pid %%a >nul 2>&1

:: Close any remaining command windows with Nyayantar titles
echo Closing service windows...
taskkill /f /fi "WINDOWTITLE eq Nyayantar Backend*" >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq Nyayantar Frontend*" >nul 2>&1

echo.
echo ========================================
echo    Services Stopped Successfully!
echo ========================================
echo.
echo All Nyayantar AI services have been stopped
echo Ports 8000 and 3000 are now free
echo.
pause
