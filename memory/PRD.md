# Maestro EGP - PRD (Product Requirements Document)

## Original Problem Statement
بناء نظام شامل للتحكم بالتكاليف ونقاط البيع (Maestro EGP) للمطاعم والكافيهات.

### المتطلبات الأساسية:
- نظام متعدد المستخدمين (Admin, Manager, Supervisor, Cashier)
- إدارة الفروع مع صلاحيات لكل فرع
- إدارة المخازن (مواد خام + منتجات نهائية)
- تتبع المبيعات والكميات بالتفصيل
- إدارة الشفتات مع تقارير تلقائية بالبريد
- دعم متعدد العملات (الدينار العراقي كأساس)
- إدارة الطاولات
- تتبع التوصيل والسائقين
- تكامل مع تطبيقات التوصيل (توترز، طلبات، بالي، عالسريع، طلباتي)
- الوضع الليلي/النهاري التلقائي
- واجهة عربية RTL

---

## What's Been Implemented (as of Jan 12, 2026)

### الميزات الجديدة في هذه الجلسة:

#### 1. نظام الصلاحيات الموسع (26 صلاحية مخصصة)
مجموعات الصلاحيات:
- **المبيعات:** نقاط البيع، إعطاء خصومات، إلغاء الطلبات، الطلبات، تعديل الطلبات، الطاولات
- **المطبخ:** شاشة المطبخ
- **المخزون:** عرض المخزون، تعديل المخزون، نقل المخزون
- **التقارير:** التقارير الأساسية، التقارير المالية، تصدير التقارير
- **المالية:** المصاريف، إضافة مصاريف، المشتريات
- **التوصيل:** التوصيل، السائقين
- **الإعدادات:** المنتجات، تعديل المنتجات، تعديل الأسعار، الفئات
- **الإدارة:** المستخدمين، الفروع، الإعدادات، الورديات، إغلاق الصندوق

#### 2. أقسام المطبخ (Kitchen Sections)
- إنشاء أقسام مطبخ متعددة (المطبخ الساخن، المطبخ البارد، المشروبات، الحلويات)
- ربط كل قسم بطابعة مخصصة
- ربط الفئات بأقسام المطبخ لتوجيه الطلبات تلقائياً
- تعديل وحذف الأقسام

#### 3. تعديل الفروع
- إضافة زر تعديل للفروع
- إمكانية تعديل اسم الفرع، العنوان، الهاتف، البريد
- إمكانية تعطيل الفرع

#### 4. إشعارات صوتية للطلبات الجديدة
- صوت تنبيه عند وصول طلب جديد
- صوت جرس المطبخ عند جاهزية الطلب
- زر تفعيل/تعطيل الصوت
- زر اختبار الصوت

#### 5. تحسينات أخرى
- إزالة بيانات المستخدمين من صفحة تسجيل الدخول
- نافذة تعديل المستخدم تفتح بالبيانات الحالية
- أزرار "تحديد الكل" و "إلغاء التحديد" للصلاحيات

---

### الميزات المنجزة سابقاً:

#### Backend (FastAPI + MongoDB)
- ✅ نظام المصادقة JWT
- ✅ CRUD للمستخدمين مع الصلاحيات والفروع
- ✅ CRUD للفروع (مع تعديل وحذف)
- ✅ CRUD للفئات والمنتجات (مع التكاليف والربح)
- ✅ CRUD للمخزون مع transactions
- ✅ CRUD للطاولات
- ✅ نظام الطلبات الكامل مع الحالات
- ✅ إدارة الشفتات (فتح/إغلاق مع حساب العجز/الفائض)
- ✅ إدارة السائقين
- ✅ إدارة المصاريف اليومية
- ✅ إدارة المشتريات
- ✅ التقارير الشاملة (7 أنواع)
- ✅ إعدادات شركات التوصيل مع نسب الاستقطاع
- ✅ إعدادات الطابعات
- ✅ أقسام المطبخ (جديد)

#### Frontend (React + Tailwind + Shadcn)
- ✅ صفحة تسجيل الدخول (بدون بيانات تجريبية)
- ✅ لوحة التحكم الرئيسية مع 8 إجراءات سريعة
- ✅ شاشة نقاط البيع (POS) كاملة
- ✅ صفحة الطاولات
- ✅ صفحة الطلبات مع إشعارات صوتية
- ✅ صفحة المخزون
- ✅ صفحة التوصيل والسائقين
- ✅ صفحة المصاريف اليومية
- ✅ صفحة التقارير الشاملة (7 تبويبات)
- ✅ صفحة الإعدادات مع 9 تبويبات:
  - المظهر
  - المستخدمين (مع 26 صلاحية مخصصة)
  - الفروع (مع تعديل وحذف)
  - أقسام المطبخ (جديد)
  - الفئات
  - المنتجات
  - الطابعات
  - شركات التوصيل
  - الإشعارات

---

## Prioritized Backlog

### P0 - Critical ✅ COMPLETED
- [x] Authentication
- [x] POS Core
- [x] Orders
- [x] Tables
- [x] User Management with Permissions (26 permissions)
- [x] Categories/Products Management
- [x] Reports (7 types)
- [x] Expenses Management
- [x] Kitchen Sections
- [x] Branch Edit/Delete

### P1 - High Priority
- [x] Inventory Management
- [x] Shift Management
- [x] Delivery Tracking
- [x] Sound Notifications
- [ ] Receipt Printing (Hardware Integration)

### P2 - Medium Priority
- [ ] Email Reports (SendGrid configured)
- [ ] Stripe Payment Integration
- [ ] Real-time Kitchen Display Screen
- [ ] Customer Loyalty Program

---

## Credentials

### Default Admin
- Email: admin@maestroegp.com
- Password: admin123

### Default Cashier
- Email: cashier@maestroegp.com
- Password: cashier123

---

## API Reference - New Endpoints

### Kitchen Sections
- `GET /api/kitchen-sections` - قائمة أقسام المطبخ
- `POST /api/kitchen-sections` - إنشاء قسم
- `PUT /api/kitchen-sections/{id}` - تعديل قسم
- `DELETE /api/kitchen-sections/{id}` - حذف قسم
- `PUT /api/categories/{id}/kitchen-section` - ربط فئة بقسم مطبخ

### Branches (Updated)
- `PUT /api/branches/{id}` - تعديل فرع
- `DELETE /api/branches/{id}` - تعطيل فرع

---

## Test Reports
- `/app/test_reports/iteration_1.json` - Initial build tests
- `/app/test_reports/iteration_2.json` - New features tests (100% pass rate)
