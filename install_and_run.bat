@echo off
REM Simple install and run script - Tries multiple Python commands
REM Run as Administrator for port 80

echo ==========================================
echo Google Business Scraper - Quick Start
echo ==========================================
echo.

REM Check for administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo WARNING: Not running as Administrator
    echo Port 80 requires admin rights. Continue anyway? (y/n)
    choice /c YN /n
    if errorlevel 2 exit /b 1
    if errorlevel 1 goto :continue
)

:continue
echo.

REM Create directories
if not exist "excel_results" mkdir excel_results
if not exist "uploads" mkdir uploads
if not exist "templates" mkdir templates

echo Installing dependencies...
echo.

REM Try python -m pip first (most reliable on Windows)
python -m pip install -r requirements.txt >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Dependencies installed using: python -m pip
    echo.
    echo Starting server...
    python app.py
    goto :end
)

REM Try py launcher
py -m pip install -r requirements.txt >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Dependencies installed using: py -m pip
    echo.
    echo Starting server...
    py app.py
    goto :end
)

REM Try pip directly
pip install -r requirements.txt >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Dependencies installed using: pip
    echo.
    echo Starting server...
    python app.py
    goto :end
)

echo.
echo ERROR: Could not install dependencies!
echo.
echo Please run manually:
echo   1. python -m pip install -r requirements.txt
echo   2. python app.py
echo.
echo OR if you have py launcher:
echo   1. py -m pip install -r requirements.txt
echo   2. py app.py
echo.

:end
pause

