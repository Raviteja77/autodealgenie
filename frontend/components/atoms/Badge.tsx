// components/atoms/Badge/Badge.tsx
import { FC } from 'react';
import { Chip, ChipProps } from '@mui/material';
import { AutoAwesome as AIIcon } from '@mui/icons-material';

export interface BadgeProps extends Omit<ChipProps, 'variant'> {
  variant?: 'ai-recommended' | 'top-pick' | 'best-value' | 'default';
  showIcon?: boolean;
}

const badgeConfig = {
  'ai-recommended': {
    label: 'AI Recommended',
    color: 'primary' as const,
    icon: <AIIcon fontSize="small" />,
  },
  'top-pick': {
    label: 'Top Pick',
    color: 'success' as const,
    icon: <AIIcon fontSize="small" />,
  },
  'best-value': {
    label: 'Best Value',
    color: 'secondary' as const,
    icon: <AIIcon fontSize="small" />,
  },
  default: {
    label: 'Featured',
    color: 'default' as const,
    icon: null,
  },
};

export const Badge: FC<BadgeProps> = ({
  variant = 'ai-recommended',
  showIcon = true,
  ...chipProps
}) => {
  const config = badgeConfig[variant];

  return (
    <Chip
      label={config.label}
      color={config.color}
      size="small"
      icon={showIcon ? config.icon || undefined : undefined}
      sx={{
        fontWeight: 600,
        '& .MuiChip-icon': {
          color: 'inherit',
        },
        ...chipProps.sx,
      }}
      {...chipProps}
    />
  );
};