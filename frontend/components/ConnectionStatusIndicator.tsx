'use client';

import React from 'react';
import {
  Box,
  Chip,
  IconButton,
  Tooltip,
  LinearProgress,
} from '@mui/material';
import {
  Wifi as WifiIcon,
  WifiOff as WifiOffIcon,
  Sync as SyncIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
  Queue as QueueIcon,
} from '@mui/icons-material';

type ConnectionStatus = "connected" | "connecting" | "disconnected" | "error" | "reconnecting";

interface ConnectionStatusIndicatorProps {
  status: ConnectionStatus;
  reconnectAttempts?: number;
  maxReconnectAttempts?: number;
  messageQueueSize?: number;
  isUsingHttpFallback?: boolean;
  onManualReconnect?: () => void;
}

/**
 * Connection status indicator component for WebSocket connections
 * Shows current connection state, reconnection attempts, and message queue status
 */
export const ConnectionStatusIndicator: React.FC<ConnectionStatusIndicatorProps> = ({
  status,
  reconnectAttempts = 0,
  maxReconnectAttempts = 5,
  messageQueueSize = 0,
  isUsingHttpFallback = false,
  onManualReconnect,
}) => {
  const getStatusConfig = () => {
    switch (status) {
      case "connected":
        return {
          icon: <WifiIcon fontSize="small" />,
          label: "Connected",
          color: "success" as const,
          description: "Real-time updates active",
        };
      case "connecting":
        return {
          icon: <SyncIcon fontSize="small" />,
          label: "Connecting",
          color: "info" as const,
          description: "Establishing connection...",
        };
      case "reconnecting":
        return {
          icon: <SyncIcon fontSize="small" className="rotating" />,
          label: `Reconnecting (${reconnectAttempts}/${maxReconnectAttempts})`,
          color: "warning" as const,
          description: "Attempting to restore connection",
        };
      case "disconnected":
        return {
          icon: <WifiOffIcon fontSize="small" />,
          label: "Disconnected",
          color: "default" as const,
          description: "Connection lost",
        };
      case "error":
        return {
          icon: <ErrorIcon fontSize="small" />,
          label: isUsingHttpFallback ? "Fallback Mode" : "Connection Error",
          color: "error" as const,
          description: isUsingHttpFallback 
            ? "Using HTTP fallback for messages"
            : "Unable to establish real-time connection",
        };
      default:
        return {
          icon: <WifiOffIcon fontSize="small" />,
          label: "Unknown",
          color: "default" as const,
          description: "Connection status unknown",
        };
    }
  };

  const statusConfig = getStatusConfig();

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      <Tooltip title={statusConfig.description} arrow>
        <Chip
          icon={statusConfig.icon}
          label={statusConfig.label}
          color={statusConfig.color}
          size="small"
          sx={{ 
            '& .rotating': {
              animation: 'spin 1s linear infinite',
            },
            '@keyframes spin': {
              '0%': { transform: 'rotate(0deg)' },
              '100%': { transform: 'rotate(360deg)' },
            },
          }}
        />
      </Tooltip>
      
      {messageQueueSize > 0 && (
        <Tooltip title={`${messageQueueSize} message${messageQueueSize > 1 ? 's' : ''} queued`} arrow>
          <Chip
            icon={<QueueIcon fontSize="small" />}
            label={messageQueueSize}
            color="warning"
            size="small"
          />
        </Tooltip>
      )}
      
      {(status === "disconnected" || status === "error") && onManualReconnect && (
        <Tooltip title="Reconnect manually" arrow>
          <IconButton
            size="small"
            onClick={onManualReconnect}
            sx={{ 
              ml: 0.5,
              '&:hover': {
                transform: 'rotate(180deg)',
                transition: 'transform 0.3s ease',
              },
            }}
          >
            <RefreshIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      )}
      
      {status === "reconnecting" && (
        <Box sx={{ width: 100, ml: 1 }}>
          <LinearProgress 
            variant="determinate" 
            value={(reconnectAttempts / maxReconnectAttempts) * 100}
            sx={{ height: 4, borderRadius: 2 }}
          />
        </Box>
      )}
    </Box>
  );
};
