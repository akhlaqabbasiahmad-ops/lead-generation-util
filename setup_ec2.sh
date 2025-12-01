#!/bin/bash
# Production setup script for EC2 instance
# Run this script on your EC2 instance to install all dependencies

set -e

echo "========================================="
echo "Google Business Scraper - EC2 Setup"
echo "========================================="

# Update system
echo "Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install Python and build tools
echo "Installing Python and build tools..."
sudo apt install -y python3 python3-pip python3-venv python3-dev build-essential

# Install Google Chrome
echo "Installing Google Chrome..."
if ! command -v google-chrome &> /dev/null; then
    wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    sudo apt install -y ./google-chrome-stable_current_amd64.deb
    rm -f google-chrome-stable_current_amd64.deb
    echo "✓ Chrome installed"
else
    echo "✓ Chrome already installed"
fi

# Install Chrome dependencies (required for headless mode)
echo "Installing Chrome dependencies..."
sudo apt install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    libatspi2.0-0 \
    libxshmfence1 \
    fonts-liberation \
    libappindicator3-1 \
    xdg-utils

echo "✓ Chrome dependencies installed"

# Install Nginx
echo "Installing Nginx..."
sudo apt install -y nginx

# Install Gunicorn dependencies
echo "Installing system dependencies for Gunicorn..."
sudo apt install -y libpq-dev

# Verify Chrome installation
echo "Testing Chrome..."
if google-chrome --headless=new --disable-gpu --no-sandbox --version > /dev/null 2>&1; then
    echo "✓ Chrome is working correctly"
else
    echo "⚠ Chrome test failed - may need additional dependencies"
fi

# Set up Python virtual environment
APP_DIR="/home/ubuntu/lead-generation-util"
if [ -d "$APP_DIR" ]; then
    cd "$APP_DIR"
    echo "Setting up Python environment in $APP_DIR..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install gunicorn
    
    echo "✓ Python environment set up"
else
    echo "⚠ Application directory not found: $APP_DIR"
    echo "Please run this script from the application directory or update APP_DIR"
fi

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Configure systemd service: sudo nano /etc/systemd/system/google-scraper.service"
echo "2. Configure Nginx: sudo nano /etc/nginx/sites-available/google-scraper"
echo "3. Start services: sudo systemctl start google-scraper && sudo systemctl start nginx"
echo ""

