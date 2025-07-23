/**
 * Patch global fetch to ensure API calls include the port
 * This is a workaround for production builds where the port gets stripped
 */

// Store the original fetch
const originalFetch = window.fetch;

// Override global fetch
window.fetch = function(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
  // Convert input to string URL
  let url: string;
  if (typeof input === 'string') {
    url = input;
  } else if (input instanceof URL) {
    url = input.toString();
  } else {
    url = input.url;
  }
  
  // Check if this is an API call
  if (url.startsWith('/api/') || url.startsWith('/ws/')) {
    // Ensure it uses the full origin with port
    const fullUrl = `${window.location.origin}${url}`;
    console.log('[fetch-patch] Intercepted API call:', url, '->', fullUrl);
    return originalFetch(fullUrl, init);
  }
  
  // For all other requests, use original fetch
  return originalFetch(input, init);
};

console.log('[fetch-patch] Global fetch patched to handle API URLs');