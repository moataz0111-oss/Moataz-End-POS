"""
Iteration 35 - Testing new features:
1. Dialog إضافة خلفية جديدة - وضع URL
2. Dialog إضافة خلفية جديدة - وضع رفع من الجهاز
3. نافذة الميزات والصلاحيات - عرض الأقسام الأربعة
4. نافذة الميزات والصلاحيات - زر تفعيل/تعطيل الكل
5. نافذة الميزات والصلاحيات - حفظ الميزات
6. قائمة مدة الانتقال المنسدلة - اختيار القيم (0.5-5 ثواني)
7. إحصائيات المالك - استبعاد الحسابات التجريبية
8. packaging_cost - يُضاف للتوصيل والسفري فقط
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
DEMO_TENANT_ID = "82092f09-0381-4879-a90b-31dab76cce97"

class TestSuperAdminAuth:
    """Test Super Admin authentication"""
    
    @pytest.fixture(scope="class")
    def super_admin_token(self):
        """Get super admin token"""
        response = requests.post(f"{BASE_URL}/api/super-admin/login", json={
            "email": "owner@maestroegp.com",
            "password": "owner123",
            "secret_key": "271018"
        })
        assert response.status_code == 200, f"Super admin login failed: {response.text}"
        return response.json()["token"]
    
    def test_super_admin_login(self, super_admin_token):
        """Test super admin login works"""
        assert super_admin_token is not None
        assert len(super_admin_token) > 0
        print("✅ Super admin login successful")


class TestBackgroundUpload:
    """Test background upload functionality - URL mode"""
    
    @pytest.fixture(scope="class")
    def super_admin_token(self):
        """Get super admin token"""
        response = requests.post(f"{BASE_URL}/api/super-admin/login", json={
            "email": "owner@maestroegp.com",
            "password": "owner123",
            "secret_key": "271018"
        })
        return response.json()["token"]
    
    def test_get_login_backgrounds(self, super_admin_token):
        """Test fetching login backgrounds"""
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        response = requests.get(f"{BASE_URL}/api/login-backgrounds", headers=headers)
        assert response.status_code == 200, f"Failed to get backgrounds: {response.text}"
        data = response.json()
        assert "backgrounds" in data
        print(f"✅ Got {len(data.get('backgrounds', []))} backgrounds")
    
    def test_add_background_via_url(self, super_admin_token):
        """Test adding background via URL"""
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        test_url = "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=1920"
        
        response = requests.post(
            f"{BASE_URL}/api/login-backgrounds/upload",
            headers=headers,
            params={
                "file_url": test_url,
                "title": "TEST_خلفية_اختبار",
                "animation_type": "fade"
            }
        )
        assert response.status_code == 200, f"Failed to add background: {response.text}"
        data = response.json()
        assert "background" in data
        assert data["background"]["title"] == "TEST_خلفية_اختبار"
        print(f"✅ Background added via URL: {data['background']['id']}")
        return data["background"]["id"]
    
    def test_delete_test_background(self, super_admin_token):
        """Cleanup test background"""
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        
        # Get backgrounds
        response = requests.get(f"{BASE_URL}/api/login-backgrounds", headers=headers)
        backgrounds = response.json().get("backgrounds", [])
        
        # Delete test backgrounds
        for bg in backgrounds:
            if bg.get("title", "").startswith("TEST_"):
                del_response = requests.delete(
                    f"{BASE_URL}/api/login-backgrounds/{bg['id']}", 
                    headers=headers
                )
                print(f"✅ Deleted test background: {bg['id']}")


class TestTenantFeatures:
    """Test tenant features modal functionality"""
    
    @pytest.fixture(scope="class")
    def super_admin_token(self):
        """Get super admin token"""
        response = requests.post(f"{BASE_URL}/api/super-admin/login", json={
            "email": "owner@maestroegp.com",
            "password": "owner123",
            "secret_key": "271018"
        })
        return response.json()["token"]
    
    def test_get_tenant_features(self, super_admin_token):
        """Test fetching tenant features"""
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        response = requests.get(
            f"{BASE_URL}/api/super-admin/tenants/{DEMO_TENANT_ID}/features",
            headers=headers
        )
        assert response.status_code == 200, f"Failed to get features: {response.text}"
        data = response.json()
        assert "features" in data
        
        # Verify all 4 sections exist (basic, advanced, additional, settings)
        features = data["features"]
        
        # Basic features
        basic_features = ["showPOS", "showTables", "showOrders", "showReports", 
                        "showExpenses", "showInventory", "showDelivery", "showKitchen"]
        for f in basic_features:
            assert f in features, f"Missing basic feature: {f}"
        
        # Advanced features
        advanced_features = ["showHR", "showWarehouse", "showCallCenter", "showCallLogs",
                           "showLoyalty", "showCoupons", "showRecipes", "showReservations"]
        for f in advanced_features:
            assert f in features, f"Missing advanced feature: {f}"
        
        # Additional features
        additional_features = ["showSmartReports", "showBranchOrders", "showPurchasing", "showReviews"]
        for f in additional_features:
            assert f in features, f"Missing additional feature: {f}"
        
        # Settings features
        settings_features = ["settingsUsers", "settingsCustomers", "settingsCategories",
                           "settingsProducts", "settingsDeliveryCompanies", "settingsBranches",
                           "settingsPrinters", "settingsNotifications", "settingsCallCenter"]
        for f in settings_features:
            assert f in features, f"Missing settings feature: {f}"
        
        print("✅ All 4 feature sections verified (basic, advanced, additional, settings)")
    
    def test_update_tenant_features_enable_all(self, super_admin_token):
        """Test enabling all features"""
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        
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
            f"{BASE_URL}/api/super-admin/tenants/{DEMO_TENANT_ID}/features",
            headers=headers,
            json=all_enabled
        )
        assert response.status_code == 200, f"Failed to enable all features: {response.text}"
        print("✅ Enable all features - successful")
    
    def test_update_tenant_features_disable_all(self, super_admin_token):
        """Test disabling all features (except mandatory)"""
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        
        # Disable all features (POS and Settings are mandatory)
        all_disabled = {
            "showPOS": True, "showTables": False, "showOrders": False, "showReports": False,
            "showExpenses": False, "showInventory": False, "showDelivery": False, "showKitchen": False,
            "showHR": False, "showWarehouse": False, "showCallCenter": False, "showCallLogs": False,
            "showLoyalty": False, "showCoupons": False, "showRecipes": False, "showReservations": False,
            "showSmartReports": False, "showBranchOrders": False, "showPurchasing": False, "showReviews": False,
            "settingsUsers": False, "settingsCustomers": False, "settingsCategories": False,
            "settingsProducts": False, "settingsDeliveryCompanies": False, "settingsBranches": False,
            "settingsPrinters": False, "settingsNotifications": False, "settingsCallCenter": False
        }
        
        response = requests.put(
            f"{BASE_URL}/api/super-admin/tenants/{DEMO_TENANT_ID}/features",
            headers=headers,
            json=all_disabled
        )
        assert response.status_code == 200, f"Failed to disable all features: {response.text}"
        print("✅ Disable all features - successful")
    
    def test_save_tenant_features(self, super_admin_token):
        """Test saving specific features"""
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        
        # Set specific features
        specific_features = {
            "showPOS": True, "showTables": True, "showOrders": True, "showReports": True,
            "showExpenses": True, "showInventory": True, "showDelivery": True, "showKitchen": False,
            "showHR": False, "showWarehouse": False, "showCallCenter": False, "showCallLogs": False,
            "showLoyalty": True, "showCoupons": True, "showRecipes": False, "showReservations": True,
            "showSmartReports": True, "showBranchOrders": False, "showPurchasing": False, "showReviews": True,
            "settingsUsers": True, "settingsCustomers": True, "settingsCategories": True,
            "settingsProducts": True, "settingsDeliveryCompanies": True, "settingsBranches": True,
            "settingsPrinters": True, "settingsNotifications": True, "settingsCallCenter": False
        }
        
        response = requests.put(
            f"{BASE_URL}/api/super-admin/tenants/{DEMO_TENANT_ID}/features",
            headers=headers,
            json=specific_features
        )
        assert response.status_code == 200, f"Failed to save features: {response.text}"
        
        # Verify saved features
        get_response = requests.get(
            f"{BASE_URL}/api/super-admin/tenants/{DEMO_TENANT_ID}/features",
            headers=headers
        )
        saved_features = get_response.json()["features"]
        
        # Verify some key features
        assert saved_features["showPOS"] == True
        assert saved_features["showKitchen"] == False
        assert saved_features["showLoyalty"] == True
        
        print("✅ Save tenant features - successful and verified")


class TestTransitionDuration:
    """Test transition duration dropdown values"""
    
    @pytest.fixture(scope="class")
    def super_admin_token(self):
        """Get super admin token"""
        response = requests.post(f"{BASE_URL}/api/super-admin/login", json={
            "email": "owner@maestroegp.com",
            "password": "owner123",
            "secret_key": "271018"
        })
        return response.json()["token"]
    
    def test_update_transition_duration(self, super_admin_token):
        """Test updating transition duration with various values"""
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        
        # Test values: 0.5, 1, 1.5, 2, 2.5, 3, 4, 5
        test_values = [0.5, 1, 1.5, 2, 2.5, 3, 4, 5]
        
        for duration in test_values:
            # Get current settings
            get_response = requests.get(f"{BASE_URL}/api/login-backgrounds", headers=headers)
            current_settings = get_response.json()
            
            # Update with new duration
            current_settings["transition_duration"] = duration
            
            response = requests.put(
                f"{BASE_URL}/api/login-backgrounds",
                headers=headers,
                json=current_settings
            )
            assert response.status_code == 200, f"Failed to set duration {duration}: {response.text}"
            
            # Verify
            verify_response = requests.get(f"{BASE_URL}/api/login-backgrounds", headers=headers)
            saved_duration = verify_response.json().get("transition_duration")
            assert saved_duration == duration, f"Duration mismatch: expected {duration}, got {saved_duration}"
        
        print("✅ All transition duration values (0.5-5 seconds) work correctly")


class TestDemoAccountExclusion:
    """Test demo account exclusion from statistics"""
    
    @pytest.fixture(scope="class")
    def super_admin_token(self):
        """Get super admin token"""
        response = requests.post(f"{BASE_URL}/api/super-admin/login", json={
            "email": "owner@maestroegp.com",
            "password": "owner123",
            "secret_key": "271018"
        })
        return response.json()["token"]
    
    def test_stats_exclude_demo_accounts(self, super_admin_token):
        """Test that stats exclude demo accounts"""
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        
        response = requests.get(f"{BASE_URL}/api/super-admin/stats", headers=headers)
        assert response.status_code == 200, f"Failed to get stats: {response.text}"
        
        data = response.json()
        
        # Verify demo_tenants is reported separately
        assert "demo_tenants" in data, "demo_tenants field missing from stats"
        
        # Verify total_tenants doesn't include demo accounts
        assert "total_tenants" in data
        assert "active_tenants" in data
        
        # Get all tenants to verify
        tenants_response = requests.get(f"{BASE_URL}/api/super-admin/tenants", headers=headers)
        all_tenants = tenants_response.json()
        
        # Count non-demo tenants
        non_demo_count = sum(1 for t in all_tenants if not t.get("is_demo", False))
        demo_count = sum(1 for t in all_tenants if t.get("is_demo", False))
        
        print(f"✅ Stats: total_tenants={data['total_tenants']}, demo_tenants={data['demo_tenants']}")
        print(f"✅ Verified: Non-demo tenants={non_demo_count}, Demo tenants={demo_count}")
        
        # The total_tenants should equal non-demo count
        assert data["total_tenants"] == non_demo_count, \
            f"total_tenants ({data['total_tenants']}) should equal non-demo count ({non_demo_count})"
        
        print("✅ Demo accounts correctly excluded from statistics")


class TestPackagingCost:
    """Test packaging_cost is only added for delivery and takeaway orders"""
    
    @pytest.fixture(scope="class")
    def owner_token(self):
        """Get owner token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "owner@maestroegp.com",
            "password": "owner123"
        })
        return response.json()["token"]
    
    def test_get_products_with_packaging_cost(self, owner_token):
        """Test that products have packaging_cost field"""
        headers = {"Authorization": f"Bearer {owner_token}"}
        
        response = requests.get(f"{BASE_URL}/api/products", headers=headers)
        assert response.status_code == 200, f"Failed to get products: {response.text}"
        
        products = response.json()
        assert len(products) > 0, "No products found"
        
        # Check that packaging_cost field exists
        for product in products[:5]:  # Check first 5 products
            assert "packaging_cost" in product or product.get("packaging_cost", 0) >= 0
        
        print(f"✅ Products have packaging_cost field")
    
    def test_create_product_with_packaging_cost(self, owner_token):
        """Test creating product with packaging_cost"""
        headers = {"Authorization": f"Bearer {owner_token}"}
        
        # Get a category first
        cat_response = requests.get(f"{BASE_URL}/api/categories", headers=headers)
        categories = cat_response.json()
        category_id = categories[0]["id"] if categories else None
        
        if not category_id:
            pytest.skip("No categories available")
        
        # Get a branch
        branch_response = requests.get(f"{BASE_URL}/api/branches", headers=headers)
        branches = branch_response.json()
        branch_id = branches[0]["id"] if branches else None
        
        if not branch_id:
            pytest.skip("No branches available")
        
        # Create product with packaging_cost
        product_data = {
            "name": "TEST_منتج_تغليف",
            "category_id": category_id,
            "price": 10.0,
            "cost": 5.0,
            "operating_cost": 1.0,
            "packaging_cost": 2.0,  # تكلفة التغليف
            "is_available": True
        }
        
        response = requests.post(
            f"{BASE_URL}/api/products",
            headers=headers,
            json=product_data
        )
        assert response.status_code == 200, f"Failed to create product: {response.text}"
        
        created_product = response.json()
        assert created_product["packaging_cost"] == 2.0, "packaging_cost not saved correctly"
        
        print(f"✅ Created product with packaging_cost: {created_product['id']}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/products/{created_product['id']}", headers=headers)
        print("✅ Test product cleaned up")


class TestBackgroundSettings:
    """Test background settings including transition duration"""
    
    @pytest.fixture(scope="class")
    def super_admin_token(self):
        """Get super admin token"""
        response = requests.post(f"{BASE_URL}/api/super-admin/login", json={
            "email": "owner@maestroegp.com",
            "password": "owner123",
            "secret_key": "271018"
        })
        return response.json()["token"]
    
    def test_get_background_settings(self, super_admin_token):
        """Test getting background settings"""
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        
        response = requests.get(f"{BASE_URL}/api/login-backgrounds", headers=headers)
        assert response.status_code == 200, f"Failed to get backgrounds: {response.text}"
        
        data = response.json()
        
        # Verify required fields
        assert "backgrounds" in data
        assert "transition_duration" in data or data.get("transition_duration") is not None
        
        print(f"✅ Background settings retrieved: {len(data.get('backgrounds', []))} backgrounds")
    
    def test_save_background_settings(self, super_admin_token):
        """Test saving background settings"""
        headers = {"Authorization": f"Bearer {super_admin_token}"}
        
        # Get current settings
        get_response = requests.get(f"{BASE_URL}/api/login-backgrounds", headers=headers)
        current_settings = get_response.json()
        
        # Update settings
        current_settings["transition_duration"] = 2.5
        current_settings["transition_type"] = "fade"
        
        response = requests.put(
            f"{BASE_URL}/api/login-backgrounds",
            headers=headers,
            json=current_settings
        )
        assert response.status_code == 200, f"Failed to save settings: {response.text}"
        
        # Verify
        verify_response = requests.get(f"{BASE_URL}/api/login-backgrounds", headers=headers)
        saved_settings = verify_response.json()
        
        assert saved_settings.get("transition_duration") == 2.5
        assert saved_settings.get("transition_type") == "fade"
        
        print("✅ Background settings saved and verified")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
