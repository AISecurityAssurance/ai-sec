import { test, expect } from '@playwright/test';

test.describe('Create Analysis', () => {
  test('can create a new analysis', async ({ page }) => {
    await page.goto('/');
    
    // Click on "New Analysis" button
    await page.click('button:has-text("New Analysis")');
    
    // Fill in system description
    const systemDescription = `
      Test Banking System
      - User authentication
      - Payment processing
      - Transaction history
      - Fraud detection
    `;
    
    await page.fill('textarea[placeholder*="Describe your system"]', systemDescription);
    
    // Select frameworks
    await page.check('input[value="stpa-sec"]');
    await page.check('input[value="stride"]');
    
    // Start analysis
    await page.click('button:has-text("Start Analysis")');
    
    // Wait for analysis to start
    await expect(page.locator('text=Analysis in progress')).toBeVisible({ timeout: 10000 });
    
    // Verify WebSocket updates are received
    await expect(page.locator('.progress-indicator')).toBeVisible();
  });

  // TODO: Implement real-time progress updates
  // test('shows real-time progress updates', async ({ page }) => {
  //   // This test is commented out until progress percentage display is implemented
  //   await page.goto('/');
  //   await expect(page.locator('text=/\\d+%/')).toBeVisible({ timeout: 15000 });
  //   await expect(page.locator('text=/Analyzing|Completed/')).toBeVisible();
  // });

  test('handles multiple framework selection', async ({ page }) => {
    await page.goto('/');
    await page.click('button:has-text("New Analysis")');
    
    // Fill system description
    await page.fill('textarea[placeholder*="Describe your system"]', 'Multi-framework test system');
    
    // Select all frameworks
    const frameworks = ['stpa-sec', 'stride', 'pasta', 'dread'];
    for (const framework of frameworks) {
      await page.check(`input[value="${framework}"]`);
    }
    
    // Verify all selected
    for (const framework of frameworks) {
      await expect(page.locator(`input[value="${framework}"]`)).toBeChecked();
    }
    
    // Start analysis
    await page.click('button:has-text("Start Analysis")');
    
    // Verify all frameworks show in progress
    for (const framework of frameworks) {
      await expect(page.locator(`text=${framework.replace('_', '-')}`)).toBeVisible({ timeout: 15000 });
    }
  });
});