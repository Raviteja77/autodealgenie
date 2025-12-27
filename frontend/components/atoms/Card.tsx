import React from 'react';
import MuiCard from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardHeader from '@mui/material/CardHeader';
import CardActions from '@mui/material/CardActions';
import { styled } from '@mui/material/styles';
import { 
  CardComponentProps, 
  CardHeaderComponentProps, 
  CardBodyProps, 
  CardFooterProps 
} from './Card.types';

const StyledCard = styled(MuiCard, {
  shouldForwardProp: (prop) => !['hover', 'shadow'].includes(prop as string),
})<CardComponentProps>(({ theme, hover, shadow = 'md' }) => ({
  ...(hover && {
    transition: 'box-shadow 0.3s ease-in-out',
    '&:hover': {
      boxShadow: theme.shadows[8],
    },
  }),
  ...(shadow === 'none' && { boxShadow: 'none' }),
  ...(shadow === 'sm' && { boxShadow: theme.shadows[1] }),
  ...(shadow === 'md' && { boxShadow: theme.shadows[3] }),
  ...(shadow === 'lg' && { boxShadow: theme.shadows[6] }),
}));

/**
 * Card component for content containers using MUI
 * 
 * @example
 * ```tsx
 * <Card shadow="md" hover>
 *   <Card.Body>Content here</Card.Body>
 * </Card>
 * ```
 */
const CardComponent = React.forwardRef<HTMLDivElement, CardComponentProps>(
  (
    {
      children,
      shadow = 'md',
      hover = false,
      ...props
    },
    ref
  ) => {
    return (
      <StyledCard ref={ref} shadow={shadow} hover={hover} {...props}>
        {children}
      </StyledCard>
    );
  }
);

CardComponent.displayName = 'Card';

/**
 * Card Header component
 */
const CardHeaderComponent = React.forwardRef<HTMLDivElement, CardHeaderComponentProps>(
  ({ children, ...props }, ref) => {
    return (
      <CardHeader ref={ref} title={children} {...props} />
    );
  }
);

CardHeaderComponent.displayName = 'CardHeader';

/**
 * Card Body component
 */
const CardBody = React.forwardRef<HTMLDivElement, CardBodyProps>(
  ({ children, ...props }, ref) => {
    return (
      <CardContent ref={ref} {...props}>
        {children}
      </CardContent>
    );
  }
);

CardBody.displayName = 'CardBody';

/**
 * Card Footer component
 */
const CardFooter = React.forwardRef<HTMLDivElement, CardFooterProps>(
  ({ children, ...props }, ref) => {
    return (
      <CardActions ref={ref} {...props}>
        {children}
      </CardActions>
    );
  }
);

CardFooter.displayName = 'CardFooter';

// Compound component pattern
type CardType = typeof CardComponent & {
  Header: typeof CardHeaderComponent;
  Body: typeof CardBody;
  Footer: typeof CardFooter;
};

export const Card = CardComponent as CardType;
Card.Header = CardHeaderComponent;
Card.Body = CardBody;
Card.Footer = CardFooter;
