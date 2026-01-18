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

## الجلسة الحالية - 18 يناير 2026 (الإصدار 16)

### ✅ ما تم إنجازه في هذه الجلسة:

#### 1. نظام فلترة الفروع الشامل ✅
- إنشاء `BranchContext.js` - Context عام للفرع المحدد
- إنشاء `BranchSelector.js` - مكون اختيار الفرع في الشريط العلوي
- تحديث `App.js` لإضافة `BranchProvider`
- تحديث `Dashboard.js` لاستخدام `useBranch`
- تحديث `Reports.js` لاستخدام الفلتر العام

#### 2. تحديث جميع نقاط النهاية للتقارير ✅
- `/api/reports/sales` - مبيعات الفرع أو الجميع
- `/api/reports/purchases` - مشتريات الفرع
- `/api/reports/inventory` - مخزون الفرع
- `/api/reports/expenses` - مصاريف الفرع
- `/api/reports/profit-loss` - أرباح وخسائر
- `/api/reports/delivery-credits` - عمولات التوصيل
- `/api/reports/products` - منتجات الفرع
- `/api/reports/cancellations` - إلغاءات
- `/api/reports/discounts` - خصومات
- `/api/reports/credit` - آجل

#### 3. ميزات الفلترة:
- **المدراء (admin/manager):** يمكنهم اختيار "جميع الفروع" أو فرع معين
- **الموظفون:** يرون فقط بيانات فرعهم المحدد
- **الاحتفاظ بالاختيار:** يتم حفظ الفرع المحدد في localStorage

### 📊 حالة النشر
✅ **جاهز للنشر** - تم التحقق من جميع متطلبات النشر:
- Environment variables configured
- CORS allows all origins
- MongoDB connection from environment
- No hardcoded URLs
- Supervisor configuration correct

## ملفات التغييرات:
- `/app/frontend/src/context/BranchContext.js` (جديد)
- `/app/frontend/src/components/BranchSelector.js` (جديد)
- `/app/frontend/src/App.js` (تحديث)
- `/app/frontend/src/pages/Dashboard.js` (تحديث)
- `/app/frontend/src/pages/Reports.js` (تحديث)
- `/app/backend/server.py` (تحديث - جميع تقارير الفروع)

## جدول الصلاحيات

### صلاحيات الصفحات الرئيسية
| ID | الاسم | الوصف |
|----|-------|--------|
| `pos` | نقاط البيع | إنشاء وإدارة الطلبات |
| `pos_discount` | إعطاء خصومات | السماح بإعطاء خصومات |
| `orders` | الطلبات | عرض الطلبات |
| `tables` | الطاولات | إدارة الطاولات |
| `kitchen` | شاشة المطبخ | عرض طلبات المطبخ |
| `delivery` | التوصيل | إدارة التوصيل |
| `inventory` | المخزون | عرض المخزون |
| `reports` | التقارير | عرض التقارير |
| `expenses` | المصاريف | عرض وإضافة المصاريف |
| `shifts_close` | إغلاق الصندوق | إغلاق صندوق الوردية |

### صلاحيات الإعدادات
| ID | الاسم | الوصف |
|----|-------|--------|
| `settings` | الإعدادات | الوصول للإعدادات |
| `settings_appearance` | المظهر | تغيير مظهر التطبيق |
| `settings_dashboard` | الرئيسية | إعدادات الصفحة الرئيسية |
| `settings_customers` | العملاء | إدارة العملاء |
| `settings_categories` | الفئات | إدارة فئات المنتجات |
| `settings_products` | المنتجات | إدارة المنتجات |
| `settings_branches` | الفروع | إدارة الفروع |
| `settings_printers` | الطابعات | إدارة الطابعات |
| `settings_kitchen` | أقسام المطبخ | إدارة أقسام المطبخ |
| `settings_delivery` | شركات التوصيل | إدارة شركات التوصيل |
| `settings_notifications` | الإشعارات | إعدادات الإشعارات |

## المهام المتبقية

### 🔴 أولوية قصوى (P0)
- [ ] إعادة هيكلة `/app/backend/server.py` (9600+ سطر)

### 🟡 أولوية عالية (P1)
- [ ] تحسين خريطة السائقين الحية
- [ ] إشعارات Push للسائقين (Firebase)

### 🟢 أولوية متوسطة (P2)
- [ ] إكمال تكامل أجهزة البصمة (ZKTeco)
- [ ] نظام ولاء العملاء (Loyalty)
- [ ] نظام إدارة الوصفات
- [ ] إضافة وضع مظلم/فاتح

## بيانات الاختبار

| الدور | البريد | كلمة المرور | الصلاحيات |
|-------|--------|-------------|-----------|
| Admin | admin@maestroegp.com | admin123 | جميع الصلاحيات |
| Super Admin | owner@maestroegp.com | owner123 | جميع الصلاحيات |
| مدير فرع | manager@test.com | 123456 | معظم الصلاحيات |
| كاشير | cashier@test.com | 123456 | فرع محدد فقط |

---
آخر تحديث: 18 يناير 2026 - 12:25 AM
نسبة الإنجاز: 99%
