import { test, expect } from '@playwright/test';

test.describe('Simple Chat API', () => {
  let analysisId: string;

  test.beforeAll(async ({ request }) => {
    // Create an analysis for chat context
    const createResponse = await request.post('http://localhost:8000/api/v1/analysis', {
      data: {
        project_id: crypto.randomUUID(),
        system_description: 'Banking system with authentication and payment processing',
        frameworks: ['stride']
      }
    });
    
    expect(createResponse.ok()).toBeTruthy();
    const analysis = await createResponse.json();
    analysisId = analysis.id;
    console.log('Created analysis for chat:', analysisId);
    
    // Wait for analysis to progress
    await new Promise(resolve => setTimeout(resolve, 10000));
  });

  test('sends a chat message and receives AI response', async ({ request }) => {
    const response = await request.post('http://localhost:8000/api/v1/chat/', {
      data: {
        message: 'What are the main security risks in this banking system?',
        analysis_id: analysisId
      }
    });
    
    expect(response.ok()).toBeTruthy();
    const chatResponse = await response.json();
    
    expect(chatResponse).toHaveProperty('id');
    expect(chatResponse).toHaveProperty('message');
    expect(chatResponse).toHaveProperty('response');
    expect(chatResponse).toHaveProperty('analysis_id', analysisId);
    expect(chatResponse).toHaveProperty('timestamp');
    
    // Response should be relevant
    expect(chatResponse.response.toLowerCase()).toMatch(/security|risk|banking|authentication|payment/);
    
    console.log('Chat response length:', chatResponse.response.length);
  });

  test('retrieves chat history', async ({ request }) => {
    const response = await request.get(`http://localhost:8000/api/v1/chat/history?analysis_id=${analysisId}`);
    
    if (!response.ok()) {
      console.log('History error:', response.status(), await response.text());
    }
    expect(response.ok()).toBeTruthy();
    const history = await response.json();
    
    expect(history).toHaveProperty('messages');
    expect(history).toHaveProperty('total');
    expect(Array.isArray(history.messages)).toBeTruthy();
    expect(history.messages.length).toBeGreaterThan(0);
    
    // Check message structure
    const firstMessage = history.messages[0];
    expect(firstMessage).toHaveProperty('id');
    expect(firstMessage).toHaveProperty('message');
    expect(firstMessage).toHaveProperty('response');
    
    console.log(`Found ${history.total} messages in history`);
  });

  test('gets chat suggestions', async ({ request }) => {
    const response = await request.post(`http://localhost:8000/api/v1/chat/suggestions`, {
      data: { analysis_id: analysisId }
    });
    
    if (!response.ok()) {
      console.log('Suggestions error:', response.status(), await response.text());
    }
    expect(response.ok()).toBeTruthy();
    const result = await response.json();
    
    expect(result).toHaveProperty('suggestions');
    expect(Array.isArray(result.suggestions)).toBeTruthy();
    expect(result.suggestions.length).toBeGreaterThan(0);
    
    console.log('Suggestions:', result.suggestions);
  });

  test('handles chat without analysis context', async ({ request }) => {
    const response = await request.post('http://localhost:8000/api/v1/chat/', {
      data: {
        message: 'What is STRIDE threat modeling?'
        // No analysis_id provided
      }
    });
    
    expect(response.ok()).toBeTruthy();
    const chatResponse = await response.json();
    
    expect(chatResponse).toHaveProperty('response');
    expect(chatResponse.response.toLowerCase()).toMatch(/stride|threat|model/);
    expect(chatResponse.analysis_id).toBeNull();
    
    console.log('General chat response received');
  });
});