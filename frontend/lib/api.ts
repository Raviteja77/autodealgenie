/**
 * API Client for AutoDealGenie
 * Handles communication with the FastAPI backend
 */

import { createErrorFromResponse, NetworkError, isApiError } from "./errors";

// TypeScript type definitions matching backend schemas

export interface Deal {
  id: number;
  customer_name: string;
  customer_email: string;
  vehicle_make: string;
  vehicle_model: string;
  vehicle_year: number;
  vehicle_mileage: number;
  vehicle_vin: string;
  asking_price: number;
  offer_price?: number | null;
  status: "pending" | "in_progress" | "completed" | "cancelled";
  notes?: string | null;
  created_at: string;
  updated_at?: string | null;
}

export interface DealCreate {
  customer_name: string;
  customer_email: string;
  vehicle_make: string;
  vehicle_model: string;
  vehicle_year: number;
  vehicle_mileage: number;
  vehicle_vin: string;
  asking_price: number;
  offer_price?: number | null;
  status?: "pending" | "in_progress" | "completed" | "cancelled";
  notes?: string | null;
}

export interface DealEvaluationRequest {
  vehicle_vin: string;
  asking_price: number;
  condition: string;
  mileage: number;
}

export interface DealEvaluationResponse {
  fair_value: number;
  score: number;
  insights: string[];
  talking_points: string[];
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
  max_results?: number; // Maximum number of results to analyze (default: 50)
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

// Evaluation types
export type EvaluationStatus = "analyzing" | "awaiting_input" | "completed";
export type PipelineStep =
  | "vehicle_condition"
  | "price"
  | "financing"
  | "risk"
  | "final";

export interface EvaluationResponse {
  id: number;
  user_id: number;
  deal_id: number;
  status: EvaluationStatus;
  current_step: PipelineStep;
  result_json: Record<string, any> | null;
  created_at: string;
  updated_at: string | null;
}

export interface EvaluationStepResult {
  evaluation_id: number;
  deal_id: number;
  status: EvaluationStatus;
  current_step: PipelineStep;
  step_result: {
    questions?: string[];
    required_fields?: string[];
    assessment?: Record<string, any>;
    completed?: boolean;
  };
  result_json: Record<string, any> | null;
}

export interface EvaluationInitiateRequest {
  answers?: Record<string, string | number> | null;
}

export type NegotiationStatus = "active" | "completed" | "cancelled";
export type MessageRole = "user" | "agent" | "dealer_sim";
export type UserAction = "confirm" | "reject" | "counter";
export interface EvaluationAnswerRequest {
  answers: Record<string, string | number>;
}

export interface LenderInfo {
  lender_id: string;
  name: string;
  description: string;
  logo_url?: string;
  min_credit_score: number;
  max_credit_score: number;
  min_loan_amount: number;
  max_loan_amount: number;
  min_term_months: number;
  max_term_months: number;
  apr_range_min: number;
  apr_range_max: number;
  features: string[];
  benefits: string[];
  affiliate_url: string;
  referral_code?: string;
}

export interface LenderMatch {
  lender: LenderInfo;
  match_score: number;
  estimated_apr: number;
  estimated_monthly_payment: number;
  recommendation_reason: string;
  rank: number;
}

export interface LenderRecommendationResponse {
  recommendations: LenderMatch[];
  total_matches: number;
  request_summary: Record<string, any>;
}

// Insurance types
export interface InsuranceProviderInfo {
  provider_id: string;
  name: string;
  description: string;
  logo_url?: string;
  coverage_types: string[];
  min_vehicle_value: number;
  max_vehicle_value: number;
  min_driver_age: number;
  max_driver_age: number;
  premium_range_min: number;
  premium_range_max: number;
  features: string[];
  benefits: string[];
  affiliate_url: string;
  referral_code?: string;
}

export interface InsuranceMatch {
  provider: InsuranceProviderInfo;
  match_score: number;
  estimated_monthly_premium: number;
  estimated_annual_premium: number;
  recommendation_reason: string;
  rank: number;
}

export interface InsuranceRecommendationRequest {
  vehicle_value: number;
  vehicle_age: number;
  vehicle_make: string;
  vehicle_model: string;
  coverage_type: "liability" | "comprehensive" | "full";
  driver_age: number;
}

export interface InsuranceRecommendationResponse {
  recommendations: InsuranceMatch[];
  total_matches: number;
  request_summary: Record<string, any>;
}

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

export interface FinancingOption {
  loan_amount: number;
  down_payment: number;
  monthly_payment_estimate: number;
  loan_term_months: number;
  estimated_apr: number;
  total_cost: number;
  total_interest: number;
}

export interface NegotiationRoundMetadata {
  suggested_price: number;
  asking_price: number;
  user_action?: string | null;
  financing_options?: FinancingOption[] | null;
  cash_savings?: number | null;
}

export interface NextRoundResponse {
  session_id: number;
  status: NegotiationStatus;
  current_round: number;
  agent_message: string;
  metadata: NegotiationRoundMetadata;
}

export interface ChatMessageRequest {
  message: string;
  message_type?: string;
}

export interface ChatMessageResponse {
  session_id: number;
  status: NegotiationStatus;
  user_message: NegotiationMessage;
  agent_message: NegotiationMessage;
}

export interface DealerInfoRequest {
  info_type: string;
  content: string;
  price_mentioned?: number | null;
  metadata?: Record<string, any> | null;
}

export interface DealerInfoResponse {
  session_id: number;
  status: NegotiationStatus;
  analysis: string;
  recommended_action?: string | null;
  user_message: NegotiationMessage;
  agent_message: NegotiationMessage;
}

export interface LenderInfo {
  lender_id: string;
  name: string;
  description: string;
  logo_url?: string | undefined;
  min_credit_score: number;
  max_credit_score: number;
  min_loan_amount: number;
  max_loan_amount: number;
  min_term_months: number;
  max_term_months: number;
  apr_range_min: number;
  apr_range_max: number;
  features: string[];
  benefits: string[];
  affiliate_url: string;
  referral_code?: string | undefined;
}

export interface LenderMatch {
  lender: LenderInfo;
  match_score: number;
  estimated_apr: number;
  estimated_monthly_payment: number;
  recommendation_reason: string;
  rank: number;
}

export interface LenderRecommendationResponse {
  recommendations: LenderMatch[];
  total_matches: number;
  request_summary: Record<string, any>;
}

export interface SavedSearch {
  id: number;
  user_id: number;
  name: string;
  make?: string | null;
  model?: string | null;
  budget_min?: number | null;
  budget_max?: number | null;
  car_type?: string | null;
  year_min?: number | null;
  year_max?: number | null;
  mileage_max?: number | null;
  fuel_type?: string | null;
  transmission?: string | null;
  condition?: string | null;
  user_priorities?: string | null;
  notification_enabled: boolean;
  new_matches_count: number;
  last_checked?: string | null;
  created_at: string;
  updated_at?: string | null;
}

export interface SavedSearchCreate {
  name: string;
  make?: string;
  model?: string;
  budget_min?: number;
  budget_max?: number;
  car_type?: string;
  year_min?: number;
  year_max?: number;
  mileage_max?: number;
  fuel_type?: string;
  transmission?: string;
  condition?: string;
  user_priorities?: string;
  notification_enabled?: boolean;
}

export interface SavedSearchList {
  searches: SavedSearch[];
  total: number;
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
    } else if (
      endpoint.includes("/api/v1/deals") &&
      endpoint.includes("evaluation")
    ) {
      // Map evaluation endpoints to mock
      const match = endpoint.match(
        /\/api\/v1\/deals\/(\d+)\/evaluation(?:\/(\d+))?(?:\/answers)?/
      );
      if (match) {
        const dealId = match[1];
        const evaluationId = match[2];

        if (endpoint.includes("/answers")) {
          return `/mock/evaluation/pipeline/${dealId}/evaluation/${evaluationId}/answers`;
        } else if (evaluationId) {
          return `/mock/evaluation/pipeline/${dealId}/evaluation/${evaluationId}`;
        } else {
          return `/mock/evaluation/pipeline/${dealId}/evaluation`;
        }
      }
      return endpoint.replace("/api/v1/deals", "/mock/evaluation/pipeline");
    }

    return endpoint;
  }

  /**
   * Generic request method with authentication support and structured error handling
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
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

        const errorMessage =
          errorData.detail ||
          errorData.message ||
          `Request failed: ${response.statusText}`;

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
      throw new NetworkError(
        "Failed to connect to the server. Please check your internet connection."
      );
    }
  }

  /**
   * Fetch all deals from the backend
   */
  async getDeals(): Promise<Deal[]> {
    return this.request<Deal[]>("/api/v1/deals");
  }

  /**
   * Create a new deal
   */
  async createDeal(deal: DealCreate): Promise<Deal> {
    return this.request<Deal>("/api/v1/deals", {
      method: "POST",
      body: JSON.stringify(deal),
    });
  }

  /**
   * Evaluate a deal with AI analysis
   */
  async evaluateDeal(request: DealEvaluationRequest): Promise<DealEvaluationResponse> {
    return this.request<DealEvaluationResponse>("/api/v1/deals/evaluate", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  hasMeaningfulValue(value: unknown): boolean {
    if (value === null || value === undefined) {
      return false;
    }
    if (typeof value === "string") {
      return value.trim().length > 0;
    }
    if (typeof value === "number") {
      return !Number.isNaN(value);
    }
    if (typeof value === "boolean") {
      return true;
    }
    if (Array.isArray(value)) {
      return value.some((item) => this.hasMeaningfulValue(item));
    }
    if (typeof value === "object") {
      return Object.values(value as Record<string, unknown>).some(
        (item) => this.hasMeaningfulValue(item)
      );
    }
    return false;
  };

  /**
   * Search for cars with AI recommendations
   */
  async searchCars(params: CarSearchRequest): Promise<CarSearchResponse> {
    // Check if all fields are null or empty
    const hasSomeValue = this.hasMeaningfulValue(params);

    if (!hasSomeValue) {
      throw new Error("At least one search criteria must be provided.");
    }
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
   * Start or continue a deal evaluation
   */
  async startEvaluation(
    dealId: number,
    request: EvaluationInitiateRequest
  ): Promise<EvaluationStepResult> {
    return this.request<EvaluationStepResult>(
      `/api/v1/deals/${dealId}/evaluation`,
      {
        method: "POST",
        body: JSON.stringify(request),
      }
    );
  }

  //  * Create a new negotiation session
  //  */
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
   * Get evaluation status
   */
  async getEvaluation(
    dealId: number,
    evaluationId: number
  ): Promise<EvaluationResponse> {
    return this.request<EvaluationResponse>(
      `/api/v1/deals/${dealId}/evaluation/${evaluationId}`
    );
  }

  /**
   * Submit answers to evaluation questions
   */
  async submitEvaluationAnswers(
    dealId: number,
    evaluationId: number,
    request: EvaluationAnswerRequest
  ): Promise<EvaluationStepResult> {
    return this.request<EvaluationStepResult>(
      `/api/v1/deals/${dealId}/evaluation/${evaluationId}/answers`,
      {
        method: "POST",
        body: JSON.stringify(request),
      }
    );
  }

  /**
   * Get lender recommendations for a deal evaluation
   */
  async getEvaluationLenders(
    dealId: number,
    evaluationId: number
  ): Promise<LenderRecommendationResponse> {
    return this.request<LenderRecommendationResponse>(
      `/api/v1/deals/${dealId}/evaluation/${evaluationId}/lenders`,
      {
        method: "GET",
      }
    );
  }

  //  * Get a negotiation session with full message history
  //  */
  async getNegotiationSession(sessionId: number): Promise<NegotiationSession> {
    return this.request<NegotiationSession>(
      `/api/v1/negotiations/${sessionId}`
    );
  }

  /**
   * Get lender recommendations for a negotiation session
   */
  async getNegotiationLenderRecommendations(
    sessionId: number,
    loanTermMonths: number = 60,
    creditScoreRange: string = "good"
  ): Promise<LenderRecommendationResponse> {
    return this.request<LenderRecommendationResponse>(
      `/api/v1/negotiations/${sessionId}/lender-recommendations?loan_term_months=${loanTermMonths}&credit_score_range=${creditScoreRange}`
    );
  }

  /**
   * Send a free-form chat message during negotiation
   */
  async sendChatMessage(
    sessionId: number,
    request: ChatMessageRequest
  ): Promise<ChatMessageResponse> {
    return this.request<ChatMessageResponse>(
      `/api/v1/negotiations/${sessionId}/chat`,
      {
        method: "POST",
        body: JSON.stringify(request),
      }
    );
  }

  /**
   * Submit dealer-provided information for analysis
   */
  async submitDealerInfo(
    sessionId: number,
    request: DealerInfoRequest
  ): Promise<DealerInfoResponse> {
    return this.request<DealerInfoResponse>(
      `/api/v1/negotiations/${sessionId}/dealer-info`,
      {
        method: "POST",
        body: JSON.stringify(request),
      }
    );
  }

  //  * Get all saved searches for the current user
  //  */
  async getSavedSearches(): Promise<SavedSearchList> {
    return this.request<SavedSearchList>("/api/v1/saved-searches");
  }

  /**
   * Create a new saved search
   */
  async createSavedSearch(search: SavedSearchCreate): Promise<SavedSearch> {
    return this.request<SavedSearch>("/api/v1/saved-searches", {
      method: "POST",
      body: JSON.stringify(search),
    });
  }

  /**
   * Delete a saved search
   */
  async deleteSavedSearch(searchId: number): Promise<void> {
    return this.request<void>(`/api/v1/saved-searches/${searchId}`, {
      method: "DELETE",
    });
  }
}

// Export a singleton instance
export const apiClient = new ApiClient();
