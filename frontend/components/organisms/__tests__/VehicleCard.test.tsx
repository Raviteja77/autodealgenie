import { render, screen, fireEvent } from '@testing-library/react';
import { VehicleCard } from '../VehicleCard';

describe('VehicleCard', () => {
  const mockVehicle = {
    vin: 'TEST123456',
    make: 'Toyota',
    model: 'Camry',
    year: 2023,
    price: 25000,
    mileage: 15000,
    fuelType: 'Gasoline',
    location: 'Los Angeles, CA',
    color: 'Silver',
    condition: 'Used',
    image: '/test-image.jpg',
  };

  it('renders vehicle information', () => {
    render(<VehicleCard vehicle={mockVehicle} />);

    expect(screen.getByText('2023 Toyota Camry')).toBeInTheDocument();
    expect(screen.getByText(/\$25,000/)).toBeInTheDocument();
    expect(screen.getByText(/15,000/)).toBeInTheDocument();
  });

  it('displays vehicle image', () => {
    render(<VehicleCard vehicle={mockVehicle} />);

    const image = screen.getByAltText('2023 Toyota Camry');
    expect(image).toBeInTheDocument();
  });

  it('shows favorite button', () => {
    const handleFavorite = jest.fn();
    render(<VehicleCard vehicle={mockVehicle} onFavorite={handleFavorite} />);

    const favoriteButton = screen.getByLabelText(/favorite/i);
    expect(favoriteButton).toBeInTheDocument();
  });

  it('calls onFavorite when favorite button is clicked', () => {
    const handleFavorite = jest.fn();
    render(<VehicleCard vehicle={mockVehicle} onFavorite={handleFavorite} />);

    const favoriteButton = screen.getByLabelText(/favorite/i);
    fireEvent.click(favoriteButton);

    expect(handleFavorite).toHaveBeenCalledWith(mockVehicle.vin);
  });

  it('shows vehicle details like fuel type and location', () => {
    render(<VehicleCard vehicle={mockVehicle} />);

    expect(screen.getByText(/Gasoline/)).toBeInTheDocument();
    expect(screen.getByText(/Los Angeles/)).toBeInTheDocument();
  });

  it('displays recommendation score when provided', () => {
    const vehicleWithScore = {
      ...mockVehicle,
      recommendation_score: 85,
    };

    render(<VehicleCard vehicle={vehicleWithScore} />);

    expect(screen.getByText(/85/)).toBeInTheDocument();
  });

  it('shows view details button', () => {
    render(<VehicleCard vehicle={mockVehicle} />);

    const viewButton = screen.getByText(/view details/i);
    expect(viewButton).toBeInTheDocument();
  });

  it('calls onViewDetails when button is clicked', () => {
    const handleViewDetails = jest.fn();
    render(<VehicleCard vehicle={mockVehicle} onViewDetails={handleViewDetails} />);

    const viewButton = screen.getByText(/view details/i);
    fireEvent.click(viewButton);

    expect(handleViewDetails).toHaveBeenCalledWith(mockVehicle.vin);
  });

  it('displays monthly payment when displayMode is monthly', () => {
    const financingParams = {
      downPayment: 5000,
      loanTermMonths: 60,
      creditScore: 'good' as const,
      interestRate: 4.5,
    };

    render(
      <VehicleCard
        vehicle={mockVehicle}
        displayMode="monthly"
        financingParams={financingParams}
      />
    );

    // Should show monthly payment calculation
    expect(screen.getByText(/\/mo/)).toBeInTheDocument();
  });

  it('displays cash price when displayMode is cash', () => {
    render(<VehicleCard vehicle={mockVehicle} displayMode="cash" />);

    // Should show full price
    expect(screen.getByText(/\$25,000/)).toBeInTheDocument();
  });

  it('shows compare button when onCompare is provided', () => {
    const handleCompare = jest.fn();
    render(<VehicleCard vehicle={mockVehicle} onCompare={handleCompare} />);

    const compareButton = screen.getByLabelText(/compare/i);
    expect(compareButton).toBeInTheDocument();
  });

  it('calls onCompare when compare button is clicked', () => {
    const handleCompare = jest.fn();
    render(<VehicleCard vehicle={mockVehicle} onCompare={handleCompare} />);

    const compareButton = screen.getByLabelText(/compare/i);
    fireEvent.click(compareButton);

    expect(handleCompare).toHaveBeenCalledWith(mockVehicle);
  });

  it('displays dealer name when provided', () => {
    const vehicleWithDealer = {
      ...mockVehicle,
      dealer_name: 'ABC Motors',
    };

    render(<VehicleCard vehicle={vehicleWithDealer} />);

    expect(screen.getByText(/ABC Motors/)).toBeInTheDocument();
  });

  it('shows highlights when provided', () => {
    const vehicleWithHighlights = {
      ...mockVehicle,
      highlights: ['Low Mileage', 'One Owner', 'Service Records'],
    };

    render(<VehicleCard vehicle={vehicleWithHighlights} />);

    expect(screen.getByText('Low Mileage')).toBeInTheDocument();
    expect(screen.getByText('One Owner')).toBeInTheDocument();
    expect(screen.getByText('Service Records')).toBeInTheDocument();
  });
});
