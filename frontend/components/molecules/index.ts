/**
 * Molecules - Simple combinations of atoms forming functional UI patterns
 * These are relatively simple components that combine a few atoms together.
 */

export { ConnectionStatusIndicator } from './ConnectionStatusIndicator';
export { Pagination } from './Pagination';
export { MonthlyPaymentDisplay, PriceDisplay, PriceSwitcher } from './PriceDisplay';
export { SaveSearchModal } from './SaveSearchModal';
export { SavedSearchesDropdown } from './SavedSearchesDropdown';
export { SortDropdown, type SortOption } from './SortDropdown';
export { VehicleDetails, VehicleImage, VehicleTitle } from './VehicleInfo';
export { ViewModeToggle } from './ViewModeToggle';

// Search-related molecules
export { BudgetRangeSlider } from './BudgetRangeSlider';
export { PaymentMethodSelector } from './PaymentMethodSelector';
export { SearchSidebar } from './SearchSidebar';

// Evaluation-related molecules
export { DealScoreDisplay } from './DealScoreDisplay';
export { KeyInsightsList } from './KeyInsightsList';
export { MarketInsights } from './MarketInsights';
export { TalkingPointsList } from './TalkingPointsList';

export type {
  MonthlyPaymentDisplayProps, PriceDisplayProps, PriceSwitcherProps
} from './PriceDisplay.types';

export type {
  VehicleDetailsProps, VehicleImageProps, VehicleTitleProps
} from './VehicleInfo.types';

export type { PaginationProps } from './Pagination';