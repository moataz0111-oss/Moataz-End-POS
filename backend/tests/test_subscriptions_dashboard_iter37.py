"""
Test Suite for Subscriptions Dashboard API - Iteration 37
Tests the new subscriptions dashboard endpoint: GET /api/super-admin/subscriptions-dashboard
"""

import pytest
import requests
import os
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
SUPER_ADMIN_EMAIL = "owner@maestroegp.com"
SUPER_ADMIN_PASSWORD = "owner123"
SECRET_KEY = "271018"


class TestSubscriptionsDashboard:
    """Tests for the subscriptions dashboard API"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - get auth token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as super admin
        login_response = self.session.post(
            f"{BASE_URL}/api/super-admin/login",
            json={
                "email": SUPER_ADMIN_EMAIL,
                "password": SUPER_ADMIN_PASSWORD,
                "secret_key": SECRET_KEY
            }
        )
        
        if login_response.status_code == 200:
            token = login_response.json().get("token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
        else:
            pytest.skip("Super admin login failed - skipping tests")
    
    def test_subscriptions_dashboard_endpoint_exists(self):
        """Test that the subscriptions dashboard endpoint exists and returns 200"""
        response = self.session.get(f"{BASE_URL}/api/super-admin/subscriptions-dashboard")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✅ Subscriptions dashboard endpoint exists and returns 200")
    
    def test_subscriptions_dashboard_response_structure(self):
        """Test that the response has the correct structure"""
        response = self.session.get(f"{BASE_URL}/api/super-admin/subscriptions-dashboard")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check main keys exist
        assert "summary" in data, "Missing 'summary' key"
        assert "subscription_types" in data, "Missing 'subscription_types' key"
        assert "expected_revenue" in data, "Missing 'expected_revenue' key"
        assert "expiring_soon_list" in data, "Missing 'expiring_soon_list' key"
        assert "expired_list" in data, "Missing 'expired_list' key"
        assert "subscription_prices" in data, "Missing 'subscription_prices' key"
        
        print("✅ Response has correct structure with all required keys")
    
    def test_summary_section_structure(self):
        """Test that the summary section has all required fields"""
        response = self.session.get(f"{BASE_URL}/api/super-admin/subscriptions-dashboard")
        assert response.status_code == 200
        
        summary = response.json().get("summary", {})
        
        # Check summary fields
        assert "total_tenants" in summary, "Missing 'total_tenants' in summary"
        assert "active_subscriptions" in summary, "Missing 'active_subscriptions' in summary"
        assert "expiring_soon" in summary, "Missing 'expiring_soon' in summary"
        assert "already_expired" in summary, "Missing 'already_expired' in summary"
        assert "days_before_alert" in summary, "Missing 'days_before_alert' in summary"
        
        # Check types
        assert isinstance(summary["total_tenants"], int), "total_tenants should be int"
        assert isinstance(summary["active_subscriptions"], int), "active_subscriptions should be int"
        assert isinstance(summary["expiring_soon"], int), "expiring_soon should be int"
        assert isinstance(summary["already_expired"], int), "already_expired should be int"
        assert isinstance(summary["days_before_alert"], int), "days_before_alert should be int"
        
        print(f"✅ Summary section has correct structure:")
        print(f"   - Total tenants: {summary['total_tenants']}")
        print(f"   - Active subscriptions: {summary['active_subscriptions']}")
        print(f"   - Expiring soon: {summary['expiring_soon']}")
        print(f"   - Already expired: {summary['already_expired']}")
        print(f"   - Days before alert: {summary['days_before_alert']}")
    
    def test_subscription_types_structure(self):
        """Test that subscription_types has correct structure"""
        response = self.session.get(f"{BASE_URL}/api/super-admin/subscriptions-dashboard")
        assert response.status_code == 200
        
        subscription_types = response.json().get("subscription_types", {})
        
        # Each subscription type should have count, active, expired
        for sub_type, data in subscription_types.items():
            assert "count" in data, f"Missing 'count' in {sub_type}"
            assert "active" in data, f"Missing 'active' in {sub_type}"
            assert "expired" in data, f"Missing 'expired' in {sub_type}"
            assert isinstance(data["count"], int), f"count should be int for {sub_type}"
            assert isinstance(data["active"], int), f"active should be int for {sub_type}"
            assert isinstance(data["expired"], int), f"expired should be int for {sub_type}"
        
        print(f"✅ Subscription types structure is correct:")
        for sub_type, data in subscription_types.items():
            print(f"   - {sub_type}: count={data['count']}, active={data['active']}, expired={data['expired']}")
    
    def test_expected_revenue_structure(self):
        """Test that expected_revenue has correct structure"""
        response = self.session.get(f"{BASE_URL}/api/super-admin/subscriptions-dashboard")
        assert response.status_code == 200
        
        expected_revenue = response.json().get("expected_revenue", {})
        
        # Check required fields
        assert "from_expiring" in expected_revenue, "Missing 'from_expiring'"
        assert "from_active" in expected_revenue, "Missing 'from_active'"
        assert "total_monthly" in expected_revenue, "Missing 'total_monthly'"
        assert "details" in expected_revenue, "Missing 'details'"
        
        # Check types
        assert isinstance(expected_revenue["from_expiring"], (int, float)), "from_expiring should be numeric"
        assert isinstance(expected_revenue["from_active"], (int, float)), "from_active should be numeric"
        assert isinstance(expected_revenue["total_monthly"], (int, float)), "total_monthly should be numeric"
        assert isinstance(expected_revenue["details"], list), "details should be a list"
        
        print(f"✅ Expected revenue structure is correct:")
        print(f"   - From expiring: {expected_revenue['from_expiring']} IQD")
        print(f"   - From active: {expected_revenue['from_active']} IQD")
        print(f"   - Total monthly: {expected_revenue['total_monthly']} IQD")
    
    def test_subscription_prices_structure(self):
        """Test that subscription_prices has correct structure"""
        response = self.session.get(f"{BASE_URL}/api/super-admin/subscriptions-dashboard")
        assert response.status_code == 200
        
        subscription_prices = response.json().get("subscription_prices", {})
        
        # Check expected subscription types exist
        expected_types = ["basic", "premium", "trial", "demo"]
        for sub_type in expected_types:
            assert sub_type in subscription_prices, f"Missing '{sub_type}' in subscription_prices"
            assert "monthly" in subscription_prices[sub_type], f"Missing 'monthly' for {sub_type}"
            assert "name" in subscription_prices[sub_type], f"Missing 'name' for {sub_type}"
        
        # Verify default prices
        assert subscription_prices["basic"]["monthly"] == 50000, "Basic price should be 50000"
        assert subscription_prices["premium"]["monthly"] == 100000, "Premium price should be 100000"
        assert subscription_prices["trial"]["monthly"] == 0, "Trial price should be 0"
        assert subscription_prices["demo"]["monthly"] == 0, "Demo price should be 0"
        
        print(f"✅ Subscription prices are correct:")
        for sub_type, data in subscription_prices.items():
            print(f"   - {sub_type}: {data['monthly']} IQD/month ({data['name']})")
    
    def test_expiring_soon_list_structure(self):
        """Test that expiring_soon_list has correct structure"""
        response = self.session.get(f"{BASE_URL}/api/super-admin/subscriptions-dashboard")
        assert response.status_code == 200
        
        expiring_soon_list = response.json().get("expiring_soon_list", [])
        
        # Should be a list
        assert isinstance(expiring_soon_list, list), "expiring_soon_list should be a list"
        
        # If there are items, check structure
        if len(expiring_soon_list) > 0:
            tenant = expiring_soon_list[0]
            # Should have tenant fields
            assert "name" in tenant or "slug" in tenant, "Tenant should have name or slug"
            if "days_left" in tenant:
                assert isinstance(tenant["days_left"], (int, type(None))), "days_left should be int or None"
        
        print(f"✅ Expiring soon list structure is correct (count: {len(expiring_soon_list)})")
    
    def test_expired_list_structure(self):
        """Test that expired_list has correct structure"""
        response = self.session.get(f"{BASE_URL}/api/super-admin/subscriptions-dashboard")
        assert response.status_code == 200
        
        expired_list = response.json().get("expired_list", [])
        
        # Should be a list
        assert isinstance(expired_list, list), "expired_list should be a list"
        
        # If there are items, check structure
        if len(expired_list) > 0:
            tenant = expired_list[0]
            # Should have tenant fields
            assert "name" in tenant or "slug" in tenant, "Tenant should have name or slug"
            if "days_expired" in tenant:
                assert isinstance(tenant["days_expired"], (int, type(None))), "days_expired should be int or None"
        
        print(f"✅ Expired list structure is correct (count: {len(expired_list)})")
    
    def test_unauthorized_access(self):
        """Test that unauthorized access is rejected"""
        # Create a new session without auth
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        response = session.get(f"{BASE_URL}/api/super-admin/subscriptions-dashboard")
        
        # Should return 401 or 403
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✅ Unauthorized access is correctly rejected")
    
    def test_non_super_admin_access(self):
        """Test that non-super-admin users cannot access the endpoint"""
        # Try to login as regular admin
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        login_response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "admin@maestroegp.com",
                "password": "admin123"
            }
        )
        
        if login_response.status_code == 200:
            token = login_response.json().get("token")
            session.headers.update({"Authorization": f"Bearer {token}"})
            
            response = session.get(f"{BASE_URL}/api/super-admin/subscriptions-dashboard")
            
            # Should return 401 or 403
            assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
            print("✅ Non-super-admin access is correctly rejected")
        else:
            print("⚠️ Could not test non-super-admin access - admin login failed")


class TestSubscriptionsDashboardDataIntegrity:
    """Tests for data integrity in subscriptions dashboard"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - get auth token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as super admin
        login_response = self.session.post(
            f"{BASE_URL}/api/super-admin/login",
            json={
                "email": SUPER_ADMIN_EMAIL,
                "password": SUPER_ADMIN_PASSWORD,
                "secret_key": SECRET_KEY
            }
        )
        
        if login_response.status_code == 200:
            token = login_response.json().get("token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
        else:
            pytest.skip("Super admin login failed - skipping tests")
    
    def test_summary_counts_consistency(self):
        """Test that summary counts are consistent with subscription_types"""
        response = self.session.get(f"{BASE_URL}/api/super-admin/subscriptions-dashboard")
        assert response.status_code == 200
        
        data = response.json()
        summary = data.get("summary", {})
        subscription_types = data.get("subscription_types", {})
        
        # Total tenants should equal sum of all subscription type counts
        total_from_types = sum(st.get("count", 0) for st in subscription_types.values())
        assert summary["total_tenants"] == total_from_types, \
            f"Total tenants mismatch: summary={summary['total_tenants']}, types sum={total_from_types}"
        
        print(f"✅ Summary counts are consistent with subscription types")
    
    def test_revenue_calculation_logic(self):
        """Test that revenue calculations are logical"""
        response = self.session.get(f"{BASE_URL}/api/super-admin/subscriptions-dashboard")
        assert response.status_code == 200
        
        data = response.json()
        expected_revenue = data.get("expected_revenue", {})
        
        # total_monthly should equal from_active
        assert expected_revenue["total_monthly"] == expected_revenue["from_active"], \
            "total_monthly should equal from_active"
        
        # All revenue values should be non-negative
        assert expected_revenue["from_expiring"] >= 0, "from_expiring should be non-negative"
        assert expected_revenue["from_active"] >= 0, "from_active should be non-negative"
        assert expected_revenue["total_monthly"] >= 0, "total_monthly should be non-negative"
        
        print(f"✅ Revenue calculations are logical")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
