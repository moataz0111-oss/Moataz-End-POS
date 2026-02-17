"""
Test Profit/Loss Report and Dashboard Stats - Iteration 85
Tests for:
1. GET /api/reports/profit-loss - Operating costs breakdown (rent, electricity, water, generator, salaries)
2. GET /api/dashboard/stats - gross_profit, operating_costs, total_profit (net)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL').rstrip('/')

# Test credentials
DEMO_EMAIL = "demo@maestroegp.com"
DEMO_PASSWORD = "demo123"
TEST_BRANCH_ID = "b45125b7-b7d3-48c6-9386-a95fcf773132"  # Branch with fixed costs


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for demo user"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": DEMO_EMAIL,
        "password": DEMO_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip(f"Authentication failed: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Headers with auth token"""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }


class TestProfitLossReport:
    """Tests for GET /api/reports/profit-loss API"""
    
    def test_profit_loss_returns_200(self, auth_headers):
        """Test that profit-loss endpoint returns 200"""
        today = "2026-01-01"
        response = requests.get(
            f"{BASE_URL}/api/reports/profit-loss",
            params={"start_date": today, "end_date": today},
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_profit_loss_has_fixed_costs_structure(self, auth_headers):
        """Test that profit-loss response includes fixed_costs with rent, electricity, water, generator"""
        today = "2026-01-01"
        response = requests.get(
            f"{BASE_URL}/api/reports/profit-loss",
            params={"start_date": today, "end_date": today},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check fixed_costs structure exists
        assert "fixed_costs" in data, "Response should include 'fixed_costs'"
        fixed_costs = data["fixed_costs"]
        
        # Check all required fields exist
        assert "rent" in fixed_costs, "fixed_costs should include 'rent'"
        assert "electricity" in fixed_costs, "fixed_costs should include 'electricity'"
        assert "water" in fixed_costs, "fixed_costs should include 'water'"
        assert "generator" in fixed_costs, "fixed_costs should include 'generator'"
        assert "total_monthly" in fixed_costs, "fixed_costs should include 'total_monthly'"
        assert "total_period" in fixed_costs, "fixed_costs should include 'total_period'"
        
        print(f"✓ Fixed costs structure: rent={fixed_costs['rent']}, electricity={fixed_costs['electricity']}, water={fixed_costs['water']}, generator={fixed_costs['generator']}")
    
    def test_profit_loss_has_salaries_structure(self, auth_headers):
        """Test that profit-loss response includes salaries breakdown"""
        today = "2026-01-01"
        response = requests.get(
            f"{BASE_URL}/api/reports/profit-loss",
            params={"start_date": today, "end_date": today},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check salaries structure exists
        assert "salaries" in data, "Response should include 'salaries'"
        salaries = data["salaries"]
        
        assert "total_monthly" in salaries, "salaries should include 'total_monthly'"
        assert "total_period" in salaries, "salaries should include 'total_period'"
        assert "employees_count" in salaries, "salaries should include 'employees_count'"
        
        print(f"✓ Salaries structure: monthly={salaries['total_monthly']}, period={salaries['total_period']}, employees={salaries['employees_count']}")
    
    def test_profit_loss_has_total_operating_costs(self, auth_headers):
        """Test that profit-loss response includes total_operating_costs breakdown"""
        today = "2026-01-01"
        response = requests.get(
            f"{BASE_URL}/api/reports/profit-loss",
            params={"start_date": today, "end_date": today},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check total_operating_costs structure exists
        assert "total_operating_costs" in data, "Response should include 'total_operating_costs'"
        operating_costs = data["total_operating_costs"]
        
        assert "fixed_costs" in operating_costs, "total_operating_costs should include 'fixed_costs'"
        assert "salaries" in operating_costs, "total_operating_costs should include 'salaries'"
        assert "other_expenses" in operating_costs, "total_operating_costs should include 'other_expenses'"
        assert "total" in operating_costs, "total_operating_costs should include 'total'"
        
        print(f"✓ Total operating costs: fixed={operating_costs['fixed_costs']}, salaries={operating_costs['salaries']}, other={operating_costs['other_expenses']}, total={operating_costs['total']}")
    
    def test_profit_loss_has_net_profit(self, auth_headers):
        """Test that profit-loss response includes net_profit after operating costs"""
        today = "2026-01-01"
        response = requests.get(
            f"{BASE_URL}/api/reports/profit-loss",
            params={"start_date": today, "end_date": today},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check net_profit structure exists
        assert "net_profit" in data, "Response should include 'net_profit'"
        net_profit = data["net_profit"]
        
        assert "amount" in net_profit, "net_profit should include 'amount'"
        assert "margin" in net_profit, "net_profit should include 'margin'"
        
        print(f"✓ Net profit: amount={net_profit['amount']}, margin={net_profit['margin']}%")
    
    def test_profit_loss_with_branch_filter(self, auth_headers):
        """Test profit-loss with specific branch filter"""
        today = "2026-01-01"
        response = requests.get(
            f"{BASE_URL}/api/reports/profit-loss",
            params={
                "start_date": today, 
                "end_date": today,
                "branch_id": TEST_BRANCH_ID
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure is complete
        assert "fixed_costs" in data
        assert "salaries" in data
        assert "total_operating_costs" in data
        assert "net_profit" in data
        
        print(f"✓ Branch-filtered profit-loss report retrieved successfully")


class TestDashboardStats:
    """Tests for GET /api/dashboard/stats API"""
    
    def test_dashboard_stats_returns_200(self, auth_headers):
        """Test that dashboard/stats endpoint returns 200"""
        response = requests.get(
            f"{BASE_URL}/api/dashboard/stats",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_dashboard_stats_has_today_with_profit_fields(self, auth_headers):
        """Test that dashboard stats 'today' includes gross_profit, operating_costs, total_profit"""
        response = requests.get(
            f"{BASE_URL}/api/dashboard/stats",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check today stats exist
        assert "today" in data, "Response should include 'today'"
        today = data["today"]
        
        # Check new profit fields
        assert "gross_profit" in today, "today should include 'gross_profit'"
        assert "operating_costs" in today, "today should include 'operating_costs'"
        assert "total_profit" in today, "today should include 'total_profit' (net profit)"
        
        print(f"✓ Today stats: gross_profit={today['gross_profit']}, operating_costs={today['operating_costs']}, total_profit={today['total_profit']}")
    
    def test_dashboard_stats_has_week_with_profit_fields(self, auth_headers):
        """Test that dashboard stats 'week' includes gross_profit, operating_costs, total_profit"""
        response = requests.get(
            f"{BASE_URL}/api/dashboard/stats",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check week stats exist
        assert "week" in data, "Response should include 'week'"
        week = data["week"]
        
        # Check new profit fields
        assert "gross_profit" in week, "week should include 'gross_profit'"
        assert "operating_costs" in week, "week should include 'operating_costs'"
        assert "total_profit" in week, "week should include 'total_profit' (net profit)"
        
        print(f"✓ Week stats: gross_profit={week['gross_profit']}, operating_costs={week['operating_costs']}, total_profit={week['total_profit']}")
    
    def test_dashboard_stats_has_month_with_profit_fields(self, auth_headers):
        """Test that dashboard stats 'month' includes gross_profit, operating_costs, total_profit"""
        response = requests.get(
            f"{BASE_URL}/api/dashboard/stats",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check month stats exist
        assert "month" in data, "Response should include 'month'"
        month = data["month"]
        
        # Check new profit fields
        assert "gross_profit" in month, "month should include 'gross_profit'"
        assert "operating_costs" in month, "month should include 'operating_costs'"
        assert "total_profit" in month, "month should include 'total_profit' (net profit)"
        
        print(f"✓ Month stats: gross_profit={month['gross_profit']}, operating_costs={month['operating_costs']}, total_profit={month['total_profit']}")
    
    def test_dashboard_stats_profit_calculation_logic(self, auth_headers):
        """Test that total_profit = gross_profit - operating_costs"""
        response = requests.get(
            f"{BASE_URL}/api/dashboard/stats",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        today = data["today"]
        gross_profit = today["gross_profit"]
        operating_costs = today["operating_costs"]
        total_profit = today["total_profit"]
        
        # Verify calculation: total_profit = gross_profit - operating_costs
        expected_total_profit = gross_profit - operating_costs
        assert abs(total_profit - expected_total_profit) < 0.01, \
            f"total_profit ({total_profit}) should equal gross_profit ({gross_profit}) - operating_costs ({operating_costs}) = {expected_total_profit}"
        
        print(f"✓ Profit calculation verified: {gross_profit} - {operating_costs} = {total_profit}")
    
    def test_dashboard_stats_with_branch_filter(self, auth_headers):
        """Test dashboard stats with specific branch filter"""
        response = requests.get(
            f"{BASE_URL}/api/dashboard/stats",
            params={"branch_id": TEST_BRANCH_ID},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure is complete
        assert "today" in data
        assert "week" in data
        assert "month" in data
        
        # Verify profit fields exist
        assert "gross_profit" in data["today"]
        assert "operating_costs" in data["today"]
        assert "total_profit" in data["today"]
        
        print(f"✓ Branch-filtered dashboard stats retrieved successfully")


class TestBreakEvenAPI:
    """Tests for Break-Even APIs (already tested in iter84, quick verification)"""
    
    def test_break_even_daily_returns_200(self, auth_headers):
        """Quick verification that break-even daily API still works"""
        response = requests.get(
            f"{BASE_URL}/api/break-even/daily",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ Break-even daily API working")
    
    def test_break_even_monthly_returns_200(self, auth_headers):
        """Quick verification that break-even monthly API still works"""
        response = requests.get(
            f"{BASE_URL}/api/break-even/monthly-summary",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ Break-even monthly API working")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
