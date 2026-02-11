// مكون Text للترجمة التلقائية
import React from 'react';
import { translate } from '../utils/autoTranslate';

// مكون بسيط يترجم النص تلقائياً
export const T = ({ children }) => {
  if (typeof children === 'string') {
    return <>{translate(children)}</>;
  }
  return <>{children}</>;
};

// دالة مساعدة للترجمة المباشرة
export const t = (text) => translate(text);

export default T;
