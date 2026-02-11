# Maestro EGP - Restaurant Management System PRD

## Original Problem Statement
نظام إدارة مطاعم متكامل يدعم لغات متعددة (عربي، إنجليزي، كردي). يشمل:
- نقطة البيع (POS)
- إدارة المخزون
- شاشة المطبخ
- إدارة التوصيل والسائقين
- إدارة الموظفين والرواتب
- التقارير الذكية
- قائمة الزبائن الرقمية

## ✅ COMPLETED: Full Translation System (Feb 2025)

### What was implemented:
1. **Centralized Translation System**
   - `useTranslation` hook with dynamic language switching
   - `autoTranslate.js` dictionary with 600+ translations
   - Supports Arabic (ar), English (en), Kurdish (ku)
   - Automatic RTL/LTR direction based on language

2. **Pages with Full Translation Support**
   - Login.js ✅
   - Dashboard.js ✅
   - Settings.js ✅
   - Orders.js ✅
   - Tables.js ✅
   - POS.js ✅
   - DriverApp.js ✅
   - KitchenDisplay.js ✅
   - SuperAdmin.js ✅
   - + All other 20+ pages have translation hooks added

3. **Components with Translation Support**
   - BranchSelector.js ✅
   - PWAInstallButton.js ✅

4. **How to Change Language**
   - Go to Settings > System Settings
   - Select language from dropdown
   - Click "Save System Settings"
   - Page will reload with new language

## Architecture

```
/app
├── backend/
│   └── server.py          # FastAPI (~14,600 lines - needs refactoring)
└── frontend/
    └── src/
        ├── components/
        │   ├── BranchSelector.js   # Translated
        │   └── PWAInstallButton.js # Translated
        ├── context/
        │   └── LanguageContext.js  # Language state management
        ├── hooks/
        │   └── useTranslation.js   # Translation hook
        ├── pages/
        │   └── [35+ pages]         # All with translation support
        └── utils/
            └── autoTranslate.js    # Translation dictionary (600+ entries)
```

## Key Features

### Kitchen Display
- Decoupled `kitchen_status` from order status
- Orders persist until marked "ready"
- Sound notifications for new orders
- Branch name display

### POS
- Table filtering by branch
- Full translation support
- Payment methods: Cash, Card, Credit

### Driver App
- Login with phone + PIN
- Order tracking
- Navigation integration
- Full translation support

## Test Credentials
- **Super Admin**: owner@maestroegp.com / owner123
- **Demo Client**: demo@maestroegp.com / demo123
- **Cashier**: Hani@maestroegp.com / test123

## Backlog

### P1 - Code Refactoring
- [ ] Split `server.py` (~14,600 lines) into routes
- [ ] Split `Settings.js` (~5,700 lines)
- [ ] Split `POS.js` (~2,800 lines)
- [ ] Split `CustomerMenu.js` (~2,000 lines)

### P2 - Enhancements
- [ ] Map design verification
- [ ] PWA installation testing

### P3 - Future
- [ ] SendGrid email integration (waiting for API key)

## 3rd Party Integrations
- OpenStreetMap Nominatim
- CARTO (map tiles)
- Leaflet & react-leaflet
- SendGrid (installed, not configured)
