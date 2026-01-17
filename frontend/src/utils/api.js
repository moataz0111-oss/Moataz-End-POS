// ملف مركزي لتحديد رابط الـ API
// يعمل تلقائياً مع بيئة المعاينة والإنتاج

const getBackendUrl = () => {
  // في بيئة الإنتاج (emergent.host)، استخدم نفس الرابط الحالي
  if (typeof window !== 'undefined' && window.location.hostname.includes('.emergent.host')) {
    return window.location.origin;
  }
  // في بيئة المعاينة أو التطوير
  return process.env.REACT_APP_BACKEND_URL || (typeof window !== 'undefined' ? window.location.origin : '');
};

// تصدير كـ singleton لتجنب إعادة الحساب
const BACKEND_URL = getBackendUrl();
const API_URL = `${BACKEND_URL}/api`;

// دالة للحصول على الـ API URL (يمكن استخدامها في أي مكان)
export const getApiUrl = () => API_URL;
export const getBaseUrl = () => BACKEND_URL;

export { BACKEND_URL, API_URL };
export default API_URL;
