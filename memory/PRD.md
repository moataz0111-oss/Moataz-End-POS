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
- أصوات النقر على الأزرار
- واجهة عربية RTL

### الإضافات المطلوبة من المستخدم:
- حفظ الطلب على الطاولة أو الديلفري باسم السائق أو التطبيق
- زر حفظ وإرسال للمطبخ قبل الدفع
- الطلبات تظهر بالمبيعات قبل الإغلاق
- ترحيل الطلبات الآجلة لشركات التوصيل

---

## User Personas

### 1. مدير النظام (Admin)
- إدارة كاملة للنظام
- إضافة وتعديل المستخدمين والفروع
- عرض جميع التقارير
- إعدادات النظام

### 2. مدير الفرع (Manager)
- إدارة موظفي فرعه
- عرض تقارير الفرع
- إدارة المخزون والمنتجات

### 3. المشرف (Supervisor)
- مراقبة العمليات
- إدارة المخزون
- عرض التقارير

### 4. الكاشير (Cashier)
- استخدام نقاط البيع
- إنشاء الطلبات
- إغلاق الشفت

---

## Core Requirements

### 1. Authentication & Authorization
- [x] تسجيل دخول JWT
- [x] صلاحيات حسب الدور
- [x] صلاحيات حسب الفرع

### 2. Branch Management
- [x] إضافة/تعديل/حذف الفروع
- [x] تعيين المستخدمين للفروع

### 3. POS System
- [x] شاشة نقاط البيع الرئيسية
- [x] الفئات والمنتجات مع الصور
- [x] السلة مع تعديل الكميات
- [x] أنواع الطلبات (داخلي، سفري، توصيل)
- [x] اختيار الطاولة للطلبات الداخلية
- [x] طرق الدفع (نقدي، بطاقة، آجل)
- [x] زر المطبخ لحفظ الطلب قبل الدفع
- [x] أصوات النقر

### 4. Table Management
- [x] عرض الطاولات بالأقسام
- [x] حالة الطاولة (متاحة، مشغولة، محجوزة)
- [x] إضافة طاولات جديدة

### 5. Order Management
- [x] قائمة الطلبات مع فلاتر
- [x] تحديث حالة الطلب
- [x] تفاصيل الطلب
- [x] الطلبات المعلقة للمطبخ

### 6. Inventory Management
- [x] المواد الخام
- [x] المنتجات النهائية
- [x] إضافة/سحب الكميات
- [x] تنبيه نقص المخزون

### 7. Delivery Management
- [x] إدارة السائقين
- [x] تعيين السائق للطلب
- [x] تتبع حالة التوصيل
- [x] تكامل تطبيقات التوصيل

### 8. Shift Management
- [x] فتح/إغلاق الشفت
- [x] حساب الفرق النقدي
- [x] تقرير إغلاق الصندوق

### 9. Reports
- [x] تقرير المبيعات اليومية
- [x] تقرير المخزون
- [x] تقرير حسابات شركات التوصيل الآجلة

### 10. Settings
- [x] إدارة المستخدمين
- [x] إدارة الفروع
- [x] إدارة الطابعات
- [x] إشعارات البريد الإلكتروني
- [x] المظهر (فاتح/داكن/تلقائي)

---

## What's Been Implemented

### Date: 2025-01-12

#### Backend (FastAPI + MongoDB)
- ✅ نظام المصادقة JWT
- ✅ CRUD للمستخدمين والفروع
- ✅ CRUD للفئات والمنتجات
- ✅ CRUD للمخزون مع transactions
- ✅ CRUD للطاولات
- ✅ نظام الطلبات الكامل مع الحالات
- ✅ إدارة الشفتات
- ✅ إدارة السائقين
- ✅ التقارير (مبيعات، مخزون، آجل)
- ✅ إعدادات النظام
- ✅ Seed data للبيانات الأولية

#### Frontend (React + Tailwind + Shadcn)
- ✅ صفحة تسجيل الدخول
- ✅ لوحة التحكم الرئيسية
- ✅ شاشة نقاط البيع (POS) كاملة
- ✅ صفحة الطاولات
- ✅ صفحة الطلبات
- ✅ صفحة المخزون
- ✅ صفحة التوصيل والسائقين
- ✅ صفحة الإعدادات
- ✅ الوضع الليلي/النهاري التلقائي
- ✅ أصوات النقر
- ✅ واجهة عربية RTL

---

## Prioritized Backlog

### P0 - Critical (Must Have)
- [x] Authentication
- [x] POS Core
- [x] Orders
- [x] Tables

### P1 - High Priority
- [x] Inventory Management
- [x] Shift Management
- [x] Delivery Tracking
- [ ] Receipt Printing (Hardware Integration)

### P2 - Medium Priority
- [x] Email Reports (SendGrid configured)
- [ ] Stripe Payment Integration
- [ ] Real-time Kitchen Display
- [ ] Customer Loyalty Program

### P3 - Low Priority
- [ ] Mobile App
- [ ] Analytics Dashboard
- [ ] Multi-language Support
- [ ] API for Third-party Integration

---

## Next Action Items

1. **إضافة طباعة الفواتير** - تكامل مع طابعات الإيصالات
2. **تفعيل SendGrid** - إضافة API Key لإرسال التقارير
3. **Stripe Integration** - تفعيل الدفع بالبطاقة
4. **شاشة المطبخ** - عرض الطلبات للتحضير في الوقت الحقيقي
5. **تقارير متقدمة** - رسوم بيانية للمبيعات والأداء

---

## Technical Stack

- **Backend:** FastAPI (Python)
- **Database:** MongoDB
- **Frontend:** React 18 + Tailwind CSS + Shadcn/UI
- **Authentication:** JWT
- **Email:** SendGrid (ready for API key)
- **Payment:** Stripe (ready for integration)

---

## Credentials

### Default Admin
- Email: admin@maestroegp.com
- Password: admin123

### Default Cashier
- Email: cashier@maestroegp.com
- Password: cashier123
