@echo off
REM Production Setup Script for Windows Server
REM Run as Administrator

echo ==========================================
echo Production Setup - Google Business Scraper
echo ==========================================
echo.

REM Check for administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator!
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo [1/5] Installing production dependencies...
pip install waitress python-dotenv
if %errorLevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

echo [2/5] Creating required directories...
if not exist "logs" mkdir logs
if not exist "uploads" mkdir uploads
if not exist "excel_results" mkdir excel_results
if not exist "templates" mkdir templates
echo [OK] Directories created
echo.

echo [3/5] Creating .env file (if not exists)...
if not exist .env (
    echo Creating .env file with default values...
    (
        echo FLASK_HOST=0.0.0.0
        echo FLASK_PORT=80
        echo FLASK_SECRET_KEY=CHANGE-THIS-TO-A-RANDOM-SECRET-KEY
        echo WAITRESS_WORKERS=4
        echo WAITRESS_THREADS=4
        echo WAITRESS_CHANNEL_TIMEOUT=300
        echo LOG_LEVEL=INFO
        echo LOG_FILE=logs/app.log
    ) > .env
    echo [OK] .env file created
    echo [WARNING] Please update FLASK_SECRET_KEY in .env file!
) else (
    echo [OK] .env file already exists
)
echo.

echo [4/5] Configuring firewall...
netsh advfirewall firewall delete rule name="Google Scraper HTTP" >nul 2>&1
netsh advfirewall firewall add rule name="Google Scraper HTTP" dir=in action=allow protocol=TCP localport=80
if %errorLevel% equ 0 (
    echo [OK] Firewall rule added for port 80
) else (
    echo [WARNING] Failed to add firewall rule
)
echo.

echo [5/5] Testing production server...
echo.
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo Next steps:
echo.
echo 1. Update .env file with your settings:
echo    - Change FLASK_SECRET_KEY to a random value
echo    - Adjust WAITRESS_WORKERS/THREADS if needed
echo.
echo 2. Test production server:
echo    python run_production.py
echo.
echo 3. Install as Windows Service (optional):
echo    a. Download NSSM from https://nssm.cc/download
echo    b. Extract to C:\nssm\win64
echo    c. Run: C:\nssm\win64\nssm.exe install GoogleScraperService
echo    d. Configure:
echo       - Path: [Your Python path]\python.exe
echo       - Startup directory: [Current directory]
echo       - Arguments: run_production.py
echo    e. Start: C:\nssm\win64\nssm.exe start GoogleScraperService
echo.
echo 4. For SSL/HTTPS, see PRODUCTION_SETUP.md
echo.
echo ==========================================
echo.
pause

