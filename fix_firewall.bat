@echo off
REM Fix Windows Firewall for Port 80
REM Must run as Administrator

echo ==========================================
echo Windows Firewall Configuration for Port 80
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

echo [1/3] Checking current firewall rules for port 80...
netsh advfirewall firewall show rule name=all | findstr /i "80"
echo.

echo [2/3] Adding firewall rule to allow port 80 inbound...
netsh advfirewall firewall delete rule name="Google Scraper HTTP" >nul 2>&1
netsh advfirewall firewall add rule name="Google Scraper HTTP" dir=in action=allow protocol=TCP localport=80

if %errorLevel% equ 0 (
    echo [OK] Firewall rule added successfully
) else (
    echo [ERROR] Failed to add firewall rule
    pause
    exit /b 1
)

echo.
echo [3/3] Verifying firewall rule...
netsh advfirewall firewall show rule name="Google Scraper HTTP"
echo.

echo ==========================================
echo Firewall Configuration Complete
echo ==========================================
echo.
echo The firewall should now allow incoming connections on port 80.
echo.
echo Test your server at: http://16.16.249.160
echo.
echo If it still doesn't work, check:
echo   1. AWS Security Group (should allow port 80 from 0.0.0.0/0)
echo   2. Network ACLs in AWS VPC
echo   3. Make sure Flask app is running
echo.
pause

