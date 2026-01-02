/**
 * LoadingState Component
 * 
 * Standardized loading state component used across dashboard pages.
 */

import { Box } from "@mui/material";
import { Spinner } from "@/components";

export interface LoadingStateProps {
  /**
   * Loading message to display
   */
  message?: string;

  /**
   * Spinner size
   */
  size?: "sm" | "md" | "lg";

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
 * Standardized loading state component
 * 
 * @example
 * if (isLoading) {
 *   return <LoadingState message="Loading vehicles..." />;
 * }
 */
export function LoadingState({
  message = "Loading...",
  size = "lg",
  fullHeight = true,
  minHeight = "400px",
}: LoadingStateProps) {
  return (
    <Box
      sx={{
        minHeight: fullHeight ? "100vh" : minHeight,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        bgcolor: "background.default",
      }}
    >
      <Spinner size={size} text={message} />
    </Box>
  );
}
