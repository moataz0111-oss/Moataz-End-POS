"""
Test Iteration 8: User Data Isolation & Tenant Edit Features
- P0: User data isolation between main system and tenants
- P1: Tenant edit API and welcome email functionality
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
SUPER_ADMIN = {"email": "owner@maestroegp.com", "password": "owner123", "secret_key": "271018"}
MAIN_ADMIN = {"email": "admin@maestroegp.com", "password": "admin123"}
TENANT_ADMIN = {"email": "ahmed@albait.com", "password": "password123"}


class TestUserDataIsolation:
    """P0: Test user data isolation between main system and tenants"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def login(self, email, password):
        """Helper to login and get token"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": email,
            "password": password
        })
        if response.status_code == 200:
            token = response.json().get("token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
            return response.json()
        return None
    
    def test_main_admin_login(self):
        """Test main system admin can login"""
        result = self.login(MAIN_ADMIN["email"], MAIN_ADMIN["password"])
        assert result is not None, "Main admin login failed"
        assert result["user"]["email"] == MAIN_ADMIN["email"]
        print(f"✓ Main admin login successful: {result['user']['full_name']}")
        print(f"  - Role: {result['user']['role']}")
        print(f"  - Tenant ID: {result['user'].get('tenant_id', 'None (main system)')}")
    
    def test_tenant_admin_login(self):
        """Test tenant admin can login"""
        result = self.login(TENANT_ADMIN["email"], TENANT_ADMIN["password"])
        assert result is not None, "Tenant admin login failed"
        assert result["user"]["email"] == TENANT_ADMIN["email"]
        print(f"✓ Tenant admin login successful: {result['user']['full_name']}")
        print(f"  - Role: {result['user']['role']}")
        print(f"  - Tenant ID: {result['user'].get('tenant_id', 'None')}")
    
    def test_main_system_sees_only_main_users(self):
        """P0: Main system admin should only see users without tenant_id"""
        result = self.login(MAIN_ADMIN["email"], MAIN_ADMIN["password"])
        assert result is not None, "Main admin login failed"
        
        response = self.session.get(f"{BASE_URL}/api/users")
        assert response.status_code == 200, f"Failed to get users: {response.text}"
        
        users = response.json()
        print(f"\n✓ Main system sees {len(users)} users:")
        
        # Check that all users either have no tenant_id or empty tenant_id
        tenant_users_leaked = []
        for user in users:
            tenant_id = user.get("tenant_id")
            has_tenant = tenant_id and tenant_id != "" and tenant_id is not None
            if has_tenant:
                tenant_users_leaked.append(user)
            print(f"  - {user['full_name']} ({user['email']}) - tenant_id: {tenant_id or 'None'}")
        
        # CRITICAL: No tenant users should be visible to main system
        assert len(tenant_users_leaked) == 0, f"DATA LEAK! Main system sees {len(tenant_users_leaked)} tenant users: {[u['email'] for u in tenant_users_leaked]}"
        print(f"\n✓ P0 PASSED: No tenant user data leaked to main system")
    
    def test_tenant_sees_only_own_users(self):
        """P0: Tenant admin should only see their own tenant's users"""
        result = self.login(TENANT_ADMIN["email"], TENANT_ADMIN["password"])
        assert result is not None, "Tenant admin login failed"
        
        tenant_id = result["user"].get("tenant_id")
        print(f"\nTenant admin's tenant_id: {tenant_id}")
        
        response = self.session.get(f"{BASE_URL}/api/users")
        assert response.status_code == 200, f"Failed to get users: {response.text}"
        
        users = response.json()
        print(f"✓ Tenant sees {len(users)} users:")
        
        # Check that all users belong to the same tenant
        wrong_tenant_users = []
        for user in users:
            user_tenant = user.get("tenant_id")
            print(f"  - {user['full_name']} ({user['email']}) - tenant_id: {user_tenant}")
            if user_tenant != tenant_id:
                wrong_tenant_users.append(user)
        
        # CRITICAL: Tenant should only see their own users
        assert len(wrong_tenant_users) == 0, f"DATA LEAK! Tenant sees {len(wrong_tenant_users)} users from other tenants: {[u['email'] for u in wrong_tenant_users]}"
        print(f"\n✓ P0 PASSED: Tenant only sees their own users")


class TestSuperAdminTenantEdit:
    """P1: Test Super Admin tenant edit functionality"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def super_admin_login(self):
        """Login as super admin (uses query params)"""
        response = self.session.post(
            f"{BASE_URL}/api/super-admin/login",
            params={
                "email": SUPER_ADMIN["email"],
                "password": SUPER_ADMIN["password"],
                "secret_key": SUPER_ADMIN["secret_key"]
            }
        )
        if response.status_code == 200:
            token = response.json().get("token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
            return response.json()
        return None
    
    def test_super_admin_login(self):
        """Test super admin can login with secret key"""
        result = self.super_admin_login()
        assert result is not None, "Super admin login failed"
        assert result["user"]["role"] == "super_admin"
        print(f"✓ Super admin login successful: {result['user']['full_name']}")
    
    def test_get_tenants_list(self):
        """Test getting list of tenants"""
        result = self.super_admin_login()
        assert result is not None, "Super admin login failed"
        
        response = self.session.get(f"{BASE_URL}/api/super-admin/tenants")
        assert response.status_code == 200, f"Failed to get tenants: {response.text}"
        
        tenants = response.json()
        print(f"\n✓ Found {len(tenants)} tenants:")
        for tenant in tenants:
            print(f"  - {tenant['name']} (ID: {tenant['id']}, Active: {tenant.get('is_active', True)})")
        
        return tenants
    
    def test_update_tenant_api(self):
        """P1: Test PUT /api/super-admin/tenants/{tenant_id} endpoint"""
        result = self.super_admin_login()
        assert result is not None, "Super admin login failed"
        
        # Get tenants list first
        response = self.session.get(f"{BASE_URL}/api/super-admin/tenants")
        assert response.status_code == 200
        tenants = response.json()
        
        # Find a non-main-system tenant to test
        test_tenant = None
        for tenant in tenants:
            if not tenant.get("is_main_system"):
                test_tenant = tenant
                break
        
        if not test_tenant:
            pytest.skip("No non-main-system tenant found for testing")
        
        print(f"\n✓ Testing update on tenant: {test_tenant['name']} (ID: {test_tenant['id']})")
        
        # Store original values
        original_name = test_tenant.get("name")
        original_phone = test_tenant.get("owner_phone")
        
        # Test update with new values
        test_update = {
            "name": f"TEST_{original_name}",
            "owner_phone": "+964 999 TEST"
        }
        
        response = self.session.put(
            f"{BASE_URL}/api/super-admin/tenants/{test_tenant['id']}",
            json=test_update
        )
        assert response.status_code == 200, f"Failed to update tenant: {response.text}"
        
        updated_tenant = response.json()
        print(f"  - Updated name: {updated_tenant.get('name')}")
        print(f"  - Updated phone: {updated_tenant.get('owner_phone')}")
        
        # Verify update was applied
        assert updated_tenant.get("name") == test_update["name"], "Name update not applied"
        assert updated_tenant.get("owner_phone") == test_update["owner_phone"], "Phone update not applied"
        
        # Revert changes
        revert_update = {
            "name": original_name,
            "owner_phone": original_phone
        }
        response = self.session.put(
            f"{BASE_URL}/api/super-admin/tenants/{test_tenant['id']}",
            json=revert_update
        )
        assert response.status_code == 200, "Failed to revert tenant changes"
        
        print(f"\n✓ P1 PASSED: Tenant update API working correctly")
    
    def test_update_tenant_subscription(self):
        """P1: Test updating tenant subscription type"""
        result = self.super_admin_login()
        assert result is not None, "Super admin login failed"
        
        # Get tenants list
        response = self.session.get(f"{BASE_URL}/api/super-admin/tenants")
        tenants = response.json()
        
        # Find a non-main-system tenant
        test_tenant = None
        for tenant in tenants:
            if not tenant.get("is_main_system"):
                test_tenant = tenant
                break
        
        if not test_tenant:
            pytest.skip("No non-main-system tenant found")
        
        original_subscription = test_tenant.get("subscription_type")
        print(f"\n✓ Testing subscription update on: {test_tenant['name']}")
        print(f"  - Original subscription: {original_subscription}")
        
        # Test subscription update
        new_subscription = "premium" if original_subscription != "premium" else "basic"
        response = self.session.put(
            f"{BASE_URL}/api/super-admin/tenants/{test_tenant['id']}",
            json={"subscription_type": new_subscription}
        )
        assert response.status_code == 200, f"Failed to update subscription: {response.text}"
        
        updated = response.json()
        assert updated.get("subscription_type") == new_subscription
        print(f"  - Updated subscription: {updated.get('subscription_type')}")
        
        # Revert
        self.session.put(
            f"{BASE_URL}/api/super-admin/tenants/{test_tenant['id']}",
            json={"subscription_type": original_subscription}
        )
        
        print(f"\n✓ P1 PASSED: Subscription update working")
    
    def test_update_tenant_with_welcome_email_flag(self):
        """P2: Test that welcome email flag is accepted (email sending is async)"""
        result = self.super_admin_login()
        assert result is not None, "Super admin login failed"
        
        # Get tenants list
        response = self.session.get(f"{BASE_URL}/api/super-admin/tenants")
        tenants = response.json()
        
        # Find a non-main-system tenant
        test_tenant = None
        for tenant in tenants:
            if not tenant.get("is_main_system"):
                test_tenant = tenant
                break
        
        if not test_tenant:
            pytest.skip("No non-main-system tenant found")
        
        print(f"\n✓ Testing welcome email flag on: {test_tenant['name']}")
        
        # Test update with welcome email flag (should not fail)
        response = self.session.put(
            f"{BASE_URL}/api/super-admin/tenants/{test_tenant['id']}",
            json={
                "send_welcome_email": True,
                "temp_password": "test123temp"
            }
        )
        
        # API should accept the request (email is sent in background)
        assert response.status_code == 200, f"API rejected welcome email flag: {response.text}"
        print(f"  - API accepted welcome email request")
        print(f"\n✓ P2 PASSED: Welcome email flag accepted by API")


class TestUserCreationWithTenantId:
    """Test that new users inherit tenant_id from creator"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def login(self, email, password):
        """Helper to login"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": email,
            "password": password
        })
        if response.status_code == 200:
            token = response.json().get("token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
            return response.json()
        return None
    
    def test_tenant_creates_user_with_tenant_id(self):
        """Test that users created by tenant admin inherit tenant_id"""
        result = self.login(TENANT_ADMIN["email"], TENANT_ADMIN["password"])
        assert result is not None, "Tenant admin login failed"
        
        creator_tenant_id = result["user"].get("tenant_id")
        print(f"\n✓ Creator tenant_id: {creator_tenant_id}")
        
        # Create a test user
        test_user = {
            "username": f"test_user_{uuid.uuid4().hex[:8]}",
            "email": f"test_{uuid.uuid4().hex[:8]}@test.com",
            "password": "testpass123",
            "full_name": "TEST User Isolation",
            "role": "cashier"
        }
        
        response = self.session.post(f"{BASE_URL}/api/users", json=test_user)
        assert response.status_code == 200, f"Failed to create user: {response.text}"
        
        created_user = response.json()
        print(f"  - Created user: {created_user['full_name']}")
        print(f"  - User tenant_id: {created_user.get('tenant_id')}")
        
        # Verify tenant_id was inherited
        assert created_user.get("tenant_id") == creator_tenant_id, \
            f"User tenant_id mismatch! Expected {creator_tenant_id}, got {created_user.get('tenant_id')}"
        
        # Cleanup - delete test user
        self.session.delete(f"{BASE_URL}/api/users/{created_user['id']}")
        
        print(f"\n✓ PASSED: New user correctly inherited tenant_id from creator")
    
    def test_main_admin_creates_user_without_tenant_id(self):
        """Test that users created by main admin have no tenant_id"""
        result = self.login(MAIN_ADMIN["email"], MAIN_ADMIN["password"])
        assert result is not None, "Main admin login failed"
        
        creator_tenant_id = result["user"].get("tenant_id")
        print(f"\n✓ Main admin tenant_id: {creator_tenant_id or 'None'}")
        
        # Create a test user
        test_user = {
            "username": f"main_test_{uuid.uuid4().hex[:8]}",
            "email": f"main_test_{uuid.uuid4().hex[:8]}@test.com",
            "password": "testpass123",
            "full_name": "TEST Main System User",
            "role": "cashier"
        }
        
        response = self.session.post(f"{BASE_URL}/api/users", json=test_user)
        assert response.status_code == 200, f"Failed to create user: {response.text}"
        
        created_user = response.json()
        print(f"  - Created user: {created_user['full_name']}")
        print(f"  - User tenant_id: {created_user.get('tenant_id') or 'None'}")
        
        # Verify tenant_id is None or empty (main system user)
        user_tenant = created_user.get("tenant_id")
        assert user_tenant is None or user_tenant == "", \
            f"Main system user should not have tenant_id! Got: {user_tenant}"
        
        # Cleanup
        self.session.delete(f"{BASE_URL}/api/users/{created_user['id']}")
        
        print(f"\n✓ PASSED: Main system user created without tenant_id")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
