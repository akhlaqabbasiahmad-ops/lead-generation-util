# Quick Start - EC2 Production Deployment

## Step 1: Install Dependencies

```bash
cd ~/lead-generation-util
chmod +x setup_ec2.sh
./setup_ec2.sh
```

## Step 2: Update Systemd Service

```bash
sudo nano /etc/systemd/system/google-scraper.service
```

Paste this configuration:

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
ExecStart=/home/ubuntu/lead-generation-util/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 --timeout 300 --access-logfile - --error-logfile - app:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Step 3: Update Nginx Config

```bash
sudo nano /etc/nginx/sites-available/google-scraper
```

Paste this:

```nginx
server {
    listen 80;
    server_name _;

    client_max_body_size 100M;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
    }
}
```

## Step 4: Start Services

```bash
sudo ln -sf /etc/nginx/sites-available/google-scraper /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl daemon-reload
sudo systemctl enable google-scraper
sudo systemctl start google-scraper
sudo systemctl restart nginx
```

## Step 5: Verify

```bash
# Check services
sudo systemctl status google-scraper
sudo systemctl status nginx

# Get your IP
curl http://169.254.169.254/latest/meta-data/public-ipv4

# Test locally
curl http://localhost
```

Access at: `http://YOUR_EC2_IP`

## Troubleshooting

```bash
# View logs
sudo journalctl -u google-scraper -f

# Restart
sudo systemctl restart google-scraper
```

