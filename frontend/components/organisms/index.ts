/**
 * Organisms - Complex UI sections combining multiple molecules and atoms
 * These are substantial, self-contained UI components that form major sections of the interface.
 */

export { VehicleCard } from './VehicleCard';
export { FilterPanel } from './FilterPanel';
export { ComparisonModal } from './ComparisonModal';
export { ComparisonBar } from './ComparisonBar';
export { ChatInput } from './ChatInput';
export { FinancingComparisonModal } from './FinancingComparisonModal';
export { InsuranceRecommendations } from './InsuranceRecommendations';
export { LenderRecommendations } from './LenderRecommendations';

// Search-related organisms
export {
  BasicVehicleFilters,
  AdvancedFilters,
  FinancingOptionsForm
} from './search';

// Export types that are explicitly exported from components
export type { VehicleDisplayProps } from './VehicleCard';
