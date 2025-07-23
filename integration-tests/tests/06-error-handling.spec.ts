import { test, expect } from '@playwright/test';

test.describe('Error Handling', () => {
  test('handles network errors gracefully', async ({ page, context }) => {
    await page.goto('/');
    
    // Intercept API calls and simulate network error
    await page.route('**/api/analysis/**', route => {
      route.abort('failed');
    });
    
    // Try to create analysis
    await page.click('button:has-text("New Analysis")');
    await page.fill('textarea[placeholder*="Describe your system"]', 'Error test system');
    await page.check('input[value="STRIDE"]');
    await page.click('button:has-text("Start Analysis")');
    
    // Should show error message
    await expect(page.locator('text=/Error|Failed|Unable to create analysis/')).toBeVisible({ timeout: 10000 });
    
    // Should allow retry
    await expect(page.locator('button:has-text("Retry")')).toBeVisible();
  });

  test('handles invalid input gracefully', async ({ page }) => {
    await page.goto('/');
    await page.click('button:has-text("New Analysis")');
    
    // Try to submit without description
    await page.click('button:has-text("Start Analysis")');
    
    // Should show validation error
    await expect(page.locator('text=/required|provide.*description/i')).toBeVisible();
    
    // Try to submit without frameworks
    await page.fill('textarea[placeholder*="Describe your system"]', 'Test system');
    await page.click('button:has-text("Start Analysis")');
    
    // Should show framework selection error
    await expect(page.locator('text=/select.*framework/i')).toBeVisible();
  });

  test('handles API timeout gracefully', async ({ page }) => {
    await page.goto('/');
    
    // Intercept and delay response
    await page.route('**/api/analysis/**', async route => {
      await new Promise(resolve => setTimeout(resolve, 35000)); // Longer than typical timeout
      route.continue();
    });
    
    // Try to load analysis
    await page.goto('/analysis/invalid-id', { waitUntil: 'domcontentloaded' });
    
    // Should show timeout or not found error
    await expect(page.locator('text=/timeout|not found|error/i')).toBeVisible({ timeout: 40000 });
  });

  test('handles WebSocket connection failure', async ({ page }) => {
    await page.goto('/');
    
    // Block WebSocket connections
    await page.route('ws://localhost:8000/ws', route => {
      route.abort();
    });
    
    // Should show connection status indicator
    await expect(page.locator('.connection-status').or(page.locator('text=/offline|disconnected/i'))).toBeVisible({ timeout: 10000 });
    
    // Should still allow basic functionality
    await expect(page.locator('button:has-text("New Analysis")')).toBeEnabled();
  });

  test('handles partial analysis failure', async ({ page, request }) => {
    // Create analysis that will partially fail
    const response = await request.post('http://localhost:8000/api/analysis/', {
      data: {
        project_id: '00000000-0000-0000-0000-000000000000',
        system_description: 'System with intentional <script>alert("XSS")</script> content to test error handling',
        frameworks: ['STRIDE', 'INVALID_FRAMEWORK'], // Mix valid and invalid
      }
    });
    
    const data = await response.json();
    const analysisId = data.id;
    
    // Wait and check results
    await page.goto(`/analysis/${analysisId}`);
    
    // Should show partial results
    await expect(page.locator('text=STRIDE')).toBeVisible({ timeout: 15000 });
    
    // Should indicate error for invalid framework
    await expect(page.locator('.error-indicator').or(page.locator('text=/error|failed/i'))).toBeVisible();
  });

  test('handles session expiration', async ({ page, context }) => {
    await page.goto('/');
    
    // Simulate session expiration by clearing cookies
    await context.clearCookies();
    
    // Try to perform authenticated action
    await page.click('button:has-text("New Analysis")');
    
    // Should redirect to login or show auth error
    await expect(
      page.locator('text=/login|authenticate|session expired/i')
    ).toBeVisible({ timeout: 10000 });
  });
});