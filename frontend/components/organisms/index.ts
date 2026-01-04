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
export { BasicVehicleFilters } from './BasicVehicleFilters';
export { AdvancedFilters } from './AdvancedFilters';
export { FinancingOptionsForm } from './FinancingOptionsForm';

// Evaluation-related organisms
export { EvaluationScoreCard } from './EvaluationScoreCard';
export { MarketAnalysisCard } from './MarketAnalysisCard';
export { MarketPosition } from './MarketPosition';
export { NegotiationTips } from './NegotiationTips';
export { PriceComparison } from './PriceComparison';

// Negotiation-related organisms
export { PriceTrackingPanel } from './PriceTrackingPanel';
export { CurrentOfferStatus } from './CurrentOfferStatus';
export { NegotiationCompletedScreen } from './NegotiationCompletedScreen';
export { NegotiationCancelledScreen } from './NegotiationCancelledScreen';

// Export types that are explicitly exported from components
export type { VehicleDisplayProps } from './VehicleCard';
