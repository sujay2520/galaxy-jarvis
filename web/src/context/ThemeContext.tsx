import React, { createContext, useContext, useState, useEffect } from 'react';

type ThemeType = 'light' | 'dark';

interface ThemeColors {
  bg: string;
  card: string;
  cardHover: string;
  border: string;
  text: string;
  textMuted: string;
  textDim: string;
  accent: string;
  accentLight: string;
}

interface ThemeContextType {
  theme: ThemeType;
  colors: ThemeColors;
  toggleTheme: () => void;
}

const darkColors: ThemeColors = {
  bg: '#0a0a18',
  card: '#12122a',
  cardHover: '#1c1c38',
  border: '#1e1e3a',
  text: '#ffffff',
  textMuted: '#9ca3af',
  textDim: '#6b7280',
  accent: '#818cf8',
  accentLight: '#a5b4fc',
};

const lightColors: ThemeColors = {
  bg: '#f8f9fc',
  card: '#ffffff',
  cardHover: '#f1f5f9',
  border: '#e2e8f0',
  text: '#1e293b',
  textMuted: '#64748b',
  textDim: '#94a3b8',
  accent: '#4f46e5',
  accentLight: '#6366f1',
};

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<ThemeType>(() => {
    const saved = localStorage.getItem('galaxy_theme');
    return (saved === 'light' || saved === 'dark') ? saved : 'dark';
  });

  useEffect(() => {
    localStorage.setItem('galaxy_theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme(t => t === 'dark' ? 'light' : 'dark');

  const colors = theme === 'dark' ? darkColors : lightColors;

  return (
    <ThemeContext.Provider value={{ theme, colors, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
