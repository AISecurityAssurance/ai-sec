/**
 * Utility to reset all persisted stores to their default values
 * Use this to clear demo mode and other persisted settings
 */
export function resetAllStores() {
  // Clear all localStorage keys used by zustand persist
  const storageKeys = [
    'analysis-storage',
    'security-platform-settings'
  ];
  
  storageKeys.forEach(key => {
    localStorage.removeItem(key);
  });
  
  // Reload the page to reinitialize stores with defaults
  window.location.reload();
}

/**
 * Check if this is the first visit (no persisted state)
 */
export function isFirstVisit(): boolean {
  return !localStorage.getItem('analysis-storage') && 
         !localStorage.getItem('security-platform-settings');
}