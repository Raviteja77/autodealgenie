/**
 * Custom hook for managing saved searches
 */

import { useState, useEffect, useCallback } from 'react';
import { apiClient, SavedSearch, SavedSearchCreate, SavedSearchList } from '../api';

export function useSavedSearches() {
  const [searches, setSearches] = useState<SavedSearch[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);

  const fetchSearches = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data: SavedSearchList = await apiClient.getSavedSearches();
      setSearches(data.searches);
      setTotal(data.total);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load saved searches';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const createSearch = useCallback(async (search: SavedSearchCreate) => {
    setError(null);
    try {
      const newSearch = await apiClient.createSavedSearch(search);
      setSearches((prev) => [newSearch, ...prev]);
      setTotal((prev) => prev + 1);
      return newSearch;
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create saved search';
      setError(errorMessage);
      throw err;
    }
  }, []);

  const deleteSearch = useCallback(async (searchId: number) => {
    setError(null);
    try {
      await apiClient.deleteSavedSearch(searchId);
      setSearches((prev) => prev.filter((s) => s.id !== searchId));
      setTotal((prev) => prev - 1);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete saved search';
      setError(errorMessage);
      throw err;
    }
  }, []);

  const totalNewMatches = searches.reduce((sum, search) => sum + search.new_matches_count, 0);

  useEffect(() => {
    fetchSearches();
  }, [fetchSearches]);

  return {
    searches,
    isLoading,
    error,
    total,
    totalNewMatches,
    fetchSearches,
    createSearch,
    deleteSearch,
  };
}
