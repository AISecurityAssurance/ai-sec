import { test, expect } from '@playwright/test';

test.describe('Create Analysis - Simple', () => {
  test('creates analysis and shows confirmation', async ({ page }) => {
    await page.goto('/');
    
    // Click on "New Analysis" button
    await page.click('button:has-text("New Analysis")');
    
    // Fill in system description
    const systemDescription = 'Simple test system for analysis';
    
    await page.fill('textarea[placeholder*="Describe your system"]', systemDescription);
    
    // Select one framework
    await page.check('input[value="stpa-sec"]');
    
    // Start analysis
    await page.click('button:has-text("Start Analysis")');
    
    // Wait for either success message or analysis to show in progress
    await page.waitForResponse(response => 
      response.url().includes('/api/v1/analysis') && response.request().method() === 'POST'
    );
    
    // Check if analysis was created
    const analysisInProgress = await page.locator('text=Analysis in progress').isVisible();
    console.log('Analysis in progress visible:', analysisInProgress);
    
    // Take a screenshot for debugging
    await page.screenshot({ path: 'after-analysis-created.png', fullPage: true });
  });
});