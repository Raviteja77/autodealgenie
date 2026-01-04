/**
 * Molecules - Simple combinations of atoms forming functional UI patterns
 * These are relatively simple components that combine a few atoms together.
 */

export { PriceDisplay, MonthlyPaymentDisplay, PriceSwitcher } from './PriceDisplay';
export { VehicleTitle, VehicleDetails, VehicleImage } from './VehicleInfo';
export { ViewModeToggle } from './ViewModeToggle';
export { SortDropdown, type SortOption } from './SortDropdown';
export { SavedSearchesDropdown } from './SavedSearchesDropdown';
export { ConnectionStatusIndicator } from './ConnectionStatusIndicator';
export { SaveSearchModal } from './SaveSearchModal';

// Search-related molecules
export { PaymentMethodSelector } from './PaymentMethodSelector';
export { BudgetRangeSlider } from './BudgetRangeSlider';
export { SearchSidebar } from './SearchSidebar';

// Evaluation-related molecules
export { DealScoreDisplay } from './DealScoreDisplay';
export { KeyInsightsList } from './KeyInsightsList';
export { TalkingPointsList } from './TalkingPointsList';
export { MarketInsights } from './MarketInsights';

export type {
  PriceDisplayProps,
  MonthlyPaymentDisplayProps,
  PriceSwitcherProps,
} from './PriceDisplay.types';

export type {
  VehicleDetailsProps,
  VehicleTitleProps,
  VehicleImageProps,
} from './VehicleInfo.types';
