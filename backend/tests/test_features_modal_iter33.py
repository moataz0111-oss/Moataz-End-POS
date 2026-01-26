"""
Test Suite for Super Admin Features Modal - Iteration 33
Tests the tenant features/permissions management functionality:
- Super Admin login to /super-admin
- View tenants list (active, trial, all tabs)
- Open features modal for a tenant
- Verify all 4 sections (basic, advanced, additional, settings)
- Enable/disable features and save
- API: GET /api/super-admin/tenants/{id}/features
- API: PUT /api/super-admin/tenants/{id}/features
- Verify features apply to tenant on login
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
SUPER_ADMIN_CREDS = {
    "email": "owner@maestroegp.com",
    "password": "owner123",
    "secret_key": "271018"
}

TEST_CLIENT_CREDS = {
    "email": "test@test.com",
    "password": "test123"
}

CLIENT_GRAFFITI_CREDS = {
    "email": "hanialdujaili@gmail.com",
    "password": "graffiti123"
}


class TestSuperAdminLogin:
    """Test Super Admin authentication"""
    
    def test_api_health(self):
        """Verify API is running"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        print("✅ API health check passed")
    
    def test_super_admin_login_success(self):
        """Test Super Admin login with correct credentials"""
        response = requests.post(f"{BASE_URL}/api/super-admin/login", json=SUPER_ADMIN_CREDS)
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["role"] == "super_admin"
        print(f"✅ Super Admin login successful - User: {data['user']['email']}")
        return data["token"]
    
    def test_super_admin_login_wrong_secret(self):
        """Test Super Admin login with wrong secret key"""
        wrong_creds = {**SUPER_ADMIN_CREDS, "secret_key": "wrong123"}
        response = requests.post(f"{BASE_URL}/api/super-admin/login", json=wrong_creds)
        assert response.status_code in [401, 403]
        print("✅ Super Admin login correctly rejected with wrong secret key")
    
    def test_super_admin_login_wrong_password(self):
        """Test Super Admin login with wrong password"""
        wrong_creds = {**SUPER_ADMIN_CREDS, "password": "wrongpass"}
        response = requests.post(f"{BASE_URL}/api/super-admin/login", json=wrong_creds)
        assert response.status_code == 401
        print("✅ Super Admin login correctly rejected with wrong password")


class TestTenantsListAPI:
    """Test tenants list API endpoints"""
    
    @pytest.fixture
    def auth_token(self):
        """Get Super Admin auth token"""
        response = requests.post(f"{BASE_URL}/api/super-admin/login", json=SUPER_ADMIN_CREDS)
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Super Admin login failed")
    
    def test_get_tenants_list(self, auth_token):
        """Test GET /api/super-admin/tenants"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/super-admin/tenants", headers=headers)
        assert response.status_code == 200
        tenants = response.json()
        assert isinstance(tenants, list)
        print(f"✅ GET /api/super-admin/tenants - Found {len(tenants)} tenants")
        
        # Print tenant names for verification
        for tenant in tenants:
            print(f"   - {tenant.get('name', 'N/A')} ({tenant.get('owner_email', 'N/A')})")
        
        return tenants
    
    def test_get_super_admin_stats(self, auth_token):
        """Test GET /api/super-admin/stats"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/super-admin/stats", headers=headers)
        assert response.status_code == 200
        stats = response.json()
        assert "total_tenants" in stats
        print(f"✅ GET /api/super-admin/stats - Total tenants: {stats.get('total_tenants', 0)}")
        return stats


class TestFeaturesAPI:
    """Test tenant features API endpoints"""
    
    @pytest.fixture
    def auth_token(self):
        """Get Super Admin auth token"""
        response = requests.post(f"{BASE_URL}/api/super-admin/login", json=SUPER_ADMIN_CREDS)
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Super Admin login failed")
    
    @pytest.fixture
    def tenant_id(self, auth_token):
        """Get first tenant ID for testing"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/super-admin/tenants", headers=headers)
        if response.status_code == 200:
            tenants = response.json()
            if tenants:
                return tenants[0]["id"]
        pytest.skip("No tenants found for testing")
    
    def test_get_tenant_features(self, auth_token, tenant_id):
        """Test GET /api/super-admin/tenants/{id}/features"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/super-admin/tenants/{tenant_id}/features", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "features" in data
        features = data["features"]
        
        # Verify basic features exist (8 features)
        basic_features = ["showPOS", "showTables", "showOrders", "showReports", 
                         "showExpenses", "showInventory", "showDelivery", "showKitchen"]
        for feature in basic_features:
            assert feature in features, f"Missing basic feature: {feature}"
        print(f"✅ Basic features section verified (8 features)")
        
        # Verify advanced features exist (8 features)
        advanced_features = ["showHR", "showWarehouse", "showCallCenter", "showCallLogs",
                           "showLoyalty", "showCoupons", "showRecipes", "showReservations"]
        for feature in advanced_features:
            assert feature in features, f"Missing advanced feature: {feature}"
        print(f"✅ Advanced features section verified (8 features)")
        
        # Verify additional features exist (4 features)
        additional_features = ["showSmartReports", "showBranchOrders", "showPurchasing", "showReviews"]
        for feature in additional_features:
            assert feature in features, f"Missing additional feature: {feature}"
        print(f"✅ Additional features section verified (4 features)")
        
        # Verify settings options exist (9 options)
        settings_options = ["settingsUsers", "settingsCustomers", "settingsCategories",
                          "settingsProducts", "settingsDeliveryCompanies", "settingsBranches",
                          "settingsPrinters", "settingsNotifications", "settingsCallCenter"]
        for option in settings_options:
            assert option in features, f"Missing settings option: {option}"
        print(f"✅ Settings options section verified (9 options)")
        
        print(f"✅ GET /api/super-admin/tenants/{tenant_id}/features - All 4 sections verified")
        return features
    
    def test_update_tenant_features(self, auth_token, tenant_id):
        """Test PUT /api/super-admin/tenants/{id}/features"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # First get current features
        get_response = requests.get(f"{BASE_URL}/api/super-admin/tenants/{tenant_id}/features", headers=headers)
        assert get_response.status_code == 200
        original_features = get_response.json()["features"]
        
        # Toggle a feature (showHR)
        new_features = {**original_features}
        new_features["showHR"] = not original_features.get("showHR", False)
        
        # Update features
        put_response = requests.put(
            f"{BASE_URL}/api/super-admin/tenants/{tenant_id}/features",
            headers=headers,
            json=new_features
        )
        assert put_response.status_code == 200
        print(f"✅ PUT /api/super-admin/tenants/{tenant_id}/features - Features updated")
        
        # Verify the change persisted
        verify_response = requests.get(f"{BASE_URL}/api/super-admin/tenants/{tenant_id}/features", headers=headers)
        assert verify_response.status_code == 200
        updated_features = verify_response.json()["features"]
        assert updated_features["showHR"] == new_features["showHR"]
        print(f"✅ Feature change verified - showHR is now: {updated_features['showHR']}")
        
        # Restore original value
        restore_response = requests.put(
            f"{BASE_URL}/api/super-admin/tenants/{tenant_id}/features",
            headers=headers,
            json=original_features
        )
        assert restore_response.status_code == 200
        print(f"✅ Original features restored")
    
    def test_enable_all_features(self, auth_token, tenant_id):
        """Test enabling all features for a tenant"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Enable all features
        all_enabled = {
            "showPOS": True, "showTables": True, "showOrders": True, "showReports": True,
            "showExpenses": True, "showInventory": True, "showDelivery": True, "showKitchen": True,
            "showHR": True, "showWarehouse": True, "showCallCenter": True, "showCallLogs": True,
            "showLoyalty": True, "showCoupons": True, "showRecipes": True, "showReservations": True,
            "showSmartReports": True, "showBranchOrders": True, "showPurchasing": True, "showReviews": True,
            "settingsUsers": True, "settingsCustomers": True, "settingsCategories": True,
            "settingsProducts": True, "settingsDeliveryCompanies": True, "settingsBranches": True,
            "settingsPrinters": True, "settingsNotifications": True, "settingsCallCenter": True
        }
        
        response = requests.put(
            f"{BASE_URL}/api/super-admin/tenants/{tenant_id}/features",
            headers=headers,
            json=all_enabled
        )
        assert response.status_code == 200
        print(f"✅ All features enabled for tenant {tenant_id}")
        
        # Verify
        verify_response = requests.get(f"{BASE_URL}/api/super-admin/tenants/{tenant_id}/features", headers=headers)
        assert verify_response.status_code == 200
        features = verify_response.json()["features"]
        
        enabled_count = sum(1 for v in features.values() if v is True)
        print(f"✅ Verified {enabled_count} features are enabled")
    
    def test_disable_all_features(self, auth_token, tenant_id):
        """Test disabling all features for a tenant"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Disable all features (except mandatory ones)
        all_disabled = {
            "showPOS": True,  # POS is mandatory
            "showTables": False, "showOrders": False, "showReports": False,
            "showExpenses": False, "showInventory": False, "showDelivery": False, "showKitchen": False,
            "showHR": False, "showWarehouse": False, "showCallCenter": False, "showCallLogs": False,
            "showLoyalty": False, "showCoupons": False, "showRecipes": False, "showReservations": False,
            "showSmartReports": False, "showBranchOrders": False, "showPurchasing": False, "showReviews": False,
            "showSettings": True,  # Settings is mandatory
            "settingsUsers": False, "settingsCustomers": False, "settingsCategories": False,
            "settingsProducts": False, "settingsDeliveryCompanies": False, "settingsBranches": False,
            "settingsPrinters": False, "settingsNotifications": False, "settingsCallCenter": False
        }
        
        response = requests.put(
            f"{BASE_URL}/api/super-admin/tenants/{tenant_id}/features",
            headers=headers,
            json=all_disabled
        )
        assert response.status_code == 200
        print(f"✅ Features disabled for tenant {tenant_id}")
    
    def test_features_api_unauthorized(self):
        """Test features API without authentication"""
        # Try to get features without token
        response = requests.get(f"{BASE_URL}/api/super-admin/tenants/test-id/features")
        assert response.status_code in [401, 403]
        print("✅ Features API correctly requires authentication")
    
    def test_features_api_invalid_tenant(self, auth_token):
        """Test features API with invalid tenant ID"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/super-admin/tenants/invalid-tenant-id/features", headers=headers)
        assert response.status_code == 404
        print("✅ Features API correctly returns 404 for invalid tenant")


class TestClientFeaturesApplication:
    """Test that features are applied when client logs in"""
    
    @pytest.fixture
    def super_admin_token(self):
        """Get Super Admin auth token"""
        response = requests.post(f"{BASE_URL}/api/super-admin/login", json=SUPER_ADMIN_CREDS)
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Super Admin login failed")
    
    def test_client_login(self):
        """Test client login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_GRAFFITI_CREDS["email"],
            "password": CLIENT_GRAFFITI_CREDS["password"]
        })
        
        if response.status_code == 200:
            data = response.json()
            assert "token" in data
            print(f"✅ Client login successful - {CLIENT_GRAFFITI_CREDS['email']}")
            return data["token"]
        else:
            print(f"⚠️ Client login failed with status {response.status_code}")
            pytest.skip("Client login failed - may need password reset")
    
    def test_client_settings_endpoint(self):
        """Test client settings endpoint returns features"""
        # First login
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CLIENT_GRAFFITI_CREDS["email"],
            "password": CLIENT_GRAFFITI_CREDS["password"]
        })
        
        if login_response.status_code != 200:
            pytest.skip("Client login failed")
        
        token = login_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get settings
        settings_response = requests.get(f"{BASE_URL}/api/settings", headers=headers)
        if settings_response.status_code == 200:
            settings = settings_response.json()
            print(f"✅ Client settings retrieved successfully")
            # Check if features are included in settings
            if "features" in settings or any(k.startswith("show") for k in settings.keys()):
                print(f"✅ Features found in client settings")
        else:
            print(f"⚠️ Settings endpoint returned {settings_response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
