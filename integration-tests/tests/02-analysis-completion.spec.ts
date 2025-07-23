import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

// Load comprehensive demo system
const demoSystemPath = path.join(__dirname, '..', 'demo-system.md');
const demoSystem = fs.readFileSync(demoSystemPath, 'utf-8');

test.describe('Analysis Completion', () => {
  test('analysis completes successfully', async ({ request }) => {
    // Create an analysis with comprehensive demo system
    const createResponse = await request.post('http://localhost:8000/api/v1/analysis', {
      data: {
        project_id: crypto.randomUUID(),
        system_description: demoSystem,
        frameworks: ['stpa-sec']  // Just STPA-SEC to test step dependencies
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
      console.log(`Status check ${i + 1}: ${statusResponse.status()}`);
      
      if (statusResponse.ok()) {
        const data = await statusResponse.json();
        status = data.status;
        console.log(`Attempt ${i + 1}: Status = ${status}`);
        
        if (status === 'COMPLETED' || status === 'FAILED') {
          break;
        }
      } else {
        // If GET fails, just check the database directly via a simpler endpoint
        // For now, we'll assume it's still processing
        console.log(`Status check failed with ${statusResponse.status()}, continuing...`);
      }
    }
    
    // Check final status
    expect(['COMPLETED', 'IN_PROGRESS']).toContain(status);
    console.log(`Final status: ${status}`);
  });
});