@echo off
REM Check Public IP Address
echo ==========================================
echo Public IP Address Checker
echo ==========================================
echo.

echo Checking your public IP address...
echo.

REM Try multiple methods to get public IP
echo Method 1: ifconfig.me
curl -s http://ifconfig.me/ip
if %errorLevel% equ 0 (
    echo.
    echo.
    goto :show_info
)

echo Method 2: ipify.org
curl -s https://api.ipify.org
if %errorLevel% equ 0 (
    echo.
    echo.
    goto :show_info
)

echo Method 3: icanhazip.com
curl -s http://icanhazip.com
if %errorLevel% equ 0 (
    echo.
    echo.
    goto :show_info
)

echo.
echo [ERROR] Could not retrieve public IP
echo Please check your internet connection
echo.
echo You can also visit: https://whatismyipaddress.com/
pause
exit /b 1

:show_info
echo ==========================================
echo Your Public IP Address (shown above)
echo ==========================================
echo.
echo Your server should be accessible at:
echo   http://[IP_ADDRESS_SHOWN_ABOVE]
echo.
echo IMPORTANT: Make sure:
echo   1. Port 80 is open in firewall
echo   2. Security group allows port 80 (if AWS)
echo   3. Router port forwarding is configured (if behind NAT)
echo.
echo ==========================================
echo.
pause

