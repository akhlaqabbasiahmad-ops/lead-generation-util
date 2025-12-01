# EC2 Production Setup Guide

Complete guide to set up the Google Business Scraper on EC2 for production use.

## Quick Setup

### 1. Run the setup script

```bash
cd ~/lead-generation-util
chmod +x setup_ec2.sh
./setup_ec2.sh
```

### 2. Configure systemd service

```bash
sudo nano /etc/systemd/system/google-scraper.service
```

Use this configuration:

```ini
[Unit]
Description=Google Business Scraper Web Application
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/lead-generation-util
Environment="PATH=/home/ubuntu/lead-generation-util/venv/bin"
Environment="FLASK_ENV=production"
Environment="FLASK_DEBUG=False"
ExecStart=/home/ubuntu/lead-generation-util/venv/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:5000 \
    --timeout 300 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    app:app

Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 3. Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/google-scraper
```

```nginx
server {
    listen 80;
    server_name _;

    client_max_body_size 100M;
    client_body_timeout 300s;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
    }
}
```

### 4. Enable and start services

```bash
# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/google-scraper /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t

# Start services
sudo systemctl daemon-reload
sudo systemctl enable google-scraper
sudo systemctl start google-scraper
sudo systemctl restart nginx

# Check status
sudo systemctl status google-scraper
sudo systemctl status nginx
```

### 5. Configure firewall

```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow ssh
sudo ufw enable
```

## Security Hardening

### 1. Update Flask Secret Key

```bash
# Generate a secure secret key
python3 -c "import secrets; print(secrets.token_hex(32))"

# Set as environment variable
sudo nano /etc/systemd/system/google-scraper.service
# Add: Environment="FLASK_SECRET_KEY=your-generated-key-here"
```

### 2. Set up SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

### 3. Configure Security Headers in Nginx

Add to your Nginx config:

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
```

## Monitoring

### View logs

```bash
# Application logs
sudo journalctl -u google-scraper -f

# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

### Check service health

```bash
# Service status
sudo systemctl status google-scraper

# Test endpoint
curl http://localhost/api/status

# Check processes
ps aux | grep gunicorn
```

## Maintenance

### Restart services

```bash
sudo systemctl restart google-scraper
sudo systemctl restart nginx
```

### Update application

```bash
cd ~/lead-generation-util
source venv/bin/activate
git pull  # If using Git
pip install -r requirements.txt
sudo systemctl restart google-scraper
```

### Backup

```bash
# Create backup script
cat > ~/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf ~/backups/scraper_$DATE.tar.gz ~/lead-generation-util/excel_results
find ~/backups -name "scraper_*.tar.gz" -mtime +7 -delete
EOF

chmod +x ~/backup.sh
mkdir -p ~/backups

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * ~/backup.sh") | crontab -
```

## Troubleshooting

### Chrome not starting

```bash
# Test Chrome manually
google-chrome --headless=new --disable-gpu --no-sandbox --version

# Check dependencies
ldd /usr/bin/google-chrome | grep "not found"

# Reinstall dependencies
sudo apt install --reinstall libnss3 libgbm1
```

### Service not starting

```bash
# Check logs
sudo journalctl -u google-scraper -n 50

# Test Gunicorn manually
cd ~/lead-generation-util
source venv/bin/activate
gunicorn --bind 127.0.0.1:5000 app:app
```

### High memory usage

```bash
# Reduce Gunicorn workers
# Edit /etc/systemd/system/google-scraper.service
# Change --workers 3 to --workers 2
sudo systemctl daemon-reload
sudo systemctl restart google-scraper
```

## Performance Tuning

### Gunicorn workers

For EC2 instances:
- t2.micro: 1-2 workers
- t2.small: 2-3 workers
- t2.medium: 3-4 workers

Formula: (2 × CPU cores) + 1

### Nginx optimization

Add to Nginx config:

```nginx
worker_processes auto;
worker_connections 1024;

gzip on;
gzip_types text/plain text/css application/json application/javascript;
```

## Production Checklist

- [ ] Chrome dependencies installed
- [ ] Systemd service configured and running
- [ ] Nginx configured and running
- [ ] Firewall configured
- [ ] SSL certificate installed (if using domain)
- [ ] Secret key updated
- [ ] Logs configured
- [ ] Backup strategy in place
- [ ] Monitoring set up
- [ ] Security headers configured

