import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import SearchBar from './SearchBar';

describe('SearchBar Component', () => {
  const mockOnSearch = jest.fn();
  const mockOnClean = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders search input and buttons', () => {
    render(<SearchBar onSearch={mockOnSearch} onClean={mockOnClean} />);

    expect(screen.getByLabelText(/search images/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /search/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /clean/i })).toBeInTheDocument();
  });

  test('updates input value when typing', () => {
    render(<SearchBar onSearch={mockOnSearch} onClean={mockOnClean} />);

    const input = screen.getByLabelText(/search images/i);
    fireEvent.change(input, { target: { value: 'mountains' } });

    expect(input).toHaveValue('mountains');
  });

  test('calls onSearch with trimmed text when form is submitted', () => {
    render(<SearchBar onSearch={mockOnSearch} onClean={mockOnClean} />);

    const input = screen.getByLabelText(/search images/i);
    const searchButton = screen.getByRole('button', { name: /search/i });

    fireEvent.change(input, { target: { value: '  test query  ' } });
    fireEvent.click(searchButton);

    expect(mockOnSearch).toHaveBeenCalledWith('test query');
  });

  test('calls onSearch when form is submitted with Enter key', () => {
    render(<SearchBar onSearch={mockOnSearch} onClean={mockOnClean} />);

    const input = screen.getByLabelText(/search images/i);

    fireEvent.change(input, { target: { value: 'nature' } });
    fireEvent.submit(input.closest('form')!);

    expect(mockOnSearch).toHaveBeenCalledWith('nature');
  });

  test('clears input and calls onClean when Clean button is clicked', () => {
    render(<SearchBar onSearch={mockOnSearch} onClean={mockOnClean} />);

    const input = screen.getByLabelText(/search images/i);
    const cleanButton = screen.getByRole('button', { name: /clean/i });

    fireEvent.change(input, { target: { value: 'test' } });
    expect(input).toHaveValue('test');

    fireEvent.click(cleanButton);

    expect(input).toHaveValue('');
    expect(mockOnClean).toHaveBeenCalledTimes(1);
  });

  test('does not call onSearch with empty string', () => {
    render(<SearchBar onSearch={mockOnSearch} onClean={mockOnClean} />);

    const searchButton = screen.getByRole('button', { name: /search/i });
    fireEvent.click(searchButton);

    expect(mockOnSearch).toHaveBeenCalledWith('');
  });
});
