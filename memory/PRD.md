# PRD - نظام إدارة المطاعم والكافيهات (Maestro EGP)

## المشكلة الأصلية
بناء نظام شامل لإدارة المطاعم والكافيهات يدعم:
- إدارة نقاط البيع (POS)
- إدارة الفروع المتعددة
- إدارة الموارد البشرية والرواتب
- إدارة المخزون والمشتريات
- نظام التوصيل وتتبع السائقين
- تقارير وإحصائيات ذكية
- دعم Multi-tenancy (عدة عملاء)

## الجلسة الحالية - 17 يناير 2026 (الإصدار 13)

### ✅ ما تم إنجازه في هذه الجلسة:

#### 1. إصلاح تقرير إغلاق الصندوق (P0) ✅
- **المشكلة:** تقرير إغلاق الصندوق كان يعرض جميع القيم كأصفار
- **السبب:** 
  - ملف `api.js` كان يستخدم `window.location.origin` (localhost:3000) بدلاً من `REACT_APP_BACKEND_URL`
  - الشرط `typeof process !== 'undefined' && process.env && process.env.REACT_APP_BACKEND_URL` كان غير صحيح لأن React يستبدل متغيرات البيئة أثناء البناء
- **الحل:**
  - تعديل `/app/frontend/src/utils/api.js` لاستخدام `process.env.REACT_APP_BACKEND_URL` مباشرة
- **الاختبارات:** تم اختبار GET /api/cash-register/summary و POST /api/cash-register/close - جميع القيم تظهر بشكل صحيح

#### 2. إكمال ميزة تحويل الطلب لسائق آخر (P1) ✅
- **المشكلة:** 
  - بيانات الطلب لا تظهر في نافذة التحويل
  - السائق الجديد لا يُعين له current_order_id
- **الحل:**
  - إضافة `current_order` للـ `DriverResponse` model في server.py
  - إضافة `driver_name` و `driver_phone` للـ `OrderResponse` model
  - إصلاح تحديث `current_order_id` للسائقين عند تحويل الطلب (إزالة من القديم، إضافة للجديد)
  - إصلاح bug: عند إنشاء طلب مع `driver_id`، يتم الآن ملء `driver_name` و `driver_phone`
- **الاختبارات:** 11/11 اختبار ناجح (100%)

#### 3. تحسين التحديث التلقائي لجميع العملاء ✅
- **الملف:** `/app/backend/init_data.py`
- **الإضافات:**
  - إعادة تعيين `current_order_id` للسائقين الذين لديهم طلبات تم تسليمها أو إلغائها
  - فحص الطلبات القديمة التي لا تحتوي على `shift_id`

### 📊 نتائج الاختبارات (Iteration 13)
- **Backend:** 11/11 اختبار ناجح (100%)
  - تسجيل الدخول
  - فتح وردية تلقائياً
  - إنشاء طلب
  - ملخص الصندوق (يعرض قيم صحيحة)
  - إغلاق الصندوق (يرجع تقرير صحيح)
  - تحويل السائق (يحدث كلا السائقين)
  - جلب السائقين مع الطلبات
  - جلب تفاصيل الطلب (يحتوي على driver_name و driver_phone)

## ملفات التغييرات:
- `/app/frontend/src/utils/api.js`: إصلاح تحديد API URL
- `/app/backend/server.py`:
  - إضافة `current_order` للـ `DriverResponse` model
  - إضافة `driver_name` و `driver_phone` للـ `OrderResponse` model
  - إصلاح تحديث `current_order_id` عند تحويل السائق
  - إصلاح ملء `driver_name` و `driver_phone` عند إنشاء طلب
- `/app/backend/init_data.py`: إضافة تحديثات تلقائية للسائقين

## الجلسات السابقة

### الجلسة 12 - 16 يناير 2026
- ✅ إصلاح مشكلة رفع شعار العميل
- ✅ إضافة null checks في filteredTenants

### الجلسة 11 - 16 يناير 2026
- ✅ حل مشكلة النشر وتهيئة قاعدة البيانات
- ✅ إضافة زر تهيئة قاعدة البيانات مع مفتاح سري

### الجلسات السابقة
- ✅ نظام المشتريات والموردين
- ✅ نظام طلبات الفروع
- ✅ صلاحيات الميزات في SuperAdmin (30 ميزة)
- ✅ خلفية Dashboard للعملاء
- ✅ فتح الوردية تلقائياً
- ✅ رفع الشعارات

## المهام المتبقية

### 🔴 أولوية قصوى (P0)
- [ ] إعادة هيكلة `/app/backend/server.py` (8000+ سطر - يحتاج تقسيم)

### 🟡 أولوية عالية (P1)
- [ ] تحسين خريطة السائقين الحية (خط السير)
- [ ] إشعارات Push للسائقين (Firebase)
- [ ] إكمال ميزة السحب والإفلات لترتيب أيقونات Dashboard

### 🟢 أولوية متوسطة (P2)
- [ ] التحقق من وظيفة PWA
- [ ] إكمال تكامل أجهزة البصمة (ZKTeco)
- [ ] بناء نظام ولاء العملاء (Loyalty)
- [ ] بناء نظام إدارة الوصفات
- [ ] إضافة وضع مظلم/فاتح

### 🔵 أولوية منخفضة (P3)
- [ ] إعادة هيكلة مكونات الواجهة الأمامية الكبيرة (Dashboard.js, Delivery.js)

## البنية التقنية

### Backend
```
/app/backend/
├── server.py              # الملف الرئيسي (8000+ سطر)
├── init_data.py           # تهيئة قاعدة البيانات والتحديثات التلقائية
├── api/
│   ├── biometric.py
│   └── login_backgrounds.py
├── uploads/
│   ├── backgrounds/
│   └── logos/
├── tests/
│   └── test_iteration*.py
└── requirements.txt
```

### Frontend
```
/app/frontend/src/
├── utils/
│   └── api.js             # تحديد API URL ديناميكياً
├── pages/
│   ├── Dashboard.js       # لوحة التحكم
│   ├── SuperAdmin.js      # إدارة العملاء
│   ├── Settings.js        # الإعدادات
│   ├── Delivery.js        # التوصيل وإدارة السائقين
│   ├── POS.js             # نقاط البيع
│   ├── Tables.js          # الطاولات
│   └── ...
└── App.js
```

### قاعدة البيانات (MongoDB)
مجموعات رئيسية:
- `users` - المستخدمين
- `orders` - الطلبات (مع driver_id, driver_name, driver_phone)
- `drivers` - السائقين (مع current_order_id, is_available)
- `shifts` - الورديات
- `tenants` - العملاء
- `branches` - الفروع
- `products` - المنتجات

## بيانات الاختبار

### Super Admin
- Email: `owner@maestroegp.com`
- Password: `owner123`
- Secret Key: `271018`
- URL: `/super-admin`

### Admin النظام الرئيسي
- Email: `admin@maestroegp.com`
- Password: `admin123`
- URL: `/login`

### فرع الاختبار
- Branch ID: `d2edb16f-240f-4323-b481-9fb676db9465`

---
آخر تحديث: 17 يناير 2026 - 9:00 PM
نسبة الإنجاز: 96%
