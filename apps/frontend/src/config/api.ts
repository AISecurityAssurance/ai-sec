/**
 * API configuration that works in both development and production
 */

// Helper to make API calls with proper URL handling
export async function apiFetch(path: string, options?: RequestInit): Promise<Response> {
  // Always use the current origin to ensure proper port handling
  // This is critical for when the app is accessed via hostname:port
  const origin = window.location.origin;
  const url = `${origin}${path}`;
  
  // Debug logging
  console.log('[apiFetch] Making request:', {
    path,
    url,
    origin,
    method: options?.method || 'GET'
  });
  
  try {
    const response = await fetch(url, options);
    console.log('[apiFetch] Response:', response.status, response.statusText);
    return response;
  } catch (error) {
    console.error('[apiFetch] Error:', error);
    throw error;
  }
}