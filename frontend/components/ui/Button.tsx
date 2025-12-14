import React, { ReactNode } from 'react';
import MuiButton, { ButtonProps as MuiButtonProps } from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import { styled } from '@mui/material/styles';

export type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'success' | 'outline';
export type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps extends Omit<MuiButtonProps, 'variant' | 'size' | 'color'> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  fullWidth?: boolean;
  children: ReactNode;
}

const StyledButton = styled(MuiButton, {
  shouldForwardProp: (prop) => prop !== 'isLoading',
})<{ isLoading?: boolean }>(({ isLoading }) => ({
  textTransform: 'none',
  fontWeight: 500,
  ...(isLoading && {
    pointerEvents: 'none',
  }),
}));

/**
 * Reusable Button component with multiple variants and sizes using MUI
 */
export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      isLoading = false,
      leftIcon,
      rightIcon,
      fullWidth = false,
      disabled,
      children,
      ...props
    },
    ref
  ) => {
    const getMuiProps = () => {
      switch (variant) {
        case 'primary':
          return { variant: 'contained' as const, color: 'primary' as const };
        case 'secondary':
          return { variant: 'contained' as const, color: 'secondary' as const };
        case 'danger':
          return { variant: 'contained' as const, color: 'error' as const };
        case 'success':
          return { variant: 'contained' as const, color: 'success' as const };
        case 'outline':
          return { variant: 'outlined' as const, color: 'primary' as const };
        default:
          return { variant: 'contained' as const, color: 'primary' as const };
      }
    };

    const getMuiSize = () => {
      switch (size) {
        case 'sm':
          return 'small' as const;
        case 'md':
          return 'medium' as const;
        case 'lg':
          return 'large' as const;
        default:
          return 'medium' as const;
      }
    };

    const muiProps = getMuiProps();

    return (
      <StyledButton
        ref={ref}
        {...muiProps}
        size={getMuiSize()}
        fullWidth={fullWidth}
        disabled={disabled || isLoading}
        isLoading={isLoading}
        startIcon={isLoading ? <CircularProgress size={16} color="inherit" /> : leftIcon}
        endIcon={rightIcon}
        {...props}
      >
        {isLoading ? 'Loading...' : children}
      </StyledButton>
    );
  }
);

Button.displayName = 'Button';
