/**
 * Custom hook for managing vehicle filtering state
 */

import { useState, useCallback, useMemo } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';

export interface FilterState {
  priceMin?: number;
  priceMax?: number;
  mileageMin?: number;
  mileageMax?: number;
  yearMin?: number;
  yearMax?: number;
  fuelTypes: string[];
  transmission?: string;
  conditions: string[];
  features: string[];
}

const DEFAULT_FILTERS: FilterState = {
  priceMin: undefined,
  priceMax: undefined,
  mileageMin: undefined,
  mileageMax: undefined,
  yearMin: undefined,
  yearMax: undefined,
  fuelTypes: [],
  transmission: undefined,
  conditions: [],
  features: [],
};

export function useFilters() {
  const router = useRouter();
  const searchParams = useSearchParams();
  
  // Initialize filters from URL params
  const initialFilters = useMemo(() => {
    return {
      priceMin: searchParams.get('priceMin') ? Number(searchParams.get('priceMin')) : undefined,
      priceMax: searchParams.get('priceMax') ? Number(searchParams.get('priceMax')) : undefined,
      mileageMin: searchParams.get('mileageMin') ? Number(searchParams.get('mileageMin')) : undefined,
      mileageMax: searchParams.get('mileageMax') ? Number(searchParams.get('mileageMax')) : undefined,
      yearMin: searchParams.get('yearMin') ? Number(searchParams.get('yearMin')) : undefined,
      yearMax: searchParams.get('yearMax') ? Number(searchParams.get('yearMax')) : undefined,
      fuelTypes: searchParams.get('fuelTypes')?.split(',').filter(Boolean) || [],
      transmission: searchParams.get('transmission') || undefined,
      conditions: searchParams.get('conditions')?.split(',').filter(Boolean) || [],
      features: searchParams.get('features')?.split(',').filter(Boolean) || [],
    };
  }, [searchParams]);

  const [filters, setFilters] = useState<FilterState>(initialFilters);
  const [isOpen, setIsOpen] = useState(false);

  const updateFilter = useCallback((key: keyof FilterState, value: any) => {
    setFilters((prev) => ({
      ...prev,
      [key]: value,
    }));
  }, []);

  const updateFilters = useCallback((newFilters: Partial<FilterState>) => {
    setFilters((prev) => ({
      ...prev,
      ...newFilters,
    }));
  }, []);

  const resetFilters = useCallback(() => {
    setFilters(DEFAULT_FILTERS);
  }, []);

  const applyFilters = useCallback(() => {
    // Build query string from current filters
    const params = new URLSearchParams(searchParams.toString());
    
    // Update all filter params
    Object.entries(filters).forEach(([key, value]) => {
      if (value === undefined || value === null || 
          (Array.isArray(value) && value.length === 0)) {
        params.delete(key);
      } else if (Array.isArray(value)) {
        params.set(key, value.join(','));
      } else {
        params.set(key, String(value));
      }
    });

    // Navigate with new params
    router.push(`?${params.toString()}`);
    setIsOpen(false);
  }, [filters, router, searchParams]);

  const hasActiveFilters = useMemo(() => {
    return Object.entries(filters).some(([key, value]) => {
      if (Array.isArray(value)) {
        return value.length > 0;
      }
      return value !== undefined && value !== null;
    });
  }, [filters]);

  const activeFilterCount = useMemo(() => {
    let count = 0;
    if (filters.priceMin !== undefined || filters.priceMax !== undefined) count++;
    if (filters.mileageMin !== undefined || filters.mileageMax !== undefined) count++;
    if (filters.yearMin !== undefined || filters.yearMax !== undefined) count++;
    if (filters.fuelTypes.length > 0) count++;
    if (filters.transmission !== undefined) count++;
    if (filters.conditions.length > 0) count++;
    if (filters.features.length > 0) count++;
    return count;
  }, [filters]);

  return {
    filters,
    updateFilter,
    updateFilters,
    resetFilters,
    applyFilters,
    hasActiveFilters,
    activeFilterCount,
    isOpen,
    setIsOpen,
  };
}
