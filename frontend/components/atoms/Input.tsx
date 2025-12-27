import React from 'react';
import TextField from '@mui/material/TextField';
import InputAdornment from '@mui/material/InputAdornment';
import { InputProps } from './Input.types';

/**
 * Reusable Input component with label, error, and helper text support using MUI
 * 
 * @example
 * ```tsx
 * <Input 
 *   label="Email" 
 *   error="Invalid email" 
 *   value={email} 
 *   onChange={handleChange} 
 * />
 * ```
 */
export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  (
    {
      label,
      error,
      helperText,
      leftIcon,
      rightIcon,
      fullWidth = false,
      multiLine = false,
      disabled,
      ...props
    },
    ref
  ) => {
    const inputProps: Record<string, unknown> = {};

    if (leftIcon) {
      inputProps.startAdornment = (
        <InputAdornment position="start">{leftIcon}</InputAdornment>
      );
    }

    if (rightIcon) {
      inputProps.endAdornment = (
        <InputAdornment position="end">{rightIcon}</InputAdornment>
      );
    }

    return multiLine ? (
      <TextField
        inputRef={ref}
        label={label}
        error={Boolean(error)}
        helperText={error || helperText}
        fullWidth={fullWidth}
        disabled={disabled}
        multiline
        minRows={4}
        InputProps={inputProps}
        {...props}
      />
    ) : (
      <TextField
        inputRef={ref}
        label={label}
        error={Boolean(error)}
        helperText={error || helperText}
        fullWidth={fullWidth}
        disabled={disabled}
        InputProps={inputProps}
        {...props}
      />
    );
  }
);

Input.displayName = 'Input';
