/**
 * Components Module Exports
 */

// Re-export UI components from atoms (for backward compatibility)
export { Button, Input, Card, Spinner, Modal } from './atoms';

// Export molecules
export {
  PriceDisplay,
  MonthlyPaymentDisplay,
  PriceSwitcher,
  VehicleTitle,
  VehicleDetails,
  VehicleImage,
} from './molecules';

// Export other components
export { ErrorBoundary } from './ErrorBoundary';
export { default as Header } from './common/Header';
export { default as Footer } from './common/Footer';
export { default as ProgressStepper } from './common/ProgressStepper';
export * from './VehicleCard';
export { ConnectionStatusIndicator } from './ConnectionStatusIndicator';
export { FinancingComparisonModal } from './FinancingComparisonModal';

// Export types
export type {
  ButtonProps,
  ButtonVariant,
  ButtonSize,
  InputProps,
  CardComponentProps,
  SpinnerProps,
  ModalProps,
} from './atoms';

export type {
  PriceDisplayProps,
  MonthlyPaymentDisplayProps,
  PriceSwitcherProps,
  VehicleDetailsProps,
  VehicleTitleProps,
  VehicleImageProps,
} from './molecules';
