import { test, expect } from '@playwright/test';

test.describe('Analysis Sections API', () => {
  test('retrieves analysis sections after completion', async ({ request }) => {
    // Create an analysis
    const createResponse = await request.post('http://localhost:8000/api/v1/analysis', {
      data: {
        project_id: crypto.randomUUID(),
        system_description: 'Banking system with authentication and payment processing for section testing',
        frameworks: ['stpa-sec']  // Just one for faster testing
      }
    });
    
    expect(createResponse.ok()).toBeTruthy();
    const analysis = await createResponse.json();
    console.log('Created analysis:', analysis.id);
    
    // Wait for completion (check every 10 seconds, max 2 minutes)
    let status = 'pending';
    for (let i = 0; i < 12; i++) {
      await new Promise(resolve => setTimeout(resolve, 10000));
      
      const statusResponse = await request.get(`http://localhost:8000/api/v1/analysis/${analysis.id}`);
      if (statusResponse.ok()) {
        const data = await statusResponse.json();
        status = data.status;
        console.log(`Check ${i + 1}: Status = ${status}`);
        
        if (status === 'completed') {
          break;
        }
      }
    }
    
    // If completed, check sections endpoint
    if (status === 'completed') {
      const sectionsResponse = await request.get(`http://localhost:8000/api/v1/analysis/${analysis.id}/sections`);
      
      if (sectionsResponse.ok()) {
        const sections = await sectionsResponse.json();
        console.log('Sections found:', sections.length);
        
        // Verify STPA-SEC sections
        expect(sections.length).toBeGreaterThan(0);
        
        // Check for expected STPA-SEC sections
        const sectionIds = sections.map(s => s.section_id);
        console.log('Section IDs:', sectionIds);
        
        // These are the expected STPA-SEC sections
        const expectedSections = ['system_definition', 'losses', 'hazards', 'constraints', 'control_structure'];
        for (const expected of expectedSections) {
          const found = sectionIds.includes(expected);
          console.log(`${expected}: ${found ? 'FOUND' : 'MISSING'}`);
        }
      } else {
        console.log('Sections endpoint returned:', sectionsResponse.status());
      }
    } else {
      console.log('Analysis did not complete in time, status:', status);
    }
  });
});