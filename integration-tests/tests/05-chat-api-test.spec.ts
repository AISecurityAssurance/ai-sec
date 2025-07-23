import { test, expect } from '@playwright/test';

test.describe('Chat API Integration', () => {
  let analysisId: string;
  let sessionId: string;

  test.beforeAll(async ({ request }) => {
    // Create an analysis for chat context
    const createResponse = await request.post('http://localhost:8000/api/v1/analysis', {
      data: {
        project_id: crypto.randomUUID(),
        system_description: 'E-commerce platform with user authentication, payment processing, and inventory management',
        frameworks: ['stride', 'stpa-sec']
      }
    });
    
    expect(createResponse.ok()).toBeTruthy();
    const analysis = await createResponse.json();
    analysisId = analysis.id;
    console.log('Created analysis for chat:', analysisId);
    
    // Wait for analysis to start processing
    await new Promise(resolve => setTimeout(resolve, 5000));
  });

  test('creates a new chat session', async ({ request }) => {
    const response = await request.post('http://localhost:8000/api/v1/chat/sessions', {
      data: {
        analysis_id: analysisId,
        title: 'Security Discussion'
      }
    });
    
    expect(response.ok()).toBeTruthy();
    const session = await response.json();
    sessionId = session.id;
    
    expect(session).toHaveProperty('id');
    expect(session).toHaveProperty('analysis_id', analysisId);
    expect(session).toHaveProperty('title', 'Security Discussion');
    expect(session).toHaveProperty('created_at');
    
    console.log('Created chat session:', sessionId);
  });

  test('sends messages and receives AI responses', async ({ request }) => {
    // Send a message
    const messageResponse = await request.post(`http://localhost:8000/api/v1/chat/sessions/${sessionId}/messages`, {
      data: {
        content: 'What are the main security risks in the authentication system?',
        role: 'user'
      }
    });
    
    expect(messageResponse.ok()).toBeTruthy();
    const message = await messageResponse.json();
    
    expect(message).toHaveProperty('id');
    expect(message).toHaveProperty('content');
    expect(message).toHaveProperty('role', 'user');
    expect(message).toHaveProperty('created_at');
    
    console.log('Sent user message:', message.id);
    
    // Wait for AI response
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Get messages to check for AI response
    const messagesResponse = await request.get(`http://localhost:8000/api/v1/chat/sessions/${sessionId}/messages`);
    expect(messagesResponse.ok()).toBeTruthy();
    
    const messages = await messagesResponse.json();
    expect(messages.length).toBeGreaterThanOrEqual(2); // User message + AI response
    
    const aiResponse = messages.find(m => m.role === 'assistant');
    expect(aiResponse).toBeTruthy();
    expect(aiResponse.content).toContain('authentication'); // Should reference the topic
    
    console.log('Received AI response with length:', aiResponse.content.length);
  });

  test('retrieves chat history', async ({ request }) => {
    const response = await request.get(`http://localhost:8000/api/v1/chat/sessions/${sessionId}/messages`);
    
    expect(response.ok()).toBeTruthy();
    const messages = await response.json();
    
    expect(Array.isArray(messages)).toBeTruthy();
    expect(messages.length).toBeGreaterThan(0);
    
    // Verify message structure
    for (const msg of messages) {
      expect(msg).toHaveProperty('id');
      expect(msg).toHaveProperty('content');
      expect(msg).toHaveProperty('role');
      expect(['user', 'assistant', 'system'].includes(msg.role)).toBeTruthy();
      expect(msg).toHaveProperty('created_at');
    }
    
    console.log(`Retrieved ${messages.length} messages from history`);
  });

  test('lists all chat sessions for an analysis', async ({ request }) => {
    const response = await request.get(`http://localhost:8000/api/v1/chat/sessions?analysis_id=${analysisId}`);
    
    expect(response.ok()).toBeTruthy();
    const sessions = await response.json();
    
    expect(Array.isArray(sessions)).toBeTruthy();
    expect(sessions.length).toBeGreaterThan(0);
    
    const ourSession = sessions.find(s => s.id === sessionId);
    expect(ourSession).toBeTruthy();
    expect(ourSession.title).toBe('Security Discussion');
    
    console.log(`Found ${sessions.length} chat sessions for analysis`);
  });

  test('updates chat session title', async ({ request }) => {
    const response = await request.patch(`http://localhost:8000/api/v1/chat/sessions/${sessionId}`, {
      data: {
        title: 'Authentication Security Analysis'
      }
    });
    
    expect(response.ok()).toBeTruthy();
    
    // Verify update
    const getResponse = await request.get(`http://localhost:8000/api/v1/chat/sessions/${sessionId}`);
    expect(getResponse.ok()).toBeTruthy();
    
    const session = await getResponse.json();
    expect(session.title).toBe('Authentication Security Analysis');
    
    console.log('Updated session title successfully');
  });

  test('handles context-aware questions', async ({ request }) => {
    // Send a context-aware question
    const messageResponse = await request.post(`http://localhost:8000/api/v1/chat/sessions/${sessionId}/messages`, {
      data: {
        content: 'Based on the STRIDE analysis, what are the spoofing threats?',
        role: 'user'
      }
    });
    
    expect(messageResponse.ok()).toBeTruthy();
    
    // Wait for response
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // Get latest messages
    const messagesResponse = await request.get(`http://localhost:8000/api/v1/chat/sessions/${sessionId}/messages`);
    const messages = await messagesResponse.json();
    
    // Find the latest AI response
    const latestAI = messages
      .filter(m => m.role === 'assistant')
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())[0];
    
    expect(latestAI).toBeTruthy();
    expect(latestAI.content.toLowerCase()).toMatch(/stride|spoof/);
    
    console.log('AI provided context-aware response about STRIDE threats');
  });

  test('exports chat session', async ({ request }) => {
    const response = await request.get(`http://localhost:8000/api/v1/chat/sessions/${sessionId}/export?format=markdown`);
    
    if (response.status() === 501) {
      console.log('Export feature not implemented yet');
      return;
    }
    
    expect(response.ok()).toBeTruthy();
    const exportData = await response.text();
    
    expect(exportData).toContain('# Security Discussion');
    expect(exportData).toContain('authentication');
    
    console.log('Exported chat session to markdown format');
  });

  test('deletes chat session', async ({ request }) => {
    // Create a temporary session to delete
    const createResponse = await request.post('http://localhost:8000/api/v1/chat/sessions', {
      data: {
        analysis_id: analysisId,
        title: 'Temporary Session'
      }
    });
    
    const tempSession = await createResponse.json();
    
    // Delete it
    const deleteResponse = await request.delete(`http://localhost:8000/api/v1/chat/sessions/${tempSession.id}`);
    expect(deleteResponse.ok()).toBeTruthy();
    
    // Verify it's gone
    const getResponse = await request.get(`http://localhost:8000/api/v1/chat/sessions/${tempSession.id}`);
    expect(getResponse.status()).toBe(404);
    
    console.log('Successfully deleted chat session');
  });

  test('handles rate limiting gracefully', async ({ request }) => {
    const messages = [];
    
    // Send multiple messages rapidly
    for (let i = 0; i < 5; i++) {
      const response = await request.post(`http://localhost:8000/api/v1/chat/sessions/${sessionId}/messages`, {
        data: {
          content: `Quick question ${i + 1}`,
          role: 'user'
        }
      });
      
      messages.push({
        status: response.status(),
        ok: response.ok()
      });
      
      // Don't wait between requests to test rate limiting
    }
    
    // At least some should succeed
    const successful = messages.filter(m => m.ok).length;
    expect(successful).toBeGreaterThan(0);
    
    // Check if any were rate limited
    const rateLimited = messages.filter(m => m.status === 429).length;
    console.log(`Sent 5 messages: ${successful} successful, ${rateLimited} rate limited`);
  });
});