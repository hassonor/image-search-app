import { useState, useMemo, useEffect } from 'react';
import { createTheme } from '@mui/material/styles';

export function useThemeMode() {
  const storedMode = localStorage.getItem('themeMode') as 'light' | 'dark' | null;
  const [mode, setMode] = useState<'light' | 'dark'>(storedMode || 'dark');

  useEffect(() => {
    localStorage.setItem('themeMode', mode);
  }, [mode]);

  const theme = useMemo(
    () =>
      createTheme({
        palette: {
          mode,
          primary: { main: '#1976d2' }
        },
      }),
    [mode]
  );

  const toggleMode = () => {
    setMode((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  return { theme, mode, toggleMode };
}
