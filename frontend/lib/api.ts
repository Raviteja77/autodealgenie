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

export interface Favorite {
  id: string;
  user_id: number;
  vin: string;
  make: string;
  model: string;
  year: number;
  price: number;
  mileage: number;
  fuel_type?: string | null;
  location?: string | null;
  color?: string | null;
  condition?: string | null;
  image?: string | null;
  created_at: string;
}

export interface FavoriteCreate {
  vin: string;
  make: string;
  model: string;
  year: number;
  price: number;
  mileage: number;
  fuel_type?: string | null;
  location?: string | null;
  color?: string | null;
  condition?: string | null;
  image?: string | null;
}

export type NegotiationStatus = "active" | "completed" | "cancelled";
export type MessageRole = "user" | "agent" | "dealer_sim";
export type UserAction = "confirm" | "reject" | "counter";

export interface NegotiationMessage {
  id: number;
  session_id: number;
  role: MessageRole;
  content: string;
  round_number: number;
  metadata?: Record<string, unknown> | null;
  created_at: string;
}

export interface NegotiationSession {
  id: number;
  user_id: number;
  deal_id: number;
  status: NegotiationStatus;
  current_round: number;
  max_rounds: number;
  created_at: string;
  updated_at?: string | null;
  messages: NegotiationMessage[];
}

export interface CreateNegotiationRequest {
  deal_id: number;
  user_target_price: number;
  strategy?: string | null;
}

export interface CreateNegotiationResponse {
  session_id: number;
  status: NegotiationStatus;
  current_round: number;
  agent_message: string;
  metadata: Record<string, unknown>;
}

export interface NextRoundRequest {
  user_action: UserAction;
  counter_offer?: number | null;
}

export interface NextRoundResponse {
  session_id: number;
  status: NegotiationStatus;
  current_round: number;
  agent_message: string;
  metadata: Record<string, unknown>;
}

/**
 * API Client class for making requests to the backend
 */
class ApiClient {
  private baseUrl: string;
  private useMock: boolean;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    this.useMock = process.env.NEXT_PUBLIC_USE_MOCK === "true";
  }

  /**
   * Get the appropriate endpoint path based on mock mode
   */
  private getEndpointPath(endpoint: string): string {
    if (!this.useMock) {
      return endpoint;
    }

    // Map real endpoints to mock endpoints
    if (endpoint.includes("/api/v1/cars/search")) {
      return "/mock/marketcheck/search";
    } else if (endpoint.includes("/api/v1/negotiations")) {
      const parts = endpoint.replace("/api/v1/negotiations", "").split("/");
      if (parts.length === 1 || parts[1] === "") {
        return "/mock/negotiation/create";
      } else if (parts[2] === "next") {
        return `/mock/negotiation/${parts[1]}/next`;
      } else {
        return `/mock/negotiation/${parts[1]}`;
      }
    } else if (endpoint.includes("/api/v1/deals") && endpoint.includes("evaluation")) {
      return endpoint.replace("/api/v1/deals", "/mock/evaluation/pipeline");
    }

    return endpoint;
  }

  /**
   * Generic request method with authentication support and structured error handling
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
  ): Promise<T> {
    // Map to mock endpoint if needed
    const mappedEndpoint = this.getEndpointPath(endpoint);
    const url = `${this.baseUrl}${mappedEndpoint}`;

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
    return this.request<CarSearchResponse>(`/api/v1/cars/search`, {
      method: "POST",
      body: JSON.stringify(params),
    });
  }

  /**
   * Get all favorites for the current user
   */
  async getFavorites(): Promise<Favorite[]> {
    return this.request<Favorite[]>("/api/v1/favorites");
  }

  /**
   * Add a car to favorites
   */
  async addFavorite(favorite: FavoriteCreate): Promise<Favorite> {
    return this.request<Favorite>("/api/v1/favorites", {
      method: "POST",
      body: JSON.stringify(favorite),
    });
  }

  /**
   * Remove a car from favorites
   */
  async removeFavorite(vin: string): Promise<void> {
    return this.request<void>(`/api/v1/favorites/${vin}`, {
      method: "DELETE",
    });
  }

  /**
   * Check if a specific vehicle is in favorites
   */
  async checkFavorite(vin: string): Promise<Favorite> {
    return this.request<Favorite>(`/api/v1/favorites/${vin}`);
  }

  /**
   * Create a new negotiation session
   */
  async createNegotiation(
    request: CreateNegotiationRequest
  ): Promise<CreateNegotiationResponse> {
    return this.request<CreateNegotiationResponse>("/api/v1/negotiations/", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  /**
   * Process the next round of negotiation
   */
  async processNextRound(
    sessionId: number,
    request: NextRoundRequest
  ): Promise<NextRoundResponse> {
    return this.request<NextRoundResponse>(
      `/api/v1/negotiations/${sessionId}/next`,
      {
        method: "POST",
        body: JSON.stringify(request),
      }
    );
  }

  /**
   * Get a negotiation session with full message history
   */
  async getNegotiationSession(sessionId: number): Promise<NegotiationSession> {
    return this.request<NegotiationSession>(
      `/api/v1/negotiations/${sessionId}`
    );
  }
}

// Export a singleton instance
export const apiClient = new ApiClient();
