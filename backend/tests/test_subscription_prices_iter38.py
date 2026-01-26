"""
Test Suite for Subscription Prices Feature - Iteration 38
Tests the ability to manually control subscription prices in USD

Features tested:
- GET /api/super-admin/subscription-prices - Fetch subscription prices
- PUT /api/super-admin/subscription-prices - Update subscription prices
- Prices stored in settings collection with type "subscription_prices"
- Default prices: basic=$25/month, premium=$50/month
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestSubscriptionPricesAPI:
    """Test subscription prices API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - login as super admin"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as super admin
        login_response = self.session.post(f"{BASE_URL}/api/super-admin/login", json={
            "email": "owner@maestroegp.com",
            "password": "owner123",
            "secret_key": "271018"
        })
        
        if login_response.status_code == 200:
            token = login_response.json().get("token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
            self.token = token
        else:
            pytest.skip(f"Super admin login failed: {login_response.status_code}")
    
    def test_01_super_admin_login_success(self):
        """Test super admin login works"""
        response = self.session.post(f"{BASE_URL}/api/super-admin/login", json={
            "email": "owner@maestroegp.com",
            "password": "owner123",
            "secret_key": "271018"
        })
        
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data, "Token not in response"
        assert data.get("user", {}).get("role") == "super_admin", "User is not super_admin"
        print("✅ Super admin login successful")
    
    def test_02_get_subscription_prices(self):
        """Test GET /api/super-admin/subscription-prices returns prices"""
        response = self.session.get(f"{BASE_URL}/api/super-admin/subscription-prices")
        
        assert response.status_code == 200, f"GET prices failed: {response.text}"
        data = response.json()
        
        # Check response structure
        assert "prices" in data, "prices key missing from response"
        assert "currency" in data, "currency key missing from response"
        assert data["currency"] == "USD", f"Currency should be USD, got {data['currency']}"
        
        prices = data["prices"]
        
        # Check all subscription types exist
        assert "basic" in prices, "basic subscription type missing"
        assert "premium" in prices, "premium subscription type missing"
        assert "trial" in prices, "trial subscription type missing"
        assert "demo" in prices, "demo subscription type missing"
        
        # Check price structure
        for sub_type in ["basic", "premium", "trial", "demo"]:
            assert "monthly" in prices[sub_type], f"{sub_type} missing monthly price"
            assert "name" in prices[sub_type], f"{sub_type} missing name"
        
        print(f"✅ GET subscription prices successful")
        print(f"   Basic: ${prices['basic']['monthly']}/month")
        print(f"   Premium: ${prices['premium']['monthly']}/month")
        print(f"   Trial: ${prices['trial']['monthly']}/month")
        print(f"   Demo: ${prices['demo']['monthly']}/month")
    
    def test_03_update_subscription_prices(self):
        """Test PUT /api/super-admin/subscription-prices updates prices"""
        # Set new prices
        new_prices = {
            "basic": 30.00,
            "premium": 60.00
        }
        
        response = self.session.put(
            f"{BASE_URL}/api/super-admin/subscription-prices",
            json=new_prices
        )
        
        assert response.status_code == 200, f"PUT prices failed: {response.text}"
        data = response.json()
        
        # Check response
        assert "message" in data, "message missing from response"
        assert "prices" in data, "prices missing from response"
        assert "currency" in data, "currency missing from response"
        assert data["currency"] == "USD", "Currency should be USD"
        
        # Verify prices were updated
        prices = data["prices"]
        assert prices["basic"]["monthly"] == 30.00, f"Basic price not updated: {prices['basic']['monthly']}"
        assert prices["premium"]["monthly"] == 60.00, f"Premium price not updated: {prices['premium']['monthly']}"
        
        print(f"✅ PUT subscription prices successful")
        print(f"   Updated Basic: ${prices['basic']['monthly']}/month")
        print(f"   Updated Premium: ${prices['premium']['monthly']}/month")
    
    def test_04_verify_prices_persisted(self):
        """Test that updated prices are persisted and returned on GET"""
        # First update prices
        update_response = self.session.put(
            f"{BASE_URL}/api/super-admin/subscription-prices",
            json={"basic": 35.00, "premium": 70.00}
        )
        assert update_response.status_code == 200, "Update failed"
        
        # Then GET to verify persistence
        get_response = self.session.get(f"{BASE_URL}/api/super-admin/subscription-prices")
        assert get_response.status_code == 200, "GET failed"
        
        data = get_response.json()
        prices = data["prices"]
        
        assert prices["basic"]["monthly"] == 35.00, f"Basic price not persisted: {prices['basic']['monthly']}"
        assert prices["premium"]["monthly"] == 70.00, f"Premium price not persisted: {prices['premium']['monthly']}"
        
        print("✅ Prices persisted correctly after update")
    
    def test_05_prices_in_subscriptions_dashboard(self):
        """Test that subscription prices appear in subscriptions dashboard"""
        response = self.session.get(f"{BASE_URL}/api/super-admin/subscriptions-dashboard")
        
        assert response.status_code == 200, f"Dashboard failed: {response.text}"
        data = response.json()
        
        # Check subscription_prices in dashboard response
        assert "subscription_prices" in data, "subscription_prices missing from dashboard"
        
        prices = data["subscription_prices"]
        assert "basic" in prices, "basic missing from dashboard prices"
        assert "premium" in prices, "premium missing from dashboard prices"
        
        print("✅ Subscription prices appear in dashboard")
        print(f"   Dashboard Basic: ${prices['basic'].get('monthly', 0)}/month")
        print(f"   Dashboard Premium: ${prices['premium'].get('monthly', 0)}/month")
    
    def test_06_unauthorized_access_rejected(self):
        """Test that unauthorized access is rejected"""
        # Create new session without auth
        unauth_session = requests.Session()
        unauth_session.headers.update({"Content-Type": "application/json"})
        
        # Try GET without auth
        get_response = unauth_session.get(f"{BASE_URL}/api/super-admin/subscription-prices")
        assert get_response.status_code in [401, 403], f"GET should be rejected: {get_response.status_code}"
        
        # Try PUT without auth
        put_response = unauth_session.put(
            f"{BASE_URL}/api/super-admin/subscription-prices",
            json={"basic": 100, "premium": 200}
        )
        assert put_response.status_code in [401, 403], f"PUT should be rejected: {put_response.status_code}"
        
        print("✅ Unauthorized access correctly rejected")
    
    def test_07_non_super_admin_rejected(self):
        """Test that non-super-admin users are rejected"""
        # Login as regular admin
        admin_session = requests.Session()
        admin_session.headers.update({"Content-Type": "application/json"})
        
        login_response = admin_session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@maestroegp.com",
            "password": "admin123"
        })
        
        if login_response.status_code == 200:
            token = login_response.json().get("token")
            admin_session.headers.update({"Authorization": f"Bearer {token}"})
            
            # Try to access subscription prices
            get_response = admin_session.get(f"{BASE_URL}/api/super-admin/subscription-prices")
            assert get_response.status_code in [401, 403], f"Non-super-admin should be rejected: {get_response.status_code}"
            
            print("✅ Non-super-admin access correctly rejected")
        else:
            print("⚠️ Admin login failed, skipping non-super-admin test")
    
    def test_08_reset_to_default_prices(self):
        """Reset prices to default values for clean state"""
        response = self.session.put(
            f"{BASE_URL}/api/super-admin/subscription-prices",
            json={"basic": 25.00, "premium": 50.00}
        )
        
        assert response.status_code == 200, f"Reset failed: {response.text}"
        
        # Verify reset
        get_response = self.session.get(f"{BASE_URL}/api/super-admin/subscription-prices")
        data = get_response.json()
        prices = data["prices"]
        
        assert prices["basic"]["monthly"] == 25.00, "Basic not reset to default"
        assert prices["premium"]["monthly"] == 50.00, "Premium not reset to default"
        
        print("✅ Prices reset to defaults: basic=$25, premium=$50")


class TestSubscriptionPricesValidation:
    """Test validation for subscription prices"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - login as super admin"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        login_response = self.session.post(f"{BASE_URL}/api/super-admin/login", json={
            "email": "owner@maestroegp.com",
            "password": "owner123",
            "secret_key": "271018"
        })
        
        if login_response.status_code == 200:
            token = login_response.json().get("token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
        else:
            pytest.skip("Super admin login failed")
    
    def test_09_decimal_prices_accepted(self):
        """Test that decimal prices are accepted"""
        response = self.session.put(
            f"{BASE_URL}/api/super-admin/subscription-prices",
            json={"basic": 29.99, "premium": 59.99}
        )
        
        assert response.status_code == 200, f"Decimal prices failed: {response.text}"
        
        data = response.json()
        prices = data["prices"]
        
        assert prices["basic"]["monthly"] == 29.99, "Decimal basic price not saved"
        assert prices["premium"]["monthly"] == 59.99, "Decimal premium price not saved"
        
        print("✅ Decimal prices accepted: basic=$29.99, premium=$59.99")
    
    def test_10_zero_prices_accepted(self):
        """Test that zero prices are accepted (for free tiers)"""
        response = self.session.put(
            f"{BASE_URL}/api/super-admin/subscription-prices",
            json={"basic": 0, "premium": 0}
        )
        
        assert response.status_code == 200, f"Zero prices failed: {response.text}"
        
        data = response.json()
        prices = data["prices"]
        
        assert prices["basic"]["monthly"] == 0, "Zero basic price not saved"
        assert prices["premium"]["monthly"] == 0, "Zero premium price not saved"
        
        print("✅ Zero prices accepted")
        
        # Reset to defaults
        self.session.put(
            f"{BASE_URL}/api/super-admin/subscription-prices",
            json={"basic": 25, "premium": 50}
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
