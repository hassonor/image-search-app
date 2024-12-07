import React from 'react';
import { Box, Typography } from '@mui/material';

const Footer: React.FC = () => {
  return (
    <Box
      component="footer"
      textAlign="center"
      py={2}
      borderTop="1px solid"
      borderColor="divider"
      bgcolor="background.paper"
    >
      <Typography variant="body2">
        © {new Date().getFullYear()} My Awesome Image Search App
      </Typography>
    </Box>
  );
};

export default Footer;
