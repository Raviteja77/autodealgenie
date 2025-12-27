import { render, screen, fireEvent } from '@testing-library/react';
import { BudgetRangeSlider } from '../../search/BudgetRangeSlider';

describe('BudgetRangeSlider', () => {
  it('renders with cash payment method title', () => {
    const handleChange = jest.fn();
    render(
      <BudgetRangeSlider
        min={10000}
        max={50000}
        onChange={handleChange}
        paymentMethod="cash"
      />
    );

    expect(screen.getByText('Budget')).toBeInTheDocument();
  });

  it('renders with finance payment method title', () => {
    const handleChange = jest.fn();
    render(
      <BudgetRangeSlider
        min={10000}
        max={50000}
        onChange={handleChange}
        paymentMethod="finance"
      />
    );

    expect(screen.getByText('Vehicle Price Range')).toBeInTheDocument();
  });

  it('renders with both payment method title', () => {
    const handleChange = jest.fn();
    render(
      <BudgetRangeSlider
        min={10000}
        max={50000}
        onChange={handleChange}
        paymentMethod="both"
      />
    );

    expect(screen.getByText('Price Range')).toBeInTheDocument();
  });

  it('displays minimum and maximum values', () => {
    const handleChange = jest.fn();
    render(
      <BudgetRangeSlider
        min={15000}
        max={45000}
        onChange={handleChange}
        paymentMethod="cash"
      />
    );

    // The values appear in the slider's value labels, may appear multiple times
    const minValues = screen.getAllByText(/\$15,000/);
    const maxValues = screen.getAllByText(/\$45,000/);
    expect(minValues.length).toBeGreaterThan(0);
    expect(maxValues.length).toBeGreaterThan(0);
  });

  it('displays error message when provided', () => {
    const handleChange = jest.fn();
    render(
      <BudgetRangeSlider
        min={10000}
        max={50000}
        onChange={handleChange}
        paymentMethod="cash"
        error="Budget max must be greater than min"
      />
    );

    expect(screen.getByText('Budget max must be greater than min')).toBeInTheDocument();
  });

  it('renders slider component', () => {
    const handleChange = jest.fn();
    const { container } = render(
      <BudgetRangeSlider
        min={10000}
        max={50000}
        onChange={handleChange}
        paymentMethod="cash"
      />
    );

    const slider = container.querySelector('.MuiSlider-root');
    expect(slider).toBeInTheDocument();
  });

  it('displays AttachMoney icon', () => {
    const handleChange = jest.fn();
    const { container } = render(
      <BudgetRangeSlider
        min={10000}
        max={50000}
        onChange={handleChange}
        paymentMethod="cash"
      />
    );

    const icon = container.querySelector('[data-testid="AttachMoneyIcon"]');
    expect(icon).toBeInTheDocument();
  });

  it('renders without error when no error prop is provided', () => {
    const handleChange = jest.fn();
    const { container } = render(
      <BudgetRangeSlider
        min={10000}
        max={50000}
        onChange={handleChange}
        paymentMethod="cash"
      />
    );

    const errorText = container.querySelector('.MuiFormHelperText-root.Mui-error');
    expect(errorText).not.toBeInTheDocument();
  });
});
