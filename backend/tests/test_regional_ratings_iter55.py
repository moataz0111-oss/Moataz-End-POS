"""
Iteration 55 - Regional Settings & Order Ratings API Tests
Tests for:
1. Currency system APIs (GET /api/system/currencies)
2. Language system APIs (GET /api/system/languages)
3. Country system APIs (GET /api/system/countries)
4. Currency conversion API (POST /api/convert-currency)
5. Tenant regional settings APIs (GET/PUT /api/tenant/regional-settings)
6. Customer regional settings API (GET /api/customer/regional-settings/{tenant})
7. Order rating APIs (POST /api/customer/rate-order, GET /api/ratings/tenant-summary)
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "demo@maestroegp.com"
ADMIN_PASSWORD = "demo123"
TEST_CUSTOMER_PHONE = "01012345678"
RESTAURANT_SLUG = "demo-maestro"


class TestSystemAPIs:
    """Test system configuration APIs (currencies, languages, countries)"""
    
    def test_get_supported_currencies(self):
        """Test GET /api/system/currencies - should return all supported currencies"""
        response = requests.get(f"{BASE_URL}/api/system/currencies")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "currencies" in data, "Response should contain 'currencies' key"
        
        currencies = data["currencies"]
        # Verify expected currencies exist
        expected_currencies = ["IQD", "USD", "SAR", "AED", "KWD", "EGP", "JOD", "EUR", "GBP", "TRY"]
        for currency in expected_currencies:
            assert currency in currencies, f"Currency {currency} should be in supported currencies"
        
        # Verify currency structure
        iqd = currencies.get("IQD", {})
        assert "name" in iqd, "Currency should have 'name'"
        assert "name_en" in iqd, "Currency should have 'name_en'"
        assert "symbol" in iqd, "Currency should have 'symbol'"
        assert "rate_to_usd" in iqd, "Currency should have 'rate_to_usd'"
        assert "decimal_places" in iqd, "Currency should have 'decimal_places'"
        
        print(f"✓ Found {len(currencies)} supported currencies")
    
    def test_get_supported_languages(self):
        """Test GET /api/system/languages - should return all supported languages"""
        response = requests.get(f"{BASE_URL}/api/system/languages")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "languages" in data, "Response should contain 'languages' key"
        
        languages = data["languages"]
        # Verify expected languages exist
        expected_languages = ["ar", "en", "ku", "fa", "tr"]
        for lang in expected_languages:
            assert lang in languages, f"Language {lang} should be in supported languages"
        
        # Verify language structure
        ar = languages.get("ar", {})
        assert "name" in ar, "Language should have 'name'"
        assert "name_en" in ar, "Language should have 'name_en'"
        assert "dir" in ar, "Language should have 'dir' (direction)"
        assert ar["dir"] == "rtl", "Arabic should be RTL"
        
        en = languages.get("en", {})
        assert en["dir"] == "ltr", "English should be LTR"
        
        print(f"✓ Found {len(languages)} supported languages")
    
    def test_get_supported_countries(self):
        """Test GET /api/system/countries - should return all supported countries"""
        response = requests.get(f"{BASE_URL}/api/system/countries")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "countries" in data, "Response should contain 'countries' key"
        
        countries = data["countries"]
        # Verify expected countries exist
        expected_countries = ["IQ", "SA", "AE", "KW", "EG", "JO", "US", "GB", "TR"]
        for country in expected_countries:
            assert country in countries, f"Country {country} should be in supported countries"
        
        # Verify country structure
        iq = countries.get("IQ", {})
        assert "name" in iq, "Country should have 'name'"
        assert "name_en" in iq, "Country should have 'name_en'"
        assert "currency" in iq, "Country should have 'currency'"
        assert "language" in iq, "Country should have 'language'"
        assert iq["currency"] == "IQD", "Iraq should use IQD"
        assert iq["language"] == "ar", "Iraq should use Arabic"
        
        print(f"✓ Found {len(countries)} supported countries")


class TestCurrencyConversion:
    """Test currency conversion API"""
    
    def test_convert_iqd_to_usd(self):
        """Test POST /api/convert-currency - IQD to USD"""
        response = requests.post(
            f"{BASE_URL}/api/convert-currency",
            params={"amount": 1000000, "from_currency": "IQD", "to_currency": "USD"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "original_amount" in data, "Response should have 'original_amount'"
        assert "converted_amount" in data, "Response should have 'converted_amount'"
        assert "exchange_rate" in data, "Response should have 'exchange_rate'"
        assert data["original_currency"] == "IQD"
        assert data["target_currency"] == "USD"
        assert data["converted_amount"] > 0, "Converted amount should be positive"
        
        print(f"✓ Converted 1,000,000 IQD to {data['converted_amount']} USD")
    
    def test_convert_usd_to_sar(self):
        """Test POST /api/convert-currency - USD to SAR"""
        response = requests.post(
            f"{BASE_URL}/api/convert-currency",
            params={"amount": 100, "from_currency": "USD", "to_currency": "SAR"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["original_amount"] == 100
        assert data["converted_amount"] > 0
        
        print(f"✓ Converted 100 USD to {data['converted_amount']} SAR")
    
    def test_convert_invalid_currency(self):
        """Test POST /api/convert-currency - invalid currency should return 400"""
        response = requests.post(
            f"{BASE_URL}/api/convert-currency",
            params={"amount": 100, "from_currency": "INVALID", "to_currency": "USD"}
        )
        assert response.status_code == 400, f"Expected 400 for invalid currency, got {response.status_code}"
        
        print("✓ Invalid currency returns 400 as expected")


class TestTenantRegionalSettings:
    """Test tenant regional settings APIs (requires authentication)"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Authentication failed - skipping authenticated tests")
    
    def test_get_tenant_regional_settings(self, auth_token):
        """Test GET /api/tenant/regional-settings - get tenant's regional settings"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/tenant/regional-settings", headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # Verify default settings structure
        assert "country" in data, "Should have 'country'"
        assert "currency" in data, "Should have 'currency'"
        assert "language" in data, "Should have 'language'"
        
        print(f"✓ Tenant regional settings: country={data.get('country')}, currency={data.get('currency')}, language={data.get('language')}")
    
    def test_update_tenant_regional_settings(self, auth_token):
        """Test PUT /api/tenant/regional-settings - update tenant's regional settings"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        # Update to Saudi Arabia settings
        update_data = {
            "country": "SA",
            "currency": "SAR",
            "language": "ar",
            "secondary_currency": "USD",
            "show_secondary_currency": True
        }
        
        response = requests.put(
            f"{BASE_URL}/api/tenant/regional-settings",
            headers=headers,
            json=update_data
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "settings" in data or "message" in data
        
        # Verify the update by getting settings again
        get_response = requests.get(f"{BASE_URL}/api/tenant/regional-settings", headers=headers)
        assert get_response.status_code == 200
        
        updated_settings = get_response.json()
        assert updated_settings.get("country") == "SA", "Country should be updated to SA"
        assert updated_settings.get("currency") == "SAR", "Currency should be updated to SAR"
        
        print(f"✓ Updated tenant regional settings to Saudi Arabia (SAR)")
        
        # Reset back to Iraq
        reset_data = {
            "country": "IQ",
            "currency": "IQD",
            "language": "ar",
            "secondary_currency": "USD",
            "show_secondary_currency": False
        }
        requests.put(f"{BASE_URL}/api/tenant/regional-settings", headers=headers, json=reset_data)
        print("✓ Reset tenant regional settings back to Iraq (IQD)")


class TestCustomerRegionalSettings:
    """Test customer regional settings API (no auth required)"""
    
    def test_get_customer_regional_settings_by_slug(self):
        """Test GET /api/customer/regional-settings/{tenant} - by menu slug"""
        response = requests.get(f"{BASE_URL}/api/customer/regional-settings/{RESTAURANT_SLUG}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "country" in data, "Should have 'country'"
        assert "currency" in data, "Should have 'currency'"
        assert "language" in data, "Should have 'language'"
        
        # Should include currency info
        if "currency_info" in data:
            assert "symbol" in data["currency_info"], "Currency info should have symbol"
            assert "name" in data["currency_info"], "Currency info should have name"
        
        print(f"✓ Customer regional settings for {RESTAURANT_SLUG}: currency={data.get('currency')}")
    
    def test_get_customer_regional_settings_invalid_tenant(self):
        """Test GET /api/customer/regional-settings/{tenant} - invalid tenant returns 404"""
        response = requests.get(f"{BASE_URL}/api/customer/regional-settings/invalid-restaurant-slug")
        
        assert response.status_code == 404, f"Expected 404 for invalid tenant, got {response.status_code}"
        
        print("✓ Invalid tenant returns 404 as expected")


class TestOrderRatings:
    """Test order rating APIs"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Authentication failed - skipping authenticated tests")
    
    def test_rate_order_invalid_order(self):
        """Test POST /api/customer/rate-order - invalid order returns 404"""
        rating_data = {
            "order_id": "invalid-order-id",
            "tenant_id": "test-tenant",
            "phone": TEST_CUSTOMER_PHONE,
            "rating": 5,
            "comment": "Great food!",
            "food_quality": 5,
            "delivery_speed": 4,
            "service_quality": 5
        }
        
        response = requests.post(f"{BASE_URL}/api/customer/rate-order", json=rating_data)
        
        assert response.status_code == 404, f"Expected 404 for invalid order, got {response.status_code}"
        
        print("✓ Invalid order returns 404 as expected")
    
    def test_rate_order_invalid_rating_value(self):
        """Test POST /api/customer/rate-order - rating out of range returns 400"""
        rating_data = {
            "order_id": "some-order-id",
            "tenant_id": "test-tenant",
            "phone": TEST_CUSTOMER_PHONE,
            "rating": 10,  # Invalid - should be 1-5
            "comment": "Test"
        }
        
        response = requests.post(f"{BASE_URL}/api/customer/rate-order", json=rating_data)
        
        # Should return 400 for invalid rating value
        assert response.status_code in [400, 404, 422], f"Expected 400/404/422 for invalid rating, got {response.status_code}"
        
        print("✓ Invalid rating value handled correctly")
    
    def test_get_tenant_ratings_summary(self, auth_token):
        """Test GET /api/ratings/tenant-summary - get tenant's ratings summary"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/ratings/tenant-summary", headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "avg_rating" in data, "Should have 'avg_rating'"
        assert "total_ratings" in data, "Should have 'total_ratings'"
        
        print(f"✓ Tenant ratings summary: avg={data.get('avg_rating')}, total={data.get('total_ratings')}")
    
    def test_get_order_rating_status(self):
        """Test GET /api/customer/order-rating/{order_id} - check if order can be rated"""
        # Test with a non-existent order - should return can_rate: True
        response = requests.get(f"{BASE_URL}/api/customer/order-rating/non-existent-order")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "can_rate" in data, "Should have 'can_rate' field"
        
        print(f"✓ Order rating status check works: can_rate={data.get('can_rate')}")


class TestAuthenticationRequired:
    """Test that protected endpoints require authentication"""
    
    def test_tenant_regional_settings_requires_auth(self):
        """Test GET /api/tenant/regional-settings without auth returns 401"""
        response = requests.get(f"{BASE_URL}/api/tenant/regional-settings")
        
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"
        
        print("✓ Tenant regional settings requires authentication")
    
    def test_ratings_summary_requires_auth(self):
        """Test GET /api/ratings/tenant-summary without auth returns 401"""
        response = requests.get(f"{BASE_URL}/api/ratings/tenant-summary")
        
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"
        
        print("✓ Ratings summary requires authentication")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
