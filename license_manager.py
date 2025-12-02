"""
License and Subscription Management System
Handles license validation, subscription tiers, and activation
"""

import json
import os
import hashlib
import hmac
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
import platform

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from payment_verification import PaymentVerifier, LocalPaymentTracker
    PAYMENT_VERIFICATION_AVAILABLE = True
except ImportError:
    PAYMENT_VERIFICATION_AVAILABLE = False


class LicenseManager:
    """Manages license keys and subscription validation"""
    
    # Subscription tiers
    TIER_TRIAL = "trial"
    TIER_BASIC = "basic"
    TIER_PRO = "pro"
    TIER_ENTERPRISE = "enterprise"
    
    # Subscription durations
    DURATION_TRIAL = 7  # days
    DURATION_MONTHLY = 30
    DURATION_YEARLY = 365
    
    def __init__(self, license_file: str = "license.dat", api_url: Optional[str] = None, 
                 payment_api_url: Optional[str] = None, require_payment: bool = True):
        """
        Initialize license manager (CLIENT-SIDE - Only validates, never generates)
        
        Args:
            license_file: Path to store license data
            api_url: Server API URL for license validation (REQUIRED for payment verification)
            payment_api_url: Optional API URL for payment verification (uses api_url if not set)
            require_payment: Whether to require payment verification
        """
        self.license_file = license_file
        self.api_url = api_url  # Server URL for validation
        self.require_payment = require_payment
        # IMPORTANT: This must match the server's SECRET_KEY
        # Client cannot generate licenses - only validates them
        self.secret_key = "CHANGE_THIS_TO_A_SECURE_RANDOM_KEY_IN_PRODUCTION_2024"
        
        # Initialize payment verification
        if PAYMENT_VERIFICATION_AVAILABLE:
            if payment_api_url:
                self.payment_verifier = PaymentVerifier(payment_api_url)
            elif api_url:
                # Use same server for payment verification
                self.payment_verifier = PaymentVerifier(api_url.replace('/api/validate', '/api/verify_payment'))
            else:
                self.payment_verifier = PaymentVerifier()  # Uses default URL
            self.payment_tracker = LocalPaymentTracker()
        else:
            self.payment_verifier = None
            self.payment_tracker = None
        
    def get_machine_id(self) -> str:
        """Generate unique machine ID"""
        machine_info = f"{platform.node()}{platform.processor()}{platform.system()}"
        return hashlib.md5(machine_info.encode()).hexdigest()
    
    def generate_license_key(self, email: str, tier: str, duration_days: int, 
                            license_id: str = None) -> str:
        """
        Generate a license key - DEPRECATED: Use server API instead
        
        NOTE: This function is kept for backward compatibility but should NOT be used.
        License generation must happen on the server for security.
        Use the server API endpoint /api/generate_license instead.
        
        This will raise an error to prevent client-side generation.
        """
        raise Exception(
            "License generation is not allowed on client side. "
            "Licenses must be generated on the server. "
            "Contact your administrator to get a license key."
        )
    
    def validate_license_key(self, license_key: str) -> Tuple[bool, Dict, str]:
        """
        Validate a license key
        
        Returns:
            (is_valid, license_data, error_message)
        """
        try:
            # Decode license
            license_json = base64.b64decode(license_key.encode()).decode()
            license_data = json.loads(license_json)
            
            # Verify signature
            signature = license_data.pop("signature")
            data_string = json.dumps(license_data, sort_keys=True)
            expected_signature = hmac.new(
                self.secret_key.encode(),
                data_string.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if signature != expected_signature:
                return False, {}, "Invalid license signature"
            
            # Check expiry
            expiry_date = datetime.fromisoformat(license_data["expiry_date"])
            if datetime.now() > expiry_date:
                return False, license_data, "License has expired"
            
            # Check machine binding (if activated)
            if license_data.get("machine_id"):
                current_machine_id = self.get_machine_id()
                if license_data["machine_id"] != current_machine_id:
                    return False, license_data, "License is bound to another machine"
            
            return True, license_data, ""
            
        except Exception as e:
            return False, {}, f"Invalid license format: {str(e)}"
    
    def activate_license(self, license_key: str) -> Tuple[bool, str]:
        """
        Activate license on this machine
        
        Returns:
            (success, message)
        """
        is_valid, license_data, error = self.validate_license_key(license_key)
        
        if not is_valid:
            return False, error
        
        # Verify with server before activation (REQUIRED)
        if self.api_url and REQUESTS_AVAILABLE:
            try:
                response = requests.post(
                    f"{self.api_url}/api/validate_license",
                    json={
                        "license_key": license_key,
                        "machine_id": self.get_machine_id(),
                        "action": "activate"
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    server_data = response.json()
                    if not server_data.get("valid", False):
                        return False, server_data.get("error", "Server validation failed")
                    if not server_data.get("paid", True):
                        return False, "Payment not confirmed by server. Please complete payment."
                elif response.status_code == 402:
                    return False, "Payment not confirmed. Please complete payment to activate license."
                else:
                    return False, f"Server validation failed: {response.json().get('error', 'Unknown error')}"
                    
            except requests.exceptions.RequestException as e:
                return False, f"Cannot connect to license server. Please check your internet connection. Error: {str(e)}"
        
        # Fallback: Check payment status locally (if server unavailable and payment not strictly required)
        elif self.require_payment and self.payment_verifier:
            email = license_data.get("email", "")
            if email:
                is_paid, payment_message, payment_data = self.payment_verifier.verify_payment(
                    email, license_key
                )
                
                if not is_paid:
                    return False, f"Payment not confirmed. {payment_message}. Please complete payment to activate license."
                
                # Mark as paid in local tracker
                if self.payment_tracker:
                    self.payment_tracker.mark_as_paid(email)
        
        # Bind to machine
        license_data["machine_id"] = self.get_machine_id()
        license_data["activated_date"] = datetime.now().isoformat()
        license_data["original_key"] = license_key  # Store original key
        
        # Save license
        self.save_license(license_data)
        
        # Optional: Validate online
        if self.api_url and REQUESTS_AVAILABLE:
            try:
                response = requests.post(
                    self.api_url,
                    json={
                        "license_key": license_key,
                        "machine_id": license_data["machine_id"],
                        "action": "activate"
                    },
                    timeout=5
                )
                if response.status_code != 200:
                    # Still allow offline activation
                    pass
            except:
                pass  # Continue with offline activation
        
        return True, "License activated successfully"
    
    def load_license(self) -> Optional[Dict]:
        """Load license from file"""
        if not os.path.exists(self.license_file):
            return None
        
        try:
            with open(self.license_file, 'r') as f:
                return json.load(f)
        except:
            return None
    
    def save_license(self, license_data: Dict):
        """Save license to file"""
        with open(self.license_file, 'w') as f:
            json.dump(license_data, f)
    
    def check_license_status(self) -> Tuple[bool, Dict, str]:
        """
        Check current license status
        
        Returns:
            (is_valid, license_data, message)
        """
        license_data = self.load_license()
        
        if not license_data:
            return False, {}, "No license found"
        
        # Check expiry
        expiry_date = datetime.fromisoformat(license_data["expiry_date"])
        if datetime.now() > expiry_date:
            return False, license_data, "License has expired"
        
        # Check machine binding
        current_machine_id = self.get_machine_id()
        if license_data.get("machine_id") != current_machine_id:
            return False, license_data, "License not activated on this machine"
        
        # Check payment status (if required)
        if self.require_payment and self.payment_verifier:
            email = license_data.get("email", "")
            if email:
                # Check local payment tracker first (faster)
                if self.payment_tracker and not self.payment_tracker.is_paid(email):
                    # Verify with server
                    is_paid, payment_message, payment_data = self.payment_verifier.verify_payment(
                        email, license_data.get("original_key", "")
                    )
                    
                    if not is_paid:
                        return False, license_data, f"Payment not confirmed. {payment_message}. Please complete payment."
                    
                    # Update local tracker
                    if self.payment_tracker:
                        self.payment_tracker.mark_as_paid(email)
        
        # Online validation with server (REQUIRED for payment verification)
        if self.api_url and REQUESTS_AVAILABLE and license_data.get("original_key"):
            try:
                response = requests.post(
                    f"{self.api_url}/api/validate_license",
                    json={
                        "license_key": license_data["original_key"],
                        "machine_id": current_machine_id,
                        "action": "validate"
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    server_data = response.json()
                    if not server_data.get("valid", False):
                        return False, license_data, server_data.get("error", "Server validation failed")
                    if not server_data.get("paid", True):
                        return False, license_data, "Payment not confirmed by server"
                elif response.status_code == 402:
                    # Payment required
                    return False, license_data, "Payment not confirmed. Please complete payment."
                else:
                    # If server is down, allow offline validation but warn
                    if self.require_payment:
                        return False, license_data, "Cannot verify payment - server unavailable"
            except requests.exceptions.RequestException:
                # Server unreachable
                if self.require_payment:
                    return False, license_data, "Cannot verify payment - server unavailable. Please check your internet connection."
                # Allow offline if payment not required
                pass
        
        days_remaining = (expiry_date - datetime.now()).days
        return True, license_data, f"License valid ({days_remaining} days remaining)"
    
    def get_subscription_limits(self, tier: str) -> Dict:
        """Get limits for subscription tier"""
        limits = {
            self.TIER_TRIAL: {
                "max_searches_per_day": 10,
                "max_results_per_search": 50,
                "features": ["basic_scraping"]
            },
            self.TIER_BASIC: {
                "max_searches_per_day": 100,
                "max_results_per_search": 500,
                "features": ["basic_scraping", "excel_export"]
            },
            self.TIER_PRO: {
                "max_searches_per_day": 1000,
                "max_results_per_search": 5000,
                "features": ["basic_scraping", "excel_export", "csv_export", "social_media"]
            },
            self.TIER_ENTERPRISE: {
                "max_searches_per_day": -1,  # Unlimited
                "max_results_per_search": -1,
                "features": ["all"]
            }
        }
        return limits.get(tier, limits[self.TIER_TRIAL])
    
    def can_perform_action(self, action: str, license_data: Dict = None) -> bool:
        """Check if user can perform an action based on license"""
        if not license_data:
            is_valid, license_data, _ = self.check_license_status()
            if not is_valid:
                return False
        
        limits = self.get_subscription_limits(license_data["tier"])
        
        if action == "scrape":
            return True  # All tiers can scrape
        elif action == "export_excel":
            return "excel_export" in limits["features"] or "all" in limits["features"]
        elif action == "export_csv":
            return "csv_export" in limits["features"] or "all" in limits["features"]
        elif action == "social_media":
            return "social_media" in limits["features"] or "all" in limits["features"]
        
        return False

