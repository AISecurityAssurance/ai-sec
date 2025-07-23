import { test, expect } from '@playwright/test';
import WebSocket from 'ws';

test.describe('WebSocket Integration', () => {
  test('connects to WebSocket and receives updates', async ({ request }) => {
    // Generate a user ID
    const userId = `test_user_${Date.now()}`;
    
    // Create WebSocket connection
    const ws = new WebSocket(`ws://localhost:8000/ws/${userId}`);
    const messages: any[] = [];
    
    // Set up message handler
    ws.on('message', (data) => {
      const message = JSON.parse(data.toString());
      messages.push(message);
      console.log('WebSocket message:', message);
    });
    
    // Wait for connection
    await new Promise<void>((resolve, reject) => {
      ws.on('open', () => {
        console.log('WebSocket connected');
        resolve();
      });
      ws.on('error', reject);
    });
    
    // Create an analysis to trigger updates
    const createResponse = await request.post('http://localhost:8000/api/v1/analysis', {
      data: {
        project_id: crypto.randomUUID(),
        system_description: 'Test system for WebSocket updates',
        frameworks: ['stride']  // Quick framework
      }
    });
    
    expect(createResponse.ok()).toBeTruthy();
    const analysis = await createResponse.json();
    console.log('Created analysis:', analysis.id);
    
    // Subscribe to analysis updates
    ws.send(JSON.stringify({
      type: 'subscribe',
      analysis_id: analysis.id
    }));
    
    // Wait for some updates
    await new Promise(resolve => setTimeout(resolve, 10000)); // 10 seconds
    
    // Check if we received any updates
    console.log(`Received ${messages.length} WebSocket messages`);
    
    // Look for analysis updates
    const analysisUpdates = messages.filter(m => m.type === 'analysis_update');
    const sectionUpdates = messages.filter(m => m.type === 'section_update');
    
    console.log(`Analysis updates: ${analysisUpdates.length}`);
    console.log(`Section updates: ${sectionUpdates.length}`);
    
    // Close WebSocket
    ws.close();
    
    // We should have received at least a connection message
    expect(messages.length).toBeGreaterThan(0);
  });
  
  test('WebSocket health check endpoint works', async () => {
    const ws = new WebSocket('ws://localhost:8000/ws');
    
    const message = await new Promise<string>((resolve, reject) => {
      ws.on('message', (data) => resolve(data.toString()));
      ws.on('error', reject);
    });
    
    expect(message).toBe('connected');
    ws.close();
  });
});