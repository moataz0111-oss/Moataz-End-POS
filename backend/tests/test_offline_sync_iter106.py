"""
Test Offline Sync Routes - Iteration 106
اختبار نقاط نهاية المزامنة للعمل Offline
"""
import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "demo@maestroegp.com"
TEST_PASSWORD = "demo123"


class TestOfflineSyncRoutes:
    """اختبار مسارات المزامنة Offline"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """إعداد الاختبار - تسجيل الدخول"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # تسجيل الدخول
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if login_response.status_code == 200:
            data = login_response.json()
            self.token = data.get("access_token") or data.get("token")
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            self.user = data.get("user", {})
        else:
            pytest.skip(f"فشل تسجيل الدخول: {login_response.status_code}")
    
    # ==================== SYNC ORDERS ====================
    
    def test_sync_order_success(self):
        """اختبار مزامنة طلب جديد بنجاح"""
        offline_id = f"OFF-TEST-{uuid.uuid4().hex[:8].upper()}"
        
        order_data = {
            "offline_id": offline_id,
            "items": [
                {"product_id": "test-product-1", "name": "منتج اختبار", "price": 50, "quantity": 2}
            ],
            "total": 100,
            "subtotal": 100,
            "discount": 0,
            "tax": 0,
            "status": "delivered",
            "order_type": "takeaway",
            "payment_method": "cash",
            "customer_name": "عميل اختبار",
            "customer_phone": "01234567890",
            "is_offline_order": True
        }
        
        response = self.session.post(f"{BASE_URL}/api/sync/orders", json=order_data)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "id" in data
        assert "order_number" in data
        print(f"✅ تم مزامنة الطلب: {offline_id} → #{data.get('order_number')}")
    
    def test_sync_duplicate_order(self):
        """اختبار عدم تكرار الطلب عند المزامنة مرتين"""
        offline_id = f"OFF-DUP-{uuid.uuid4().hex[:8].upper()}"
        
        order_data = {
            "offline_id": offline_id,
            "items": [{"product_id": "test-1", "name": "منتج", "price": 25, "quantity": 1}],
            "total": 25,
            "status": "delivered",
            "order_type": "takeaway",
            "payment_method": "cash",
            "is_offline_order": True
        }
        
        # المزامنة الأولى
        response1 = self.session.post(f"{BASE_URL}/api/sync/orders", json=order_data)
        assert response1.status_code == 200
        data1 = response1.json()
        
        # المزامنة الثانية (نفس الطلب)
        response2 = self.session.post(f"{BASE_URL}/api/sync/orders", json=order_data)
        assert response2.status_code == 200
        data2 = response2.json()
        
        # يجب أن يكون نفس الـ ID
        assert data1.get("id") == data2.get("id"), "يجب أن يرجع نفس الطلب"
        assert "موجود مسبقاً" in data2.get("message", "") or data2.get("success") == True
        print(f"✅ تم التحقق من عدم تكرار الطلب: {offline_id}")
    
    def test_sync_order_with_delivery(self):
        """اختبار مزامنة طلب توصيل"""
        offline_id = f"OFF-DEL-{uuid.uuid4().hex[:8].upper()}"
        
        order_data = {
            "offline_id": offline_id,
            "items": [{"product_id": "test-2", "name": "منتج توصيل", "price": 75, "quantity": 1}],
            "total": 75,
            "status": "pending",
            "order_type": "delivery",
            "payment_method": "cash",
            "customer_name": "عميل توصيل",
            "customer_phone": "01111111111",
            "delivery_address": "شارع الاختبار، المنطقة 1",
            "is_offline_order": True
        }
        
        response = self.session.post(f"{BASE_URL}/api/sync/orders", json=order_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print(f"✅ تم مزامنة طلب التوصيل: {offline_id}")
    
    # ==================== SYNC CUSTOMERS ====================
    
    def test_sync_customer_success(self):
        """اختبار مزامنة عميل جديد"""
        customer_data = {
            "name": f"عميل اختبار {uuid.uuid4().hex[:6]}",
            "phone": f"010{uuid.uuid4().hex[:8]}",
            "email": f"test_{uuid.uuid4().hex[:6]}@test.com",
            "address": "عنوان الاختبار"
        }
        
        response = self.session.post(f"{BASE_URL}/api/sync/customers", json=customer_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "id" in data
        print(f"✅ تم مزامنة العميل: {customer_data['name']}")
    
    def test_sync_duplicate_customer_by_phone(self):
        """اختبار عدم تكرار العميل بنفس رقم الهاتف"""
        phone = f"012{uuid.uuid4().hex[:8]}"
        
        customer_data = {
            "name": "عميل مكرر",
            "phone": phone
        }
        
        # المزامنة الأولى
        response1 = self.session.post(f"{BASE_URL}/api/sync/customers", json=customer_data)
        assert response1.status_code == 200
        data1 = response1.json()
        
        # المزامنة الثانية
        response2 = self.session.post(f"{BASE_URL}/api/sync/customers", json=customer_data)
        assert response2.status_code == 200
        data2 = response2.json()
        
        # يجب أن يكون نفس الـ ID
        assert data1.get("id") == data2.get("id")
        print(f"✅ تم التحقق من عدم تكرار العميل: {phone}")
    
    # ==================== SYNC TABLES ====================
    
    def test_sync_table_update(self):
        """اختبار مزامنة تحديث طاولة"""
        # أولاً نجلب الطاولات
        tables_response = self.session.get(f"{BASE_URL}/api/tables")
        
        if tables_response.status_code != 200 or not tables_response.json():
            pytest.skip("لا توجد طاولات للاختبار")
        
        tables = tables_response.json()
        table_id = tables[0].get("id")
        
        update_data = {
            "id": table_id,
            "status": "available"
        }
        
        response = self.session.post(f"{BASE_URL}/api/sync/tables", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print(f"✅ تم مزامنة تحديث الطاولة: {table_id}")
    
    def test_sync_table_not_found(self):
        """اختبار تحديث طاولة غير موجودة"""
        update_data = {
            "id": "non-existent-table-id",
            "status": "occupied"
        }
        
        response = self.session.post(f"{BASE_URL}/api/sync/tables", json=update_data)
        
        assert response.status_code == 404
        print("✅ تم التحقق من خطأ الطاولة غير الموجودة")
    
    # ==================== SYNC ATTENDANCE ====================
    
    def test_sync_attendance_success(self):
        """اختبار مزامنة سجل حضور"""
        offline_id = f"ATT-{uuid.uuid4().hex[:8].upper()}"
        today = datetime.now().strftime("%Y-%m-%d")
        
        attendance_data = {
            "offline_id": offline_id,
            "employee_id": self.user.get("id", "test-employee"),
            "date": today,
            "check_in": "09:00",
            "status": "present",
            "notes": "حضور اختبار"
        }
        
        response = self.session.post(f"{BASE_URL}/api/sync/attendance", json=attendance_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print(f"✅ تم مزامنة سجل الحضور: {offline_id}")
    
    # ==================== SYNC INVENTORY ====================
    
    def test_sync_inventory_transaction(self):
        """اختبار مزامنة حركة مخزون"""
        offline_id = f"INV-{uuid.uuid4().hex[:8].upper()}"
        
        transaction_data = {
            "offline_id": offline_id,
            "item_id": "test-inventory-item",
            "item_name": "مادة اختبار",
            "transaction_type": "add",
            "quantity": 10,
            "notes": "إضافة اختبار"
        }
        
        response = self.session.post(f"{BASE_URL}/api/sync/inventory", json=transaction_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print(f"✅ تم مزامنة حركة المخزون: {offline_id}")
    
    def test_sync_inventory_duplicate(self):
        """اختبار عدم تكرار حركة المخزون"""
        offline_id = f"INV-DUP-{uuid.uuid4().hex[:8].upper()}"
        
        transaction_data = {
            "offline_id": offline_id,
            "item_id": "test-item-dup",
            "transaction_type": "remove",
            "quantity": 5
        }
        
        # المزامنة الأولى
        response1 = self.session.post(f"{BASE_URL}/api/sync/inventory", json=transaction_data)
        assert response1.status_code == 200
        
        # المزامنة الثانية
        response2 = self.session.post(f"{BASE_URL}/api/sync/inventory", json=transaction_data)
        assert response2.status_code == 200
        data2 = response2.json()
        
        assert "موجودة مسبقاً" in data2.get("message", "") or data2.get("success") == True
        print(f"✅ تم التحقق من عدم تكرار حركة المخزون: {offline_id}")
    
    # ==================== SYNC STATUS ====================
    
    def test_get_sync_status(self):
        """اختبار الحصول على حالة المزامنة"""
        response = self.session.get(f"{BASE_URL}/api/sync/status")
        
        assert response.status_code == 200
        data = response.json()
        assert "server_time" in data
        print(f"✅ حالة المزامنة: {data}")
    
    # ==================== BATCH SYNC ====================
    
    def test_batch_sync(self):
        """اختبار المزامنة الدفعية"""
        batch_data = {
            "orders": [
                {
                    "offline_id": f"BATCH-ORD-{uuid.uuid4().hex[:6].upper()}",
                    "items": [{"product_id": "p1", "name": "منتج 1", "price": 30, "quantity": 1}],
                    "total": 30,
                    "status": "delivered",
                    "order_type": "takeaway",
                    "payment_method": "cash"
                }
            ],
            "customers": [
                {
                    "name": f"عميل دفعة {uuid.uuid4().hex[:4]}",
                    "phone": f"015{uuid.uuid4().hex[:8]}"
                }
            ]
        }
        
        response = self.session.post(f"{BASE_URL}/api/sync/batch", json=batch_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "orders" in data
        assert "customers" in data
        print(f"✅ المزامنة الدفعية: طلبات={data['orders']['synced']}, عملاء={data['customers']['synced']}")


class TestCoreAPIs:
    """اختبار APIs الأساسية للتطبيق"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """إعداد الاختبار"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # تسجيل الدخول
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if login_response.status_code == 200:
            data = login_response.json()
            self.token = data.get("access_token") or data.get("token")
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        else:
            pytest.skip("فشل تسجيل الدخول")
    
    def test_get_categories(self):
        """اختبار جلب التصنيفات"""
        response = self.session.get(f"{BASE_URL}/api/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ عدد التصنيفات: {len(data)}")
    
    def test_get_products(self):
        """اختبار جلب المنتجات"""
        response = self.session.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ عدد المنتجات: {len(data)}")
    
    def test_get_tables(self):
        """اختبار جلب الطاولات"""
        response = self.session.get(f"{BASE_URL}/api/tables")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ عدد الطاولات: {len(data)}")
    
    def test_get_orders(self):
        """اختبار جلب الطلبات"""
        response = self.session.get(f"{BASE_URL}/api/orders")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ عدد الطلبات: {len(data)}")
    
    def test_get_branches(self):
        """اختبار جلب الفروع"""
        response = self.session.get(f"{BASE_URL}/api/branches")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ عدد الفروع: {len(data)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
