# Quick License Management Guide

## For You (License Generator)

### Generate a License Key

**Option 1: Use the generator script**
```bash
python generate_license.py
```

**Option 2: Use Python directly**
```python
from license_manager import LicenseManager

lm = LicenseManager()
key = lm.generate_license_key("customer@email.com", "pro", 30)
print(key)
```

### Subscription Tiers

- `"trial"` - 7 days, limited features
- `"basic"` - 30 days, Excel export
- `"pro"` - 30 days, all features
- `"enterprise"` - 365 days, unlimited

### Example: Generate Pro License for 30 days

```python
from license_manager import LicenseManager

lm = LicenseManager()
license_key = lm.generate_license_key(
    email="customer@example.com",
    tier="pro",
    duration_days=30
)
print(license_key)
# Send this key to your customer
```

## For Your Customers

1. **Receive License Key** - You send them a license key
2. **Open Application** - Launch GoogleBusinessScraper.exe
3. **Click "License" Button** - Top right corner
4. **Paste License Key** - Enter the key you provided
5. **Click "Activate License"** - Done!

## License Status

The application shows license status in the top right:
- **Green**: Active license with days remaining
- **Orange**: License expiring soon (< 7 days)
- **Red**: No license or expired

## Features by Tier

| Feature | Trial | Basic | Pro | Enterprise |
|---------|-------|-------|-----|------------|
| Scraping | ✓ | ✓ | ✓ | ✓ |
| Excel Export | ✗ | ✓ | ✓ | ✓ |
| CSV Export | ✗ | ✗ | ✓ | ✓ |
| Social Media | ✗ | ✗ | ✓ | ✓ |
| Daily Limit | 10 | 100 | 1000 | Unlimited |

## Important Security Note

**Before distributing your EXE:**

1. Open `license_manager.py`
2. Find this line:
   ```python
   self.secret_key = "CHANGE_THIS_TO_A_SECURE_RANDOM_KEY_IN_PRODUCTION_2024"
   ```
3. Change it to a secure random string (at least 32 characters)
4. **Keep this key secret!** Anyone with it can generate valid licenses

Example:
```python
import secrets
self.secret_key = secrets.token_hex(32)  # Generates a secure random key
```

## License File Location

Licenses are stored in: `license.dat` (same folder as EXE)

## Troubleshooting

**"License not activated on this machine"**
- License is machine-bound (one per computer)
- User must activate on the same machine
- Or generate a new license key

**"License has expired"**
- Generate a new license with extended duration

**"Invalid license signature"**
- License key is corrupted
- Make sure secret key matches between generation and validation

