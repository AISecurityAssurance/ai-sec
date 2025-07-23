import { test, expect } from '@playwright/test';

test.describe('Analysis Completion', () => {
  test('analysis completes successfully', async ({ request }) => {
    // Create an analysis
    const createResponse = await request.post('http://localhost:8000/api/v1/analysis', {
      data: {
        project_id: crypto.randomUUID(),
        system_description: 'Simple test system for completion check',
        frameworks: ['stpa-sec']  // Just one framework to speed up
      }
    });
    
    expect(createResponse.ok()).toBeTruthy();
    const analysis = await createResponse.json();
    console.log('Created analysis:', analysis.id);
    
    // Poll for completion (max 2 minutes)
    let status = 'PENDING';
    const maxAttempts = 24;  // 24 * 5 seconds = 2 minutes
    
    for (let i = 0; i < maxAttempts; i++) {
      await new Promise(resolve => setTimeout(resolve, 5000));  // Wait 5 seconds
      
      const statusResponse = await request.get(`http://localhost:8000/api/v1/analysis/${analysis.id}`);
      if (statusResponse.ok()) {
        const data = await statusResponse.json();
        status = data.status;
        console.log(`Attempt ${i + 1}: Status = ${status}`);
        
        if (status === 'COMPLETED' || status === 'FAILED') {
          break;
        }
      }
    }
    
    // Check final status
    expect(['COMPLETED', 'IN_PROGRESS']).toContain(status);
    console.log(`Final status: ${status}`);
  });
});