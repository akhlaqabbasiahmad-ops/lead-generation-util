# License Management Guide

## Overview

The application includes a built-in license management system that allows you to:
- Generate license keys for different subscription tiers
- Activate licenses on user machines
- Validate licenses (online or offline)
- Enforce feature limits based on subscription tier

## Subscription Tiers

1. **Trial** - 7 days, 10 searches/day, 50 results/search
2. **Basic** - 30 days, 100 searches/day, 500 results/search, Excel export
3. **Pro** - 30 days, 1000 searches/day, 5000 results/search, Excel/CSV export, Social media extraction
4. **Enterprise** - 365 days, Unlimited searches, Unlimited results, All features

## Generating License Keys

### Method 1: Using Python Script

Create a file `generate_license.py`:

```python
from license_manager import LicenseManager

# Initialize license manager
lm = LicenseManager()

# Generate license keys
email = "customer@example.com"
tier = LicenseManager.TIER_PRO  # or TIER_BASIC, TIER_ENTERPRISE
duration = 30  # days

license_key = lm.generate_license_key(email, tier, duration)
print(f"License Key for {email}:")
print(license_key)
print("\nSend this key to the customer.")
```

### Method 2: Using Command Line

```python
python -c "from license_manager import LicenseManager; lm = LicenseManager(); print(lm.generate_license_key('user@example.com', 'pro', 30))"
```

## License Activation

Users activate licenses through the GUI:
1. Click "License" button in the application
2. Enter the license key
3. Click "Activate License"

## License Validation

### Offline Mode (Default)

- License is validated locally
- No internet connection required
- Machine-bound (one license per machine)

### Online Mode (Optional)

To enable online validation:

1. Set up a license server (see `license_server_example.py`)
2. Update `license_manager.py`:
   ```python
   self.api_url = "https://your-license-server.com/api/validate"
   ```

## Security Considerations

### IMPORTANT: Change the Secret Key

Before distributing, change the secret key in `license_manager.py`:

```python
# Change this line:
self.secret_key = "CHANGE_THIS_TO_A_SECURE_RANDOM_KEY_IN_PRODUCTION_2024"

# To something like:
import secrets
self.secret_key = secrets.token_hex(32)  # Generate a secure random key
```

**Keep this key secret!** Anyone with this key can generate valid licenses.

## License File Location

Licenses are stored in: `license.dat` (in the same directory as the EXE)

## Feature Limits by Tier

| Feature | Trial | Basic | Pro | Enterprise |
|---------|-------|-------|-----|------------|
| Basic Scraping | ✓ | ✓ | ✓ | ✓ |
| Excel Export | ✗ | ✓ | ✓ | ✓ |
| CSV Export | ✗ | ✗ | ✓ | ✓ |
| Social Media | ✗ | ✗ | ✓ | ✓ |
| Max Searches/Day | 10 | 100 | 1000 | Unlimited |
| Max Results/Search | 50 | 500 | 5000 | Unlimited |

## Managing Licenses

### Check License Status

```python
from license_manager import LicenseManager

lm = LicenseManager()
is_valid, license_data, message = lm.check_license_status()

if is_valid:
    print(f"License valid: {license_data['tier']}")
    print(f"Expires: {license_data['expiry_date']}")
else:
    print(f"License invalid: {message}")
```

### Validate License Key

```python
license_key = "YOUR_LICENSE_KEY_HERE"
is_valid, license_data, error = lm.validate_license_key(license_key)

if is_valid:
    print("License key is valid!")
else:
    print(f"Invalid: {error}")
```

## License Server (Optional)

For online validation, deploy a license server. See `license_server_example.py` for a Flask-based example.

## Distribution

1. Generate license keys for customers
2. Send license keys via email or your purchase system
3. Customers activate in the application
4. Application validates license on each startup

## Troubleshooting

### "License not activated on this machine"
- License is machine-bound
- User needs to activate on the same machine
- Or generate a new license key

### "License has expired"
- License duration has passed
- Generate a new license key with extended duration

### "Invalid license signature"
- License key is corrupted or invalid
- Check the secret key matches between generation and validation

## Best Practices

1. **Store license keys securely** - Use a database or secure file
2. **Track license usage** - Log activations and validations
3. **Set expiration dates** - Don't create permanent licenses
4. **Use different keys per customer** - Track who has which license
5. **Implement renewal system** - Allow license extensions
6. **Monitor for abuse** - Watch for license sharing attempts

