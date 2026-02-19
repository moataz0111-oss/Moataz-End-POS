"""
Test Cash Register Summary API - Verify expected_cash calculation fix
Issue: expected_cash was showing 0 despite having sales
Fix: Corrected field name from closed_at to ended_at for finding last closed shift
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestCashRegisterSummary:
    """Test cash register summary endpoint - expected_cash fix verification"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test with authentication"""
        # Login to get token
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "demo@maestroegp.com", "password": "demo123"}
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        self.token = login_response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_cash_register_summary_returns_expected_cash(self):
        """Test that /api/cash-register/summary returns non-zero expected_cash when there are sales"""
        response = requests.get(
            f"{BASE_URL}/api/cash-register/summary",
            headers=self.headers
        )
        
        # Should return 200 if there's an open shift
        if response.status_code == 404:
            pytest.skip("No open shift found - cannot test expected_cash")
        
        assert response.status_code == 200, f"API returned {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify response structure
        assert "expected_cash" in data, "Response missing expected_cash field"
        assert "total_sales" in data, "Response missing total_sales field"
        assert "cash_sales" in data, "Response missing cash_sales field"
        assert "opening_cash" in data, "Response missing opening_cash field"
        assert "total_expenses" in data, "Response missing total_expenses field"
        
        # Verify expected_cash calculation: opening_cash + cash_sales - total_expenses
        expected_calculation = data["opening_cash"] + data["cash_sales"] - data["total_expenses"]
        assert data["expected_cash"] == expected_calculation, \
            f"expected_cash mismatch: got {data['expected_cash']}, expected {expected_calculation}"
        
        # If there are cash sales, expected_cash should not be zero (unless expenses equal cash_sales)
        if data["cash_sales"] > 0 and data["total_expenses"] < data["cash_sales"]:
            assert data["expected_cash"] > 0, \
                f"expected_cash should be > 0 when cash_sales ({data['cash_sales']}) > expenses ({data['total_expenses']})"
        
        print(f"✓ expected_cash: {data['expected_cash']}")
        print(f"✓ cash_sales: {data['cash_sales']}")
        print(f"✓ total_sales: {data['total_sales']}")
        print(f"✓ opening_cash: {data['opening_cash']}")
        print(f"✓ total_expenses: {data['total_expenses']}")
    
    def test_cash_register_summary_includes_all_required_fields(self):
        """Test that summary includes all required fields for the close dialog"""
        response = requests.get(
            f"{BASE_URL}/api/cash-register/summary",
            headers=self.headers
        )
        
        if response.status_code == 404:
            pytest.skip("No open shift found")
        
        assert response.status_code == 200
        data = response.json()
        
        required_fields = [
            "shift_id", "branch_id", "branch_name", "cashier_id", "cashier_name",
            "started_at", "opening_cash", "total_sales", "total_cost", "gross_profit",
            "total_orders", "cash_sales", "card_sales", "credit_sales", "non_cash_amount",
            "delivery_app_sales", "driver_sales", "discounts_total", "cancelled_orders",
            "cancelled_amount", "cancelled_by", "total_expenses", "net_profit", "expected_cash"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        print(f"✓ All {len(required_fields)} required fields present")
    
    def test_current_shift_exists(self):
        """Test that current shift endpoint works"""
        response = requests.get(
            f"{BASE_URL}/api/shifts/current",
            headers=self.headers
        )
        
        # Can be 200 (shift exists) or 404/null (no shift)
        assert response.status_code in [200, 404], f"Unexpected status: {response.status_code}"
        
        if response.status_code == 200 and response.json():
            data = response.json()
            assert "id" in data, "Shift missing id"
            assert "status" in data, "Shift missing status"
            print(f"✓ Current shift found: {data.get('id')}")
        else:
            print("✓ No current shift (expected behavior if none open)")


class TestCashRegisterClose:
    """Test cash register close endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test with authentication"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "demo@maestroegp.com", "password": "demo123"}
        )
        assert login_response.status_code == 200
        self.token = login_response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_cash_register_close_requires_auth(self):
        """Test that close endpoint requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/cash-register/close",
            json={"denominations": {}, "notes": "test"}
        )
        assert response.status_code in [401, 403], "Should require authentication"
        print("✓ Close endpoint requires authentication")
    
    def test_cash_register_summary_requires_auth(self):
        """Test that summary endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/cash-register/summary")
        assert response.status_code in [401, 403], "Should require authentication"
        print("✓ Summary endpoint requires authentication")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
