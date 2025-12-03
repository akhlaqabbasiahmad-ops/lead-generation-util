@echo off
REM Google Business Scraper - Windows Server Setup Script
REM Run this script as Administrator to set up and start the application on port 80

echo ==========================================
echo Google Business Scraper - Server Setup
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

REM Step 1: Install Python dependencies
echo Step 1: Installing Python dependencies...

REM Try different pip commands (Windows can have different Python installations)
echo Checking for Python and pip...

REM Check Python version
python --version >nul 2>&1
if %errorLevel% equ 0 (
    echo Found: python
    python -m pip install -r requirements.txt
    if %errorLevel% equ 0 goto :deps_installed
)

REM Try py launcher
py --version >nul 2>&1
if %errorLevel% equ 0 (
    echo Found: py launcher
    py -m pip install -r requirements.txt
    if %errorLevel% equ 0 goto :deps_installed
)

REM Try pip directly
pip --version >nul 2>&1
if %errorLevel% equ 0 (
    echo Found: pip
    pip install -r requirements.txt
    if %errorLevel% equ 0 goto :deps_installed
)

REM Try pip3
pip3 --version >nul 2>&1
if %errorLevel% equ 0 (
    echo Found: pip3
    pip3 install -r requirements.txt
    if %errorLevel% equ 0 goto :deps_installed
)

echo.
echo ERROR: Could not find Python or pip!
echo.
echo Please ensure Python is installed and in your PATH.
echo You can download Python from: https://www.python.org/downloads/
echo.
echo Or try running manually:
echo   python -m pip install -r requirements.txt
echo   OR
echo   py -m pip install -r requirements.txt
echo.
pause
exit /b 1

:deps_installed

echo [OK] Dependencies installed successfully
echo.

REM Step 2: Create necessary directories
echo Step 2: Creating necessary directories...
if not exist "excel_results" mkdir excel_results
if not exist "uploads" mkdir uploads
if not exist "templates" mkdir templates

echo [OK] Directories created
echo.

REM Step 3: Check if port 80 is available
echo Step 3: Checking port 80 availability...
netstat -ano | findstr ":80 " >nul
if %errorLevel% equ 0 (
    echo [WARNING] Port 80 is already in use
    echo You may need to stop IIS or another web server
    echo.
    netstat -ano | findstr ":80 "
    echo.
    pause
)

REM Step 4: Start the application on port 80
echo.
echo Step 4: Starting application on port 80...
echo ==========================================
echo Server will be accessible at:
echo   - http://localhost
echo   - http://your-server-ip
echo.
echo Press Ctrl+C to stop the server
echo ==========================================
echo.

REM Try different Python commands
python --version >nul 2>&1
if %errorLevel% equ 0 (
    python app.py
    goto :end
)

py --version >nul 2>&1
if %errorLevel% equ 0 (
    py app.py
    goto :end
)

echo ERROR: Could not find Python!
echo Please ensure Python is installed.
pause
exit /b 1

:end

pause

