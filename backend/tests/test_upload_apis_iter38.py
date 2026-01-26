"""
Test suite for image upload APIs - Iteration 38
Tests: /api/upload/logo, /api/upload/image, /api/upload/background
"""
import pytest
import requests
import os
from io import BytesIO
from PIL import Image

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
SUPER_ADMIN_CREDS = {
    "email": "owner@maestroegp.com",
    "password": "owner123",
    "secret_key": "271018"
}

DEMO_CLIENT_CREDS = {
    "email": "demo@maestroegp.com",
    "password": "demo123"
}


def create_test_image(width=100, height=100, color='blue'):
    """Create a test image in memory"""
    img = Image.new('RGB', (width, height), color=color)
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer


@pytest.fixture(scope="module")
def super_admin_token():
    """Get super admin authentication token"""
    response = requests.post(
        f"{BASE_URL}/api/super-admin/login",
        json=SUPER_ADMIN_CREDS
    )
    assert response.status_code == 200, f"Super admin login failed: {response.text}"
    return response.json()["token"]


@pytest.fixture(scope="module")
def demo_client_token():
    """Get demo client authentication token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json=DEMO_CLIENT_CREDS
    )
    assert response.status_code == 200, f"Demo client login failed: {response.text}"
    return response.json()["token"]


class TestUploadLogoAPI:
    """Tests for /api/upload/logo endpoint"""
    
    def test_upload_logo_success(self, super_admin_token):
        """Test successful logo upload by super admin"""
        test_image = create_test_image(200, 200, 'red')
        
        response = requests.post(
            f"{BASE_URL}/api/upload/logo",
            headers={"Authorization": f"Bearer {super_admin_token}"},
            files={"file": ("test_logo.png", test_image, "image/png")}
        )
        
        assert response.status_code == 200, f"Logo upload failed: {response.text}"
        data = response.json()
        assert "logo_url" in data, "Response missing logo_url"
        assert data["logo_url"].startswith("/api/uploads/logos/"), "Invalid logo URL format"
        assert "message" in data, "Response missing message"
        print(f"✅ Logo uploaded successfully: {data['logo_url']}")
    
    def test_upload_logo_with_tenant_id(self, super_admin_token):
        """Test logo upload with tenant_id parameter"""
        test_image = create_test_image(150, 150, 'green')
        
        response = requests.post(
            f"{BASE_URL}/api/upload/logo",
            headers={"Authorization": f"Bearer {super_admin_token}"},
            files={"file": ("tenant_logo.png", test_image, "image/png")},
            data={"tenant_id": "test-tenant-123"}
        )
        
        assert response.status_code == 200, f"Logo upload with tenant_id failed: {response.text}"
        data = response.json()
        assert "logo_url" in data
        print(f"✅ Logo with tenant_id uploaded: {data['logo_url']}")
    
    def test_upload_logo_unauthorized(self, demo_client_token):
        """Test logo upload by non-super-admin (should fail)"""
        test_image = create_test_image()
        
        response = requests.post(
            f"{BASE_URL}/api/upload/logo",
            headers={"Authorization": f"Bearer {demo_client_token}"},
            files={"file": ("test.png", test_image, "image/png")}
        )
        
        # Should be forbidden for non-super-admin
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✅ Non-super-admin correctly rejected from logo upload")
    
    def test_upload_logo_invalid_file_type(self, super_admin_token):
        """Test logo upload with invalid file type"""
        response = requests.post(
            f"{BASE_URL}/api/upload/logo",
            headers={"Authorization": f"Bearer {super_admin_token}"},
            files={"file": ("test.txt", BytesIO(b"not an image"), "text/plain")}
        )
        
        assert response.status_code == 400, f"Expected 400 for invalid file type, got {response.status_code}"
        print("✅ Invalid file type correctly rejected")


class TestUploadImageAPI:
    """Tests for /api/upload/image endpoint"""
    
    def test_upload_product_image(self, demo_client_token):
        """Test product image upload"""
        test_image = create_test_image(400, 400, 'yellow')
        
        response = requests.post(
            f"{BASE_URL}/api/upload/image",
            headers={"Authorization": f"Bearer {demo_client_token}"},
            files={"file": ("product.png", test_image, "image/png")},
            data={"type": "product"}
        )
        
        assert response.status_code == 200, f"Product image upload failed: {response.text}"
        data = response.json()
        assert "image_url" in data, "Response missing image_url"
        assert "/products/" in data["image_url"], "Product image URL should contain /products/"
        print(f"✅ Product image uploaded: {data['image_url']}")
    
    def test_upload_category_image(self, demo_client_token):
        """Test category image upload"""
        test_image = create_test_image(300, 300, 'purple')
        
        response = requests.post(
            f"{BASE_URL}/api/upload/image",
            headers={"Authorization": f"Bearer {demo_client_token}"},
            files={"file": ("category.png", test_image, "image/png")},
            data={"type": "category"}
        )
        
        assert response.status_code == 200, f"Category image upload failed: {response.text}"
        data = response.json()
        assert "image_url" in data
        assert "/categories/" in data["image_url"], "Category image URL should contain /categories/"
        print(f"✅ Category image uploaded: {data['image_url']}")
    
    def test_upload_general_image(self, demo_client_token):
        """Test general image upload"""
        test_image = create_test_image(500, 500, 'orange')
        
        response = requests.post(
            f"{BASE_URL}/api/upload/image",
            headers={"Authorization": f"Bearer {demo_client_token}"},
            files={"file": ("general.png", test_image, "image/png")},
            data={"type": "general"}
        )
        
        assert response.status_code == 200, f"General image upload failed: {response.text}"
        data = response.json()
        assert "image_url" in data
        print(f"✅ General image uploaded: {data['image_url']}")
    
    def test_upload_image_unauthorized(self):
        """Test image upload without authentication"""
        test_image = create_test_image()
        
        response = requests.post(
            f"{BASE_URL}/api/upload/image",
            files={"file": ("test.png", test_image, "image/png")},
            data={"type": "product"}
        )
        
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✅ Unauthenticated upload correctly rejected")
    
    def test_upload_image_invalid_type(self, demo_client_token):
        """Test image upload with invalid file type"""
        response = requests.post(
            f"{BASE_URL}/api/upload/image",
            headers={"Authorization": f"Bearer {demo_client_token}"},
            files={"file": ("test.pdf", BytesIO(b"PDF content"), "application/pdf")},
            data={"type": "product"}
        )
        
        assert response.status_code == 400, f"Expected 400 for invalid file type, got {response.status_code}"
        print("✅ Invalid file type correctly rejected")


class TestUploadBackgroundAPI:
    """Tests for /api/upload/background endpoint"""
    
    def test_upload_background_success(self, super_admin_token):
        """Test successful background upload"""
        test_image = create_test_image(1920, 1080, 'navy')
        
        response = requests.post(
            f"{BASE_URL}/api/upload/background",
            headers={"Authorization": f"Bearer {super_admin_token}"},
            files={"file": ("background.png", test_image, "image/png")},
            data={
                "title": "Test Background",
                "animation_type": "fade"
            }
        )
        
        assert response.status_code == 200, f"Background upload failed: {response.text}"
        data = response.json()
        assert "background" in data, "Response missing background object"
        assert "image_url" in data["background"], "Background missing image_url"
        assert "id" in data["background"], "Background missing id"
        assert data["background"]["title"] == "Test Background"
        assert data["background"]["animation_type"] == "fade"
        print(f"✅ Background uploaded: {data['background']['image_url']}")
    
    def test_upload_background_with_animation(self, super_admin_token):
        """Test background upload with different animation types"""
        animation_types = ["fade", "zoom", "kenburns", "slide"]
        
        for anim_type in animation_types:
            test_image = create_test_image(800, 600, 'teal')
            
            response = requests.post(
                f"{BASE_URL}/api/upload/background",
                headers={"Authorization": f"Bearer {super_admin_token}"},
                files={"file": (f"bg_{anim_type}.png", test_image, "image/png")},
                data={
                    "title": f"Background {anim_type}",
                    "animation_type": anim_type
                }
            )
            
            assert response.status_code == 200, f"Background upload with {anim_type} failed"
            data = response.json()
            assert data["background"]["animation_type"] == anim_type
            print(f"✅ Background with {anim_type} animation uploaded")
    
    def test_upload_background_unauthorized(self, demo_client_token):
        """Test background upload by non-super-admin (should fail)"""
        test_image = create_test_image()
        
        response = requests.post(
            f"{BASE_URL}/api/upload/background",
            headers={"Authorization": f"Bearer {demo_client_token}"},
            files={"file": ("bg.png", test_image, "image/png")},
            data={"title": "Test", "animation_type": "fade"}
        )
        
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✅ Non-super-admin correctly rejected from background upload")


class TestUploadedFilesAccessibility:
    """Tests to verify uploaded files are accessible"""
    
    def test_uploaded_logo_accessible(self, super_admin_token):
        """Test that uploaded logo is accessible via URL"""
        # First upload a logo
        test_image = create_test_image(100, 100, 'cyan')
        
        upload_response = requests.post(
            f"{BASE_URL}/api/upload/logo",
            headers={"Authorization": f"Bearer {super_admin_token}"},
            files={"file": ("access_test.png", test_image, "image/png")}
        )
        
        assert upload_response.status_code == 200
        logo_url = upload_response.json()["logo_url"]
        
        # Try to access the uploaded file
        full_url = f"{BASE_URL}{logo_url}"
        access_response = requests.get(full_url)
        
        assert access_response.status_code == 200, f"Could not access uploaded logo at {full_url}"
        assert "image" in access_response.headers.get("content-type", ""), "Response is not an image"
        print(f"✅ Uploaded logo accessible at {full_url}")
    
    def test_uploaded_image_accessible(self, demo_client_token):
        """Test that uploaded product image is accessible"""
        test_image = create_test_image(200, 200, 'magenta')
        
        upload_response = requests.post(
            f"{BASE_URL}/api/upload/image",
            headers={"Authorization": f"Bearer {demo_client_token}"},
            files={"file": ("access_test.png", test_image, "image/png")},
            data={"type": "product"}
        )
        
        assert upload_response.status_code == 200
        image_url = upload_response.json()["image_url"]
        
        # Try to access the uploaded file
        full_url = f"{BASE_URL}{image_url}"
        access_response = requests.get(full_url)
        
        assert access_response.status_code == 200, f"Could not access uploaded image at {full_url}"
        print(f"✅ Uploaded image accessible at {full_url}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
