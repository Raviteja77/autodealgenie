import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { SaveSearchModal } from '../SaveSearchModal';

describe('SaveSearchModal', () => {
  const mockOnClose = jest.fn();
  const mockOnSave = jest.fn();
  const mockSearchCriteria = {
    make: 'Toyota',
    model: 'Camry',
    year_min: 2020,
    year_max: 2023,
    price_min: 20000,
    price_max: 30000,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockOnSave.mockResolvedValue(undefined);
  });

  it('renders when open', () => {
    render(
      <SaveSearchModal
        isOpen={true}
        onClose={mockOnClose}
        onSave={mockOnSave}
        currentSearchCriteria={mockSearchCriteria}
      />
    );

    expect(screen.getByText('Save Search')).toBeInTheDocument();
  });

  it('does not render when closed', () => {
    render(
      <SaveSearchModal
        isOpen={false}
        onClose={mockOnClose}
        onSave={mockOnSave}
        currentSearchCriteria={mockSearchCriteria}
      />
    );

    expect(screen.queryByText('Save Search')).not.toBeInTheDocument();
  });

  it('allows entering a search name', async () => {
    const user = userEvent.setup();
    render(
      <SaveSearchModal
        isOpen={true}
        onClose={mockOnClose}
        onSave={mockOnSave}
        currentSearchCriteria={mockSearchCriteria}
      />
    );

    const input = screen.getByLabelText(/search name/i);
    await user.type(input, 'My Saved Search');

    expect(input).toHaveValue('My Saved Search');
  });

  it('shows notification toggle', () => {
    render(
      <SaveSearchModal
        isOpen={true}
        onClose={mockOnClose}
        onSave={mockOnSave}
        currentSearchCriteria={mockSearchCriteria}
      />
    );

    expect(screen.getByRole('checkbox')).toBeInTheDocument();
  });

  it('calls onSave with correct data when save button is clicked', async () => {
    const user = userEvent.setup();
    render(
      <SaveSearchModal
        isOpen={true}
        onClose={mockOnClose}
        onSave={mockOnSave}
        currentSearchCriteria={mockSearchCriteria}
      />
    );

    const input = screen.getByLabelText(/search name/i);
    await user.type(input, 'Test Search');

    const saveButton = screen.getByRole('button', { name: /save/i });
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(mockOnSave).toHaveBeenCalledWith(
        expect.objectContaining({
          name: 'Test Search',
          ...mockSearchCriteria,
        })
      );
    });
  });

  it('calls onClose after successful save', async () => {
    const user = userEvent.setup();
    render(
      <SaveSearchModal
        isOpen={true}
        onClose={mockOnClose}
        onSave={mockOnSave}
        currentSearchCriteria={mockSearchCriteria}
      />
    );

    const input = screen.getByLabelText(/search name/i);
    await user.type(input, 'Test Search');

    const saveButton = screen.getByRole('button', { name: /save/i });
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(mockOnClose).toHaveBeenCalled();
    });
  });

  it('displays error message when save fails', async () => {
    const user = userEvent.setup();
    mockOnSave.mockRejectedValue(new Error('Save failed'));

    render(
      <SaveSearchModal
        isOpen={true}
        onClose={mockOnClose}
        onSave={mockOnSave}
        currentSearchCriteria={mockSearchCriteria}
      />
    );

    const input = screen.getByLabelText(/search name/i);
    await user.type(input, 'Test Search');

    const saveButton = screen.getByRole('button', { name: /save/i });
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(screen.getByText(/save failed/i)).toBeInTheDocument();
    });
  });

  it('disables save button while saving', async () => {
    const user = userEvent.setup();
    // Make save take time
    mockOnSave.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

    render(
      <SaveSearchModal
        isOpen={true}
        onClose={mockOnClose}
        onSave={mockOnSave}
        currentSearchCriteria={mockSearchCriteria}
      />
    );

    const input = screen.getByLabelText(/search name/i);
    await user.type(input, 'Test Search');

    const saveButton = screen.getByRole('button', { name: /save/i });
    fireEvent.click(saveButton);

    // Button should be disabled while saving
    expect(saveButton).toBeDisabled();
  });

  it('calls onClose when cancel button is clicked', () => {
    render(
      <SaveSearchModal
        isOpen={true}
        onClose={mockOnClose}
        onSave={mockOnSave}
        currentSearchCriteria={mockSearchCriteria}
      />
    );

    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    fireEvent.click(cancelButton);

    expect(mockOnClose).toHaveBeenCalled();
  });
});
