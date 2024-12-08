const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8080';

interface SearchResponse {
  query: string;
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

  const data: SearchResponse = await response.json();
  return data;
}
