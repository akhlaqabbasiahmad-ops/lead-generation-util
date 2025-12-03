@echo off
REM Quick start script - Run the server on port 80
REM Must be run as Administrator

echo Starting Google Business Scraper on port 80...
echo.

REM Check for administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator!
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

python app.py

pause

