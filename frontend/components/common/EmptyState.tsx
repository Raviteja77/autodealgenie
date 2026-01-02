/**
 * EmptyState Component
 * 
 * Standardized empty state component used across dashboard pages.
 */

import { Box, Typography, Stack } from "@mui/material";
import { Button } from "@/components";
import { ReactNode } from "react";

export interface EmptyStateProps {
  /**
   * Main message to display
   */
  message: string;

  /**
   * Optional description
   */
  description?: string;

  /**
   * Optional icon to display
   */
  icon?: ReactNode;

  /**
   * Action button label
   */
  actionLabel?: string;

  /**
   * Action button handler
   */
  onAction?: () => void;

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
 * Standardized empty state component
 * 
 * @example
 * if (vehicles.length === 0) {
 *   return (
 *     <EmptyState
 *       message="No vehicles found"
 *       description="Try adjusting your search filters"
 *       actionLabel="Back to Search"
 *       onAction={() => router.push('/dashboard/search')}
 *     />
 *   );
 * }
 */
export function EmptyState({
  message,
  description,
  icon,
  actionLabel,
  onAction,
  fullHeight = false,
  minHeight = "400px",
}: EmptyStateProps) {
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
      <Stack spacing={3} alignItems="center" sx={{ maxWidth: 500, textAlign: "center" }}>
        {icon && <Box sx={{ fontSize: 64, color: "text.secondary" }}>{icon}</Box>}
        
        <Typography variant="h5" color="text.primary">
          {message}
        </Typography>

        {description && (
          <Typography variant="body1" color="text.secondary">
            {description}
          </Typography>
        )}

        {actionLabel && onAction && (
          <Button variant="contained" onClick={onAction}>
            {actionLabel}
          </Button>
        )}
      </Stack>
    </Box>
  );
}
