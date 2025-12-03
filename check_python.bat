@echo off
REM Check Python Installation
echo ==========================================
echo Checking Python Installation
echo ==========================================
echo.

echo Checking for Python...
python --version >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Found: python
    python --version
    python -m pip --version
    echo.
    echo Python path:
    where python
    echo.
    echo Pip path:
    where pip
    goto :end
)

py --version >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Found: py launcher
    py --version
    py -m pip --version
    echo.
    echo Python path:
    where py
    goto :end
)

echo [ERROR] Python not found!
echo.
echo Please install Python from: https://www.python.org/downloads/
echo Make sure to check "Add Python to PATH" during installation
echo.

:end
echo.
pause

