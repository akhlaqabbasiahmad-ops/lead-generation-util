@echo off
REM Restore All Access - RDP and HTTP
REM Must run as Administrator

echo ==========================================
echo Restoring RDP and HTTP Access
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

echo Adding firewall rules for both RDP and HTTP...
echo.

REM Enable RDP
echo [1/3] Enabling RDP (Port 3389)...
reg add "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0 /f >nul 2>&1
netsh advfirewall firewall delete rule name="Remote Desktop" >nul 2>&1
netsh advfirewall firewall add rule name="Remote Desktop" dir=in action=allow protocol=TCP localport=3389
if %errorLevel% equ 0 (
    echo [OK] RDP rule added
) else (
    echo [ERROR] Failed to add RDP rule
)

echo.
echo [2/3] Enabling HTTP (Port 80)...
netsh advfirewall firewall delete rule name="Google Scraper HTTP" >nul 2>&1
netsh advfirewall firewall add rule name="Google Scraper HTTP" dir=in action=allow protocol=TCP localport=80
if %errorLevel% equ 0 (
    echo [OK] HTTP rule added
) else (
    echo [ERROR] Failed to add HTTP rule
)

echo.
echo [3/3] Verifying rules...
echo.
echo RDP Rule (Port 3389):
netsh advfirewall firewall show rule name="Remote Desktop"
echo.
echo HTTP Rule (Port 80):
netsh advfirewall firewall show rule name="Google Scraper HTTP"

echo.
echo ==========================================
echo Configuration Complete
echo ==========================================
echo.
echo Both services should now be accessible:
echo   - RDP: Port 3389
echo   - HTTP: Port 80
echo.
echo IMPORTANT: Also check AWS Security Group:
echo   - RDP (3389) from your IP or 0.0.0.0/0
echo   - HTTP (80) from 0.0.0.0/0
echo.
pause

