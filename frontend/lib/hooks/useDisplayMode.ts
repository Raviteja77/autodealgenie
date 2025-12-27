/**
 * Custom hook for managing vehicle display mode (cash vs monthly payment)
 */

import { useState, useCallback } from 'react';

export type DisplayMode = 'cash' | 'monthly';

export interface UseDisplayModeOptions {
  defaultMode?: DisplayMode;
  allowToggle?: boolean;
}

export function useDisplayMode(options: UseDisplayModeOptions = {}) {
  const { defaultMode = 'cash', allowToggle = true } = options;
  
  const [displayMode, setDisplayMode] = useState<DisplayMode>(defaultMode);

  const toggleMode = useCallback(() => {
    if (!allowToggle) return;
    
    setDisplayMode((prev) => (prev === 'cash' ? 'monthly' : 'cash'));
  }, [allowToggle]);

  const setToCash = useCallback(() => {
    setDisplayMode('cash');
  }, []);

  const setToMonthly = useCallback(() => {
    setDisplayMode('monthly');
  }, []);

  return {
    displayMode,
    isCashMode: displayMode === 'cash',
    isMonthlyMode: displayMode === 'monthly',
    toggleMode,
    setToCash,
    setToMonthly,
    setDisplayMode,
  };
}
