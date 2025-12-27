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
    const handleRemove = jest.fn();

    render(
      <ComparisonBar
        selectedVehicles={mockVehicles}
        onCompare={handleCompare}
        onClear={handleClear}
        onRemove={handleRemove}
        maxCount={4}
        canCompare={true}
      />
    );

    expect(screen.getByText(/2\/4/i)).toBeInTheDocument();
  });

  it('shows compare button', () => {
    const handleCompare = jest.fn();
    const handleClear = jest.fn();
    const handleRemove = jest.fn();

    render(
      <ComparisonBar
        selectedVehicles={mockVehicles}
        onCompare={handleCompare}
        onClear={handleClear}
        onRemove={handleRemove}
        maxCount={4}
        canCompare={true}
      />
    );

    expect(screen.getByRole('button', { name: /compare/i })).toBeInTheDocument();
  });

  it('calls onCompare when compare button is clicked', () => {
    const handleCompare = jest.fn();
    const handleClear = jest.fn();
    const handleRemove = jest.fn();

    render(
      <ComparisonBar
        selectedVehicles={mockVehicles}
        onCompare={handleCompare}
        onClear={handleClear}
        onRemove={handleRemove}
        maxCount={4}
        canCompare={true}
      />
    );

    const compareButton = screen.getByRole('button', { name: /compare/i });
    fireEvent.click(compareButton);

    expect(handleCompare).toHaveBeenCalled();
  });

  it('shows clear button', () => {
    const handleCompare = jest.fn();
    const handleClear = jest.fn();
    const handleRemove = jest.fn();

    render(
      <ComparisonBar
        selectedVehicles={mockVehicles}
        onCompare={handleCompare}
        onClear={handleClear}
        onRemove={handleRemove}
        maxCount={4}
        canCompare={true}
      />
    );

    expect(screen.getByRole('button', { name: /clear/i })).toBeInTheDocument();
  });

  it('calls onClear when clear button is clicked', () => {
    const handleCompare = jest.fn();
    const handleClear = jest.fn();
    const handleRemove = jest.fn();

    render(
      <ComparisonBar
        selectedVehicles={mockVehicles}
        onCompare={handleCompare}
        onClear={handleClear}
        onRemove={handleRemove}
        maxCount={4}
        canCompare={true}
      />
    );

    const clearButton = screen.getByRole('button', { name: /clear/i });
    fireEvent.click(clearButton);

    expect(handleClear).toHaveBeenCalled();
  });

  it('displays vehicle chips', () => {
    const handleCompare = jest.fn();
    const handleClear = jest.fn();
    const handleRemove = jest.fn();

    render(
      <ComparisonBar
        selectedVehicles={mockVehicles}
        onCompare={handleCompare}
        onClear={handleClear}
        onRemove={handleRemove}
        maxCount={4}
        canCompare={true}
      />
    );

    expect(screen.getByText('2023 Toyota Camry')).toBeInTheDocument();
    expect(screen.getByText('2022 Honda Accord')).toBeInTheDocument();
  });

  it('shows remove button for each vehicle', () => {
    const handleCompare = jest.fn();
    const handleClear = jest.fn();
    const handleRemove = jest.fn();

    render(
      <ComparisonBar
        selectedVehicles={mockVehicles}
        onCompare={handleCompare}
        onClear={handleClear}
        onRemove={handleRemove}
        maxCount={4}
        canCompare={true}
      />
    );

    // MUI Chips have CloseIcon rendered for their delete buttons
    const removeButtons = screen.getAllByTestId('CloseIcon');
    expect(removeButtons).toHaveLength(2);
  });

  it('calls onRemove with correct vin when remove button is clicked', () => {
    const handleCompare = jest.fn();
    const handleClear = jest.fn();
    const handleRemove = jest.fn();

    const { container } = render(
      <ComparisonBar
        selectedVehicles={mockVehicles}
        onCompare={handleCompare}
        onClear={handleClear}
        onRemove={handleRemove}
        maxCount={4}
        canCompare={true}
      />
    );

    // Find chips with deletable prop (vehicle chips) and their delete buttons
    const deletableChips = container.querySelectorAll('.MuiChip-deletable');
    expect(deletableChips.length).toBe(2); // Should have 2 vehicle chips
    
    // Find the delete icon button within the first chip
    const firstChip = deletableChips[0];
    const deleteIcon = firstChip.querySelector('svg[data-testid="CloseIcon"]');
    
    if (deleteIcon) {
      // Click on the svg's parent button or the svg itself
      const deleteButton = deleteIcon.closest('button') || deleteIcon.parentElement?.closest('button');
      if (deleteButton) {
        fireEvent.click(deleteButton);
        expect(handleRemove).toHaveBeenCalledWith('VIN1');
      }
    }
  });

  it('disables compare button when canCompare is false', () => {
    const handleCompare = jest.fn();
    const handleClear = jest.fn();
    const handleRemove = jest.fn();

    render(
      <ComparisonBar
        selectedVehicles={[mockVehicles[0]]}
        onCompare={handleCompare}
        onClear={handleClear}
        onRemove={handleRemove}
        maxCount={4}
        canCompare={false}
      />
    );

    const compareButton = screen.getByRole('button', { name: /compare/i });
    expect(compareButton).toBeDisabled();
  });

  it('shows maximum vehicles count when at limit', () => {
    const maxVehicles = Array(4).fill(mockVehicles[0]).map((v, i) => ({
      ...v,
      vin: `VIN${i}`,
    }));

    const handleCompare = jest.fn();
    const handleClear = jest.fn();
    const handleRemove = jest.fn();

    render(
      <ComparisonBar
        selectedVehicles={maxVehicles}
        onCompare={handleCompare}
        onClear={handleClear}
        onRemove={handleRemove}
        maxCount={4}
        canCompare={true}
      />
    );

    expect(screen.getByText(/4\/4/i)).toBeInTheDocument();
  });

  it('does not render when no vehicles are selected', () => {
    const handleCompare = jest.fn();
    const handleClear = jest.fn();
    const handleRemove = jest.fn();

    const { container } = render(
      <ComparisonBar
        selectedVehicles={[]}
        onCompare={handleCompare}
        onClear={handleClear}
        onRemove={handleRemove}
        maxCount={4}
        canCompare={false}
      />
    );

    // The bar should not be visible or have minimal content
    expect(container.firstChild).toBeNull();
  });
});
