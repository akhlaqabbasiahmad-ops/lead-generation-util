@echo off
REM Google Business Scraper - Windows Server Setup Script
REM Run this script as Administrator to set up and start the application on port 80

echo ==========================================
echo Google Business Scraper - Server Setup
echo ==========================================
echo.

REM Step 0: Check for Python installation
echo Step 0: Checking Python installation...
python --version >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Python found
    python --version
    set PYTHON_CMD=python
    set PIP_CMD=python -m pip
    goto :check_admin
)

py --version >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Python found (via py launcher)
    py --version
    set PYTHON_CMD=py
    set PIP_CMD=py -m pip
    goto :check_admin
)

echo [ERROR] Python is NOT installed or not in PATH!
echo.
echo ==========================================
echo Python Installation Required
echo ==========================================
echo.
echo Please install Python 3.7 or higher from:
echo   https://www.python.org/downloads/
echo.
echo IMPORTANT: During installation, check:
echo   [x] Add Python to PATH
echo   [x] Install pip
echo.
echo After installation:
echo   1. Close and reopen this window
echo   2. Run this script again
echo.
echo ==========================================
echo.
echo Would you like to open the download page? (Y/N)
choice /c YN /n /m "Open Python download page"
if errorlevel 2 goto :end
if errorlevel 1 (
    start https://www.python.org/downloads/
    echo.
    echo Download page opened in your browser.
    echo Please install Python and run this script again.
    pause
    exit /b 1
)

:end
pause
exit /b 1

:check_admin
REM Check for administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo ERROR: This script must be run as Administrator!
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

REM Step 1: Install Python dependencies
echo.
echo Step 1: Installing Python dependencies...
echo Using: %PIP_CMD%

%PIP_CMD% install -r requirements.txt

if %errorLevel% neq 0 (
    echo.
    echo ERROR: Failed to install dependencies!
    echo.
    echo Trying alternative methods...
    echo.
    
    REM Try pip directly
    pip --version >nul 2>&1
    if %errorLevel% equ 0 (
        echo Trying: pip
        pip install -r requirements.txt
        if %errorLevel% equ 0 goto :deps_installed
    )
    
    REM Try pip3
    pip3 --version >nul 2>&1
    if %errorLevel% equ 0 (
        echo Trying: pip3
        pip3 install -r requirements.txt
        if %errorLevel% equ 0 goto :deps_installed
    )
    
    echo.
    echo All installation methods failed!
    echo Please check your internet connection and try again.
    echo.
    echo Manual installation:
    echo   %PIP_CMD% install -r requirements.txt
    echo.
    pause
    exit /b 1
)

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

REM Run the application using detected Python command
%PYTHON_CMD% app.py

:end

pause

