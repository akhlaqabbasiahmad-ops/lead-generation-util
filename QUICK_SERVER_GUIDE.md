# Quick Server Setup Guide

## Deploy License Server

### 1. Install Dependencies

```bash
pip install flask flask-cors gunicorn
```

### 2. Configure Server

Edit `license_server.py`:
- Set `SECRET_KEY` (must match client)
- Set `ADMIN_KEY` (for admin functions)

### 3. Run Server

```bash
# Development
python license_server.py

# Production
gunicorn -w 4 -b 0.0.0.0:5000 license_server:app
```

## Generate License for Customer

### After Customer Pays:

```python
# On your server
from server_admin_tools import process_new_customer

result = process_new_customer(
    email="customer@email.com",
    tier="pro",
    duration=30,
    amount=99.99,
    transaction_id="TXN123"
)

# Send license_key to customer
license_key = result["license_key"]
```

## Renew Expired License

### After Customer Pays Renewal:

```python
# On your server
from server_admin_tools import process_renewal

result = process_renewal(
    email="customer@email.com",
    tier="pro",
    duration=30,
    amount=99.99,
    transaction_id="TXN456"
)

# Send new license_key to customer
license_key = result["license_key"]
```

## Client App Configuration

In `google_scraper_gui.py`, set server URL:

```python
SERVER_URL = 'https://your-license-server.com'
```

## Security Checklist

- [ ] Change SECRET_KEY (same on server and client)
- [ ] Change ADMIN_KEY (server only)
- [ ] Use HTTPS in production
- [ ] Set up firewall rules
- [ ] Use environment variables for keys
- [ ] Implement rate limiting
- [ ] Add authentication to admin endpoints

## Summary

✅ **Server generates licenses**  
✅ **Client validates licenses**  
✅ **Payment required before activation**  
✅ **No license generation in client app**

