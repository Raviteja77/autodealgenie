import { render, screen, fireEvent } from '@testing-library/react';
import { ComparisonBar } from '../ComparisonBar';

describe('ComparisonBar', () => {
  const mockVehicles = [
    {
      vin: 'VIN1',
      make: 'Toyota',
      model: 'Camry',
      year: 2023,
      price: 25000,
      image: '/car1.jpg',
    },
    {
      vin: 'VIN2',
      make: 'Honda',
      model: 'Accord',
      year: 2022,
      price: 24000,
      image: '/car2.jpg',
    },
  ];

  it('renders with vehicles count', () => {
    const handleCompare = jest.fn();
    const handleClear = jest.fn();

    render(
      <ComparisonBar
        vehicles={mockVehicles}
        onCompare={handleCompare}
        onClear={handleClear}
      />
    );

    expect(screen.getByText(/2 vehicles selected/i)).toBeInTheDocument();
  });

  it('shows compare button', () => {
    const handleCompare = jest.fn();
    const handleClear = jest.fn();

    render(
      <ComparisonBar
        vehicles={mockVehicles}
        onCompare={handleCompare}
        onClear={handleClear}
      />
    );

    expect(screen.getByText(/compare/i)).toBeInTheDocument();
  });

  it('calls onCompare when compare button is clicked', () => {
    const handleCompare = jest.fn();
    const handleClear = jest.fn();

    render(
      <ComparisonBar
        vehicles={mockVehicles}
        onCompare={handleCompare}
        onClear={handleClear}
      />
    );

    const compareButton = screen.getByText(/compare/i);
    fireEvent.click(compareButton);

    expect(handleCompare).toHaveBeenCalled();
  });

  it('shows clear button', () => {
    const handleCompare = jest.fn();
    const handleClear = jest.fn();

    render(
      <ComparisonBar
        vehicles={mockVehicles}
        onCompare={handleCompare}
        onClear={handleClear}
      />
    );

    expect(screen.getByText(/clear/i)).toBeInTheDocument();
  });

  it('calls onClear when clear button is clicked', () => {
    const handleCompare = jest.fn();
    const handleClear = jest.fn();

    render(
      <ComparisonBar
        vehicles={mockVehicles}
        onCompare={handleCompare}
        onClear={handleClear}
      />
    );

    const clearButton = screen.getByText(/clear/i);
    fireEvent.click(clearButton);

    expect(handleClear).toHaveBeenCalled();
  });

  it('displays vehicle thumbnails', () => {
    const handleCompare = jest.fn();
    const handleClear = jest.fn();

    render(
      <ComparisonBar
        vehicles={mockVehicles}
        onCompare={handleCompare}
        onClear={handleClear}
      />
    );

    expect(screen.getByAltText('2023 Toyota Camry')).toBeInTheDocument();
    expect(screen.getByAltText('2022 Honda Accord')).toBeInTheDocument();
  });

  it('shows remove button for each vehicle', () => {
    const handleCompare = jest.fn();
    const handleClear = jest.fn();
    const handleRemove = jest.fn();

    render(
      <ComparisonBar
        vehicles={mockVehicles}
        onCompare={handleCompare}
        onClear={handleClear}
        onRemove={handleRemove}
      />
    );

    const removeButtons = screen.getAllByLabelText(/remove/i);
    expect(removeButtons).toHaveLength(2);
  });

  it('calls onRemove with correct vin when remove button is clicked', () => {
    const handleCompare = jest.fn();
    const handleClear = jest.fn();
    const handleRemove = jest.fn();

    render(
      <ComparisonBar
        vehicles={mockVehicles}
        onCompare={handleCompare}
        onClear={handleClear}
        onRemove={handleRemove}
      />
    );

    const removeButtons = screen.getAllByLabelText(/remove/i);
    fireEvent.click(removeButtons[0]);

    expect(handleRemove).toHaveBeenCalledWith('VIN1');
  });

  it('disables compare button when less than 2 vehicles', () => {
    const handleCompare = jest.fn();
    const handleClear = jest.fn();

    render(
      <ComparisonBar
        vehicles={[mockVehicles[0]]}
        onCompare={handleCompare}
        onClear={handleClear}
      />
    );

    const compareButton = screen.getByText(/compare/i);
    expect(compareButton).toBeDisabled();
  });

  it('shows maximum vehicles message when at limit', () => {
    const maxVehicles = Array(4).fill(mockVehicles[0]).map((v, i) => ({
      ...v,
      vin: `VIN${i}`,
    }));

    const handleCompare = jest.fn();
    const handleClear = jest.fn();

    render(
      <ComparisonBar
        vehicles={maxVehicles}
        onCompare={handleCompare}
        onClear={handleClear}
      />
    );

    expect(screen.getByText(/4 vehicles selected/i)).toBeInTheDocument();
  });

  it('does not render when no vehicles are selected', () => {
    const handleCompare = jest.fn();
    const handleClear = jest.fn();

    const { container } = render(
      <ComparisonBar
        vehicles={[]}
        onCompare={handleCompare}
        onClear={handleClear}
      />
    );

    // The bar should not be visible or have minimal content
    expect(container.firstChild).toBeNull();
  });
});
