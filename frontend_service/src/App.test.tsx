import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import App from './App';

// Mock the components
jest.mock('./components/Layout', () => {
  return function Layout({ children, onToggleTheme }: any) {
    return (
      <div>
        <button onClick={onToggleTheme} data-testid="theme-toggle">Toggle Theme</button>
        {children}
      </div>
    );
  };
});

jest.mock('./components/SearchBar', () => {
  return function SearchBar({ onSearch, onClean }: any) {
    return (
      <div>
        <input
          data-testid="search-input"
          onChange={(e) => onSearch(e.target.value)}
        />
        <button onClick={onClean} data-testid="clean-button">Clean</button>
      </div>
    );
  };
});

jest.mock('./components/ImageGrid', () => {
  return function ImageGrid({ query }: any) {
    return <div data-testid="image-grid">Images for: {query}</div>;
  };
});

jest.mock('./components/PaginationControls', () => {
  return function PaginationControls({ page, onPageChange }: any) {
    return (
      <div>
        <button onClick={() => onPageChange(page + 1)} data-testid="next-page">Next</button>
        <span data-testid="current-page">{page}</span>
      </div>
    );
  };
});

jest.mock('./hooks/useThemeMode', () => ({
  useThemeMode: () => ({
    theme: {},
    mode: 'light',
    toggleMode: jest.fn(),
  }),
}));

describe('App Component', () => {
  test('renders without crashing', () => {
    render(<App />);
    expect(screen.getByTestId('search-input')).toBeInTheDocument();
  });

  test('shows ImageGrid when query is set', () => {
    render(<App />);
    const searchInput = screen.getByTestId('search-input');

    fireEvent.change(searchInput, { target: { value: 'mountains' } });

    expect(screen.getByTestId('image-grid')).toBeInTheDocument();
  });

  test('clean button resets query', () => {
    render(<App />);
    const searchInput = screen.getByTestId('search-input');
    const cleanButton = screen.getByTestId('clean-button');

    fireEvent.change(searchInput, { target: { value: 'mountains' } });
    expect(screen.getByTestId('image-grid')).toBeInTheDocument();

    fireEvent.click(cleanButton);

    // After cleaning, ImageGrid should not be visible
    expect(screen.queryByText(/Images for:/)).not.toBeInTheDocument();
  });

  test('pagination controls appear when query is set', () => {
    render(<App />);
    const searchInput = screen.getByTestId('search-input');

    fireEvent.change(searchInput, { target: { value: 'nature' } });

    expect(screen.getByTestId('current-page')).toBeInTheDocument();
    expect(screen.getByTestId('next-page')).toBeInTheDocument();
  });

  test('page number updates when next is clicked', () => {
    render(<App />);
    const searchInput = screen.getByTestId('search-input');

    fireEvent.change(searchInput, { target: { value: 'nature' } });

    const currentPage = screen.getByTestId('current-page');
    expect(currentPage).toHaveTextContent('1');

    const nextButton = screen.getByTestId('next-page');
    fireEvent.click(nextButton);

    expect(currentPage).toHaveTextContent('2');
  });
});
