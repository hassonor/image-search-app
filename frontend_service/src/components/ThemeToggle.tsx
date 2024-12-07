import React from 'react';
import { IconButton, Tooltip } from '@mui/material';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import LightModeIcon from '@mui/icons-material/LightMode';

interface ThemeToggleProps {
  onToggleTheme: () => void;
  currentMode: 'light' | 'dark';
}

const ThemeToggle: React.FC<ThemeToggleProps> = ({ onToggleTheme, currentMode }) => {
  const isDark = currentMode === 'dark';

  return (
    <Tooltip title={`Switch to ${isDark ? 'Light' : 'Dark'} Mode`}>
      <IconButton onClick={onToggleTheme} color="inherit">
        {isDark ? <LightModeIcon /> : <DarkModeIcon />}
      </IconButton>
    </Tooltip>
  );
};

export default ThemeToggle;
