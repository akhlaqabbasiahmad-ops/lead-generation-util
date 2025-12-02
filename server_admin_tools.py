"""
Server Admin Tools - For managing licenses and payments on your server
Run these functions on your server to manage customers
"""

import requests
import json
from datetime import datetime, timedelta

# Server configuration
SERVER_URL = "http://localhost:5000"  # Change to your server URL
ADMIN_KEY = "your-admin-secret-key"  # Change to match your server's ADMIN_KEY


def mark_customer_paid(email: str, amount: float = None, transaction_id: str = None):
    """Mark a customer as paid"""
    response = requests.post(
        f"{SERVER_URL}/api/mark_payment",
        json={
            "admin_key": ADMIN_KEY,
            "email": email,
            "amount": amount,
            "transaction_id": transaction_id
        }
    )
    
    if response.status_code == 200:
        print(f"✓ Payment marked for {email}")
        return response.json()
    else:
        print(f"✗ Error: {response.json()}")
        return None


def generate_license_for_customer(email: str, tier: str = "pro", duration: int = 30):
    """Generate a license key for a paid customer"""
    response = requests.post(
        f"{SERVER_URL}/api/generate_license",
        json={
            "admin_key": ADMIN_KEY,
            "email": email,
            "tier": tier,
            "duration": duration
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ License generated for {email}")
        print(f"  Tier: {tier}")
        print(f"  Duration: {duration} days")
        print(f"  License Key: {data['license_key']}")
        return data
    else:
        print(f"✗ Error: {response.json()}")
        return None


def renew_customer_license(email: str, tier: str = None, duration: int = 30):
    """Renew an expired license (after payment)"""
    response = requests.post(
        f"{SERVER_URL}/api/renew_license",
        json={
            "admin_key": ADMIN_KEY,
            "email": email,
            "tier": tier,
            "duration": duration
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ License renewed for {email}")
        print(f"  New License Key: {data['license_key']}")
        return data
    else:
        print(f"✗ Error: {response.json()}")
        return None


def get_customer_status(email: str):
    """Get customer payment and license status"""
    response = requests.get(
        f"{SERVER_URL}/api/customer_status",
        params={
            "admin_key": ADMIN_KEY,
            "email": email
        }
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"✗ Error: {response.json()}")
        return None


def process_new_customer(email: str, tier: str, duration: int, amount: float, transaction_id: str):
    """Complete workflow: Mark paid + Generate license"""
    print(f"Processing new customer: {email}")
    
    # Step 1: Mark as paid
    payment_result = mark_customer_paid(email, amount, transaction_id)
    if not payment_result:
        return None
    
    # Step 2: Generate license
    license_result = generate_license_for_customer(email, tier, duration)
    if not license_result:
        return None
    
    print(f"\n✓ Complete! Send this license key to customer:")
    print(f"  {license_result['license_key']}")
    
    return license_result


def process_renewal(email: str, tier: str = None, duration: int = 30, amount: float = None, transaction_id: str = None):
    """Complete workflow: Mark paid + Renew license"""
    print(f"Processing renewal for: {email}")
    
    # Step 1: Mark payment (if provided)
    if amount:
        payment_result = mark_customer_paid(email, amount, transaction_id)
        if not payment_result:
            return None
    
    # Step 2: Renew license
    license_result = renew_customer_license(email, tier, duration)
    if not license_result:
        return None
    
    print(f"\n✓ Complete! Send this license key to customer:")
    print(f"  {license_result['license_key']}")
    
    return license_result


# Example usage
if __name__ == "__main__":
    # Example 1: New customer
    # process_new_customer(
    #     email="customer@example.com",
    #     tier="pro",
    #     duration=30,
    #     amount=99.99,
    #     transaction_id="TXN123456"
    # )
    
    # Example 2: Renewal
    # process_renewal(
    #     email="customer@example.com",
    #     tier="pro",
    #     duration=30,
    #     amount=99.99,
    #     transaction_id="TXN789012"
    # )
    
    # Example 3: Check status
    # status = get_customer_status("customer@example.com")
    # print(json.dumps(status, indent=2))
    
    print("Server Admin Tools")
    print("Import this module and use the functions to manage licenses")

