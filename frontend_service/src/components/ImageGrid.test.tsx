import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import ImageGrid from './ImageGrid';
import * as client from '../api/client';

// Mock the API client
jest.mock('../api/client');

// Mock child components
jest.mock('./NoResults', () => {
  return function NoResults({ query }: any) {
    return <div>No results for: {query}</div>;
  };
});

jest.mock('./ImageModel', () => {
  return function ImageModal() {
    return <div>Image Modal</div>;
  };
});

const mockFetchImages = client.fetchImages as jest.MockedFunction<typeof client.fetchImages>;

describe('ImageGrid Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('shows message when no query is provided', () => {
    render(<ImageGrid query="" page={1} />);
    expect(screen.getByText(/enter a query to search for images/i)).toBeInTheDocument();
  });

  test('shows loading state while fetching images', async () => {
    mockFetchImages.mockImplementation(() => new Promise(() => {})); // Never resolves

    render(<ImageGrid query="mountains" page={1} />);

    expect(screen.getByText(/loading images/i)).toBeInTheDocument();
  });

  test('displays images when fetch is successful', async () => {
    const mockData = {
      query: 'mountains',
      results: [
        { image_id: 1, image_url: 'http://example.com/1.jpg', score: 0.95 },
        { image_id: 2, image_url: 'http://example.com/2.jpg', score: 0.85 },
      ],
    };

    mockFetchImages.mockResolvedValue(mockData);

    render(<ImageGrid query="mountains" page={1} />);

    await waitFor(() => {
      expect(screen.getByText(/score: 0.95/i)).toBeInTheDocument();
      expect(screen.getByText(/score: 0.85/i)).toBeInTheDocument();
    });
  });

  test('shows no results component when results array is empty', async () => {
    mockFetchImages.mockResolvedValue({
      query: 'unknown',
      results: [],
    });

    render(<ImageGrid query="unknown" page={1} />);

    await waitFor(() => {
      expect(screen.getByText(/no results for: unknown/i)).toBeInTheDocument();
    });
  });

  test('shows error message when fetch fails', async () => {
    mockFetchImages.mockRejectedValue(new Error('Network error'));

    render(<ImageGrid query="mountains" page={1} />);

    await waitFor(() => {
      expect(screen.getByText(/failed to fetch images/i)).toBeInTheDocument();
    });
  });

  test('refetches images when query changes', async () => {
    const mockData1 = {
      query: 'mountains',
      results: [{ image_id: 1, image_url: 'http://example.com/1.jpg', score: 0.95 }],
    };

    const mockData2 = {
      query: 'ocean',
      results: [{ image_id: 2, image_url: 'http://example.com/2.jpg', score: 0.88 }],
    };

    mockFetchImages.mockResolvedValueOnce(mockData1);

    const { rerender } = render(<ImageGrid query="mountains" page={1} />);

    await waitFor(() => {
      expect(screen.getByText(/score: 0.95/i)).toBeInTheDocument();
    });

    mockFetchImages.mockResolvedValueOnce(mockData2);

    rerender(<ImageGrid query="ocean" page={1} />);

    await waitFor(() => {
      expect(screen.getByText(/score: 0.88/i)).toBeInTheDocument();
    });

    expect(mockFetchImages).toHaveBeenCalledTimes(2);
  });

  test('refetches images when page changes', async () => {
    const mockData = {
      query: 'mountains',
      results: [{ image_id: 1, image_url: 'http://example.com/1.jpg', score: 0.95 }],
    };

    mockFetchImages.mockResolvedValue(mockData);

    const { rerender } = render(<ImageGrid query="mountains" page={1} />);

    await waitFor(() => {
      expect(mockFetchImages).toHaveBeenCalledWith('mountains', 1);
    });

    rerender(<ImageGrid query="mountains" page={2} />);

    await waitFor(() => {
      expect(mockFetchImages).toHaveBeenCalledWith('mountains', 2);
    });

    expect(mockFetchImages).toHaveBeenCalledTimes(2);
  });
});
