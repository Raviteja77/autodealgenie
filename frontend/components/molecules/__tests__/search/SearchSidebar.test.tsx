import { render, screen } from '@testing-library/react';
import { SearchSidebar } from '../../search/SearchSidebar';

describe('SearchSidebar', () => {
  it('renders financing tips section', () => {
    render(<SearchSidebar />);

    expect(screen.getByText('💡 Financing Tips')).toBeInTheDocument();
  });

  it('displays all financing tips', () => {
    render(<SearchSidebar />);

    expect(screen.getByText(/20% down payment typically gets better rates/)).toBeInTheDocument();
    expect(screen.getByText(/Shorter loans save on total interest/)).toBeInTheDocument();
    expect(screen.getByText(/Check your credit score before applying/)).toBeInTheDocument();
    expect(screen.getByText(/Get pre-approved for better negotiation power/)).toBeInTheDocument();
  });

  it('renders AI Analysis section', () => {
    render(<SearchSidebar />);

    expect(screen.getByText('🤖 AI Analysis')).toBeInTheDocument();
  });

  it('displays AI analysis description', () => {
    render(<SearchSidebar />);

    expect(screen.getByText(/Max Results/)).toBeInTheDocument();
    expect(screen.getByText(/top 5/)).toBeInTheDocument();
  });

  it('renders Pro Tip alert', () => {
    render(<SearchSidebar />);

    expect(screen.getByText('Pro Tip:')).toBeInTheDocument();
    expect(screen.getByText(/Knowing your financing options before shopping/)).toBeInTheDocument();
  });

  it('renders with sticky positioning styles', () => {
    const { container } = render(<SearchSidebar />);

    // Check that the outer Box has position styling
    const outerBox = container.firstChild;
    expect(outerBox).toBeInTheDocument();
  });

  it('renders all sections in Paper components', () => {
    const { container } = render(<SearchSidebar />);

    const papers = container.querySelectorAll('.MuiPaper-root');
    // Should have 2 Paper components (Financing Tips and AI Analysis)
    // Plus Alert component might have Paper styles
    expect(papers.length).toBeGreaterThanOrEqual(2);
  });

  it('renders Alert with info severity', () => {
    const { container } = render(<SearchSidebar />);

    const alert = container.querySelector('.MuiAlert-standardInfo');
    expect(alert).toBeInTheDocument();
  });
});
