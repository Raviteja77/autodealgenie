/**
 * Components Module Exports
 * 
 * This module provides centralized exports following Atomic Design principles:
 * - Atoms: Basic building blocks (Button, Input, Card, Modal, Spinner)
 * - Molecules: Simple combinations of atoms
 * - Organisms: Complex UI sections
 * - Common: Shared layout components
 */

// Re-export UI components from atoms (for backward compatibility)
export { Button, Input, Card, Spinner, Modal } from './atoms';

// Also maintain backward compatibility with './ui' exports
export * from './ui';

// Export molecules
export {
  PriceDisplay,
  MonthlyPaymentDisplay,
  PriceSwitcher,
  VehicleTitle,
  VehicleDetails,
  VehicleImage,
  ViewModeToggle,
  SortDropdown,
  SavedSearchesDropdown,
  ConnectionStatusIndicator,
  SaveSearchModal,
} from './molecules';
export type { SortOption } from './molecules';

// Export organisms
export {
  VehicleCard,
  FilterPanel,
  ComparisonModal,
  ComparisonBar,
  ChatInput,
  FinancingComparisonModal,
  InsuranceRecommendations,
  LenderRecommendations,
} from './organisms';

// Export common components
export { ErrorBoundary } from './ErrorBoundary';
export { default as Header } from './common/Header';
export { default as Footer } from './common/Footer';
export { default as ProgressStepper } from './common/ProgressStepper';

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

export type {
  VehicleDisplayProps,
} from './organisms';
