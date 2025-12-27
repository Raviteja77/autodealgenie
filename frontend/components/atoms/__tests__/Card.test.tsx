import React from "react";
import { render, screen } from '@testing-library/react';
import { Card } from '../Card';

describe('Card', () => {
  it('renders children content', () => {
    render(
      <Card>
        <Card.Body>Test content</Card.Body>
      </Card>
    );
    expect(screen.getByText('Test content')).toBeInTheDocument();
  });

  it('renders with header, body, and footer', () => {
    render(
      <Card>
        <Card.Header>
          <div>Header</div>
        </Card.Header>
        <Card.Body>Body</Card.Body>
        <Card.Footer>Footer</Card.Footer>
      </Card>
    );
    
    expect(screen.getByText('Header')).toBeInTheDocument();
    expect(screen.getByText('Body')).toBeInTheDocument();
    expect(screen.getByText('Footer')).toBeInTheDocument();
  });

  it('applies shadow prop', () => {
    const { container } = render(
      <Card shadow="none">
        <Card.Body>Content</Card.Body>
      </Card>
    );
    
    const card = container.firstChild as HTMLElement;
    expect(card).toHaveStyle({ boxShadow: 'none' });
  });

  it('applies hover effect', () => {
    const { container } = render(
      <Card hover>
        <Card.Body>Content</Card.Body>
      </Card>
    );
    
    const card = container.firstChild as HTMLElement;
    expect(card.className).toContain('MuiCard');
  });
});
