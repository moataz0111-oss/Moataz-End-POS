// ملف مركزي لتحديد رابط الـ API
// يعمل تلقائياً مع بيئة المعاينة والإنتاج والتطوير

const getBackendUrl = () => {
  // التأكد من وجود window (للتوافق مع SSR)
  if (typeof window === 'undefined') {
    return process.env.REACT_APP_BACKEND_URL || '';
  }
  
  const hostname = window.location.hostname;
  
  // في بيئة الإنتاج (emergent.host)، استخدم نفس الرابط الحالي
  if (hostname.includes('.emergent.host')) {
    return window.location.origin;
  }
  
  // في بيئة المعاينة (preview.emergentagent.com)
  if (hostname.includes('.emergentagent.com')) {
    return window.location.origin;
  }
  
  // في بيئة التطوير المحلية (localhost)
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    // استخدم REACT_APP_BACKEND_URL إذا كان متاحاً، وإلا استخدم localhost
    return process.env.REACT_APP_BACKEND_URL || window.location.origin;
  }
  
  // Fallback: استخدم origin الحالي للتعامل مع أي نطاق مخصص
  return window.location.origin;
};

// تصدير كـ singleton
export const BACKEND_URL = getBackendUrl();
export const API_URL = `${BACKEND_URL}/api`;

// دالة للحصول على URL (للاستخدام في أماكن تحتاج دالة)
export const getApiUrl = () => API_URL;
export const getBackendUrlFn = () => BACKEND_URL;

export default API_URL;
