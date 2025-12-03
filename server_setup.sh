#!/bin/bash
# Google Business Scraper - Server Setup Script
# Run this script to set up and start the application on port 80

echo "=========================================="
echo "Google Business Scraper - Server Setup"
echo "=========================================="

# Step 1: Install Python dependencies
echo ""
echo "Step 1: Installing Python dependencies..."
pip3 install -r requirements.txt

# Check if installation was successful
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed successfully"

# Step 2: Create necessary directories
echo ""
echo "Step 2: Creating necessary directories..."
mkdir -p excel_results
mkdir -p uploads
mkdir -p templates

echo "✓ Directories created"

# Step 3: Check if port 80 is available
echo ""
echo "Step 3: Checking port 80 availability..."
if sudo netstat -tuln | grep -q ':80 '; then
    echo "⚠️  Warning: Port 80 is already in use"
    echo "   You may need to stop the existing service or use a different port"
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 4: Start the application on port 80
echo ""
echo "Step 4: Starting application on port 80..."
echo "=========================================="
echo "Server will be accessible at:"
echo "  - http://localhost"
echo "  - http://<your-server-ip>"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=========================================="
echo ""

# Run with sudo to bind to port 80 (requires root privileges)
sudo python3 app.py

