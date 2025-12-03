@echo off
REM Python Installation Helper Script
echo ==========================================
echo Python Installation Checker
echo ==========================================
echo.

REM Check for Python
python --version >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Python is installed!
    python --version
    echo.
    echo Python location:
    where python
    echo.
    echo You can proceed with server setup.
    pause
    exit /b 0
)

py --version >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Python is installed (via py launcher)!
    py --version
    echo.
    echo Python launcher location:
    where py
    echo.
    echo You can proceed with server setup.
    pause
    exit /b 0
)

echo [ERROR] Python is NOT installed or not in PATH!
echo.
echo ==========================================
echo Python Installation Required
echo ==========================================
echo.
echo Please install Python 3.7 or higher from:
echo https://www.python.org/downloads/
echo.
echo IMPORTANT: During installation, check:
echo   [x] Add Python to PATH
echo   [x] Install pip
echo.
echo After installation:
echo   1. Close and reopen this window
echo   2. Run this script again to verify
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
    echo After installing Python, please restart this script.
)

:end
pause

