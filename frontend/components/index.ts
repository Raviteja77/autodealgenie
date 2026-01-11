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
export { Badge, Button, Card, Input, Modal, Spinner } from './atoms';

// Export molecules
export {
  BudgetRangeSlider, ConnectionStatusIndicator, DealScoreDisplay,
  KeyInsightsList, MarketInsights, MonthlyPaymentDisplay, Pagination, PaymentMethodSelector, PriceDisplay, PriceSwitcher, SaveSearchModal, SavedSearchesDropdown, SearchSidebar, SortDropdown, TalkingPointsList, VehicleDetails,
  VehicleImage, VehicleTitle, ViewModeToggle
} from './molecules';
export type { SortOption } from './molecules';

// Export organisms
export {
  AdvancedFilters, BasicVehicleFilters, ChatInput, ComparisonBar, ComparisonModal, CurrentOfferStatus, EvaluationScoreCard, FilterPanel, FinancingComparisonModal, FinancingOptionsForm, InsuranceRecommendations,
  LenderRecommendations, MarketAnalysisCard,
  MarketPosition, NegotiationCancelledScreen, NegotiationCompletedScreen, NegotiationTips,
  PriceComparison,
  PriceTrackingPanel, VehicleCard
} from './organisms';

// Export common components
export { ErrorBoundary } from './ErrorBoundary';
export { EmptyState } from './common/EmptyState';
export { ErrorState } from './common/ErrorState';
export { default as Footer } from './common/Footer';
export { default as Header } from './common/Header';
export { LoadingState } from './common/LoadingState';
export { default as ProgressStepper } from './common/ProgressStepper';

// Export vehicle components
export * from './vehicle';

// Export types
export type {
  ButtonProps, ButtonSize, ButtonVariant, CardComponentProps, InputProps, ModalProps, SpinnerProps
} from './atoms';

export type {
  MonthlyPaymentDisplayProps, PriceDisplayProps, PriceSwitcherProps,
  VehicleDetailsProps, VehicleImageProps, VehicleTitleProps
} from './molecules';

export type {
  VehicleDisplayProps
} from './organisms';

export type { BadgeProps } from './atoms/Badge';
export type { PaginationProps } from './molecules/Pagination';
