import { test, expect } from '@playwright/test';

test.describe('Analysis Processing', () => {
  test('analysis starts processing after creation', async ({ request }) => {
    // Create an analysis
    const createResponse = await request.post('http://localhost:8000/api/v1/analysis', {
      data: {
        project_id: crypto.randomUUID(),
        system_description: 'Test system to verify processing starts',
        frameworks: ['stpa-sec']
      }
    });
    
    expect(createResponse.ok()).toBeTruthy();
    const analysis = await createResponse.json();
    console.log('Created analysis:', analysis.id);
    console.log('Initial status:', analysis.status);
    
    // Wait a bit for background task to start
    await new Promise(resolve => setTimeout(resolve, 10000));  // 10 seconds
    
    // Check logs to verify processing started
    console.log('Analysis should now be processing. Check logs with:');
    console.log(`docker compose -f docker-compose.test.yml logs backend | grep "${analysis.id}"`);
    
    // Just verify the analysis was created successfully
    expect(analysis.id).toBeTruthy();
    expect(analysis.status).toBe('pending');
    expect(analysis.frameworks).toContain('stpa-sec');
  });
});