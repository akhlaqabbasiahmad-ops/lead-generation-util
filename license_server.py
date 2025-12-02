"""
License Server - Server-Side License Generation and Management
Deploy this on your server to generate and manage licenses
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib
import hmac
import base64
import json
from datetime import datetime, timedelta
from typing import Dict, Optional
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for client requests

# IMPORTANT: Change this to a secure random key
SECRET_KEY = os.environ.get('LICENSE_SECRET_KEY', 'CHANGE_THIS_TO_A_SECURE_RANDOM_KEY_IN_PRODUCTION_2024')

# In-memory database (replace with real database in production)
# Structure: {email: {paid: bool, tier: str, expiry: str, license_key: str, ...}}
CUSTOMERS_DB = {}
PAYMENTS_DB = {}  # {email: {paid: bool, payment_date: str, amount: float, ...}}


class LicenseGenerator:
    """Server-side license key generator"""
    
    TIER_TRIAL = "trial"
    TIER_BASIC = "basic"
    TIER_PRO = "pro"
    TIER_ENTERPRISE = "enterprise"
    
    DURATION_TRIAL = 7
    DURATION_MONTHLY = 30
    DURATION_YEARLY = 365
    
    @staticmethod
    def generate_license_key(email: str, tier: str, duration_days: int, 
                            license_id: str = None) -> str:
        """Generate a license key (SERVER-SIDE ONLY)"""
        if not license_id:
            license_id = hashlib.md5(f"{email}{datetime.now().isoformat()}".encode()).hexdigest()
        
        expiry_date = (datetime.now() + timedelta(days=duration_days)).isoformat()
        
        license_data = {
            "license_id": license_id,
            "email": email,
            "tier": tier,
            "expiry_date": expiry_date,
            "machine_id": None,  # Will be set on client activation
            "created_date": datetime.now().isoformat(),
            "generated_by": "server"
        }
        
        # Create signature
        data_string = json.dumps(license_data, sort_keys=True)
        signature = hmac.new(
            SECRET_KEY.encode(),
            data_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        license_data["signature"] = signature
        
        # Encode license
        license_json = json.dumps(license_data)
        license_key = base64.b64encode(license_json.encode()).decode()
        
        return license_key


@app.route('/api/verify_payment', methods=['POST'])
def verify_payment():
    """Verify if customer has paid"""
    data = request.json
    email = data.get('email', '').strip().lower()
    
    if not email:
        return jsonify({"error": "Email required"}), 400
    
    # Check payment status
    payment_info = PAYMENTS_DB.get(email, {"paid": False})
    is_paid = payment_info.get("paid", False)
    
    return jsonify({
        "paid": is_paid,
        "message": "Payment confirmed" if is_paid else "Payment not confirmed",
        "payment_data": payment_info
    })


@app.route('/api/generate_license', methods=['POST'])
def generate_license():
    """Generate a new license key (requires payment verification)"""
    data = request.json
    email = data.get('email', '').strip().lower()
    tier = data.get('tier', 'basic')
    duration = data.get('duration', 30)
    
    # Admin authentication (add your auth method here)
    admin_key = data.get('admin_key', '')
    if admin_key != os.environ.get('ADMIN_KEY', 'your-admin-secret-key'):
        return jsonify({"error": "Unauthorized"}), 401
    
    if not email:
        return jsonify({"error": "Email required"}), 400
    
    # Verify payment
    payment_info = PAYMENTS_DB.get(email, {"paid": False})
    if not payment_info.get("paid", False):
        return jsonify({
            "error": "Payment not confirmed",
            "message": "Customer must complete payment before license generation"
        }), 402  # Payment Required
    
    # Generate license
    license_key = LicenseGenerator.generate_license_key(email, tier, duration)
    
    # Store in database
    CUSTOMERS_DB[email] = {
        "email": email,
        "tier": tier,
        "duration": duration,
        "license_key": license_key,
        "generated_date": datetime.now().isoformat(),
        "expiry_date": (datetime.now() + timedelta(days=duration)).isoformat(),
        "paid": True
    }
    
    return jsonify({
        "success": True,
        "license_key": license_key,
        "email": email,
        "tier": tier,
        "duration": duration,
        "expiry_date": CUSTOMERS_DB[email]["expiry_date"]
    })


@app.route('/api/renew_license', methods=['POST'])
def renew_license():
    """Renew an expired license (requires payment verification)"""
    data = request.json
    email = data.get('email', '').strip().lower()
    tier = data.get('tier', None)  # Can upgrade/downgrade
    duration = data.get('duration', 30)
    
    # Admin authentication
    admin_key = data.get('admin_key', '')
    if admin_key != os.environ.get('ADMIN_KEY', 'your-admin-secret-key'):
        return jsonify({"error": "Unauthorized"}), 401
    
    if not email:
        return jsonify({"error": "Email required"}), 400
    
    # Check if customer exists
    customer = CUSTOMERS_DB.get(email)
    if customer:
        # Use existing tier if not specified
        if not tier:
            tier = customer.get("tier", "basic")
    else:
        tier = tier or "basic"
    
    # Verify payment for renewal
    payment_info = PAYMENTS_DB.get(email, {"paid": False})
    if not payment_info.get("paid", False):
        return jsonify({
            "error": "Payment not confirmed",
            "message": "Customer must complete payment for renewal"
        }), 402
    
    # Generate new license
    license_key = LicenseGenerator.generate_license_key(email, tier, duration)
    
    # Update database
    CUSTOMERS_DB[email] = {
        "email": email,
        "tier": tier,
        "duration": duration,
        "license_key": license_key,
        "generated_date": datetime.now().isoformat(),
        "expiry_date": (datetime.now() + timedelta(days=duration)).isoformat(),
        "paid": True,
        "renewed": True,
        "previous_expiry": customer.get("expiry_date") if customer else None
    }
    
    return jsonify({
        "success": True,
        "license_key": license_key,
        "email": email,
        "tier": tier,
        "duration": duration,
        "expiry_date": CUSTOMERS_DB[email]["expiry_date"],
        "message": "License renewed successfully"
    })


@app.route('/api/validate_license', methods=['POST'])
def validate_license():
    """Validate a license key (called by client app)"""
    data = request.json
    license_key = data.get('license_key', '')
    machine_id = data.get('machine_id', '')
    action = data.get('action', 'validate')  # 'validate' or 'activate'
    
    if not license_key:
        return jsonify({"error": "License key required"}), 400
    
    try:
        # Decode and validate license
        license_json = base64.b64decode(license_key.encode()).decode()
        license_data = json.loads(license_json)
        
        # Verify signature
        signature = license_data.pop("signature")
        data_string = json.dumps(license_data, sort_keys=True)
        expected_signature = hmac.new(
            SECRET_KEY.encode(),
            data_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if signature != expected_signature:
            return jsonify({"valid": False, "error": "Invalid license signature"}), 400
        
        email = license_data.get("email", "").lower()
        
        # Check expiry
        expiry_date = datetime.fromisoformat(license_data["expiry_date"])
        if datetime.now() > expiry_date:
            return jsonify({
                "valid": False,
                "error": "License has expired",
                "expiry_date": license_data["expiry_date"]
            }), 400
        
        # Verify payment status
        payment_info = PAYMENTS_DB.get(email, {"paid": False})
        if not payment_info.get("paid", False):
            return jsonify({
                "valid": False,
                "error": "Payment not confirmed",
                "message": "Please complete payment to use this license"
            }), 402
        
        # If activating, store machine binding
        if action == "activate" and machine_id:
            license_data["machine_id"] = machine_id
            license_data["activated_date"] = datetime.now().isoformat()
            
            # Update in database
            if email in CUSTOMERS_DB:
                CUSTOMERS_DB[email]["machine_id"] = machine_id
                CUSTOMERS_DB[email]["activated_date"] = license_data["activated_date"]
        
        # Check machine binding
        if license_data.get("machine_id") and action == "validate":
            if license_data["machine_id"] != machine_id:
                return jsonify({
                    "valid": False,
                    "error": "License is bound to another machine"
                }), 400
        
        days_remaining = (expiry_date - datetime.now()).days
        
        return jsonify({
            "valid": True,
            "license_data": {
                "email": email,
                "tier": license_data.get("tier"),
                "expiry_date": license_data["expiry_date"],
                "days_remaining": days_remaining
            },
            "paid": True
        })
        
    except Exception as e:
        return jsonify({"valid": False, "error": f"Invalid license format: {str(e)}"}), 400


@app.route('/api/mark_payment', methods=['POST'])
def mark_payment():
    """Mark customer as paid (admin function)"""
    data = request.json
    
    # Admin authentication
    admin_key = data.get('admin_key', '')
    if admin_key != os.environ.get('ADMIN_KEY', 'your-admin-secret-key'):
        return jsonify({"error": "Unauthorized"}), 401
    
    email = data.get('email', '').strip().lower()
    amount = data.get('amount', 0)
    transaction_id = data.get('transaction_id', '')
    
    if not email:
        return jsonify({"error": "Email required"}), 400
    
    # Mark as paid
    PAYMENTS_DB[email] = {
        "paid": True,
        "payment_date": datetime.now().isoformat(),
        "amount": amount,
        "transaction_id": transaction_id
    }
    
    return jsonify({
        "success": True,
        "message": f"Payment marked for {email}",
        "payment_data": PAYMENTS_DB[email]
    })


@app.route('/api/customer_status', methods=['GET'])
def customer_status():
    """Get customer status (admin function)"""
    email = request.args.get('email', '').strip().lower()
    admin_key = request.args.get('admin_key', '')
    
    if admin_key != os.environ.get('ADMIN_KEY', 'your-admin-secret-key'):
        return jsonify({"error": "Unauthorized"}), 401
    
    if not email:
        return jsonify({"error": "Email required"}), 400
    
    customer = CUSTOMERS_DB.get(email, {})
    payment = PAYMENTS_DB.get(email, {"paid": False})
    
    return jsonify({
        "email": email,
        "customer_data": customer,
        "payment_data": payment
    })


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "service": "license-server"})


if __name__ == '__main__':
    # For production, use gunicorn or similar
    # gunicorn -w 4 -b 0.0.0.0:5000 license_server:app
    app.run(debug=True, host='0.0.0.0', port=5000)

