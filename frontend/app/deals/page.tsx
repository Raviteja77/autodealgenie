'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { apiClient, Deal } from '@/lib/api';

export default function DealsPage() {
  const [deals, setDeals] = useState<Deal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchDeals() {
      try {
        setLoading(true);
        const data = await apiClient.getDeals();
        setDeals(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch deals');
      } finally {
        setLoading(false);
      }
    }

    fetchDeals();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-300">Loading deals...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 dark:text-red-400 mb-4">Error: {error}</p>
          <p className="text-gray-600 dark:text-gray-300 mb-4">
            Make sure the backend API is running at {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}
          </p>
          <Link
            href="/"
            className="inline-block bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
          >
            Go Home
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Deals</h1>
            <p className="text-gray-600 dark:text-gray-300 mt-2">
              Manage your automotive deals
            </p>
          </div>
          <div className="flex gap-4">
            <Link
              href="/"
              className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded transition-colors"
            >
              Home
            </Link>
            <button
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded transition-colors"
              onClick={() => window.location.reload()}
            >
              Refresh
            </button>
          </div>
        </div>

        {deals.length === 0 ? (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8 text-center">
            <p className="text-gray-600 dark:text-gray-300 mb-4">
              No deals found. The backend is connected but no deals have been created yet.
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              You can create deals using the API at {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/docs
            </p>
          </div>
        ) : (
          <div className="grid gap-6">
            {deals.map((deal) => (
              <div
                key={deal.id}
                className="bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-lg transition-shadow p-6"
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                      {deal.vehicle_year} {deal.vehicle_make} {deal.vehicle_model}
                    </h3>
                    <p className="text-gray-600 dark:text-gray-300">
                      {deal.customer_name} ({deal.customer_email})
                    </p>
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-sm font-semibold ${getStatusColor(
                      deal.status
                    )}`}
                  >
                    {deal.status.replace('_', ' ').toUpperCase()}
                  </span>
                </div>
                <div className="grid md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">Mileage:</span>
                    <p className="font-semibold text-gray-900 dark:text-white">
                      {deal.vehicle_mileage.toLocaleString()} miles
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">Asking Price:</span>
                    <p className="font-semibold text-gray-900 dark:text-white">
                      ${deal.asking_price.toLocaleString()}
                    </p>
                  </div>
                  {deal.offer_price && (
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Offer Price:</span>
                      <p className="font-semibold text-gray-900 dark:text-white">
                        ${deal.offer_price.toLocaleString()}
                      </p>
                    </div>
                  )}
                </div>
                {deal.notes && (
                  <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                    <p className="text-gray-600 dark:text-gray-300 text-sm">{deal.notes}</p>
                  </div>
                )}
                <div className="mt-4 text-xs text-gray-500 dark:text-gray-400">
                  Created: {new Date(deal.created_at).toLocaleString()}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
