/**
 * API Client for AutoDealGenie
 * Handles communication with the FastAPI backend
 */

import {
  createErrorFromResponse,
  NetworkError,
  isApiError,
} from './errors';

// TypeScript type definitions matching backend schemas

export interface Deal {
  id: number;
  customer_name: string;
  customer_email: string;
  vehicle_make: string;
  vehicle_model: string;
  vehicle_year: number;
  vehicle_mileage: number;
  asking_price: number;
  offer_price?: number | null;
  status: "pending" | "in_progress" | "completed" | "cancelled";
  notes?: string | null;
  created_at: string;
  updated_at?: string | null;
}

export interface CarSearchRequest {
  make?: string;
  model?: string;
  budget_min?: number;
  budget_max?: number;
  car_type?: string;
  year_min?: number;
  year_max?: number;
  mileage_max?: number;
  user_priorities?: string;
}

export interface SearchCriteria {
  make?: string | null;
  model?: string | null;
  price_min?: number | null;
  price_max?: number | null;
  condition?: string | null;
  year_min?: number | null;
  year_max?: number | null;
  mileage_max?: number | null;
  location?: string | null;
}

export interface VehicleRecommendation {
  vin?: string | null;
  make?: string | null;
  model?: string | null;
  year?: number | null;
  trim?: string | null;
  mileage?: number | null;
  price?: number | null;
  msrp?: number | null;
  location?: string | null;
  dealer_name?: string | null;
  dealer_contact?: string | null;
  photo_links?: string[];
  vdp_url?: string | null;
  exterior_color?: string | null;
  interior_color?: string | null;
  drivetrain?: string | null;
  transmission?: string | null;
  engine?: string | null;
  fuel_type?: string | null;
  carfax_1_owner?: boolean | null;
  carfax_clean_title?: boolean | null;
  inventory_type?: string | null;
  days_on_market?: number | null;
  recommendation_score?: number | null;
  highlights?: string[];
  recommendation_summary?: string | null;
}

export interface CarSearchResponse {
  search_criteria: SearchCriteria;
  top_vehicles: VehicleRecommendation[];
  total_found: number;
  total_analyzed: number;
  message?: string | null;
}

/**
 * API Client class for making requests to the backend
 */
class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  }

  /**
   * Generic request method with authentication support and structured error handling
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    // Always include credentials (cookies)
    const config: RequestInit = {
      ...options,
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        // Try to parse error response
        const errorData = await response
          .json()
          .catch(() => ({ detail: response.statusText }));
        
        const errorMessage = errorData.detail || errorData.message || `Request failed: ${response.statusText}`;
        
        // Create and throw structured error
        throw createErrorFromResponse(response.status, errorMessage, errorData);
      }

      return response.json();
    } catch (error) {
      // Re-throw if it's already a structured API error (use type guard)
      if (isApiError(error)) {
        throw error;
      }
      
      // Otherwise, it's likely a network error
      throw new NetworkError('Failed to connect to the server. Please check your internet connection.');
    }
  }

  /**
   * Fetch all deals from the backend
   */
  async getDeals(): Promise<Deal[]> {
    return this.request<Deal[]>("/api/v1/deals");
  }

  /**
   * Search for cars with AI recommendations
   */
  async searchCars(params: CarSearchRequest): Promise<CarSearchResponse> {
    const queryParams = new URLSearchParams();

    if (params.make) queryParams.append("make", params.make);
    if (params.model) queryParams.append("model", params.model);
    if (params.budget_min !== undefined)
      queryParams.append("budget_min", params.budget_min.toString());
    if (params.budget_max !== undefined)
      queryParams.append("budget_max", params.budget_max.toString());
    if (params.car_type) queryParams.append("car_type", params.car_type);
    if (params.year_min !== undefined)
      queryParams.append("year_min", params.year_min.toString());
    if (params.year_max !== undefined)
      queryParams.append("year_max", params.year_max.toString());
    if (params.mileage_max !== undefined)
      queryParams.append("mileage_max", params.mileage_max.toString());
    if (params.user_priorities)
      queryParams.append("user_priorities", params.user_priorities);

    const queryString = queryParams.toString()
      ? "?" + queryParams.toString()
      : "";
    return this.request<CarSearchResponse>(`/api/v1/cars/search${queryString}`, {
      method: "POST",
    });
  }
}

// Export a singleton instance
export const apiClient = new ApiClient();
