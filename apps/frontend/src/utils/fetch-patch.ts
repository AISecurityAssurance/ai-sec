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
  
  console.log('[fetch-patch] Intercepting fetch:', url);
  
  // Check if this is an API call
  if (url.includes('/api/') || url.includes('/ws/')) {
    // Extract the pathname if it's a full URL
    let pathname = url;
    try {
      const urlObj = new URL(url);
      pathname = urlObj.pathname;
      
      // If the URL is missing the port, fix it
      if (urlObj.port === '' && window.location.port !== '') {
        urlObj.port = window.location.port;
        url = urlObj.toString();
        console.log('[fetch-patch] Fixed missing port:', url);
      }
    } catch (e) {
      // Not a full URL, construct it
      url = `${window.location.origin}${pathname}`;
      console.log('[fetch-patch] Constructed full URL:', url);
    }
  }
  
  // Call original fetch with potentially modified URL
  return originalFetch(url, init);
};

console.log('[fetch-patch] Global fetch patched to handle API URLs');