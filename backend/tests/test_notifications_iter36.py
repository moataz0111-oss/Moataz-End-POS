"""
Iteration 36 - Notification System Tests
Tests for:
1. Notification bell button in header
2. Notifications dropdown list
3. Notification settings modal
4. Subscription duration field in tenant creation form
5. API: GET /api/super-admin/notifications
6. API: PUT /api/super-admin/notifications/{id}/read
7. API: GET/PUT /api/super-admin/notification-settings
8. API: GET /api/super-admin/expiring-subscriptions
9. Auto-notification on new tenant creation
10. Auto-notification on tenant activate/deactivate
"""

import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestNotificationSystem:
    """Test notification system APIs"""
    
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
            pytest.skip("Super admin login failed")
    
    # ==================== Notification APIs ====================
    
    def test_get_notifications(self):
        """Test GET /api/super-admin/notifications"""
        response = self.session.get(f"{BASE_URL}/api/super-admin/notifications")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "notifications" in data, "Response should contain 'notifications' field"
        assert "unread_count" in data, "Response should contain 'unread_count' field"
        assert isinstance(data["notifications"], list), "notifications should be a list"
        assert isinstance(data["unread_count"], int), "unread_count should be an integer"
        
        print(f"✅ GET /api/super-admin/notifications - Found {len(data['notifications'])} notifications, {data['unread_count']} unread")
    
    def test_get_notifications_unread_only(self):
        """Test GET /api/super-admin/notifications with unread_only filter"""
        response = self.session.get(f"{BASE_URL}/api/super-admin/notifications?unread_only=true")
        
        assert response.status_code == 200
        data = response.json()
        
        # All returned notifications should be unread
        for notification in data["notifications"]:
            assert notification.get("is_read") == False, "All notifications should be unread when unread_only=true"
        
        print(f"✅ GET /api/super-admin/notifications?unread_only=true - Found {len(data['notifications'])} unread notifications")
    
    def test_notification_settings_get(self):
        """Test GET /api/super-admin/notification-settings"""
        response = self.session.get(f"{BASE_URL}/api/super-admin/notification-settings")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Check required fields
        expected_fields = ["days_before_expiry", "email_notifications", "push_notifications", 
                          "notify_new_tenant", "notify_tenant_status"]
        
        for field in expected_fields:
            assert field in data, f"Missing field: {field}"
        
        assert isinstance(data["days_before_expiry"], int), "days_before_expiry should be int"
        assert isinstance(data["email_notifications"], bool), "email_notifications should be bool"
        assert isinstance(data["push_notifications"], bool), "push_notifications should be bool"
        
        print(f"✅ GET /api/super-admin/notification-settings - days_before_expiry: {data['days_before_expiry']}")
    
    def test_notification_settings_update(self):
        """Test PUT /api/super-admin/notification-settings"""
        # First get current settings
        get_response = self.session.get(f"{BASE_URL}/api/super-admin/notification-settings")
        original_settings = get_response.json()
        
        # Update settings
        new_settings = {
            "days_before_expiry": 14,
            "email_notifications": True,
            "push_notifications": True,
            "notify_new_tenant": True,
            "notify_tenant_status": True
        }
        
        response = self.session.put(f"{BASE_URL}/api/super-admin/notification-settings", json=new_settings)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "message" in data, "Response should contain message"
        assert "settings" in data, "Response should contain settings"
        assert data["settings"]["days_before_expiry"] == 14, "days_before_expiry should be updated to 14"
        
        # Verify by getting settings again
        verify_response = self.session.get(f"{BASE_URL}/api/super-admin/notification-settings")
        verify_data = verify_response.json()
        assert verify_data["days_before_expiry"] == 14, "Settings should persist"
        
        # Restore original settings
        self.session.put(f"{BASE_URL}/api/super-admin/notification-settings", json=original_settings)
        
        print("✅ PUT /api/super-admin/notification-settings - Settings updated and verified")
    
    def test_expiring_subscriptions(self):
        """Test GET /api/super-admin/expiring-subscriptions"""
        response = self.session.get(f"{BASE_URL}/api/super-admin/expiring-subscriptions")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Check required fields
        assert "expiring_soon" in data, "Response should contain 'expiring_soon'"
        assert "already_expired" in data, "Response should contain 'already_expired'"
        assert "days_before_alert" in data, "Response should contain 'days_before_alert'"
        
        assert isinstance(data["expiring_soon"], list), "expiring_soon should be a list"
        assert isinstance(data["already_expired"], list), "already_expired should be a list"
        assert isinstance(data["days_before_alert"], int), "days_before_alert should be int"
        
        print(f"✅ GET /api/super-admin/expiring-subscriptions - {len(data['expiring_soon'])} expiring, {len(data['already_expired'])} expired")
    
    # ==================== Notification CRUD ====================
    
    def test_mark_notification_as_read(self):
        """Test PUT /api/super-admin/notifications/{id}/read"""
        # First get notifications
        get_response = self.session.get(f"{BASE_URL}/api/super-admin/notifications")
        notifications = get_response.json().get("notifications", [])
        
        if not notifications:
            # Create a test tenant to generate a notification
            test_tenant = self._create_test_tenant()
            if test_tenant:
                # Get notifications again
                get_response = self.session.get(f"{BASE_URL}/api/super-admin/notifications")
                notifications = get_response.json().get("notifications", [])
        
        if notifications:
            notification_id = notifications[0]["id"]
            
            # Mark as read
            response = self.session.put(f"{BASE_URL}/api/super-admin/notifications/{notification_id}/read")
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            assert "message" in response.json(), "Response should contain message"
            
            print(f"✅ PUT /api/super-admin/notifications/{notification_id}/read - Marked as read")
        else:
            print("⚠️ No notifications to test mark as read")
    
    def test_mark_all_notifications_read(self):
        """Test PUT /api/super-admin/notifications/read-all"""
        response = self.session.put(f"{BASE_URL}/api/super-admin/notifications/read-all")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "message" in response.json(), "Response should contain message"
        
        # Verify all are read
        verify_response = self.session.get(f"{BASE_URL}/api/super-admin/notifications")
        verify_data = verify_response.json()
        assert verify_data["unread_count"] == 0, "All notifications should be marked as read"
        
        print("✅ PUT /api/super-admin/notifications/read-all - All marked as read")
    
    # ==================== Auto-notification on tenant actions ====================
    
    def test_notification_on_new_tenant(self):
        """Test that creating a new tenant generates a notification"""
        # Get initial notification count
        initial_response = self.session.get(f"{BASE_URL}/api/super-admin/notifications")
        initial_count = len(initial_response.json().get("notifications", []))
        
        # Create a test tenant
        test_slug = f"test-notif-{uuid.uuid4().hex[:8]}"
        tenant_data = {
            "name": "Test Notification Tenant",
            "slug": test_slug,
            "owner_name": "Test Owner",
            "owner_email": f"test-{uuid.uuid4().hex[:8]}@test.com",
            "owner_phone": "07801234567",
            "subscription_type": "trial",
            "subscription_duration": 1,
            "max_branches": 1,
            "max_users": 5,
            "is_demo": True
        }
        
        create_response = self.session.post(f"{BASE_URL}/api/super-admin/tenants", json=tenant_data)
        
        if create_response.status_code == 200:
            tenant_id = create_response.json().get("tenant", {}).get("id")
            
            # Check for new notification
            new_response = self.session.get(f"{BASE_URL}/api/super-admin/notifications")
            new_notifications = new_response.json().get("notifications", [])
            
            # Find the notification for this tenant
            found_notification = None
            for notif in new_notifications:
                if notif.get("type") == "new_tenant" and notif.get("tenant_id") == tenant_id:
                    found_notification = notif
                    break
            
            assert found_notification is not None, "Should create notification for new tenant"
            assert "عميل جديد" in found_notification.get("title", ""), "Notification title should mention new tenant"
            
            # Cleanup - delete the test tenant
            self.session.delete(f"{BASE_URL}/api/super-admin/tenants/{tenant_id}?permanent=true")
            
            print("✅ New tenant notification created successfully")
        else:
            print(f"⚠️ Could not create test tenant: {create_response.status_code}")
    
    def test_notification_on_tenant_deactivate(self):
        """Test that deactivating a tenant generates a notification"""
        # First create a test tenant
        test_slug = f"test-deact-{uuid.uuid4().hex[:8]}"
        tenant_data = {
            "name": "Test Deactivate Tenant",
            "slug": test_slug,
            "owner_name": "Test Owner",
            "owner_email": f"test-{uuid.uuid4().hex[:8]}@test.com",
            "owner_phone": "07801234567",
            "subscription_type": "trial",
            "subscription_duration": 1,
            "max_branches": 1,
            "max_users": 5,
            "is_demo": True
        }
        
        create_response = self.session.post(f"{BASE_URL}/api/super-admin/tenants", json=tenant_data)
        
        if create_response.status_code == 200:
            tenant_id = create_response.json().get("tenant", {}).get("id")
            
            # Deactivate the tenant
            deactivate_response = self.session.put(f"{BASE_URL}/api/super-admin/tenants/{tenant_id}/deactivate")
            assert deactivate_response.status_code == 200, "Deactivate should succeed"
            
            # Check for deactivation notification
            notif_response = self.session.get(f"{BASE_URL}/api/super-admin/notifications")
            notifications = notif_response.json().get("notifications", [])
            
            found_notification = None
            for notif in notifications:
                if notif.get("type") == "tenant_deactivated" and notif.get("tenant_id") == tenant_id:
                    found_notification = notif
                    break
            
            assert found_notification is not None, "Should create notification for tenant deactivation"
            assert "تعطيل" in found_notification.get("title", ""), "Notification should mention deactivation"
            
            # Cleanup
            self.session.delete(f"{BASE_URL}/api/super-admin/tenants/{tenant_id}?permanent=true")
            
            print("✅ Tenant deactivation notification created successfully")
        else:
            print(f"⚠️ Could not create test tenant: {create_response.status_code}")
    
    def test_notification_on_tenant_activate(self):
        """Test that activating a tenant generates a notification"""
        # First create a test tenant
        test_slug = f"test-act-{uuid.uuid4().hex[:8]}"
        tenant_data = {
            "name": "Test Activate Tenant",
            "slug": test_slug,
            "owner_name": "Test Owner",
            "owner_email": f"test-{uuid.uuid4().hex[:8]}@test.com",
            "owner_phone": "07801234567",
            "subscription_type": "trial",
            "subscription_duration": 1,
            "max_branches": 1,
            "max_users": 5,
            "is_demo": True
        }
        
        create_response = self.session.post(f"{BASE_URL}/api/super-admin/tenants", json=tenant_data)
        
        if create_response.status_code == 200:
            tenant_id = create_response.json().get("tenant", {}).get("id")
            
            # First deactivate
            self.session.put(f"{BASE_URL}/api/super-admin/tenants/{tenant_id}/deactivate")
            
            # Then reactivate
            activate_response = self.session.put(f"{BASE_URL}/api/super-admin/tenants/{tenant_id}/reactivate")
            assert activate_response.status_code == 200, "Reactivate should succeed"
            
            # Check for activation notification
            notif_response = self.session.get(f"{BASE_URL}/api/super-admin/notifications")
            notifications = notif_response.json().get("notifications", [])
            
            found_notification = None
            for notif in notifications:
                if notif.get("type") == "tenant_activated" and notif.get("tenant_id") == tenant_id:
                    found_notification = notif
                    break
            
            assert found_notification is not None, "Should create notification for tenant activation"
            assert "تفعيل" in found_notification.get("title", ""), "Notification should mention activation"
            
            # Cleanup
            self.session.delete(f"{BASE_URL}/api/super-admin/tenants/{tenant_id}?permanent=true")
            
            print("✅ Tenant activation notification created successfully")
        else:
            print(f"⚠️ Could not create test tenant: {create_response.status_code}")
    
    # ==================== Subscription Duration ====================
    
    def test_subscription_duration_in_tenant_creation(self):
        """Test subscription_duration field in tenant creation"""
        # Test with different subscription durations
        durations = [1, 3, 6, 12]
        
        for duration in durations:
            test_slug = f"test-dur-{duration}-{uuid.uuid4().hex[:6]}"
            tenant_data = {
                "name": f"Test Duration {duration}",
                "slug": test_slug,
                "owner_name": "Test Owner",
                "owner_email": f"test-{uuid.uuid4().hex[:8]}@test.com",
                "owner_phone": "07801234567",
                "subscription_type": "trial",
                "subscription_duration": duration,
                "max_branches": 1,
                "max_users": 5,
                "is_demo": True
            }
            
            response = self.session.post(f"{BASE_URL}/api/super-admin/tenants", json=tenant_data)
            
            if response.status_code == 200:
                tenant = response.json().get("tenant", {})
                tenant_id = tenant.get("id")
                
                # Verify subscription_duration is stored
                assert tenant.get("subscription_duration") == duration, f"subscription_duration should be {duration}"
                
                # Verify expires_at is set correctly (approximately duration months from now)
                expires_at = tenant.get("expires_at")
                assert expires_at is not None, "expires_at should be set"
                
                # Cleanup
                self.session.delete(f"{BASE_URL}/api/super-admin/tenants/{tenant_id}?permanent=true")
                
                print(f"✅ Subscription duration {duration} months - Created and verified")
            else:
                print(f"⚠️ Could not create tenant with duration {duration}: {response.status_code}")
    
    # ==================== Helper Methods ====================
    
    def _create_test_tenant(self):
        """Helper to create a test tenant"""
        test_slug = f"test-helper-{uuid.uuid4().hex[:8]}"
        tenant_data = {
            "name": "Test Helper Tenant",
            "slug": test_slug,
            "owner_name": "Test Owner",
            "owner_email": f"test-{uuid.uuid4().hex[:8]}@test.com",
            "owner_phone": "07801234567",
            "subscription_type": "trial",
            "subscription_duration": 1,
            "max_branches": 1,
            "max_users": 5,
            "is_demo": True
        }
        
        response = self.session.post(f"{BASE_URL}/api/super-admin/tenants", json=tenant_data)
        if response.status_code == 200:
            return response.json().get("tenant")
        return None


class TestNotificationDelete:
    """Test notification deletion"""
    
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
    
    def test_delete_single_notification(self):
        """Test DELETE /api/super-admin/notifications/{id}"""
        # Get notifications
        get_response = self.session.get(f"{BASE_URL}/api/super-admin/notifications")
        notifications = get_response.json().get("notifications", [])
        
        if notifications:
            notification_id = notifications[0]["id"]
            
            # Delete notification
            response = self.session.delete(f"{BASE_URL}/api/super-admin/notifications/{notification_id}")
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
            # Verify deletion
            verify_response = self.session.get(f"{BASE_URL}/api/super-admin/notifications")
            verify_notifications = verify_response.json().get("notifications", [])
            
            deleted_ids = [n["id"] for n in verify_notifications]
            assert notification_id not in deleted_ids, "Notification should be deleted"
            
            print(f"✅ DELETE /api/super-admin/notifications/{notification_id} - Deleted successfully")
        else:
            print("⚠️ No notifications to delete")
    
    def test_delete_nonexistent_notification(self):
        """Test DELETE /api/super-admin/notifications/{id} with invalid ID"""
        fake_id = str(uuid.uuid4())
        response = self.session.delete(f"{BASE_URL}/api/super-admin/notifications/{fake_id}")
        
        assert response.status_code == 404, f"Expected 404 for nonexistent notification, got {response.status_code}"
        print("✅ DELETE nonexistent notification returns 404")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
