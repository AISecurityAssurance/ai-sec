import { test, expect } from '@playwright/test';

test.describe('Create Analysis - Debug', () => {
  test('debug - check page content', async ({ page }) => {
    // Listen for console messages
    page.on('console', msg => console.log('Browser console:', msg.type(), msg.text()));
    page.on('pageerror', error => console.log('Page error:', error.message));
    
    await page.goto('/');
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Wait a bit more for React to render
    await page.waitForTimeout(2000);
    
    // Take a screenshot
    await page.screenshot({ path: 'debug-homepage.png', fullPage: true });
    
    // Log all button text
    const buttons = await page.locator('button').all();
    console.log(`Found ${buttons.length} buttons:`);
    for (const button of buttons) {
      const text = await button.textContent();
      console.log(`  Button: "${text}"`);
    }
    
    // Check if "New Analysis" text exists anywhere
    const newAnalysisElements = await page.locator('text="New Analysis"').count();
    console.log(`Found ${newAnalysisElements} elements with "New Analysis" text`);
    
    // Check the page HTML
    const bodyHTML = await page.locator('body').innerHTML();
    if (bodyHTML.includes('New Analysis')) {
      console.log('✅ "New Analysis" text found in HTML');
    } else {
      console.log('❌ "New Analysis" text NOT found in HTML');
      console.log('First 500 chars of body:', bodyHTML.substring(0, 500));
    }
    
    // Try different selectors
    const selectors = [
      'button:has-text("New Analysis")',
      'button:text("New Analysis")',
      '*:text("New Analysis")',
      '.btn-primary',
      '.user-layout-header button'
    ];
    
    for (const selector of selectors) {
      const count = await page.locator(selector).count();
      console.log(`Selector "${selector}": ${count} matches`);
    }
  });
});