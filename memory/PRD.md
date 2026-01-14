# Maestro EGP - PRD (Product Requirements Document)

## Original Problem Statement
نظام شامل لإدارة المطاعم والكافيهات باسم "Maestro EGP" مع دعم Multi-tenant، تتبع السائقين، نظام كول سنتر، إدارة الموارد البشرية، وتحويلات المخزون.

---

## ✅ Completed Features (Jan 15, 2026)

### Core System
- [x] نظام المصادقة (JWT)
- [x] إدارة المنتجات والتصنيفات
- [x] إدارة الطلبات (محلي، سفري، توصيل)
- [x] إدارة الطاولات
- [x] إدارة الورديات والصندوق
- [x] إدارة السائقين والتوصيل
- [x] إشعارات صوتية

### Multi-tenant System
- [x] لوحة تحكم Super Admin
- [x] فصل البيانات بين العملاء
- [x] نظام صلاحيات الميزات (Feature Flags)
- [x] تعديل بيانات العملاء + بريد ترحيبي

### Login Page 
- [x] خلفيات متحركة قابلة للتخصيص
- [x] 5 أنواع حركات
- [x] تحكم كامل من Super Admin

### Kitchen Display System (KDS)
- [x] شاشة المطبخ KDS كاملة
- [x] تتبع الطلبات والأوقات

### Excel Export
- [x] تصدير تقارير المبيعات
- [x] تصدير تقارير المنتجات والمصاريف

### Call Center
- [x] Webhook للمكالمات
- [x] إشعار منبثق + سجل مكالمات

### HR System
- [x] إدارة الموظفين (CRUD)
- [x] تسجيل الحضور والانصراف
- [x] نظام السلف والخصومات
- [x] كشوفات الرواتب

### Warehouse System
- [x] تحويلات المخزون
- [x] طلبات الشراء

### 🆕 PWA Enhancement (Jan 15, 2026)
- [x] Service Worker v3 محسّن
- [x] manifest-admin.json للوحة الإدارة
- [x] مكون PWAInstallButton
- [x] تعليمات التثبيت لجميع الأجهزة

### 🆕 Biometric Device Integration (Jan 15, 2026)
- [x] pyzk مثبت للاتصال بأجهزة ZKTeco
- [x] واجهة API كاملة للأجهزة
- [x] واجهة مستخدم في HR
- [x] دعم Push SDK

### 🆕 Loyalty Program (Jan 15, 2026)
- [x] نظام نقاط الولاء الكامل
- [x] 4 مستويات (برونزي، فضي، ذهبي، بلاتيني)
- [x] كسب واستبدال النقاط
- [x] نقاط ترحيب وإحالة وعيد ميلاد
- [x] مضاعفات النقاط حسب المستوى
- [x] واجهة مستخدم كاملة `/loyalty`

### 🆕 Recipes & Raw Materials (Jan 15, 2026)
- [x] إدارة المواد الخام (11 تصنيف)
- [x] إنشاء وصفات للمنتجات
- [x] حساب التكلفة التلقائي
- [x] حساب هامش الربح
- [x] تنبيهات المخزون المنخفض
- [x] واجهة مستخدم كاملة `/recipes`

### 🆕 Invoice Customization & Printing (Jan 15, 2026)
- [x] قوالب فواتير مخصصة
- [x] دعم طابعات حرارية (58mm/80mm)
- [x] إعدادات الشعار والعنوان والتذييل
- [x] معاينة الفاتورة
- [x] إدارة الطابعات (Network/USB/Bluetooth)
- [x] واجهة مستخدم كاملة `/invoices`

### 🆕 Push Notifications Infrastructure (Jan 15, 2026)
- [x] واجهة API لتسجيل FCM tokens
- [x] إرسال إشعارات (user/role/branch/all)
- [x] قوالب إشعارات جاهزة
- [x] سجل الإشعارات
- [x] firebase-admin مثبت

---

## 🔄 Needs Testing/Configuration

### PWA
- [ ] يحتاج اختبار من المستخدم على جهاز فعلي (iOS/Android/Desktop)

### Biometric Devices
- [ ] يحتاج اتصال فعلي بجهاز ZKTeco لاختبار المزامنة

### Push Notifications
- [ ] يحتاج تكوين Firebase project وإضافة المفاتيح

---

## 📋 Future Tasks (P2)
- [ ] إشعارات Push حية للسائقين (يحتاج Firebase setup)
- [ ] ربط السلف والخصومات بالرواتب تلقائياً
- [ ] كشوف رواتب مطبوعة
- [ ] إكمال إعادة هيكلة server.py

---

## 🔑 Test Credentials

### Super Admin
- URL: `/super-admin`
- Email: `owner@maestroegp.com`
- Password: `owner123`
- Secret Key: `271018`

### Main System Admin
- URL: `/login`
- Email: `admin@maestroegp.com`
- Password: `admin123`

---

## 📡 New API Endpoints (Jan 15, 2026)

### Loyalty Program
- `GET /api/loyalty/settings` - إعدادات الولاء
- `PUT /api/loyalty/settings` - تحديث الإعدادات
- `GET /api/loyalty/members` - قائمة الأعضاء
- `POST /api/loyalty/members` - إضافة عضو
- `POST /api/loyalty/earn` - كسب نقاط
- `POST /api/loyalty/redeem` - استبدال نقاط
- `GET /api/loyalty/transactions/{member_id}` - سجل المعاملات

### Recipes & Raw Materials
- `GET /api/recipes/categories` - تصنيفات المواد
- `GET /api/recipes/materials` - قائمة المواد الخام
- `POST /api/recipes/materials` - إضافة مادة
- `GET /api/recipes` - قائمة الوصفات
- `POST /api/recipes` - إنشاء وصفة
- `GET /api/recipes/alerts/low-stock` - تنبيهات المخزون

### Invoice & Printing
- `GET /api/invoices/templates` - قوالب الفواتير
- `POST /api/invoices/templates` - إنشاء قالب
- `GET /api/invoices/printers` - قائمة الطابعات
- `POST /api/invoices/printers` - إضافة طابعة
- `POST /api/invoices/print/{order_id}` - طباعة فاتورة

### Push Notifications
- `POST /api/notifications/fcm/register` - تسجيل token
- `POST /api/notifications/send` - إرسال إشعار
- `GET /api/notifications/logs` - سجل الإشعارات

---

## 📁 New Files Created (Jan 15, 2026)

### Backend
- `/app/backend/api/loyalty.py` - نماذج الولاء
- `/app/backend/api/recipes.py` - نماذج الوصفات
- `/app/backend/api/invoices.py` - نماذج الفواتير
- `/app/backend/api/notifications.py` - نماذج الإشعارات

### Frontend
- `/app/frontend/src/pages/Loyalty.js` - صفحة الولاء
- `/app/frontend/src/pages/Recipes.js` - صفحة الوصفات
- `/app/frontend/src/pages/Invoices.js` - صفحة الفواتير
- `/app/frontend/src/components/PWAInstallButton.js`
- `/app/frontend/src/components/BiometricDevices.js`
- `/app/frontend/public/manifest-admin.json`

---

## 🛠️ Tech Stack
- **Frontend**: React + Tailwind CSS + Shadcn/UI
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **Maps**: Leaflet / OpenStreetMap
- **Excel**: openpyxl
- **Biometric**: pyzk (ZKTeco)
- **Push**: firebase-admin

---

## 📊 Deployment Status
- ✅ All Core APIs Working
- ✅ Kitchen Display: Working
- ✅ Excel Export: Working
- ✅ Login Backgrounds: Working
- ✅ Driver Map: Working
- ✅ Biometric Devices UI: Working
- ✅ PWA Install Button: Working
- ✅ Loyalty Program: Working
- ✅ Recipes System: Working
- ✅ Invoice Templates: Working
- ✅ Ready for Production

---

## ⚠️ Notes
1. **PWA**: يحتاج اختبار على أجهزة فعلية
2. **Biometric**: يحتاج جهاز ZKTeco للاتصال الفعلي
3. **Push Notifications**: يحتاج إعداد Firebase project
4. **Refactoring**: server.py أصبح ~6700 سطر - يُفضل التقسيم تدريجياً
