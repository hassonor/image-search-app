import React from 'react';
import { Box, Typography } from '@mui/material';
import ThemeToggle from './ThemeToggle';

interface HeaderProps {
  onToggleTheme: () => void;
  currentMode: 'light' | 'dark';
}

const Header: React.FC<HeaderProps> = ({ onToggleTheme, currentMode }) => {
  return (
    <Box
      component="header"
      display="flex"
      justifyContent="space-between"
      alignItems="center"
      p={2}
      borderBottom="1px solid"
      borderColor="divider"
    >
      <Typography variant="h5">
        Image Search
      </Typography>
      <ThemeToggle currentMode={currentMode} onToggleTheme={onToggleTheme} />
    </Box>
  );
};

export default Header;
