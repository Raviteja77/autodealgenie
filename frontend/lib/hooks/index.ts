/**
 * Custom React Hooks
 * 
 * This module exports all custom hooks for the AutoDealGenie frontend.
 */

export { useApi } from './useApi';
export { useDebounce } from './useDebounce';
export { useLocalStorage } from './useLocalStorage';
export { useOnlineStatus } from './useOnlineStatus';
export { useFilters } from './useFilters';
export { useComparison } from './useComparison';
export { useViewMode } from './useViewMode';
export { useSavedSearches } from './useSavedSearches';
export { useNegotiationState } from './useNegotiationState';
export { useFinancingCalculation, useAffordability } from './useFinancing';
export { useDisplayMode } from './useDisplayMode';

export type { CurrentOfferStatus, OfferInfo, NegotiationStateData } from './useNegotiationState';
export type { FilterState } from './useFilters';
export type { ComparisonVehicle } from './useComparison';
export type { FinancingParams, PaymentCalculation } from './useFinancing';
export type { DisplayMode, UseDisplayModeOptions } from './useDisplayMode';
