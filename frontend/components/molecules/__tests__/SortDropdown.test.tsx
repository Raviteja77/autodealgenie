import React from "react";
import { render, screen, fireEvent } from '@testing-library/react';
import { SortDropdown, SortOption } from '../SortDropdown';

describe('SortDropdown', () => {
  it('renders with default value', () => {
    const handleChange = jest.fn();
    render(<SortDropdown value="price_low" onChange={handleChange} />);
    
    // Check that the dropdown displays the current selection
    expect(screen.getByText('Price: Low to High')).toBeInTheDocument();
  });

  it('displays all sort options when opened', () => {
    const handleChange = jest.fn();
    render(<SortDropdown value="price_low" onChange={handleChange} />);
    
    // Open the dropdown
    const select = screen.getByRole('combobox');
    fireEvent.mouseDown(select);
    
    // Check all options are present using getAllByText since text appears in both select and menu
    expect(screen.getAllByText('Price: Low to High').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Price: High to Low').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Mileage: Low to High').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Year: Newest First').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Recommendation Score').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Recently Added').length).toBeGreaterThan(0);
  });

  it('calls onChange when selecting a different option', () => {
    const handleChange = jest.fn();
    render(<SortDropdown value="price_low" onChange={handleChange} />);
    
    // Open the dropdown
    const select = screen.getByRole('combobox');
    fireEvent.mouseDown(select);
    
    // Select a different option using getAllByText and click the last one (in the menu)
    const options = screen.getAllByText('Mileage: Low to High');
    fireEvent.click(options[options.length - 1]);
    
    expect(handleChange).toHaveBeenCalledWith('mileage_low');
  });

  it('displays correct label for each sort option', () => {
    const handleChange = jest.fn();
    const sortOptions: Array<{ value: SortOption; label: string }> = [
      { value: 'price_low', label: 'Price: Low to High' },
      { value: 'price_high', label: 'Price: High to Low' },
      { value: 'mileage_low', label: 'Mileage: Low to High' },
      { value: 'year_new', label: 'Year: Newest First' },
      { value: 'score_high', label: 'Recommendation Score' },
      { value: 'recently_added', label: 'Recently Added' },
    ];

    sortOptions.forEach(({ value, label }) => {
      const { unmount } = render(<SortDropdown value={value} onChange={handleChange} />);
      expect(screen.getByText(label)).toBeInTheDocument();
      unmount();
    });
  });

  it('renders with sort icon', () => {
    const handleChange = jest.fn();
    const { container } = render(<SortDropdown value="price_low" onChange={handleChange} />);
    
    // Check for MUI SortIcon (it should be in the component)
    const icon = container.querySelector('[data-testid="SortIcon"]');
    expect(icon).toBeInTheDocument();
  });

  it('is accessible with proper aria attributes', () => {
    const handleChange = jest.fn();
    render(<SortDropdown value="price_low" onChange={handleChange} />);
    
    const select = screen.getByRole('combobox');
    expect(select).toBeInTheDocument();
  });
});
