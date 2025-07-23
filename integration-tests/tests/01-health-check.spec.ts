import { test, expect } from '@playwright/test';

test.describe('Health Check', () => {
  test('frontend is accessible', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/Security Analyst/);
  });

  test('backend API is accessible', async ({ request }) => {
    const response = await request.get('http://localhost:8000/api/health');
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data.status).toBe('healthy');
  });

  test('WebSocket endpoint is available', async ({ page }) => {
    await page.goto('/');
    
    // Check if WebSocket can connect
    const wsConnected = await page.evaluate(() => {
      return new Promise((resolve) => {
        const ws = new WebSocket('ws://localhost:8000/ws');
        ws.onopen = () => {
          ws.close();
          resolve(true);
        };
        ws.onerror = () => resolve(false);
        setTimeout(() => resolve(false), 5000);
      });
    });
    
    expect(wsConnected).toBeTruthy();
  });
});