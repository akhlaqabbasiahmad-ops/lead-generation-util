# Windows Server Setup Guide

## Quick Start Commands

### Option 1: Complete Automated Setup (Recommended - First Time)

**Run as Administrator:**

```cmd
# Complete setup - checks Python, installs dependencies, starts server
complete_setup.bat
```

This script will:
1. ✅ Check if Python is installed
2. ✅ Guide you to install Python if needed
3. ✅ Install all dependencies
4. ✅ Create required folders
5. ✅ Start the server

### Option 2: Standard Setup

**Run as Administrator:**

```cmd
# Double-click or run from Command Prompt (as Admin)
server_setup.bat
```

Or using PowerShell (as Administrator):

```powershell
.\server_setup.ps1
```

### Option 2: Manual Setup

#### Step 1: Open Command Prompt or PowerShell as Administrator
- Right-click on Command Prompt or PowerShell
- Select "Run as administrator"

#### Step 2: Navigate to Project Directory
```cmd
cd "D:\my work place\GoogleMapData"
```

#### Step 3: Install Dependencies
```cmd
pip install -r requirements.txt
```

#### Step 5: Create Required Directories
```cmd
mkdir excel_results
mkdir uploads
mkdir templates
```

#### Step 6: Run on Port 80
```cmd
python app.py
# OR if using py launcher:
py app.py
```

## Important Notes for Port 80

### Port 80 Requires Administrator Privileges
- You **MUST** run Command Prompt or PowerShell as Administrator
- Right-click → "Run as administrator"

### If Port 80 is Already in Use

**Check what's using port 80:**
```cmd
netstat -ano | findstr :80
```

**Common services using port 80:**
- **IIS (Internet Information Services)** - Windows Web Server
- **Apache** - If installed
- **Other web applications**

**Stop IIS (if running):**
```cmd
# Stop IIS
iisreset /stop

# Or disable IIS service
net stop w3svc
```

**Or use a different port:**
```cmd
# Set environment variable for custom port
set FLASK_PORT=8080
set FLASK_HOST=0.0.0.0

# Run without admin (if using custom port)
python app.py
```

Then access at: `http://your-server-ip:8080`

## Windows Firewall Configuration

Allow port 80 through Windows Firewall:

**Using GUI:**
1. Open Windows Defender Firewall
2. Click "Advanced settings"
3. Click "Inbound Rules" → "New Rule"
4. Select "Port" → Next
5. Select "TCP" and enter port "80"
6. Allow the connection
7. Apply to all profiles
8. Name it "Google Scraper Web App"

**Using Command Line (as Admin):**
```cmd
netsh advfirewall firewall add rule name="Google Scraper Web App" dir=in action=allow protocol=TCP localport=80
```

## Running as Windows Service (Optional)

To run the application as a Windows service that starts automatically:

### Using NSSM (Non-Sucking Service Manager)

1. **Download NSSM:**
   - Download from: https://nssm.cc/download
   - Extract to a folder (e.g., `C:\nssm`)

2. **Install as Service:**
```cmd
# Open Command Prompt as Administrator
cd C:\nssm\win64
nssm install GoogleScraperService

# In the GUI that opens:
# - Path: C:\Python\python.exe (or your Python path)
# - Startup directory: D:\my work place\GoogleMapData
# - Arguments: app.py
# - Service name: GoogleScraperService
```

3. **Start the Service:**
```cmd
nssm start GoogleScraperService
```

4. **Check Status:**
```cmd
nssm status GoogleScraperService
```

## Access the Application

Once running, access at:
- **Local:** `http://localhost`
- **Network:** `http://<your-server-ip>`
- **Custom Port:** `http://<your-server-ip>:8080` (if using custom port)

## Troubleshooting

### "Permission Denied" Error
- **Solution:** Run Command Prompt/PowerShell as Administrator

### "Port 80 already in use"
- **Solution 1:** Stop IIS: `iisreset /stop`
- **Solution 2:** Use different port (set FLASK_PORT environment variable)
- **Solution 3:** Check what's using port 80: `netstat -ano | findstr :80`

### "Module not found" Error
- **Solution:** Install dependencies: `pip install -r requirements.txt`
- **Check Python version:** `python --version` (should be 3.7+)

### Can't Access from Other Computers
- **Check Windows Firewall:** Allow port 80
- **Check Network:** Ensure server is on same network or has public IP
- **Check Host:** Ensure `FLASK_HOST=0.0.0.0` (already set in app.py)

### Application Stops When Closing Terminal
- **Solution 1:** Use `start_server.bat` (keeps window open)
- **Solution 2:** Install as Windows Service (see above)
- **Solution 3:** Use `start python app.py` to run in background

## Quick Reference Commands

```cmd
# Install dependencies
pip install -r requirements.txt

# Run on port 80 (as Admin)
python app.py

# Run on custom port (no Admin needed)
set FLASK_PORT=8080
python app.py

# Check if port 80 is in use
netstat -ano | findstr :80

# Stop IIS
iisreset /stop

# Check Python version
python --version

# Check if app is running
netstat -ano | findstr python
```

