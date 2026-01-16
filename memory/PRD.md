# Maestro EGP - PRD (Product Requirements Document)

## Original Problem Statement
نظام شامل لإدارة المطاعم والكافيهات باسم "Maestro EGP" مع دعم Multi-tenant، تتبع السائقين، نظام كول سنتر، إدارة الموارد البشرية، وتحويلات المخزون.

---

## ✅ All Completed Features (Updated Jan 16, 2026)

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
- [x] خلفيات متحركة قابلة للتخصيص (6 خلفيات)
- [x] 5 أنواع حركات (fade, zoom, kenburns, slide, parallax)
- [x] تحكم كامل من Super Admin
- [x] رفع خلفيات من الجهاز

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
- [x] كشوفات الرواتب + صفحة طباعة

### Warehouse System
- [x] تحويلات المخزون
- [x] طلبات الشراء

### PWA Enhancement
- [x] Service Worker v3 محسّن
- [x] manifest-admin.json للوحة الإدارة
- [x] مكون PWAInstallButton
- [x] تعليمات التثبيت لجميع الأجهزة

### Biometric Device Integration
- [x] pyzk مثبت للاتصال بأجهزة ZKTeco
- [x] واجهة API كاملة للأجهزة
- [x] واجهة مستخدم في HR
- [x] دعم Push SDK

### Loyalty Program
- [x] نظام نقاط الولاء الكامل
- [x] 4 مستويات (برونزي، فضي، ذهبي، بلاتيني)
- [x] كسب واستبدال النقاط

### Recipes & Raw Materials
- [x] إدارة المواد الخام
- [x] إنشاء وصفات للمنتجات
- [x] حساب التكلفة التلقائي

### Coupons & Promotions System
- [x] نظام الكوبونات الكامل
- [x] نظام العروض الترويجية
- [x] واجهة مستخدم كاملة `/coupons`

### 🆕 Background & Logo Upload System (Jan 16, 2026)
- [x] **رفع الخلفيات من الجهاز**: خيار جديد لرفع الصور مباشرة
- [x] **معالجة تلقائية للصور**: تحويل جميع الصيغ إلى JPEG بحجم مناسب
- [x] **دعم صيغ متعددة**: JPEG, PNG, GIF, WEBP, HEIC, BMP, TIFF
- [x] **6 خلفيات متاحة** للنظام

### 🆕 Tenant Identity Management (Jan 16, 2026)
- [x] **شعار المطعم**: رفع شعار مخصص لكل عميل
- [x] **اسم المطعم (عربي/إنجليزي)**: حقول جديدة
- [x] **تحكم من المالك**: يتحكم Super Admin فقط

### 🆕 Dashboard Reorder Feature (Jan 16, 2026)
- [x] **ميزة السحب والإفلات**: اضغط مطولاً لإعادة ترتيب الأيقونات
- [x] **حفظ الترتيب**: يحفظ في localStorage لكل مستخدم
- [x] **تصميم جديد**: أيقونات بتدرجات لونية جميلة
- [x] **شبكة محسنة**: 3/4/6 أعمدة حسب حجم الشاشة

### 🆕 New Pages (Jan 16, 2026)
- [x] **الحجوزات** (`/reservations`): إدارة حجوزات الطاولات
  - إنشاء حجز جديد
  - تأكيد/إلغاء الحجوزات
  - فلترة بالتاريخ والحالة
  - إحصائيات يومية
  
- [x] **التقييمات** (`/reviews`): نظام تقييم العملاء
  - عرض التقييمات مع النجوم
  - تقييم مفصل (طعام، خدمة، توصيل)
  - إضافة ردود الإدارة
  - إحصائيات وتوزيع التقييمات
  
- [x] **التقارير الذكية** (`/smart-reports`): تحليلات متقدمة
  - إحصائيات المبيعات والطلبات
  - رؤى ذكية (Insights)
  - المنتجات الأكثر مبيعاً مع نسب النمو
  - المبيعات حسب الساعة
  - مقارنات الأداء (يومي/أسبوعي/شهري)
  - توزيع أنواع الطلبات (Pie Chart)

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

## 📡 API Endpoints

### File Upload
- `POST /api/upload/background` - رفع خلفية من الجهاز
- `POST /api/upload/logo` - رفع شعار للعميل

### Reservations
- `GET /api/reservations` - جلب الحجوزات
- `POST /api/reservations` - إنشاء حجز
- `PUT /api/reservations/{id}/status` - تحديث حالة الحجز
- `DELETE /api/reservations/{id}` - حذف حجز

### Reviews
- `GET /api/reviews` - جلب التقييمات
- `POST /api/reviews/{id}/reply` - إضافة رد

### Smart Reports
- `GET /api/reports/smart` - جلب التقارير الذكية

---

## 📁 Project Structure

```
/app
├── backend/
│   ├── server.py (6000+ lines - needs refactoring)
│   ├── api/
│   │   ├── biometric.py
│   │   ├── login_backgrounds.py
│   │   └── ... (other modules)
│   └── uploads/
│       ├── backgrounds/
│       └── logos/
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── Dashboard.js (✅ with reorder feature)
│       │   ├── Reservations.js (🆕)
│       │   ├── Reviews.js (🆕)
│       │   ├── SmartReports.js (🆕)
│       │   └── ...
│       └── App.js
└── memory/
    └── PRD.md
```

---

## 🛠️ Tech Stack
- **Frontend**: React + Tailwind CSS + Shadcn/UI
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **Maps**: Leaflet / OpenStreetMap
- **Excel**: openpyxl
- **Biometric**: pyzk (ZKTeco)
- **Image Processing**: Pillow (PIL)

---

## 📊 Deployment Status
- ✅ All Core APIs Working
- ✅ Kitchen Display: Working
- ✅ Excel Export: Working
- ✅ Login Backgrounds: Working (6 backgrounds)
- ✅ Driver Map: Working
- ✅ PWA Install Button: Working
- ✅ Loyalty Program: Working
- ✅ Recipes System: Working
- ✅ Coupons & Promotions: Working
- ✅ Background Upload: Working
- ✅ Logo Upload: Working
- ✅ Dashboard Reorder: Working
- ✅ Reservations: Working
- ✅ Reviews: Working
- ✅ Smart Reports: Working
- ✅ Ready for Production

---

## 🔄 Needs Configuration
1. **PWA**: يحتاج اختبار على أجهزة فعلية
2. **Biometric**: يحتاج جهاز ZKTeco للاتصال الفعلي
3. **Push Notifications**: يحتاج إعداد Firebase project

---

## 📋 Backlog / Future Enhancements

### P0 - High Priority
- [ ] إعادة هيكلة server.py (ملف كبير جداً)
- [ ] نظام طلبات بين الفروع والمخزن
- [ ] نظام متكامل للمشتريات
- [ ] تنبيهات تلقائية عند انخفاض المخزون

### P1 - Medium Priority
- [ ] تحسين خريطة السائقين الحية
- [ ] إشعارات Push (Firebase) للسائقين
- [ ] تكامل أجهزة البصمة ZKTeco (كتابة منطق الاتصال)
- [ ] الخلفيات المتجاوبة (وضع مظلم/فاتح)

### P2 - Low Priority
- [ ] أزرار رجوع موحدة في جميع الصفحات
- [ ] تقسيم ملفات SuperAdmin.js و HR.js
