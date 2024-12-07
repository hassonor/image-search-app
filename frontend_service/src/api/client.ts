const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8080';

interface SearchResponse {
  query: string;
  page: number;
  size: number;
  total: number;
  results: { image_id: number; image_url: string; score: number }[];
}

export async function fetchImages(query: string, page: number): Promise<SearchResponse> {
  const url = new URL('/get_image', API_BASE_URL);
  url.searchParams.append('query_string', query);
  url.searchParams.append('page', page.toString());
  const response = await fetch(url.toString());
  if (!response.ok) {
    throw new Error('Failed to fetch images');
  }
  // If the backend returns a list directly (no pagination wrapper), adjust accordingly
  // In previous code we returned a dict with keys, so ensure consistency with that structure.

  // Example return from previous code was a list of {image_id, image_url, score}.
  // Here we assume a pagination response. If needed, adapt to actual API.
  // For simplicity, let's assume the API returns a JSON list of results, not a dict:

  const data = await response.json();
  // If it's just a list, wrap it:
  return {
    query,
    page,
    size: 20, // default if not returned
    total: data.length,
    results: data
  };
}
