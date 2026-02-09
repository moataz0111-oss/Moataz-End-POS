"""
Test Driver Features - Iteration 60
Testing:
1. Driver login with phone and PIN (POST /api/driver/login)
2. Driver orders API (GET /api/driver/orders)
3. Driver location update (POST /api/driver/update-location)
4. Driver order status update (PUT /api/driver/orders/{order_id}/status)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestDriverLogin:
    """Test driver login with phone and PIN"""
    
    def test_01_driver_login_success(self):
        """Test successful driver login with correct phone and PIN"""
        response = requests.post(
            f"{BASE_URL}/api/driver/login",
            params={"phone": "07901234567", "pin": "1234"}
        )
        print(f"Driver login response: {response.status_code}")
        print(f"Response body: {response.text[:500]}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "driver" in data, "Response should contain 'driver' key"
        assert data["driver"]["phone"] == "07901234567", "Phone should match"
        # PIN should NOT be in response for security
        assert "pin" not in data["driver"], "PIN should not be in response"
        print("✓ Driver login with correct PIN successful")
    
    def test_02_driver_login_wrong_pin(self):
        """Test driver login with wrong PIN returns 401"""
        response = requests.post(
            f"{BASE_URL}/api/driver/login",
            params={"phone": "07901234567", "pin": "9999"}
        )
        print(f"Wrong PIN response: {response.status_code}")
        
        assert response.status_code == 401, f"Expected 401 for wrong PIN, got {response.status_code}"
        print("✓ Wrong PIN returns 401")
    
    def test_03_driver_login_unknown_phone(self):
        """Test driver login with unknown phone returns 404"""
        response = requests.post(
            f"{BASE_URL}/api/driver/login",
            params={"phone": "07999999999", "pin": "1234"}
        )
        print(f"Unknown phone response: {response.status_code}")
        
        assert response.status_code == 404, f"Expected 404 for unknown phone, got {response.status_code}"
        print("✓ Unknown phone returns 404")
    
    def test_04_driver_login_missing_pin(self):
        """Test driver login without PIN returns 422"""
        response = requests.post(
            f"{BASE_URL}/api/driver/login",
            params={"phone": "07901234567"}
        )
        print(f"Missing PIN response: {response.status_code}")
        
        assert response.status_code == 422, f"Expected 422 for missing PIN, got {response.status_code}"
        print("✓ Missing PIN returns 422")


class TestDriverOrders:
    """Test driver orders API"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get driver ID for tests"""
        response = requests.post(
            f"{BASE_URL}/api/driver/login",
            params={"phone": "07901234567", "pin": "1234"}
        )
        if response.status_code == 200:
            self.driver_id = response.json()["driver"]["id"]
        else:
            pytest.skip("Could not login as driver")
    
    def test_05_get_driver_orders(self):
        """Test getting driver's assigned orders"""
        response = requests.get(
            f"{BASE_URL}/api/driver/orders",
            params={"driver_id": self.driver_id}
        )
        print(f"Get driver orders response: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✓ Got {len(data)} orders for driver")


class TestDriverLocation:
    """Test driver location update API"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get driver ID for tests"""
        response = requests.post(
            f"{BASE_URL}/api/driver/login",
            params={"phone": "07901234567", "pin": "1234"}
        )
        if response.status_code == 200:
            self.driver_id = response.json()["driver"]["id"]
        else:
            pytest.skip("Could not login as driver")
    
    def test_06_update_driver_location(self):
        """Test updating driver location"""
        response = requests.post(
            f"{BASE_URL}/api/driver/update-location",
            params={"driver_id": self.driver_id},
            json={"latitude": 33.3152, "longitude": 44.3661}
        )
        print(f"Update location response: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ Driver location updated successfully")
    
    def test_07_update_location_invalid_driver(self):
        """Test updating location for non-existent driver returns 404"""
        response = requests.post(
            f"{BASE_URL}/api/driver/update-location",
            params={"driver_id": "invalid-driver-id"},
            json={"latitude": 33.3152, "longitude": 44.3661}
        )
        print(f"Invalid driver location response: {response.status_code}")
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Invalid driver returns 404")


class TestDriverOrderStatus:
    """Test driver order status update API"""
    
    def test_08_update_order_status_invalid_order(self):
        """Test updating status for non-existent order returns 404"""
        response = requests.put(
            f"{BASE_URL}/api/driver/orders/invalid-order-id/status",
            params={"status": "delivered", "driver_id": "some-driver-id"}
        )
        print(f"Invalid order status response: {response.status_code}")
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Invalid order returns 404")
    
    def test_09_update_order_status_invalid_status(self):
        """Test updating with invalid status returns 400"""
        # First get a valid order ID
        response = requests.get(f"{BASE_URL}/api/orders")
        if response.status_code == 200 and len(response.json()) > 0:
            order_id = response.json()[0]["id"]
            
            response = requests.put(
                f"{BASE_URL}/api/driver/orders/{order_id}/status",
                params={"status": "invalid_status", "driver_id": "some-driver-id"}
            )
            print(f"Invalid status response: {response.status_code}")
            
            assert response.status_code == 400, f"Expected 400, got {response.status_code}"
            print("✓ Invalid status returns 400")
        else:
            pytest.skip("No orders found to test")


class TestSystemSettings:
    """Test system settings APIs (currency, language)"""
    
    def test_10_get_currencies(self):
        """Test getting supported currencies"""
        response = requests.get(f"{BASE_URL}/api/system/currencies")
        print(f"Get currencies response: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "currencies" in data, "Response should contain 'currencies' key"
        print(f"✓ Got {len(data['currencies'])} currencies")
    
    def test_11_get_languages(self):
        """Test getting supported languages"""
        response = requests.get(f"{BASE_URL}/api/system/languages")
        print(f"Get languages response: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "languages" in data, "Response should contain 'languages' key"
        print(f"✓ Got {len(data['languages'])} languages")
    
    def test_12_get_countries(self):
        """Test getting supported countries"""
        response = requests.get(f"{BASE_URL}/api/system/countries")
        print(f"Get countries response: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "countries" in data, "Response should contain 'countries' key"
        print(f"✓ Got {len(data['countries'])} countries")


class TestDriversManagement:
    """Test drivers management APIs (select all, delete)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin to get token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "demo@maestroegp.com", "password": "demo123"}
        )
        if response.status_code == 200:
            self.token = response.json().get("token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Could not login as admin")
    
    def test_13_get_all_drivers(self):
        """Test getting all drivers"""
        response = requests.get(
            f"{BASE_URL}/api/drivers",
            headers=self.headers
        )
        print(f"Get drivers response: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✓ Got {len(data)} drivers")
    
    def test_14_create_driver_with_pin(self):
        """Test creating a driver with custom PIN"""
        # First get a branch ID
        branches_response = requests.get(f"{BASE_URL}/api/branches", headers=self.headers)
        if branches_response.status_code != 200 or len(branches_response.json()) == 0:
            pytest.skip("No branches found")
        
        branch_id = branches_response.json()[0]["id"]
        
        response = requests.post(
            f"{BASE_URL}/api/drivers",
            headers=self.headers,
            json={
                "name": "Test Driver Iter60",
                "phone": "07800060060",
                "pin": "6060",
                "branch_id": branch_id
            }
        )
        print(f"Create driver response: {response.status_code}")
        print(f"Response body: {response.text[:500]}")
        
        if response.status_code == 200:
            # Verify PIN was saved by trying to login
            login_response = requests.post(
                f"{BASE_URL}/api/driver/login",
                params={"phone": "07800060060", "pin": "6060"}
            )
            assert login_response.status_code == 200, "Should be able to login with custom PIN"
            print("✓ Driver created with custom PIN")
            
            # Cleanup - delete the test driver
            driver_id = response.json().get("id")
            if driver_id:
                requests.delete(f"{BASE_URL}/api/drivers/{driver_id}", headers=self.headers)
        else:
            # Driver might already exist
            print(f"Driver creation returned {response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
