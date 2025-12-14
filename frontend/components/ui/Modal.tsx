'use client';

import React, { ReactNode } from 'react';
import MuiDialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import IconButton from '@mui/material/IconButton';
import CloseIcon from '@mui/icons-material/Close';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  closeOnOverlayClick?: boolean;
  showCloseButton?: boolean;
}

/**
 * Modal component for dialogs and overlays using MUI
 */
export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
  closeOnOverlayClick = true,
  showCloseButton = true,
}) => {
  const handleClose = (_event: unknown, reason: string) => {
    if (reason === 'backdropClick' && !closeOnOverlayClick) {
      return;
    }
    onClose();
  };

  return (
    <MuiDialog
      open={isOpen}
      onClose={handleClose}
      maxWidth={size}
      fullWidth
      aria-labelledby={title ? 'modal-title' : undefined}
    >
      {(title || showCloseButton) && (
        <DialogTitle id="modal-title">
          {title}
          {showCloseButton && (
            <IconButton
              aria-label="close"
              onClick={onClose}
              sx={{
                position: 'absolute',
                right: 8,
                top: 8,
                color: (theme) => theme.palette.grey[500],
              }}
            >
              <CloseIcon />
            </IconButton>
          )}
        </DialogTitle>
      )}
      <DialogContent>{children}</DialogContent>
    </MuiDialog>
  );
};
