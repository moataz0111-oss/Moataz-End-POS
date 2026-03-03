"""
Test Offline-First Sync System - Iteration 109
اختبار شامل لنظام Offline-First ومزامنة البيانات متعددة الأجهزة

Tests:
1. Sync Orders API (/api/sync/orders)
2. Sync Customers API (/api/sync/customers)
3. Sync Tables API (/api/sync/tables)
4. Sync Attendance API (/api/sync/attendance)
5. Sync Inventory API (/api/sync/inventory)
6. Batch Sync API (/api/sync/batch)
7. Sync Status API (/api/sync/status)
8. Duplicate handling (same offline_id)
9. Order status updates
"""
import pytest
import requests
import os
import uuid
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "demo@maestroegp.com"
TEST_PASSWORD = "demo123"


class TestSyncOrdersAPI:
    """اختبار API مزامنة الطلبات /api/sync/orders"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """إعداد الاختبار - تسجيل الدخول"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
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
    
    def test_sync_order_basic(self):
        """اختبار مزامنة طلب أساسي"""
        offline_id = f"OFF-BASIC-{uuid.uuid4().hex[:8].upper()}"
        
        order_data = {
            "offline_id": offline_id,
            "items": [
                {"product_id": "prod-1", "name": "برجر", "price": 50, "quantity": 2}
            ],
            "total": 100,
            "subtotal": 100,
            "status": "pending",
            "order_type": "takeaway",
            "payment_method": "cash",
            "is_offline_order": True
        }
        
        response = self.session.post(f"{BASE_URL}/api/sync/orders", json=order_data)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "id" in data
        assert "order_number" in data
        assert isinstance(data.get("order_number"), int)
        print(f"✅ مزامنة طلب أساسي: {offline_id} → #{data.get('order_number')}")
    
    def test_sync_order_with_customer_info(self):
        """اختبار مزامنة طلب مع بيانات العميل"""
        offline_id = f"OFF-CUST-{uuid.uuid4().hex[:8].upper()}"
        
        order_data = {
            "offline_id": offline_id,
            "items": [
                {"product_id": "prod-2", "name": "بيتزا", "price": 80, "quantity": 1}
            ],
            "total": 80,
            "status": "pending",
            "order_type": "delivery",
            "payment_method": "cash",
            "customer_name": "أحمد محمد",
            "customer_phone": "01012345678",
            "delivery_address": "شارع التحرير، القاهرة",
            "is_offline_order": True
        }
        
        response = self.session.post(f"{BASE_URL}/api/sync/orders", json=order_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print(f"✅ مزامنة طلب مع بيانات العميل: {offline_id}")
    
    def test_sync_order_with_discount(self):
        """اختبار مزامنة طلب مع خصم"""
        offline_id = f"OFF-DISC-{uuid.uuid4().hex[:8].upper()}"
        
        order_data = {
            "offline_id": offline_id,
            "items": [
                {"product_id": "prod-3", "name": "شاورما", "price": 40, "quantity": 3}
            ],
            "total": 108,  # 120 - 12 (10% discount)
            "subtotal": 120,
            "discount": 12,
            "discount_type": "percentage",
            "discount_value": 10,
            "status": "delivered",
            "order_type": "dine_in",
            "payment_method": "card",
            "is_offline_order": True
        }
        
        response = self.session.post(f"{BASE_URL}/api/sync/orders", json=order_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print(f"✅ مزامنة طلب مع خصم: {offline_id}")
    
    def test_sync_duplicate_order_same_offline_id(self):
        """اختبار عدم تكرار الطلب عند المزامنة بنفس offline_id"""
        offline_id = f"OFF-DUP-{uuid.uuid4().hex[:8].upper()}"
        
        order_data = {
            "offline_id": offline_id,
            "items": [{"product_id": "p1", "name": "منتج", "price": 25, "quantity": 1}],
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
        first_id = data1.get("id")
        first_order_number = data1.get("order_number")
        
        # المزامنة الثانية (نفس offline_id)
        response2 = self.session.post(f"{BASE_URL}/api/sync/orders", json=order_data)
        assert response2.status_code == 200
        data2 = response2.json()
        
        # يجب أن يرجع نفس الطلب
        assert data2.get("id") == first_id, "يجب أن يرجع نفس ID الطلب"
        assert data2.get("order_number") == first_order_number, "يجب أن يرجع نفس رقم الطلب"
        print(f"✅ التحقق من عدم تكرار الطلب: {offline_id} (ID: {first_id})")
    
    def test_sync_order_dine_in_with_table(self):
        """اختبار مزامنة طلب داخلي مع طاولة"""
        # جلب طاولة متاحة
        tables_response = self.session.get(f"{BASE_URL}/api/tables")
        if tables_response.status_code != 200 or not tables_response.json():
            pytest.skip("لا توجد طاولات")
        
        tables = tables_response.json()
        table_id = tables[0].get("id")
        
        offline_id = f"OFF-TABLE-{uuid.uuid4().hex[:8].upper()}"
        
        order_data = {
            "offline_id": offline_id,
            "items": [{"product_id": "p1", "name": "طبق", "price": 60, "quantity": 2}],
            "total": 120,
            "status": "pending",
            "order_type": "dine_in",
            "table_id": table_id,
            "payment_method": "pending",
            "is_offline_order": True
        }
        
        response = self.session.post(f"{BASE_URL}/api/sync/orders", json=order_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print(f"✅ مزامنة طلب داخلي مع طاولة: {offline_id}")
    
    def test_sync_order_unauthorized(self):
        """اختبار رفض المزامنة بدون توكن"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        order_data = {
            "offline_id": "UNAUTH-TEST",
            "items": [{"product_id": "p1", "name": "منتج", "price": 10, "quantity": 1}],
            "total": 10,
            "status": "pending",
            "order_type": "takeaway"
        }
        
        response = session.post(f"{BASE_URL}/api/sync/orders", json=order_data)
        
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✅ التحقق من رفض المزامنة بدون توكن")


class TestSyncCustomersAPI:
    """اختبار API مزامنة العملاء /api/sync/customers"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
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
    
    def test_sync_customer_basic(self):
        """اختبار مزامنة عميل أساسي"""
        customer_data = {
            "name": f"عميل اختبار {uuid.uuid4().hex[:6]}",
            "phone": f"010{uuid.uuid4().hex[:8]}"
        }
        
        response = self.session.post(f"{BASE_URL}/api/sync/customers", json=customer_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "id" in data
        print(f"✅ مزامنة عميل: {customer_data['name']}")
    
    def test_sync_customer_full_info(self):
        """اختبار مزامنة عميل مع كل البيانات"""
        customer_data = {
            "name": f"عميل كامل {uuid.uuid4().hex[:6]}",
            "phone": f"011{uuid.uuid4().hex[:8]}",
            "email": f"customer_{uuid.uuid4().hex[:6]}@test.com",
            "address": "شارع الملك فيصل، الجيزة",
            "notes": "عميل VIP"
        }
        
        response = self.session.post(f"{BASE_URL}/api/sync/customers", json=customer_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print(f"✅ مزامنة عميل كامل: {customer_data['name']}")
    
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
        assert data1.get("id") == data2.get("id"), "يجب أن يرجع نفس العميل"
        print(f"✅ التحقق من عدم تكرار العميل: {phone}")


class TestSyncTablesAPI:
    """اختبار API مزامنة الطاولات /api/sync/tables"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
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
    
    def test_sync_table_status_update(self):
        """اختبار تحديث حالة طاولة"""
        # جلب الطاولات
        tables_response = self.session.get(f"{BASE_URL}/api/tables")
        
        if tables_response.status_code != 200 or not tables_response.json():
            pytest.skip("لا توجد طاولات")
        
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
        print(f"✅ تحديث حالة الطاولة: {table_id}")
    
    def test_sync_table_with_order(self):
        """اختبار ربط طاولة بطلب"""
        tables_response = self.session.get(f"{BASE_URL}/api/tables")
        
        if tables_response.status_code != 200 or not tables_response.json():
            pytest.skip("لا توجد طاولات")
        
        tables = tables_response.json()
        table_id = tables[0].get("id")
        
        update_data = {
            "id": table_id,
            "status": "occupied",
            "current_order_id": f"order-{uuid.uuid4().hex[:8]}"
        }
        
        response = self.session.post(f"{BASE_URL}/api/sync/tables", json=update_data)
        
        assert response.status_code == 200
        print(f"✅ ربط طاولة بطلب: {table_id}")
    
    def test_sync_table_not_found(self):
        """اختبار تحديث طاولة غير موجودة"""
        update_data = {
            "id": "non-existent-table-12345",
            "status": "occupied"
        }
        
        response = self.session.post(f"{BASE_URL}/api/sync/tables", json=update_data)
        
        assert response.status_code == 404
        print("✅ التحقق من خطأ الطاولة غير الموجودة")


class TestSyncAttendanceAPI:
    """اختبار API مزامنة الحضور /api/sync/attendance"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
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
            pytest.skip("فشل تسجيل الدخول")
    
    def test_sync_attendance_check_in(self):
        """اختبار مزامنة تسجيل حضور"""
        offline_id = f"ATT-IN-{uuid.uuid4().hex[:8].upper()}"
        today = datetime.now().strftime("%Y-%m-%d")
        
        attendance_data = {
            "offline_id": offline_id,
            "employee_id": self.user.get("id", "emp-test"),
            "date": today,
            "check_in": "08:30",
            "status": "present",
            "notes": "حضور صباحي"
        }
        
        response = self.session.post(f"{BASE_URL}/api/sync/attendance", json=attendance_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print(f"✅ مزامنة تسجيل حضور: {offline_id}")
    
    def test_sync_attendance_check_out(self):
        """اختبار مزامنة تسجيل انصراف"""
        offline_id = f"ATT-OUT-{uuid.uuid4().hex[:8].upper()}"
        today = datetime.now().strftime("%Y-%m-%d")
        
        attendance_data = {
            "offline_id": offline_id,
            "employee_id": self.user.get("id", "emp-test"),
            "date": today,
            "check_in": "09:00",
            "check_out": "17:00",
            "status": "present"
        }
        
        response = self.session.post(f"{BASE_URL}/api/sync/attendance", json=attendance_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print(f"✅ مزامنة تسجيل انصراف: {offline_id}")
    
    def test_sync_attendance_update_existing(self):
        """اختبار تحديث سجل حضور موجود"""
        employee_id = self.user.get("id", "emp-test")
        # استخدام تاريخ مختلف لتجنب التعارض
        test_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
        
        # إنشاء سجل أولي
        attendance_data = {
            "offline_id": f"ATT-UPD-{uuid.uuid4().hex[:6].upper()}",
            "employee_id": employee_id,
            "date": test_date,
            "check_in": "09:00",
            "status": "present"
        }
        
        response1 = self.session.post(f"{BASE_URL}/api/sync/attendance", json=attendance_data)
        assert response1.status_code == 200
        
        # تحديث بإضافة وقت الانصراف
        attendance_data["check_out"] = "18:00"
        attendance_data["offline_id"] = f"ATT-UPD2-{uuid.uuid4().hex[:6].upper()}"
        
        response2 = self.session.post(f"{BASE_URL}/api/sync/attendance", json=attendance_data)
        assert response2.status_code == 200
        print(f"✅ تحديث سجل حضور موجود: {employee_id}")


class TestSyncInventoryAPI:
    """اختبار API مزامنة المخزون /api/sync/inventory"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
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
    
    def test_sync_inventory_add(self):
        """اختبار مزامنة إضافة مخزون"""
        offline_id = f"INV-ADD-{uuid.uuid4().hex[:8].upper()}"
        
        transaction_data = {
            "offline_id": offline_id,
            "item_id": f"item-{uuid.uuid4().hex[:6]}",
            "item_name": "طماطم",
            "transaction_type": "add",
            "quantity": 50,
            "notes": "توريد جديد"
        }
        
        response = self.session.post(f"{BASE_URL}/api/sync/inventory", json=transaction_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print(f"✅ مزامنة إضافة مخزون: {offline_id}")
    
    def test_sync_inventory_remove(self):
        """اختبار مزامنة سحب مخزون"""
        offline_id = f"INV-REM-{uuid.uuid4().hex[:8].upper()}"
        
        transaction_data = {
            "offline_id": offline_id,
            "item_id": f"item-{uuid.uuid4().hex[:6]}",
            "item_name": "بصل",
            "transaction_type": "remove",
            "quantity": 10,
            "notes": "استخدام في المطبخ"
        }
        
        response = self.session.post(f"{BASE_URL}/api/sync/inventory", json=transaction_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print(f"✅ مزامنة سحب مخزون: {offline_id}")
    
    def test_sync_inventory_adjust(self):
        """اختبار مزامنة تعديل مخزون"""
        offline_id = f"INV-ADJ-{uuid.uuid4().hex[:8].upper()}"
        
        transaction_data = {
            "offline_id": offline_id,
            "item_id": f"item-{uuid.uuid4().hex[:6]}",
            "item_name": "زيت",
            "transaction_type": "adjust",
            "quantity": 25,
            "notes": "جرد شهري"
        }
        
        response = self.session.post(f"{BASE_URL}/api/sync/inventory", json=transaction_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print(f"✅ مزامنة تعديل مخزون: {offline_id}")
    
    def test_sync_inventory_duplicate(self):
        """اختبار عدم تكرار حركة المخزون"""
        offline_id = f"INV-DUP-{uuid.uuid4().hex[:8].upper()}"
        
        transaction_data = {
            "offline_id": offline_id,
            "item_id": "item-dup-test",
            "transaction_type": "add",
            "quantity": 5
        }
        
        # المزامنة الأولى
        response1 = self.session.post(f"{BASE_URL}/api/sync/inventory", json=transaction_data)
        assert response1.status_code == 200
        data1 = response1.json()
        
        # المزامنة الثانية
        response2 = self.session.post(f"{BASE_URL}/api/sync/inventory", json=transaction_data)
        assert response2.status_code == 200
        data2 = response2.json()
        
        # يجب أن يرجع نفس الـ ID أو رسالة موجود مسبقاً
        assert data1.get("id") == data2.get("id") or "موجودة مسبقاً" in data2.get("message", "")
        print(f"✅ التحقق من عدم تكرار حركة المخزون: {offline_id}")


class TestBatchSyncAPI:
    """اختبار API المزامنة الدفعية /api/sync/batch"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
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
    
    def test_batch_sync_orders_only(self):
        """اختبار مزامنة دفعية للطلبات فقط"""
        batch_data = {
            "orders": [
                {
                    "offline_id": f"BATCH-O1-{uuid.uuid4().hex[:6].upper()}",
                    "items": [{"product_id": "p1", "name": "منتج 1", "price": 30, "quantity": 1}],
                    "total": 30,
                    "status": "delivered",
                    "order_type": "takeaway",
                    "payment_method": "cash"
                },
                {
                    "offline_id": f"BATCH-O2-{uuid.uuid4().hex[:6].upper()}",
                    "items": [{"product_id": "p2", "name": "منتج 2", "price": 45, "quantity": 2}],
                    "total": 90,
                    "status": "delivered",
                    "order_type": "takeaway",
                    "payment_method": "card"
                }
            ],
            "customers": []
        }
        
        response = self.session.post(f"{BASE_URL}/api/sync/batch", json=batch_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "orders" in data
        assert data["orders"]["synced"] == 2
        print(f"✅ مزامنة دفعية للطلبات: {data['orders']['synced']} طلب")
    
    def test_batch_sync_customers_only(self):
        """اختبار مزامنة دفعية للعملاء فقط"""
        batch_data = {
            "orders": [],
            "customers": [
                {
                    "name": f"عميل دفعة 1 {uuid.uuid4().hex[:4]}",
                    "phone": f"015{uuid.uuid4().hex[:8]}"
                },
                {
                    "name": f"عميل دفعة 2 {uuid.uuid4().hex[:4]}",
                    "phone": f"016{uuid.uuid4().hex[:8]}"
                }
            ]
        }
        
        response = self.session.post(f"{BASE_URL}/api/sync/batch", json=batch_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "customers" in data
        assert data["customers"]["synced"] == 2
        print(f"✅ مزامنة دفعية للعملاء: {data['customers']['synced']} عميل")
    
    def test_batch_sync_mixed(self):
        """اختبار مزامنة دفعية مختلطة"""
        batch_data = {
            "orders": [
                {
                    "offline_id": f"BATCH-MIX-{uuid.uuid4().hex[:6].upper()}",
                    "items": [{"product_id": "p1", "name": "منتج", "price": 50, "quantity": 1}],
                    "total": 50,
                    "status": "delivered",
                    "order_type": "takeaway",
                    "payment_method": "cash"
                }
            ],
            "customers": [
                {
                    "name": f"عميل مختلط {uuid.uuid4().hex[:4]}",
                    "phone": f"017{uuid.uuid4().hex[:8]}"
                }
            ]
        }
        
        response = self.session.post(f"{BASE_URL}/api/sync/batch", json=batch_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["orders"]["synced"] >= 1
        assert data["customers"]["synced"] >= 1
        print(f"✅ مزامنة دفعية مختلطة: طلبات={data['orders']['synced']}, عملاء={data['customers']['synced']}")
    
    def test_batch_sync_empty(self):
        """اختبار مزامنة دفعية فارغة"""
        batch_data = {
            "orders": [],
            "customers": []
        }
        
        response = self.session.post(f"{BASE_URL}/api/sync/batch", json=batch_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["orders"]["synced"] == 0
        assert data["customers"]["synced"] == 0
        print("✅ مزامنة دفعية فارغة")


class TestSyncStatusAPI:
    """اختبار API حالة المزامنة /api/sync/status"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
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
    
    def test_get_sync_status(self):
        """اختبار الحصول على حالة المزامنة"""
        response = self.session.get(f"{BASE_URL}/api/sync/status")
        
        assert response.status_code == 200
        data = response.json()
        assert "server_time" in data
        assert "offline_orders_today" in data
        assert "total_orders_today" in data
        print(f"✅ حالة المزامنة: {data}")
    
    def test_sync_status_structure(self):
        """اختبار هيكل استجابة حالة المزامنة"""
        response = self.session.get(f"{BASE_URL}/api/sync/status")
        
        assert response.status_code == 200
        data = response.json()
        
        # التحقق من الحقول المطلوبة
        assert isinstance(data.get("server_time"), str)
        assert isinstance(data.get("offline_orders_today"), int)
        assert isinstance(data.get("total_orders_today"), int)
        print("✅ هيكل حالة المزامنة صحيح")


class TestOrderStatusUpdates:
    """اختبار تحديث حالة الطلبات"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
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
    
    def test_sync_order_then_update_status(self):
        """اختبار مزامنة طلب ثم تحديث حالته"""
        offline_id = f"OFF-STATUS-{uuid.uuid4().hex[:8].upper()}"
        
        # إنشاء طلب
        order_data = {
            "offline_id": offline_id,
            "items": [{"product_id": "p1", "name": "منتج", "price": 40, "quantity": 1}],
            "total": 40,
            "status": "pending",
            "order_type": "takeaway",
            "payment_method": "cash",
            "is_offline_order": True
        }
        
        response = self.session.post(f"{BASE_URL}/api/sync/orders", json=order_data)
        assert response.status_code == 200
        data = response.json()
        order_id = data.get("id")
        
        # تحديث الحالة إلى preparing
        status_response = self.session.put(f"{BASE_URL}/api/orders/{order_id}/status?status=preparing")
        assert status_response.status_code == 200
        
        # تحديث الحالة إلى ready
        status_response = self.session.put(f"{BASE_URL}/api/orders/{order_id}/status?status=ready")
        assert status_response.status_code == 200
        
        # تحديث الحالة إلى delivered
        status_response = self.session.put(f"{BASE_URL}/api/orders/{order_id}/status?status=delivered")
        assert status_response.status_code == 200
        
        print(f"✅ تحديث حالة الطلب: {offline_id} (pending → preparing → ready → delivered)")


class TestCoreDataAPIs:
    """اختبار APIs البيانات الأساسية للتخزين المحلي"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
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
    
    def test_get_categories_for_offline(self):
        """اختبار جلب التصنيفات للتخزين المحلي"""
        response = self.session.get(f"{BASE_URL}/api/categories")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            category = data[0]
            assert "id" in category
            assert "name" in category
        
        print(f"✅ التصنيفات: {len(data)} تصنيف")
    
    def test_get_products_for_offline(self):
        """اختبار جلب المنتجات للتخزين المحلي"""
        response = self.session.get(f"{BASE_URL}/api/products")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            product = data[0]
            assert "id" in product
            assert "name" in product
            assert "price" in product
        
        print(f"✅ المنتجات: {len(data)} منتج")
    
    def test_get_tables_for_offline(self):
        """اختبار جلب الطاولات للتخزين المحلي"""
        response = self.session.get(f"{BASE_URL}/api/tables")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            table = data[0]
            assert "id" in table
            assert "number" in table
        
        print(f"✅ الطاولات: {len(data)} طاولة")
    
    def test_get_branches_for_offline(self):
        """اختبار جلب الفروع للتخزين المحلي"""
        response = self.session.get(f"{BASE_URL}/api/branches")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            branch = data[0]
            assert "id" in branch
            assert "name" in branch
        
        print(f"✅ الفروع: {len(data)} فرع")
    
    def test_get_customers_for_offline(self):
        """اختبار جلب العملاء للتخزين المحلي"""
        response = self.session.get(f"{BASE_URL}/api/customers")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ العملاء: {len(data)} عميل")
    
    def test_get_inventory_for_offline(self):
        """اختبار جلب المخزون للتخزين المحلي"""
        response = self.session.get(f"{BASE_URL}/api/inventory")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ المخزون: {len(data)} عنصر")
    
    def test_get_employees_for_offline(self):
        """اختبار جلب الموظفين للتخزين المحلي"""
        response = self.session.get(f"{BASE_URL}/api/employees")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ الموظفين: {len(data)} موظف")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
