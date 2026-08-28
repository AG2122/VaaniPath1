@echo off
cd /d "D:\New folder\VaaniPath\backend"

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1

echo.
echo ========================================
echo       Starting VaniPath...
echo ========================================
echo.
python -m uvicorn app.main:app

pause