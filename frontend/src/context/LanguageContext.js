import React, { createContext, useContext, useState, useEffect } from 'react';
import { getCurrentLanguage, setLanguage as setLang, t as translate } from '../utils/translations';

const LanguageContext = createContext();

export const LanguageProvider = ({ children }) => {
  const [language, setLanguageState] = useState(() => {
    // تحميل اللغة من localStorage عند البدء
    const savedLang = localStorage.getItem('app_language');
    return savedLang || 'ar';
  });
  
  // تحديث اللغة
  const setLanguage = (lang) => {
    setLang(lang);
    setLanguageState(lang);
    // إعادة تحميل الصفحة لتطبيق التغييرات
    window.location.reload();
  };
  
  // تطبيق الاتجاه عند التحميل والتغيير
  useEffect(() => {
    const isRTL = ['ar', 'ku', 'fa', 'he'].includes(language);
    document.documentElement.dir = isRTL ? 'rtl' : 'ltr';
    document.documentElement.lang = language;
    // حفظ اللغة في localStorage
    localStorage.setItem('app_language', language);
  }, [language]);
  
  // الاستماع لتغييرات localStorage من الصفحات الأخرى
  useEffect(() => {
    const handleStorageChange = (e) => {
      if (e.key === 'app_language' && e.newValue && e.newValue !== language) {
        setLanguageState(e.newValue);
      }
    };
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [language]);
  
  return (
    <LanguageContext.Provider value={{ language, setLanguage, t: translate }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    return { language: 'ar', setLanguage: () => {}, t: translate };
  }
  return context;
};

export default LanguageContext;
