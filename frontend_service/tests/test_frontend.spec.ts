import { render, screen } from '@testing-library/react';
import App from '../App';

test('renders search input', () => {
  render(<App />);
  const input = screen.getByLabelText(/search images/i);
  expect(input).toBeInTheDocument();
});
