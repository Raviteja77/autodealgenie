import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import EvaluationPage from '../page';
import { apiClient } from '@/lib/api';

// Mock dependencies
jest.mock('@/lib/api');
jest.mock('@/app/context', () => ({
  useStepper: () => ({
    completeStep: jest.fn(),
    getStepData: jest.fn(() => null),
    setStepData: jest.fn(),
  }),
}));

jest.mock('@/lib/auth', () => ({
  useAuth: () => ({
    user: {
      email: 'test@example.com',
      full_name: 'Test User',
      username: 'testuser',
    },
    isAuthenticated: true,
    login: jest.fn(),
    logout: jest.fn(),
    signup: jest.fn(),
  }),
}));

jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    back: jest.fn(),
  }),
  useSearchParams: () => ({
    get: (key: string) => {
      const params: Record<string, string> = {
        vin: 'TEST123456789',
        make: 'Toyota',
        model: 'Camry',
        year: '2020',
        price: '25000',
        mileage: '30000',
        fuelType: 'Gasoline',
        zipCode: '90210',
      };
      return params[key] || null;
    },
  }),
}));

const mockEvaluationData = {
  fair_value: 23500,
  score: 8.5,
  insights: [
    'Price is below market average',
    'Vehicle has low mileage for its age',
    'Good condition based on inspection',
  ],
  talking_points: [
    'Mention lower prices for similar vehicles in the area',
    'Highlight the high mileage compared to similar models',
    'Ask about any warranty options',
  ],
};

describe('EvaluationPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock API client methods
    (apiClient.evaluateDeal as jest.Mock).mockResolvedValue(mockEvaluationData);
    (apiClient.getDealByEmailAndVin as jest.Mock).mockResolvedValue({
      id: 1,
      customer_email: 'test@example.com',
      vehicle_vin: 'TEST123456789',
    });
    (apiClient.createDeal as jest.Mock).mockResolvedValue({
      id: 1,
      customer_email: 'test@example.com',
      vehicle_vin: 'TEST123456789',
    });
    (apiClient.updateDeal as jest.Mock).mockResolvedValue({
      id: 1,
      status: 'in_progress',
    });
  });

  it('renders loading state initially', () => {
    (apiClient.evaluateDeal as jest.Mock).mockImplementation(
      () => new Promise(() => {}) // Never resolves to keep loading
    );

    render(<EvaluationPage />);
    
    expect(screen.getByText(/Evaluating Deal/i)).toBeInTheDocument();
  });

  it('displays evaluation results after successful API call', async () => {
    (apiClient.evaluateDeal as jest.Mock).mockResolvedValue(mockEvaluationData);

    render(<EvaluationPage />);

    await waitFor(() => {
      expect(screen.getByText(/2020 Toyota Camry/i)).toBeInTheDocument();
    });

    // Check if score is displayed
    expect(screen.getByText('8.5')).toBeInTheDocument();
    expect(screen.getByText('/10')).toBeInTheDocument();

    // Check if recommendation is shown
    expect(screen.getByText(/Excellent Deal/i)).toBeInTheDocument();
  });

  it('displays key insights section', async () => {
    (apiClient.evaluateDeal as jest.Mock).mockResolvedValue(mockEvaluationData);

    render(<EvaluationPage />);

    await waitFor(() => {
      expect(screen.getByText(/Key Market Insights/i)).toBeInTheDocument();
    });

    // Check if insights are displayed
    mockEvaluationData.insights.forEach((insight) => {
      expect(screen.getByText(insight)).toBeInTheDocument();
    });
  });

  it('displays negotiation talking points section', async () => {
    (apiClient.evaluateDeal as jest.Mock).mockResolvedValue(mockEvaluationData);

    render(<EvaluationPage />);

    await waitFor(() => {
      expect(screen.getByText(/Negotiation Talking Points/i)).toBeInTheDocument();
    });

    // Check if talking points are displayed
    mockEvaluationData.talking_points.forEach((point) => {
      expect(screen.getByText(point)).toBeInTheDocument();
    });
  });

  it('shows correct score color and icon for excellent deal', async () => {
    (apiClient.evaluateDeal as jest.Mock).mockResolvedValue({
      ...mockEvaluationData,
      score: 9.0,
    });

    render(<EvaluationPage />);

    await waitFor(() => {
      expect(screen.getByText('9.0')).toBeInTheDocument();
    });

    expect(screen.getByText(/Excellent Deal - Highly Recommended/i)).toBeInTheDocument();
  });

  it('handles API errors gracefully', async () => {
    (apiClient.evaluateDeal as jest.Mock).mockRejectedValue(
      new Error('Failed to evaluate deal')
    );

    render(<EvaluationPage />);

    // Wait for error to be displayed
    await waitFor(() => {
      expect(screen.queryByText(/Evaluating Deal/i)).not.toBeInTheDocument();
    });

    // After error, component should show error state or allow retry
    // The evaluation component may handle errors differently, so we test for basic error recovery
    expect(screen.queryByText('8.5')).not.toBeInTheDocument();
  });

  it('displays vehicle summary with all details', async () => {
    (apiClient.evaluateDeal as jest.Mock).mockResolvedValue(mockEvaluationData);

    render(<EvaluationPage />);

    await waitFor(() => {
      const vehicleSummary = screen.getByText(/2020 Toyota Camry/i);
      expect(vehicleSummary).toBeInTheDocument();
    });

    // Check mileage
    expect(screen.getByText(/30,000 miles/i)).toBeInTheDocument();

    // Check VIN
    expect(screen.getByText(/TEST123456789/i)).toBeInTheDocument();
  });
});
