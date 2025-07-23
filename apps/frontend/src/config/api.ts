/**
 * API configuration that works in both development and production
 */

// In production, we need to ensure API calls use the correct base URL
// This handles cases where the app is accessed via hostname:port
export function getApiUrl(path: string): string {
  // If we're in development mode (Vite dev server), use relative paths
  if (import.meta.env.DEV) {
    return path;
  }
  
  // In production, construct the full URL with the current origin
  // This ensures the port is included (e.g., http://ubuntusungoddess:3002/api/...)
  const origin = window.location.origin;
  return `${origin}${path}`;
}

// Helper to make API calls with proper URL handling
export async function apiFetch(path: string, options?: RequestInit): Promise<Response> {
  const url = getApiUrl(path);
  return fetch(url, options);
}