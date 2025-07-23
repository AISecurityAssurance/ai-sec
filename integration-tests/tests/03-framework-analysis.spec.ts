import { test, expect } from '@playwright/test';

test.describe('Framework Analysis Results', () => {
  let analysisId: string;

  test.beforeAll(async ({ request }) => {
    // Create an analysis via API for testing
    const response = await request.post('http://localhost:8000/api/analysis/', {
      data: {
        project_id: '00000000-0000-0000-0000-000000000000',
        system_description: 'Test banking system for framework testing',
        frameworks: ['STRIDE', 'STPA_SEC'],
      }
    });
    
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    analysisId = data.id;
    
    // Wait for analysis to complete (mock or speed up for testing)
    await new Promise(resolve => setTimeout(resolve, 5000));
  });

  test('STRIDE analysis shows all sections', async ({ page }) => {
    await page.goto(`/analysis/${analysisId}`);
    
    // Check STRIDE sections
    const strideSections = [
      'Data Flow Diagram',
      'Trust Boundaries',
      'Assets',
      'Threat Identification',
      'Threat Analysis',
      'Risk Matrix',
      'Mitigations',
      'Residual Risks'
    ];
    
    for (const section of strideSections) {
      await expect(page.locator(`text=${section}`)).toBeVisible({ timeout: 10000 });
    }
  });

  test('STPA-SEC analysis shows all sections', async ({ page }) => {
    await page.goto(`/analysis/${analysisId}`);
    
    // Switch to STPA-SEC tab
    await page.click('text=STPA-SEC');
    
    // Check STPA-SEC sections
    const stpaSections = [
      'System Definition',
      'Losses',
      'Hazards',
      'System-Level Constraints',
      'Control Structure',
      'Control Actions',
      'Unsafe Control Actions',
      'Loss Scenarios',
      'Security Requirements',
      'Mitigation Strategies'
    ];
    
    for (const section of stpaSections) {
      await expect(page.locator(`text=${section}`)).toBeVisible({ timeout: 10000 });
    }
  });

  test('can view detailed results for each section', async ({ page }) => {
    await page.goto(`/analysis/${analysisId}`);
    
    // Click on a section to expand
    await page.click('text=Threat Identification');
    
    // Check for table content
    await expect(page.locator('table')).toBeVisible();
    await expect(page.locator('th:has-text("Threat")')).toBeVisible();
    await expect(page.locator('th:has-text("Category")')).toBeVisible();
  });

  test('risk matrix visualization works', async ({ page }) => {
    await page.goto(`/analysis/${analysisId}`);
    
    // Find and check risk matrix
    await page.click('text=Risk Matrix');
    
    // Check for heat map visualization
    await expect(page.locator('.heat-map-container')).toBeVisible({ timeout: 10000 });
    
    // Verify interactive elements
    const cell = page.locator('.heat-map-cell').first();
    await cell.hover();
    await expect(page.locator('.tooltip')).toBeVisible();
  });
});