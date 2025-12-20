/**
 * Custom hook for managing vehicle comparison state
 */

import { useState, useCallback, useMemo } from 'react';

export interface ComparisonVehicle {
  vin: string;
  make: string;
  model: string;
  year: number;
  price: number;
  mileage: number;
  fuelType?: string;
  transmission?: string;
  condition?: string;
  image?: string;
  highlights?: string[];
  recommendation_score?: number | null;
}

const MAX_COMPARISON_VEHICLES = 3;

export function useComparison() {
  const [selectedVehicles, setSelectedVehicles] = useState<ComparisonVehicle[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const addVehicle = useCallback((vehicle: ComparisonVehicle) => {
    setSelectedVehicles((prev) => {
      // Check if vehicle is already selected
      if (prev.some((v) => v.vin === vehicle.vin)) {
        return prev;
      }
      
      // Check if we've reached the maximum
      if (prev.length >= MAX_COMPARISON_VEHICLES) {
        return prev;
      }

      return [...prev, vehicle];
    });
  }, []);

  const removeVehicle = useCallback((vin: string) => {
    setSelectedVehicles((prev) => prev.filter((v) => v.vin !== vin));
  }, []);

  const toggleVehicle = useCallback((vehicle: ComparisonVehicle) => {
    setSelectedVehicles((prev) => {
      const isSelected = prev.some((v) => v.vin === vehicle.vin);
      
      if (isSelected) {
        return prev.filter((v) => v.vin !== vehicle.vin);
      } else {
        if (prev.length >= MAX_COMPARISON_VEHICLES) {
          return prev;
        }
        return [...prev, vehicle];
      }
    });
  }, []);

  const clearAll = useCallback(() => {
    setSelectedVehicles([]);
  }, []);

  const isSelected = useCallback((vin: string) => {
    return selectedVehicles.some((v) => v.vin === vin);
  }, [selectedVehicles]);

  const canAddMore = useMemo(() => {
    return selectedVehicles.length < MAX_COMPARISON_VEHICLES;
  }, [selectedVehicles.length]);

  const canCompare = useMemo(() => {
    return selectedVehicles.length >= 2;
  }, [selectedVehicles.length]);

  const openModal = useCallback(() => {
    if (canCompare) {
      setIsModalOpen(true);
    }
  }, [canCompare]);

  const closeModal = useCallback(() => {
    setIsModalOpen(false);
  }, []);

  return {
    selectedVehicles,
    addVehicle,
    removeVehicle,
    toggleVehicle,
    clearAll,
    isSelected,
    canAddMore,
    canCompare,
    count: selectedVehicles.length,
    maxCount: MAX_COMPARISON_VEHICLES,
    isModalOpen,
    openModal,
    closeModal,
  };
}
