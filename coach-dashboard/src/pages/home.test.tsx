import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { HomePage } from './home';

describe('HomePage', () => {
  it('renders Dashboard heading', () => {
    render(<HomePage />);
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });

  it('renders queue instructions', () => {
    render(<HomePage />);
    expect(screen.getByText(/select a swing from the review queue/i)).toBeInTheDocument();
  });
});
