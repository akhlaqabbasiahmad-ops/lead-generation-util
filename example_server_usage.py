"""
Example: How to use the license server
Run this on YOUR SERVER to manage licenses
"""

from server_admin_tools import (
    mark_customer_paid,
    generate_license_for_customer,
    renew_customer_license,
    get_customer_status,
    process_new_customer,
    process_renewal
)

# ============================================
# EXAMPLE 1: New Customer (After Payment)
# ============================================

def example_new_customer():
    """Customer just paid - generate license"""
    
    email = "newcustomer@example.com"
    tier = "pro"
    duration = 30  # days
    amount = 99.99
    transaction_id = "TXN123456"
    
    # Complete workflow: Mark paid + Generate license
    result = process_new_customer(
        email=email,
        tier=tier,
        duration=duration,
        amount=amount,
        transaction_id=transaction_id
    )
    
    if result:
        license_key = result["license_key"]
        print(f"\n✓ License generated!")
        print(f"Send this to customer: {license_key}")


# ============================================
# EXAMPLE 2: License Renewal (After Payment)
# ============================================

def example_renewal():
    """Customer's license expired - renew after payment"""
    
    email = "customer@example.com"
    tier = "pro"  # Can upgrade/downgrade
    duration = 30
    amount = 99.99
    transaction_id = "TXN789012"
    
    # Complete workflow: Mark paid + Renew license
    result = process_renewal(
        email=email,
        tier=tier,
        duration=duration,
        amount=amount,
        transaction_id=transaction_id
    )
    
    if result:
        new_license_key = result["license_key"]
        print(f"\n✓ License renewed!")
        print(f"Send this to customer: {new_license_key}")


# ============================================
# EXAMPLE 3: Manual Steps
# ============================================

def example_manual():
    """Step-by-step manual process"""
    
    email = "customer@example.com"
    
    # Step 1: Mark as paid
    mark_customer_paid(
        email=email,
        amount=99.99,
        transaction_id="TXN345678"
    )
    
    # Step 2: Generate license
    result = generate_license_for_customer(
        email=email,
        tier="pro",
        duration=30
    )
    
    if result:
        license_key = result["license_key"]
        print(f"License: {license_key}")


# ============================================
# EXAMPLE 4: Check Customer Status
# ============================================

def example_check_status():
    """Check if customer has paid and has license"""
    
    email = "customer@example.com"
    status = get_customer_status(email)
    
    if status:
        print(f"Customer: {email}")
        print(f"Paid: {status['payment_data'].get('paid', False)}")
        print(f"Has License: {bool(status['customer_data'])}")
        if status['customer_data']:
            print(f"Tier: {status['customer_data'].get('tier')}")
            print(f"Expires: {status['customer_data'].get('expiry_date')}")


if __name__ == "__main__":
    print("=" * 60)
    print("License Server Usage Examples")
    print("=" * 60)
    print("\nUncomment the example you want to run:")
    print()
    print("# Example 1: New customer")
    print("# example_new_customer()")
    print()
    print("# Example 2: Renewal")
    print("# example_renewal()")
    print()
    print("# Example 3: Manual steps")
    print("# example_manual()")
    print()
    print("# Example 4: Check status")
    print("# example_check_status()")
    print()
    print("=" * 60)

