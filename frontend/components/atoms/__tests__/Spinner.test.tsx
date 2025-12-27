import { render, screen } from '@testing-library/react';
import { Spinner } from '../Spinner';

describe('Spinner', () => {
  it('renders with default props', () => {
    const { container } = render(<Spinner />);
    const spinner = container.querySelector('.MuiCircularProgress-root');
    expect(spinner).toBeInTheDocument();
  });

  it('renders with text', () => {
    render(<Spinner text="Loading..." />);
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('applies size prop', () => {
    const { container, rerender } = render(<Spinner size="sm" />);
    let spinner = container.querySelector('.MuiCircularProgress-root') as HTMLElement;
    expect(spinner).toHaveStyle({ width: '20px', height: '20px' });

    rerender(<Spinner size="lg" />);
    spinner = container.querySelector('.MuiCircularProgress-root') as HTMLElement;
    expect(spinner).toHaveStyle({ width: '60px', height: '60px' });
  });

  it('renders as fullscreen backdrop', () => {
    const { container } = render(<Spinner fullScreen />);
    const backdrop = container.querySelector('.MuiBackdrop-root');
    expect(backdrop).toBeInTheDocument();
  });

  it('applies color prop', () => {
    const { container } = render(<Spinner color="secondary" />);
    const spinner = container.querySelector('.MuiCircularProgress-colorSecondary');
    expect(spinner).toBeInTheDocument();
  });
});
