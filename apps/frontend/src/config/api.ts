/**
 * API configuration that works in both development and production
 */

// In production, we need to ensure API calls use the correct base URL
// This handles cases where the app is accessed via hostname:port
export function getApiUrl(path: string): string {
  // Always use the current origin to ensure proper port handling
  // This works for both dev and prod when accessed via hostname:port
  const origin = window.location.origin;
  const url = `${origin}${path}`;
  
  // Log for debugging
  console.log('API URL:', url, 'Origin:', origin, 'Path:', path);
  
  return url;
}

// Helper to make API calls with proper URL handling
export async function apiFetch(path: string, options?: RequestInit): Promise<Response> {
  const url = getApiUrl(path);
  return fetch(url, options);
}