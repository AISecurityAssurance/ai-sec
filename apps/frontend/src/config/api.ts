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
    method: options?.method || 'GET',
    port: window.location.port || '80'
  });
  
  try {
    // Use window.fetch explicitly to ensure we get the patched version
    const response = await window.fetch(url, options);
    console.log('[apiFetch] Response:', response.status, response.statusText);
    return response;
  } catch (error) {
    console.error('[apiFetch] Error:', error);
    throw error;
  }
}