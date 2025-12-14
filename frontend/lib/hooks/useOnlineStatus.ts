'use client';

import { useState, useEffect } from 'react';

/**
 * Custom hook to track browser online/offline status
 * 
 * @example
 * ```tsx
 * const isOnline = useOnlineStatus();
 * 
 * return (
 *   <div>
 *     {!isOnline && (
 *       <div className="bg-yellow-100 p-2 text-center">
 *         You are currently offline
 *       </div>
 *     )}
 *   </div>
 * );
 * ```
 */
export function useOnlineStatus(): boolean {
  const [isOnline, setIsOnline] = useState(
    typeof navigator !== 'undefined' ? navigator.onLine : true
  );

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }

    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return isOnline;
}
