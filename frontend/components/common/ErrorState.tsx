/**
 * ErrorState Component
 * 
 * Standardized error state component used across dashboard pages.
 */

import { Box, Typography, Alert, AlertTitle } from "@mui/material";
import { Button } from "@/components";

export interface ErrorStateProps {
  /**
   * Error message to display
   */
  message: string;

  /**
   * Optional error title
   */
  title?: string;

  /**
   * Whether to show a retry button
   */
  showRetry?: boolean;

  /**
   * Retry button handler
   */
  onRetry?: () => void;

  /**
   * Retry button label
   */
  retryLabel?: string;

  /**
   * Whether to center vertically in full viewport
   */
  fullHeight?: boolean;

  /**
   * Minimum height when not full height
   */
  minHeight?: string | number;
}

/**
 * Standardized error state component
 * 
 * @example
 * if (error) {
 *   return (
 *     <ErrorState
 *       message={error}
 *       showRetry
 *       onRetry={() => refetch()}
 *     />
 *   );
 * }
 */
export function ErrorState({
  message,
  title = "Error",
  showRetry = false,
  onRetry,
  retryLabel = "Try Again",
  fullHeight = false,
  minHeight = "200px",
}: ErrorStateProps) {
  return (
    <Box
      sx={{
        minHeight: fullHeight ? "100vh" : minHeight,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        bgcolor: "background.default",
        p: 3,
      }}
    >
      <Box sx={{ maxWidth: 600, width: "100%" }}>
        <Alert severity="error">
          <AlertTitle>{title}</AlertTitle>
          <Typography variant="body2" sx={{ mb: showRetry ? 2 : 0 }}>
            {message}
          </Typography>
          {showRetry && onRetry && (
            <Button
              variant="outlined"
              color="error"
              onClick={onRetry}
              size="small"
            >
              {retryLabel}
            </Button>
          )}
        </Alert>
      </Box>
    </Box>
  );
}
