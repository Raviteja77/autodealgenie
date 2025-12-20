/**
 * Custom hook for managing view mode state
 */

import { useState, useCallback } from 'react';
import { useLocalStorage } from './useLocalStorage';

export type ViewMode = 'grid' | 'list' | 'compact';

const VIEW_MODE_STORAGE_KEY = 'vehicleViewMode';

export function useViewMode(defaultMode: ViewMode = 'grid') {
  const [storedMode, setStoredMode] = useLocalStorage<ViewMode>(
    VIEW_MODE_STORAGE_KEY,
    defaultMode
  );
  
  const [viewMode, setViewModeState] = useState<ViewMode>(storedMode);

  const setViewMode = useCallback((mode: ViewMode) => {
    setViewModeState(mode);
    setStoredMode(mode);
  }, [setStoredMode]);

  const isGridView = viewMode === 'grid';
  const isListView = viewMode === 'list';
  const isCompactView = viewMode === 'compact';

  return {
    viewMode,
    setViewMode,
    isGridView,
    isListView,
    isCompactView,
  };
}
