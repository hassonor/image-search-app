import React, { useState } from 'react';
import Layout from './components/Layout';
import SearchBar from './components/SearchBar';
import ImageGrid from './components/ImageGrid';
import PaginationControls from './components/PaginationControls';
import { useThemeMode } from './hooks/useThemeMode';
import { ThemeProvider } from '@mui/material/styles';

function App() {
  const { theme, mode, toggleMode } = useThemeMode();
  const [query, setQuery] = useState('');
  const [page, setPage] = useState(1);

  const handleClean = () => {
    setQuery('');
    setPage(1);
  };

  return (
    <ThemeProvider theme={theme}>
      <Layout onToggleTheme={toggleMode} currentMode={mode}>
        <SearchBar
          onSearch={(q) => { setQuery(q); setPage(1); }}
          onClean={handleClean}
        />
        {query && <ImageGrid query={query} page={page} />}
        {query && <PaginationControls page={page} onPageChange={(p) => setPage(p)} />}
      </Layout>
    </ThemeProvider>
  );
}

export default App;
