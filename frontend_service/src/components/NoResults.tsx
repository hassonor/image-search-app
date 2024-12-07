import React from 'react';
import { Box, Typography } from '@mui/material';

interface NoResultsProps {
  query: string;
}

const NoResults: React.FC<NoResultsProps> = ({ query }) => {
  return (
    <Box textAlign="center" mt={4}>
      <Typography variant="h6">No images found for "{query}"</Typography>
      {/* You could add an illustration or a fun graphic here */}
    </Box>
  );
};

export default NoResults;
