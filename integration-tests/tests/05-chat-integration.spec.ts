import { test, expect } from '@playwright/test';

test.describe('Chat Integration', () => {
  let analysisId: string;

  test.beforeAll(async ({ request }) => {
    // Create an analysis with results
    const response = await request.post('http://localhost:8000/api/analysis/', {
      data: {
        project_id: '00000000-0000-0000-0000-000000000000',
        system_description: 'Banking system with authentication and payment processing',
        frameworks: ['STRIDE'],
      }
    });
    
    const data = await response.json();
    analysisId = data.id;
    
    // Wait for analysis to have some results
    await new Promise(resolve => setTimeout(resolve, 5000));
  });

  test('can ask questions about analysis', async ({ page }) => {
    await page.goto(`/analysis/${analysisId}`);
    
    // Open chat panel
    await page.click('button[aria-label="Open chat"]');
    
    // Type a question
    const question = 'What are the main security threats identified?';
    await page.fill('input[placeholder*="Ask about"]', question);
    await page.press('input[placeholder*="Ask about"]', 'Enter');
    
    // Wait for response
    await expect(page.locator('.chat-message.assistant')).toBeVisible({ timeout: 15000 });
    
    // Verify response contains relevant information
    const response = await page.locator('.chat-message.assistant').textContent();
    expect(response).toBeTruthy();
    expect(response?.toLowerCase()).toContain('threat');
  });

  test('chat maintains context across messages', async ({ page }) => {
    await page.goto(`/analysis/${analysisId}`);
    await page.click('button[aria-label="Open chat"]');
    
    // First question
    await page.fill('input[placeholder*="Ask about"]', 'What is STRIDE?');
    await page.press('input[placeholder*="Ask about"]', 'Enter');
    await expect(page.locator('.chat-message.assistant').first()).toBeVisible({ timeout: 15000 });
    
    // Follow-up question
    await page.fill('input[placeholder*="Ask about"]', 'Can you give me an example of the first threat type?');
    await page.press('input[placeholder*="Ask about"]', 'Enter');
    
    // Wait for second response
    await expect(page.locator('.chat-message.assistant').nth(1)).toBeVisible({ timeout: 15000 });
    
    // Verify context was maintained (should reference Spoofing from STRIDE)
    const response = await page.locator('.chat-message.assistant').nth(1).textContent();
    expect(response?.toLowerCase()).toMatch(/spoofing|authentication|identity/);
  });

  test('suggested questions work correctly', async ({ page }) => {
    await page.goto(`/analysis/${analysisId}`);
    await page.click('button[aria-label="Open chat"]');
    
    // Check for suggested questions
    await expect(page.locator('.suggested-questions')).toBeVisible({ timeout: 10000 });
    
    // Click a suggested question
    const suggestionButton = page.locator('.suggested-question-button').first();
    const suggestionText = await suggestionButton.textContent();
    await suggestionButton.click();
    
    // Verify question was sent
    await expect(page.locator('.chat-message.user').last()).toHaveText(suggestionText || '');
    
    // Wait for response
    await expect(page.locator('.chat-message.assistant').last()).toBeVisible({ timeout: 15000 });
  });

  test('chat persists across page navigation', async ({ page }) => {
    await page.goto(`/analysis/${analysisId}`);
    await page.click('button[aria-label="Open chat"]');
    
    // Send a message
    await page.fill('input[placeholder*="Ask about"]', 'Test persistence');
    await page.press('input[placeholder*="Ask about"]', 'Enter');
    await expect(page.locator('.chat-message.user:has-text("Test persistence")')).toBeVisible();
    
    // Navigate away and back
    await page.goto('/');
    await page.goto(`/analysis/${analysisId}`);
    await page.click('button[aria-label="Open chat"]');
    
    // Verify message history is preserved
    await expect(page.locator('.chat-message.user:has-text("Test persistence")')).toBeVisible();
  });
});