import React, { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext(null);

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState(() => {
    const saved = localStorage.getItem('theme');
    if (saved) return saved;
    return 'system';
  });

  const [resolvedTheme, setResolvedTheme] = useState('dark');

  useEffect(() => {
    const updateTheme = () => {
      let effectiveTheme = theme;
      
      if (theme === 'system') {
        // Auto switch based on time of day
        const hour = new Date().getHours();
        // Light mode from 6 AM to 6 PM
        effectiveTheme = (hour >= 6 && hour < 18) ? 'light' : 'dark';
      }
      
      setResolvedTheme(effectiveTheme);
      
      const root = window.document.documentElement;
      root.classList.remove('light', 'dark');
      root.classList.add(effectiveTheme);
    };

    updateTheme();
    
    // Update every minute to handle day/night transition
    const interval = setInterval(updateTheme, 60000);
    
    return () => clearInterval(interval);
  }, [theme]);

  const setThemeValue = (newTheme) => {
    localStorage.setItem('theme', newTheme);
    setTheme(newTheme);
  };

  return (
    <ThemeContext.Provider value={{
      theme,
      resolvedTheme,
      setTheme: setThemeValue,
      isDark: resolvedTheme === 'dark'
    }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export default ThemeContext;
