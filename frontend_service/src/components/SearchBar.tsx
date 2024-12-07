import React, { useState } from 'react';
import { TextField, Button, Box } from '@mui/material';

interface SearchBarProps {
  onSearch: (query: string) => void;
  onClean: () => void;
}

const SearchBar: React.FC<SearchBarProps> = ({ onSearch, onClean }) => {
  const [text, setText] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(text.trim());
  };

  const handleClean = () => {
    setText('');
    onClean();
  };

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      sx={{ mb: 2, display: 'flex', gap: '10px', alignItems: 'center' }}
    >
      <TextField
        label="Search images..."
        variant="outlined"
        fullWidth
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <Button type="submit" variant="contained" color="primary">Search</Button>
      <Button type="button" variant="outlined" color="secondary" onClick={handleClean}>
        Clean
      </Button>
    </Box>
  );
};

export default SearchBar;
