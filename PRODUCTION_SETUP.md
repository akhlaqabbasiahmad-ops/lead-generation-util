# Production Setup Guide - Windows Server

## Overview

This guide will help you set up the Google Business Scraper for production use on Windows Server with:
- ✅ Production WSGI server (Waitress)
- ✅ Windows Service (auto-start, auto-restart)
- ✅ Security hardening
- ✅ SSL/HTTPS support
- ✅ Monitoring and logging

---

## Prerequisites

- Windows Server (2016 or later recommended)
- Python 3.7+ installed
- Administrator access
- Domain name (optional, for SSL)

---

## Step 1: Install Production Dependencies

```cmd
# Install Waitress (production WSGI server for Windows)
pip install waitress

# Install other production tools
pip install python-dotenv
```

Update `requirements.txt`:
```txt
waitress>=3.0.0
python-dotenv>=1.0.0
```

---

## Step 2: Create Production Configuration

### Create `production_config.py`:

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Production settings
PRODUCTION = True
DEBUG = False
HOST = os.getenv('FLASK_HOST', '0.0.0.0')
PORT = int(os.getenv('FLASK_PORT', 80))
WORKERS = int(os.getenv('WAITRESS_WORKERS', 4))
THREADS = int(os.getenv('WAITRESS_THREADS', 4))

# Security
SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'change-this-in-production')
SESSION_COOKIE_SECURE = True  # For HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
```

### Create `.env` file:

```env
FLASK_HOST=0.0.0.0
FLASK_PORT=80
FLASK_SECRET_KEY=your-super-secret-key-change-this
WAITRESS_WORKERS=4
WAITRESS_THREADS=4
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

---

## Step 3: Create Production Server Script

### Create `run_production.py`:

```python
"""
Production server using Waitress WSGI server
"""
import os
import sys
from waitress import serve
from app import app

# Production configuration
HOST = os.getenv('FLASK_HOST', '0.0.0.0')
PORT = int(os.getenv('FLASK_PORT', 80))
THREADS = int(os.getenv('WAITRESS_THREADS', 4))
CHANNEL_TIMEOUT = 120  # 2 minutes for long-running scrapes

if __name__ == '__main__':
    print("=" * 50)
    print("Google Business Scraper - Production Server")
    print("=" * 50)
    print(f"Server: Waitress")
    print(f"Host: {HOST}")
    print(f"Port: {PORT}")
    print(f"Threads: {THREADS}")
    print(f"Access: http://{HOST}:{PORT}")
    print("=" * 50)
    print("Press Ctrl+C to stop")
    print("=" * 50)
    print()
    
    # Start Waitress server
    serve(
        app,
        host=HOST,
        port=PORT,
        threads=THREADS,
        channel_timeout=CHANNEL_TIMEOUT,
        cleanup_interval=30,
        asyncore_use_poll=True
    )
```

---

## Step 4: Install as Windows Service (NSSM)

### Download NSSM:
1. Download from: https://nssm.cc/download
2. Extract to: `C:\nssm\win64`

### Install Service:

```cmd
# Open Command Prompt as Administrator
cd C:\nssm\win64

# Install the service
nssm install GoogleScraperService

# In the GUI that opens, configure:
# Path: C:\Python\python.exe (or your Python path)
# Startup directory: D:\my work place\GoogleMapData
# Arguments: run_production.py
# Service name: GoogleScraperService
```

### Configure Service:

```cmd
# Set service description
nssm set GoogleScraperService Description "Google Business Scraper Web Application"

# Set startup type to automatic
nssm set GoogleScraperService Start SERVICE_AUTO_START

# Set working directory
nssm set GoogleScraperService AppDirectory "D:\my work place\GoogleMapData"

# Set environment variables
nssm set GoogleScraperService AppEnvironmentExtra "FLASK_HOST=0.0.0.0" "FLASK_PORT=80"

# Set output/error logs
nssm set GoogleScraperService AppStdout "D:\my work place\GoogleMapData\logs\service_output.log"
nssm set GoogleScraperService AppStderr "D:\my work place\GoogleMapData\logs\service_error.log"
```

### Start Service:

```cmd
nssm start GoogleScraperService
```

### Check Status:

```cmd
nssm status GoogleScraperService
```

### Useful Commands:

```cmd
# Stop service
nssm stop GoogleScraperService

# Restart service
nssm restart GoogleScraperService

# Remove service
nssm remove GoogleScraperService confirm
```

---

## Step 5: Setup Logging

### Create logs directory:

```cmd
mkdir logs
```

### Update `app.py` to add logging:

```python
import logging
from logging.handlers import RotatingFileHandler
import os

# Setup logging
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler(
        'logs/app.log', 
        maxBytes=10240000, 
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Application startup')
```

---

## Step 6: Security Hardening

### 1. Update Secret Key:

```python
# In app.py or .env
SECRET_KEY = os.urandom(32).hex()  # Generate random key
```

### 2. Disable Debug Mode:

```python
# In app.py
DEBUG = False
```

### 3. Add Rate Limiting (Optional):

```cmd
pip install flask-limiter
```

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

### 4. Configure Firewall:

```cmd
# Allow only necessary ports
netsh advfirewall firewall add rule name="Google Scraper HTTP" dir=in action=allow protocol=TCP localport=80
netsh advfirewall firewall add rule name="Google Scraper HTTPS" dir=in action=allow protocol=TCP localport=443
```

---

## Step 7: SSL/HTTPS Setup (Recommended)

### Option A: Using IIS as Reverse Proxy

1. **Install IIS:**
   ```cmd
   # PowerShell as Admin
   Install-WindowsFeature -name Web-Server -IncludeManagementTools
   ```

2. **Install URL Rewrite and ARR:**
   - Download: https://www.iis.net/downloads/microsoft/url-rewrite
   - Download: https://www.iis.net/downloads/microsoft/application-request-routing

3. **Configure IIS:**
   - Create site in IIS Manager
   - Bind to port 443 (HTTPS)
   - Configure SSL certificate
   - Set up reverse proxy to `http://localhost:80`

### Option B: Using Let's Encrypt (with Certbot)

```cmd
# Install Certbot
pip install certbot

# Get certificate
certbot certonly --standalone -d yourdomain.com
```

---

## Step 8: Monitoring

### Create `monitor_service.bat`:

```cmd
@echo off
REM Monitor service and restart if down
:loop
nssm status GoogleScraperService | findstr "SERVICE_RUNNING" >nul
if %errorLevel% neq 0 (
    echo Service is down, restarting...
    nssm restart GoogleScraperService
)
timeout /t 60 /nobreak >nul
goto loop
```

### Or use Windows Task Scheduler:

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily or at startup
4. Action: Start a program
5. Program: `C:\nssm\win64\nssm.exe`
6. Arguments: `start GoogleScraperService`

---

## Step 9: Production Checklist

- [ ] Waitress installed and configured
- [ ] Windows Service installed and running
- [ ] Service set to auto-start
- [ ] Logging configured
- [ ] Secret key changed
- [ ] Debug mode disabled
- [ ] Firewall rules configured
- [ ] SSL/HTTPS configured (optional)
- [ ] Monitoring set up
- [ ] Backup strategy in place
- [ ] Security group allows port 80/443
- [ ] Environment variables set in .env

---

## Quick Start Script

### Create `setup_production.bat`:

```cmd
@echo off
REM Production Setup Script
echo Setting up production environment...

REM Install dependencies
pip install waitress python-dotenv

REM Create directories
mkdir logs 2>nul
mkdir uploads 2>nul
mkdir excel_results 2>nul

REM Create .env if not exists
if not exist .env (
    echo Creating .env file...
    echo FLASK_HOST=0.0.0.0 > .env
    echo FLASK_PORT=80 >> .env
    echo FLASK_SECRET_KEY=%RANDOM%%RANDOM%%RANDOM% >> .env
    echo WAITRESS_WORKERS=4 >> .env
    echo WAITRESS_THREADS=4 >> .env
)

echo.
echo Production setup complete!
echo.
echo Next steps:
echo 1. Review and update .env file
echo 2. Test: python run_production.py
echo 3. Install as service: nssm install GoogleScraperService
echo.
pause
```

---

## Testing Production Setup

### Test Waitress Server:

```cmd
python run_production.py
```

Access: `http://16.16.249.160`

### Test Windows Service:

```cmd
nssm start GoogleScraperService
nssm status GoogleScraperService
```

---

## Troubleshooting

### Service Won't Start:
- Check logs: `logs\service_error.log`
- Verify Python path in NSSM
- Check firewall rules

### High Memory Usage:
- Reduce `WAITRESS_WORKERS` in .env
- Reduce `WAITRESS_THREADS` in .env

### Slow Performance:
- Increase `WAITRESS_WORKERS`
- Check server resources
- Monitor logs for errors

---

## Maintenance

### Update Application:

```cmd
# Stop service
nssm stop GoogleScraperService

# Update code
git pull  # or copy new files

# Restart service
nssm start GoogleScraperService
```

### View Logs:

```cmd
# Application logs
type logs\app.log

# Service logs
type logs\service_output.log
type logs\service_error.log
```

---

## Support

For issues, check:
- Service logs: `logs\service_error.log`
- Application logs: `logs\app.log`
- Windows Event Viewer: Applications and Services Logs

