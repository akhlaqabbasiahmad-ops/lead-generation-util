@echo off
REM Fix RDP Access - Must run as Administrator
REM This will restore RDP access while keeping HTTP port 80 open

echo ==========================================
echo Fixing RDP Access
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

echo [1/4] Checking current RDP status...
reg query "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Terminal Server" /v fDenyTSConnections >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] RDP registry key found
) else (
    echo [WARNING] Could not check RDP registry
)

echo.
echo [2/4] Enabling RDP in registry...
reg add "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0 /f >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] RDP enabled in registry
) else (
    echo [ERROR] Failed to enable RDP in registry
)

echo.
echo [3/4] Adding/Verifying RDP firewall rule (Port 3389)...
netsh advfirewall firewall delete rule name="Remote Desktop" >nul 2>&1
netsh advfirewall firewall add rule name="Remote Desktop" dir=in action=allow protocol=TCP localport=3389

if %errorLevel% equ 0 (
    echo [OK] RDP firewall rule added/verified
) else (
    echo [ERROR] Failed to add RDP firewall rule
)

echo.
echo [4/4] Verifying HTTP port 80 rule still exists...
netsh advfirewall firewall show rule name="Google Scraper HTTP" >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] HTTP port 80 rule exists
) else (
    echo [WARNING] HTTP port 80 rule not found, adding it...
    netsh advfirewall firewall add rule name="Google Scraper HTTP" dir=in action=allow protocol=TCP localport=80
)

echo.
echo ==========================================
echo RDP Access Fixed
echo ==========================================
echo.
echo Both RDP (port 3389) and HTTP (port 80) should now work.
echo.
echo If RDP still doesn't work:
echo   1. Check AWS Security Group allows RDP (port 3389)
echo   2. Try reconnecting in a few seconds
echo   3. Use AWS Systems Manager Session Manager as backup
echo.
pause

