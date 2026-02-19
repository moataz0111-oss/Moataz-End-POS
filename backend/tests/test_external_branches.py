"""
Test External Branches APIs - Iteration 91
Tests for the new External Branches Management feature
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestExternalBranchesAPIs:
    """Test External Branches Management APIs"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - Login and get auth token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login with demo credentials
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo@maestroegp.com",
            "password": "demo123"
        })
        
        if login_response.status_code == 200:
            data = login_response.json()
            token = data.get("access_token") or data.get("token")
            if token:
                self.session.headers.update({"Authorization": f"Bearer {token}"})
                self.auth_success = True
            else:
                self.auth_success = False
        else:
            self.auth_success = False
    
    def test_01_dashboard_stats(self):
        """Test GET /api/external-branches/dashboard/stats"""
        if not self.auth_success:
            pytest.skip("Authentication failed")
        
        response = self.session.get(f"{BASE_URL}/api/external-branches/dashboard/stats")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Verify response structure
        assert "sold_branches_count" in data, "Missing sold_branches_count"
        assert "current_month" in data, "Missing current_month"
        assert "monthly_revenue" in data, "Missing monthly_revenue"
        assert "monthly_materials" in data, "Missing monthly_materials"
        assert "total_monthly_due" in data, "Missing total_monthly_due"
        
        print(f"✓ Dashboard stats: {data['sold_branches_count']} sold branches, revenue: {data['monthly_revenue']}")
    
    def test_02_get_sold_branches_list(self):
        """Test GET /api/external-branches/"""
        if not self.auth_success:
            pytest.skip("Authentication failed")
        
        response = self.session.get(f"{BASE_URL}/api/external-branches/")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Expected list response"
        
        print(f"✓ Sold branches list: {len(data)} branches")
    
    def test_03_monthly_report(self):
        """Test GET /api/external-branches/reports/monthly"""
        if not self.auth_success:
            pytest.skip("Authentication failed")
        
        response = self.session.get(f"{BASE_URL}/api/external-branches/reports/monthly")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Verify response structure
        assert "month" in data, "Missing month"
        assert "period_start" in data, "Missing period_start"
        assert "period_end" in data, "Missing period_end"
        assert "branches" in data, "Missing branches"
        assert "total_revenue" in data, "Missing total_revenue"
        assert "total_materials" in data, "Missing total_materials"
        assert "total_due" in data, "Missing total_due"
        
        print(f"✓ Monthly report for {data['month']}: {len(data['branches'])} branches, total due: {data['total_due']}")
    
    def test_04_monthly_report_with_month_param(self):
        """Test GET /api/external-branches/reports/monthly with month parameter"""
        if not self.auth_success:
            pytest.skip("Authentication failed")
        
        response = self.session.get(f"{BASE_URL}/api/external-branches/reports/monthly?month=2026-01")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["month"] == "2026-01", f"Expected month 2026-01, got {data['month']}"
        
        print(f"✓ Monthly report with param: {data['month']}")
    
    def test_05_register_branch_validation(self):
        """Test POST /api/external-branches/register - validation"""
        if not self.auth_success:
            pytest.skip("Authentication failed")
        
        # Test with missing required fields
        response = self.session.post(f"{BASE_URL}/api/external-branches/register", json={
            "branch_id": "",
            "buyer_name": ""
        })
        
        # Should fail validation (400 or 422)
        assert response.status_code in [400, 422, 404], f"Expected validation error, got {response.status_code}"
        
        print(f"✓ Register validation works: {response.status_code}")
    
    def test_06_register_branch_nonexistent(self):
        """Test POST /api/external-branches/register - non-existent branch"""
        if not self.auth_success:
            pytest.skip("Authentication failed")
        
        response = self.session.post(f"{BASE_URL}/api/external-branches/register", json={
            "branch_id": "nonexistent-branch-id-12345",
            "buyer_name": "Test Buyer",
            "owner_percentage": 10
        })
        
        # Should return 404 for non-existent branch
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
        
        print(f"✓ Non-existent branch returns 404")


class TestOwnerWalletAPI:
    """Test Owner Wallet API to verify it still works"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - Login and get auth token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo@maestroegp.com",
            "password": "demo123"
        })
        
        if login_response.status_code == 200:
            data = login_response.json()
            token = data.get("access_token") or data.get("token")
            if token:
                self.session.headers.update({"Authorization": f"Bearer {token}"})
                self.auth_success = True
            else:
                self.auth_success = False
        else:
            self.auth_success = False
    
    def test_owner_wallet_summary(self):
        """Test GET /api/owner-wallet/summary"""
        if not self.auth_success:
            pytest.skip("Authentication failed")
        
        response = self.session.get(f"{BASE_URL}/api/owner-wallet/summary")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "total_deposits" in data, "Missing total_deposits"
        assert "total_withdrawals" in data, "Missing total_withdrawals"
        assert "available_balance" in data, "Missing available_balance"
        assert "safe_balance" in data, "Missing safe_balance"
        
        print(f"✓ Owner wallet summary: balance={data['available_balance']}, safe={data['safe_balance']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
