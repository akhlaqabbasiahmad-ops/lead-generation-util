@echo off
REM Install Windows Service using NSSM
REM Must run as Administrator

echo ==========================================
echo Install Windows Service - NSSM Setup
echo ==========================================
echo.

REM Check for administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator!
    pause
    exit /b 1
)

REM Check if NSSM exists
if not exist "C:\nssm\win64\nssm.exe" (
    echo [ERROR] NSSM not found at C:\nssm\win64\nssm.exe
    echo.
    echo Please:
    echo 1. Download NSSM from: https://nssm.cc/download
    echo 2. Extract to: C:\nssm\win64
    echo 3. Run this script again
    echo.
    pause
    exit /b 1
)

echo [1/4] Finding Python executable...
where python >nul 2>&1
if %errorLevel% equ 0 (
    for /f "delims=" %%i in ('where python') do set PYTHON_PATH=%%i
    echo [OK] Found Python: %PYTHON_PATH%
) else (
    echo [ERROR] Python not found in PATH
    echo Please provide Python path manually
    set /p PYTHON_PATH="Enter Python executable path: "
)

echo.
echo [2/4] Getting current directory...
cd
set CURRENT_DIR=%CD%
echo [OK] Working directory: %CURRENT_DIR%
echo.

echo [3/4] Installing service...
C:\nssm\win64\nssm.exe install GoogleScraperService "%PYTHON_PATH%" "run_production.py"
if %errorLevel% neq 0 (
    echo [ERROR] Failed to install service
    pause
    exit /b 1
)

echo [OK] Service installed
echo.

echo [4/4] Configuring service...
C:\nssm\win64\nssm.exe set GoogleScraperService AppDirectory "%CURRENT_DIR%"
C:\nssm\win64\nssm.exe set GoogleScraperService Description "Google Business Scraper Web Application - Production Service"
C:\nssm\win64\nssm.exe set GoogleScraperService Start SERVICE_AUTO_START
C:\nssm\win64\nssm.exe set GoogleScraperService AppStdout "%CURRENT_DIR%\logs\service_output.log"
C:\nssm\win64\nssm.exe set GoogleScraperService AppStderr "%CURRENT_DIR%\logs\service_error.log"

echo [OK] Service configured
echo.

echo ==========================================
echo Service Installation Complete
echo ==========================================
echo.
echo Service Name: GoogleScraperService
echo.
echo Useful commands:
echo   Start:   C:\nssm\win64\nssm.exe start GoogleScraperService
echo   Stop:    C:\nssm\win64\nssm.exe stop GoogleScraperService
echo   Restart: C:\nssm\win64\nssm.exe restart GoogleScraperService
echo   Status:  C:\nssm\win64\nssm.exe status GoogleScraperService
echo   Remove:  C:\nssm\win64\nssm.exe remove GoogleScraperService confirm
echo.
echo Start the service now? (Y/N)
choice /c YN /n
if errorlevel 2 goto :end
if errorlevel 1 (
    echo.
    echo Starting service...
    C:\nssm\win64\nssm.exe start GoogleScraperService
    timeout /t 3 /nobreak >nul
    C:\nssm\win64\nssm.exe status GoogleScraperService
)

:end
echo.
pause

