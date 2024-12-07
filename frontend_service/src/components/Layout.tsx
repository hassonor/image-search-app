import React from 'react';
import { Box, Container } from '@mui/material';
import Header from './Header';
import Footer from './Footer';

interface LayoutProps {
  children: React.ReactNode;
  onToggleTheme: () => void;
  currentMode: 'light' | 'dark';
}

const Layout: React.FC<LayoutProps> = ({ children, onToggleTheme, currentMode }) => {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        bgcolor: 'background.default',
        color: 'text.primary',
        display: 'flex',
        flexDirection: 'column'
      }}
    >
      <Header onToggleTheme={onToggleTheme} currentMode={currentMode} />
      <Container maxWidth="md" sx={{ py: 3, flex: '1 0 auto' }}>
        {children}
      </Container>
      <Footer />
    </Box>
  );
};

export default Layout;
