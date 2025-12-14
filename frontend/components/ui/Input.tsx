import React, { ReactNode } from "react";
import TextField, { TextFieldProps } from "@mui/material/TextField";
import InputAdornment from "@mui/material/InputAdornment";

interface InputProps extends Omit<TextFieldProps, "error"> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  fullWidth?: boolean;
  multiline?: boolean;
}

/**
 * Reusable Input component with label, error, and helper text support using MUI
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
      multiline = false,
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

    return multiline ? (
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

Input.displayName = "Input";
