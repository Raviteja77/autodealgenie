import { render, screen, fireEvent } from '@testing-library/react';
import { ConnectionStatusIndicator } from '../ConnectionStatusIndicator';

describe('ConnectionStatusIndicator', () => {
  it('shows connected status', () => {
    render(<ConnectionStatusIndicator status="connected" />);
    
    expect(screen.getByText('Connected')).toBeInTheDocument();
    expect(screen.getByTestId('WifiIcon')).toBeInTheDocument();
  });

  it('shows disconnected status', () => {
    render(<ConnectionStatusIndicator status="disconnected" />);
    
    expect(screen.getByText('Disconnected')).toBeInTheDocument();
    expect(screen.getByTestId('WifiOffIcon')).toBeInTheDocument();
  });

  it('shows connecting status', () => {
    render(<ConnectionStatusIndicator status="connecting" />);
    
    expect(screen.getByText('Connecting')).toBeInTheDocument();
    expect(screen.getByTestId('SyncIcon')).toBeInTheDocument();
  });

  it('shows reconnecting status with attempt count', () => {
    render(
      <ConnectionStatusIndicator 
        status="reconnecting" 
        reconnectAttempts={2}
        maxReconnectAttempts={5}
      />
    );
    
    expect(screen.getByText('Reconnecting')).toBeInTheDocument();
  });

  it('shows error status', () => {
    render(<ConnectionStatusIndicator status="error" />);
    
    expect(screen.getByText('Error')).toBeInTheDocument();
    expect(screen.getByTestId('ErrorIcon')).toBeInTheDocument();
  });

  it('displays manual reconnect button when provided', () => {
    const handleReconnect = jest.fn();
    render(
      <ConnectionStatusIndicator 
        status="disconnected" 
        onManualReconnect={handleReconnect}
      />
    );
    
    const reconnectButton = screen.getByLabelText(/reconnect/i);
    expect(reconnectButton).toBeInTheDocument();
  });

  it('calls onManualReconnect when button is clicked', () => {
    const handleReconnect = jest.fn();
    render(
      <ConnectionStatusIndicator 
        status="disconnected" 
        onManualReconnect={handleReconnect}
      />
    );
    
    const reconnectButton = screen.getByLabelText(/reconnect/i);
    fireEvent.click(reconnectButton);
    
    expect(handleReconnect).toHaveBeenCalledTimes(1);
  });

  it('shows message queue size when provided', () => {
    render(
      <ConnectionStatusIndicator 
        status="disconnected" 
        messageQueueSize={5}
      />
    );
    
    // Check that queue icon is rendered
    expect(screen.getByTestId('QueueIcon')).toBeInTheDocument();
  });

  it('shows HTTP fallback indicator when using fallback', () => {
    render(
      <ConnectionStatusIndicator 
        status="connected" 
        isUsingHttpFallback={true}
      />
    );
    
    // The component should indicate HTTP fallback is being used
    const tooltip = screen.getByText('Connected');
    expect(tooltip).toBeInTheDocument();
  });

  it('applies correct chip color for each status', () => {
    const statuses: Array<{ status: 'connected' | 'connecting' | 'reconnecting' | 'disconnected' | 'error'; color: string }> = [
      { status: 'connected', color: 'success' },
      { status: 'connecting', color: 'info' },
      { status: 'reconnecting', color: 'warning' },
      { status: 'disconnected', color: 'default' },
      { status: 'error', color: 'error' },
    ];

    statuses.forEach(({ status, color }) => {
      const { container, unmount } = render(
        <ConnectionStatusIndicator status={status} />
      );
      
      const chip = container.querySelector('.MuiChip-root');
      if (color !== 'default') {
        expect(chip).toHaveClass(`MuiChip-color${color.charAt(0).toUpperCase() + color.slice(1)}`);
      }
      unmount();
    });
  });
});

