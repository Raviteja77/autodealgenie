import { ReactNode } from 'react';
import { CardProps as MuiCardProps } from '@mui/material/Card';

export interface CardComponentProps extends MuiCardProps {
  children: ReactNode;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  shadow?: 'none' | 'sm' | 'md' | 'lg';
  hover?: boolean;
}

export interface CardHeaderComponentProps {
  children: ReactNode;
}

export interface CardBodyProps {
  children: ReactNode;
  sx?: Record<string, unknown>;
}

export interface CardFooterProps {
  children: ReactNode;
  sx?: Record<string, unknown>;
}
