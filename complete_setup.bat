@echo off
REM Complete Setup Script - Checks Python, Installs Dependencies, and Runs Server
REM Run as Administrator for port 80

echo ==========================================
echo Google Business Scraper - Complete Setup
echo ==========================================
echo.

REM Step 1: Check Python Installation
echo [1/4] Checking Python installation...
call install_python.bat
if %errorLevel% neq 0 (
    echo.
    echo Setup cannot continue without Python.
    echo Please install Python and run this script again.
    pause
    exit /b 1
)

echo.
echo [2/4] Python is installed. Proceeding...
echo.

REM Step 2: Check for administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [WARNING] Not running as Administrator
    echo Port 80 requires admin rights.
    echo.
    choice /c YN /n /m "Continue anyway (will use port 5000)?"
    if errorlevel 2 exit /b 1
    if errorlevel 1 (
        set FLASK_PORT=5000
        set FLASK_HOST=0.0.0.0
    )
)

REM Step 3: Install Dependencies
echo.
echo [3/4] Installing Python dependencies...

REM Detect Python command
python --version >nul 2>&1
if %errorLevel% equ 0 (
    set PYTHON_CMD=python
    set PIP_CMD=python -m pip
) else (
    set PYTHON_CMD=py
    set PIP_CMD=py -m pip
)

echo Using: %PIP_CMD%
%PIP_CMD% install -r requirements.txt

if %errorLevel% neq 0 (
    echo.
    echo ERROR: Failed to install dependencies!
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)

echo [OK] Dependencies installed successfully!
echo.

REM Step 4: Create Directories
echo [4/4] Creating required directories...
if not exist "excel_results" mkdir excel_results
if not exist "uploads" mkdir uploads
if not exist "templates" mkdir templates
echo [OK] Directories created
echo.

REM Step 5: Start Server
echo ==========================================
echo Starting Server...
echo ==========================================
echo.
if defined FLASK_PORT (
    echo Server will run on port %FLASK_PORT% (non-admin mode)
    echo Access at: http://localhost:%FLASK_PORT%
) else (
    echo Server will run on port 80 (admin mode)
    echo Access at: http://localhost
)
echo.
echo Press Ctrl+C to stop the server
echo ==========================================
echo.

%PYTHON_CMD% app.py

pause

