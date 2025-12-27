import { ReactNode } from 'react';
import { TextFieldProps } from '@mui/material/TextField';

export interface InputProps extends Omit<TextFieldProps, "error"> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  fullWidth?: boolean;
  multiLine?: boolean;
}
