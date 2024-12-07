import React from 'react';
import { Button, Typography, Box } from '@mui/material';

interface PaginationControlsProps {
  page: number;
  onPageChange: (page: number) => void;
}

const PaginationControls: React.FC<PaginationControlsProps> = ({ page, onPageChange }) => {
  return (
    <Box display="flex" alignItems="center" gap="10px" marginTop="20px" justifyContent="center">
      {page > 1 && (
        <Button variant="outlined" onClick={() => onPageChange(page - 1)}>
          Previous
        </Button>
      )}
      <Typography>Page {page}</Typography>
      <Button variant="outlined" onClick={() => onPageChange(page + 1)}>
        Next
      </Button>
    </Box>
  );
};

export default PaginationControls;
