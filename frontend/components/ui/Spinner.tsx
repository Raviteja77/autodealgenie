import React from 'react';
import CircularProgress from '@mui/material/CircularProgress';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Backdrop from '@mui/material/Backdrop';

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  color?: 'primary' | 'secondary' | 'white';
  fullScreen?: boolean;
  text?: string;
}

const sizeMap = {
  sm: 20,
  md: 40,
  lg: 60,
};

/**
 * Loading Spinner component using MUI
 * 
 * @example
 * ```tsx
 * // Inline spinner
 * <Spinner size="sm" color="primary" />
 * 
 * // Full screen loading
 * <Spinner fullScreen text="Loading..." />
 * ```
 */
export const Spinner: React.FC<SpinnerProps> = ({
  size = 'md',
  color = 'primary',
  fullScreen = false,
  text,
}) => {
  const spinner = (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 2,
      }}
    >
      <CircularProgress
        size={sizeMap[size]}
        color={color === 'white' ? 'inherit' : color}
        sx={color === 'white' ? { color: 'white' } : {}}
      />
      {text && (
        <Typography
          variant="body2"
          color={color === 'white' ? 'white' : 'textSecondary'}
        >
          {text}
        </Typography>
      )}
    </Box>
  );

  if (fullScreen) {
    return (
      <Backdrop
        open={true}
        sx={{
          color: '#fff',
          zIndex: (theme) => theme.zIndex.drawer + 1,
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
        }}
      >
        {spinner}
      </Backdrop>
    );
  }

  return spinner;
};
