import { test, expect } from '@playwright/test';

test.describe('WebSocket Real-time Updates', () => {
  test('receives real-time progress updates', async ({ page, context }) => {
    // Open two pages to test cross-tab updates
    const page1 = page;
    const page2 = await context.newPage();
    
    // Navigate both to home
    await page1.goto('/');
    await page2.goto('/');
    
    // Start analysis on page1
    await page1.click('button:has-text("New Analysis")');
    await page1.fill('textarea[placeholder*="Describe your system"]', 'WebSocket test system');
    await page1.check('input[value="STRIDE"]');
    await page1.click('button:has-text("Start Analysis")');
    
    // Check both pages receive updates
    await expect(page1.locator('text=Analysis in progress')).toBeVisible({ timeout: 10000 });
    await expect(page2.locator('text=Analysis in progress')).toBeVisible({ timeout: 10000 });
    
    // Verify progress percentage updates on both
    await expect(page1.locator('text=/\\d+%/')).toBeVisible();
    await expect(page2.locator('text=/\\d+%/')).toBeVisible();
  });

  test('updates section status in real-time', async ({ page }) => {
    await page.goto('/');
    
    // Start a new analysis
    await page.click('button:has-text("New Analysis")');
    await page.fill('textarea[placeholder*="Describe your system"]', 'Section update test');
    await page.check('input[value="PASTA"]');
    await page.click('button:has-text("Start Analysis")');
    
    // Wait for analysis to start
    await expect(page.locator('text=Analysis in progress')).toBeVisible({ timeout: 10000 });
    
    // Monitor section status changes
    const sectionStatuses = page.locator('.section-status');
    
    // Check that sections transition from pending to in-progress to completed
    await expect(sectionStatuses.first()).toHaveClass(/pending|in-progress|completed/, { timeout: 20000 });
    
    // Verify status icon changes
    await expect(page.locator('.status-icon.completed')).toBeVisible({ timeout: 30000 });
  });

  test('handles WebSocket reconnection', async ({ page, context }) => {
    await page.goto('/');
    
    // Simulate WebSocket disconnection
    await page.evaluate(() => {
      // Access the WebSocket client if exposed globally
      if ((window as any).wsClient) {
        (window as any).wsClient.disconnect();
      }
    });
    
    // Wait a moment
    await page.waitForTimeout(2000);
    
    // Verify reconnection indicator
    await expect(page.locator('.connection-status.reconnecting')).toBeVisible();
    
    // Wait for reconnection
    await expect(page.locator('.connection-status.connected')).toBeVisible({ timeout: 10000 });
  });

  test('preserves analysis state across page refresh', async ({ page }) => {
    await page.goto('/');
    
    // Start analysis
    await page.click('button:has-text("New Analysis")');
    await page.fill('textarea[placeholder*="Describe your system"]', 'Persistence test');
    await page.check('input[value="DREAD"]');
    await page.click('button:has-text("Start Analysis")');
    
    // Wait for analysis to start
    await expect(page.locator('text=Analysis in progress')).toBeVisible({ timeout: 10000 });
    
    // Get analysis ID from URL
    await page.waitForURL(/\/analysis\/[\w-]+/);
    const url = page.url();
    
    // Refresh page
    await page.reload();
    
    // Verify state is preserved
    await expect(page).toHaveURL(url);
    await expect(page.locator('text=/Analysis in progress|Completed/')).toBeVisible({ timeout: 10000 });
  });
});