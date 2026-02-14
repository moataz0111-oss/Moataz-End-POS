# نظام إدارة المطاعم - PRD

## المشكلة الأساسية
نظام إدارة مطاعم متكامل يحتاج إلى ترجمة شاملة وكاملة لواجهة المستخدم بين اللغات العربية والإنجليزية والكردية.

## متطلبات المنتج

### P0 - الأولوية الحرجة ✅ تم الإنجاز
1. **الترجمة الشاملة** 
   - يجب ترجمة كل نص مرئي في واجهة المستخدم عند تبديل اللغة
   - تم إصلاح جميع الصفحات المذكورة

### P1 - أولوية عالية ✅ تم الإنجاز
1. **وظائف التقارير**
   - تم استبدال أزرار تصدير Excel/PDF بأزرار طباعة (`window.print`)
   
2. **الأرقام والتواريخ بالإنجليزية** ✅ تم الإنجاز
   - تم تغيير جميع `ar-IQ` إلى `en-US` في 17 ملف

### P2 - أولوية متوسطة (مؤجل)
1. **إعادة هيكلة الكود**
   - تقسيم الملفات الضخمة مثل `server.py`, `SuperAdmin.js`, `Settings.js`

## ما تم إنجازه (15 فبراير 2026)

### Session 3 - إصلاحات إضافية بناءً على ملاحظات المستخدم
- ✅ SuperAdmin: "مميز" → "Premium"
- ✅ Dashboard Alert: "يوجد طلبات معلقة..." → ترجمة كاملة
- ✅ Call Logs: "عميل جديد" → "New Customer" (Backend + Frontend)
- ✅ Call Logs: التواريخ بالإنجليزية (en-US format)
- ✅ Coupons: "واحصل على" → "and get"
- ✅ Smart Reports: "غير معروف" → "Unknown" (Backend)
- ✅ تغيير جميع `ar-IQ` إلى `en-US` في 17 ملف
- ✅ أزرار المكالمات: "رد" → "Answer", "رفض" → "Reject"

### الملفات التي تم تعديلها لتنسيق التاريخ:
- Reports.js, Dashboard.js, Orders.js, HR.js, SystemAdmin.js
- Delivery.js, Ratings.js, WarehouseTransfers.js, PayrollPrint.js
- WarehouseManufacturing.js, InventoryReports.js, Invoices.js
- Settings.js, Loyalty.js, BranchOrders.js, Purchasing.js
- CustomerMenu.js, CallLogs.js

## تقارير الاختبار
- `/app/test_reports/iteration_79.json` - الصفحات الأساسية (100% نجاح)
- `/app/test_reports/iteration_80.json` - صفحة الإعدادات (100% نجاح)
- `/app/test_reports/iteration_81.json` - المشاكل الخمس من ملاحظات المستخدم (95% نجاح)

## بيانات الاختبار
- **Super Admin:** `owner@maestroegp.com` / `owner123` (المفتاح السري: `271018`)
- **Demo User:** `demo@maestroegp.com` / `demo123`

## ملاحظة مهمة
- أسماء المنتجات والفئات هي **بيانات مُدخلة من المستخدم** ولا تُترجم تلقائياً
- البيانات المخزنة مسبقاً في قاعدة البيانات (مثل سجلات المكالمات القديمة) ستظل بالعربية
