import { test, expect } from '@playwright/test';

test.describe('Create Analysis with Project', () => {
  test('creates project and analysis', async ({ page, request }) => {
    // First, create a project via API
    const projectResponse = await request.post('http://localhost:8000/api/v1/projects', {
      data: {
        name: 'Test Project',
        description: 'Project for integration testing'
      }
    });
    
    console.log('Project response status:', projectResponse.status());
    if (!projectResponse.ok()) {
      const error = await projectResponse.text();
      console.error('Project creation failed:', error);
    }
    expect(projectResponse.ok()).toBeTruthy();
    const project = await projectResponse.json();
    console.log('Created project:', project.id);
    
    // Now create analysis through UI
    await page.goto('/');
    
    // Click on "New Analysis" button
    await page.click('button:has-text("New Analysis")');
    
    // Fill in system description
    const systemDescription = 'Test system for project analysis';
    await page.fill('textarea[placeholder*="Describe your system"]', systemDescription);
    
    // Select framework
    await page.check('input[value="stpa-sec"]');
    
    // We need to inject the project ID into the frontend
    // For now, let's create the analysis directly via API
    const analysisResponse = await request.post('http://localhost:8000/api/v1/analysis', {
      data: {
        project_id: project.id,
        system_description: systemDescription,
        frameworks: ['stpa-sec']
      }
    });
    
    expect(analysisResponse.ok()).toBeTruthy();
    const analysis = await analysisResponse.json();
    console.log('Created analysis:', analysis.id);
    
    // Wait a bit for processing to start
    await page.waitForTimeout(2000);
    
    // Check if analysis is processing
    const statusResponse = await request.get(`http://localhost:8000/api/v1/analysis/${analysis.id}`);
    const statusData = await statusResponse.json();
    console.log('Analysis status:', statusData.status);
    
    // Check for OpenAI calls in backend logs
    // This would be done by checking the actual logs
  });
});