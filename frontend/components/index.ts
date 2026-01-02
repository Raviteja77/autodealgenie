/**
 * Components Module Exports
 * 
 * This module provides centralized exports following Atomic Design principles:
 * - Atoms: Basic building blocks (Button, Input, Card, Modal, Spinner)
 * - Molecules: Simple combinations of atoms
 * - Organisms: Complex UI sections
 * - Common: Shared layout components
 * - Vehicle: Reusable vehicle-related components
 * - Evaluation: Evaluation page specific components
 */

// Export atoms - basic building blocks
export { Button, Input, Card, Spinner, Modal } from './atoms';

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
  PaymentMethodSelector,
  BudgetRangeSlider,
  SearchSidebar,
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
  BasicVehicleFilters,
  AdvancedFilters,
  FinancingOptionsForm,
} from './organisms';

// Export common components
export { ErrorBoundary } from './ErrorBoundary';
export { default as Header } from './common/Header';
export { default as Footer } from './common/Footer';
export { default as ProgressStepper } from './common/ProgressStepper';
export { LoadingState } from './common/LoadingState';
export { ErrorState } from './common/ErrorState';
export { EmptyState } from './common/EmptyState';

// Export vehicle components
export * from './vehicle';

// Export evaluation components
export * from './evaluation';

// Export negotiation components
export { CurrentOfferStatus } from './negotiation/CurrentOfferStatus';

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
