import { test, expect } from '@playwright/test';

test.describe('Chat UI Integration', () => {
  test('chat panel is visible on analysis page', async ({ page }) => {
    // Navigate to the analysis page
    await page.goto('/analysis');
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle');
    
    // Check if chat panel exists
    const chatPanel = page.locator('.chat-panel');
    await expect(chatPanel).toBeVisible({ timeout: 10000 });
    
    // Check for input field
    const chatInput = page.locator('.chat-input-field, textarea[placeholder*="Ask about"]');
    await expect(chatInput).toBeVisible();
    
    console.log('Chat panel found on analysis page');
  });

  test('can send a message in chat', async ({ page }) => {
    await page.goto('/analysis');
    await page.waitForLoadState('networkidle');
    
    // Find and fill the chat input
    const chatInput = page.locator('.chat-input-field, textarea[placeholder*="Ask about"]');
    await chatInput.fill('What is STRIDE analysis?');
    
    // Send the message (Enter key or send button)
    const sendButton = page.locator('.send-btn');
    if (await sendButton.isVisible()) {
      await sendButton.click();
    } else {
      await chatInput.press('Enter');
    }
    
    // Wait for a response (either mock or real)
    await expect(page.locator('.message.assistant')).toBeVisible({ timeout: 15000 });
    
    console.log('Successfully sent a chat message');
  });

  test('chat shows on user app analysis view', async ({ page }) => {
    // Go to user app
    await page.goto('/');
    
    // Click on an analysis if available, or create one
    const analysisItems = page.locator('.analysis-item, .sidebar-item');
    const count = await analysisItems.count();
    
    if (count > 0) {
      // Click the first analysis
      await analysisItems.first().click();
      console.log('Clicked existing analysis');
    } else {
      // Create a new analysis
      const newAnalysisBtn = page.locator('button:has-text("New Analysis")');
      if (await newAnalysisBtn.isVisible()) {
        await newAnalysisBtn.click();
        await page.fill('textarea[placeholder*="Describe your system"]', 'Test system');
        await page.check('input[value="stride"]');
        await page.click('button:has-text("Start Analysis")');
        console.log('Created new analysis');
      }
    }
    
    // Wait for chat panel
    await expect(page.locator('.chat-panel')).toBeVisible({ timeout: 10000 });
    
    console.log('Chat panel visible in user app');
  });

  test('chat input accepts text and shows send button', async ({ page }) => {
    await page.goto('/analysis');
    await page.waitForLoadState('networkidle');
    
    const chatInput = page.locator('.chat-input-field, textarea[placeholder*="Ask about"]');
    const sendButton = page.locator('.send-btn');
    
    // Initially send button should be disabled
    await expect(sendButton).toBeDisabled();
    
    // Type in the input
    await chatInput.fill('Test message');
    
    // Send button should now be enabled
    await expect(sendButton).toBeEnabled();
    
    console.log('Chat input and send button work correctly');
  });

  test('chat shows suggested questions', async ({ page }) => {
    await page.goto('/analysis');
    await page.waitForLoadState('networkidle');
    
    // Look for suggestion chips or links
    const suggestions = page.locator('.suggestion-chips-container, .suggestion-link');
    
    // Should have at least one suggestion visible
    await expect(suggestions.first()).toBeVisible({ timeout: 10000 });
    
    // Click a suggestion
    const firstSuggestion = suggestions.first();
    const suggestionText = await firstSuggestion.textContent();
    await firstSuggestion.click();
    
    // Check if the input was populated
    const chatInput = page.locator('.chat-input-field, textarea[placeholder*="Ask about"]');
    const inputValue = await chatInput.inputValue();
    
    expect(inputValue).toBeTruthy();
    console.log(`Suggestion clicked: "${suggestionText}" -> Input: "${inputValue}"`);
  });
});