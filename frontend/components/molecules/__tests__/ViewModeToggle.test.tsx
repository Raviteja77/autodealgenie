import { render, screen, fireEvent } from '@testing-library/react';
import { ViewModeToggle } from '../ViewModeToggle';
import { ViewMode } from '@/lib/hooks/useViewMode';

describe('ViewModeToggle', () => {
  it('renders with grid view selected by default', () => {
    const handleChange = jest.fn();
    render(<ViewModeToggle value="grid" onChange={handleChange} />);
    
    const gridButton = screen.getByLabelText('grid view');
    expect(gridButton).toHaveClass('Mui-selected');
  });

  it('calls onChange when list view is clicked', () => {
    const handleChange = jest.fn();
    render(<ViewModeToggle value="grid" onChange={handleChange} />);
    
    const listButton = screen.getByLabelText('list view');
    fireEvent.click(listButton);
    
    expect(handleChange).toHaveBeenCalledWith('list');
  });

  it('calls onChange when compact view is clicked', () => {
    const handleChange = jest.fn();
    render(<ViewModeToggle value="grid" onChange={handleChange} />);
    
    const compactButton = screen.getByLabelText('compact view');
    fireEvent.click(compactButton);
    
    expect(handleChange).toHaveBeenCalledWith('compact');
  });

  it('does not call onChange when clicking already selected view', () => {
    const handleChange = jest.fn();
    render(<ViewModeToggle value="grid" onChange={handleChange} />);
    
    const gridButton = screen.getByLabelText('grid view');
    fireEvent.click(gridButton);
    
    // MUI ToggleButtonGroup doesn't call onChange if clicking selected button
    expect(handleChange).not.toHaveBeenCalled();
  });

  it('renders all three view mode options', () => {
    const handleChange = jest.fn();
    render(<ViewModeToggle value="grid" onChange={handleChange} />);
    
    expect(screen.getByLabelText('grid view')).toBeInTheDocument();
    expect(screen.getByLabelText('list view')).toBeInTheDocument();
    expect(screen.getByLabelText('compact view')).toBeInTheDocument();
  });

  it('shows correct view as selected', () => {
    const handleChange = jest.fn();
    const { rerender } = render(<ViewModeToggle value="grid" onChange={handleChange} />);
    
    expect(screen.getByLabelText('grid view')).toHaveClass('Mui-selected');
    
    rerender(<ViewModeToggle value="list" onChange={handleChange} />);
    expect(screen.getByLabelText('list view')).toHaveClass('Mui-selected');
    
    rerender(<ViewModeToggle value="compact" onChange={handleChange} />);
    expect(screen.getByLabelText('compact view')).toHaveClass('Mui-selected');
  });
});
