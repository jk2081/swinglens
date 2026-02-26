import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import { HomePage } from './home';

describe('HomePage', () => {
  it('renders the SwingLens title', () => {
    render(
      <MemoryRouter>
        <HomePage />
      </MemoryRouter>,
    );
    expect(screen.getByText('SwingLens')).toBeInTheDocument();
  });

  it('renders the Coach Dashboard subtitle', () => {
    render(
      <MemoryRouter>
        <HomePage />
      </MemoryRouter>,
    );
    expect(screen.getByText('Coach Dashboard')).toBeInTheDocument();
  });
});
