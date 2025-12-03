# Server Setup Guide

## Quick Start Commands

### Option 1: Full Setup (First Time)
```bash
# Make script executable
chmod +x server_setup.sh

# Run setup script
./server_setup.sh
```

### Option 2: Manual Setup

#### 1. Install Dependencies
```bash
pip3 install -r requirements.txt
```

#### 2. Create Required Directories
```bash
mkdir -p excel_results uploads templates
```

#### 3. Run on Port 80 (Requires sudo/root)
```bash
sudo python3 app.py
```

### Option 3: Run Without Root (Alternative Port)

If you don't have root access or port 80 is unavailable, you can use a different port:

```bash
# Set environment variable for custom port
export FLASK_PORT=8080
export FLASK_HOST=0.0.0.0

# Run without sudo
python3 app.py
```

Then access at: `http://<your-server-ip>:8080`

## Using Systemd Service (Recommended for Production)

Create a systemd service file for automatic startup:

```bash
sudo nano /etc/systemd/system/google-scraper.service
```

Add the following content:

```ini
[Unit]
Description=Google Business Scraper Web Application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/GoogleMapData
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 /path/to/GoogleMapData/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Replace `/path/to/GoogleMapData` with your actual directory path.

Then enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable google-scraper
sudo systemctl start google-scraper
sudo systemctl status google-scraper
```

## Using Nginx Reverse Proxy (Recommended)

If you want to run on port 80 without root privileges, use Nginx as a reverse proxy:

### 1. Install Nginx
```bash
sudo apt-get update
sudo apt-get install nginx
```

### 2. Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/google-scraper
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/google-scraper /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4. Run App on Port 5000 (No Root Needed)
```bash
export FLASK_PORT=5000
export FLASK_HOST=127.0.0.1
python3 app.py
```

## Firewall Configuration

If using a firewall, allow port 80:

```bash
# UFW (Ubuntu)
sudo ufw allow 80/tcp

# Firewalld (CentOS/RHEL)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --reload

# iptables
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
```

## Troubleshooting

### Port 80 Already in Use
```bash
# Check what's using port 80
sudo netstat -tulpn | grep :80
sudo lsof -i :80

# Stop Apache (if installed)
sudo systemctl stop apache2

# Stop Nginx (if installed)
sudo systemctl stop nginx
```

### Permission Denied
- Port 80 requires root privileges
- Use `sudo` to run the application
- Or use a reverse proxy (Nginx) and run app on port 5000

### Dependencies Not Found
```bash
# Use pip3 instead of pip
pip3 install -r requirements.txt

# Or use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Access the Application

Once running, access at:
- `http://localhost` (local)
- `http://<your-server-ip>` (remote)
- `http://<your-domain>` (if domain configured)

