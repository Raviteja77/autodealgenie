'use client';

import React, { Component, ErrorInfo, ReactNode } from 'react';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import { styled } from '@mui/material/styles';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

const ErrorContainer = styled(Box)({
  minHeight: '100vh',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  backgroundColor: '#f9fafb',
  padding: '1rem',
});

const ErrorCard = styled(Card)({
  maxWidth: 500,
  width: '100%',
});

const IconWrapper = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  width: 48,
  height: 48,
  margin: '0 auto 1rem',
  backgroundColor: theme.palette.error.light,
  borderRadius: '50%',
}));

/**
 * Error Boundary component to catch and handle React errors gracefully
 * 
 * @example
 * ```tsx
 * <ErrorBoundary fallback={<div>Something went wrong</div>}>
 *   <YourComponent />
 * </ErrorBoundary>
 * ```
 */
export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log error to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('Error caught by boundary:', error, errorInfo);
    }

    // Call optional error handler
    this.props.onError?.(error, errorInfo);

    // In production, you might want to log to an error tracking service
    // Example: Sentry.captureException(error, { extra: errorInfo });
  }

  render() {
    if (this.state.hasError) {
      // Render custom fallback UI if provided
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default error UI
      return (
        <ErrorContainer>
          <ErrorCard>
            <CardContent>
              <IconWrapper>
                <ErrorOutlineIcon color="error" fontSize="large" />
              </IconWrapper>
              <Typography variant="h5" align="center" gutterBottom fontWeight={600}>
                Oops! Something went wrong
              </Typography>
              <Typography variant="body1" align="center" color="text.secondary" sx={{ mb: 3 }}>
                We&apos;re sorry for the inconvenience. Please try refreshing the page.
              </Typography>
              {process.env.NODE_ENV === 'development' && this.state.error && (
                <Box sx={{ mt: 2, p: 2, backgroundColor: '#f3f4f6', borderRadius: 1 }}>
                  <Typography variant="caption" component="details" sx={{ cursor: 'pointer' }}>
                    <summary style={{ fontWeight: 500, marginBottom: 8 }}>
                      Error Details (Development Only)
                    </summary>
                    <Box
                      component="pre"
                      sx={{
                        fontSize: '0.75rem',
                        color: 'error.main',
                        overflow: 'auto',
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-word',
                      }}
                    >
                      {this.state.error.toString()}
                      {this.state.error.stack}
                    </Box>
                  </Typography>
                </Box>
              )}
              <Button
                variant="contained"
                fullWidth
                onClick={() => window.location.reload()}
                sx={{ mt: 2 }}
              >
                Refresh Page
              </Button>
            </CardContent>
          </ErrorCard>
        </ErrorContainer>
      );
    }

    return this.props.children;
  }
}
