#!/bin/bash
# Quick start script - Run the server on port 80

# Make sure we're in the right directory
cd "$(dirname "$0")"

# Start the server with sudo (required for port 80)
sudo python3 app.py

