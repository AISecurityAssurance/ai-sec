import { test, expect } from '@playwright/test';

test.describe('All Frameworks Integration', () => {
  const frameworks = [
    { id: 'STPA_SEC', name: 'STPA-SEC', sections: 10 },
    { id: 'STRIDE', name: 'STRIDE', sections: 8 },
    { id: 'PASTA', name: 'PASTA', sections: 7 },
    { id: 'DREAD', name: 'DREAD', sections: 6 },
    { id: 'MAESTRO', name: 'MAESTRO', sections: 8 },
    { id: 'LINDDUN', name: 'LINDDUN', sections: 8 },
    { id: 'HAZOP', name: 'HAZOP', sections: 8 },
    { id: 'OCTAVE', name: 'OCTAVE', sections: 8 }
  ];

  test('can select and run all 8 frameworks', async ({ page, request }) => {
    // Create analysis with all frameworks via API for speed
    const response = await request.post('http://localhost:8000/api/analysis/', {
      data: {
        project_id: '00000000-0000-0000-0000-000000000000',
        system_description: `
          Comprehensive Security Test System
          - Authentication and authorization components
          - Data storage and processing
          - Network communication layers
          - AI/ML components for testing MAESTRO
          - Personal data handling for LINDDUN
          - Process controls for HAZOP
          - Organizational assets for OCTAVE
        `,
        frameworks: frameworks.map(f => f.id),
      }
    });
    
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    const analysisId = data.id;
    
    // Navigate to analysis page
    await page.goto(`/analysis/${analysisId}`);
    
    // Verify all framework tabs are present
    for (const framework of frameworks) {
      await expect(page.locator(`text=${framework.name}`)).toBeVisible({ timeout: 30000 });
    }
  });

  test.describe('Individual Framework Tests', () => {
    let analysisId: string;

    test.beforeAll(async ({ request }) => {
      // Create comprehensive analysis
      const response = await request.post('http://localhost:8000/api/analysis/', {
        data: {
          project_id: '00000000-0000-0000-0000-000000000000',
          system_description: 'Comprehensive test system for all frameworks',
          frameworks: frameworks.map(f => f.id),
        }
      });
      
      const data = await response.json();
      analysisId = data.id;
      
      // Wait for analysis to progress
      await new Promise(resolve => setTimeout(resolve, 10000));
    });

    test('STPA-SEC shows safety and security analysis', async ({ page }) => {
      await page.goto(`/analysis/${analysisId}`);
      await page.click('text=STPA-SEC');
      
      // Check for key STPA-SEC elements
      await expect(page.locator('text=Control Structure')).toBeVisible();
      await expect(page.locator('text=Unsafe Control Actions')).toBeVisible();
      await expect(page.locator('text=Loss Scenarios')).toBeVisible();
    });

    test('STRIDE shows threat categories', async ({ page }) => {
      await page.goto(`/analysis/${analysisId}`);
      await page.click('text=STRIDE');
      
      // Check for STRIDE categories
      const categories = ['Spoofing', 'Tampering', 'Repudiation', 'Information Disclosure', 'Denial of Service', 'Elevation of Privilege'];
      for (const category of categories) {
        await expect(page.locator(`text=/${category}/i`)).toBeVisible({ timeout: 15000 });
      }
    });

    test('PASTA shows process stages', async ({ page }) => {
      await page.goto(`/analysis/${analysisId}`);
      await page.click('text=PASTA');
      
      // Check for PASTA stages
      await expect(page.locator('text=/Business Objectives|Risk Analysis|Attack Simulation/')).toBeVisible();
    });

    test('DREAD shows risk scoring', async ({ page }) => {
      await page.goto(`/analysis/${analysisId}`);
      await page.click('text=DREAD');
      
      // Check for DREAD scoring elements
      await expect(page.locator('text=/Damage|Reproducibility|Exploitability/')).toBeVisible();
      await expect(page.locator('text=/Risk Score|Priority/')).toBeVisible();
    });

    test('MAESTRO shows AI/ML security analysis', async ({ page }) => {
      await page.goto(`/analysis/${analysisId}`);
      await page.click('text=MAESTRO');
      
      // Check for AI-specific threats
      await expect(page.locator('text=/AI.*Assets|Model|Agent/')).toBeVisible();
      await expect(page.locator('text=/Adversarial|Poisoning|Hallucination/')).toBeVisible();
    });

    test('LINDDUN shows privacy threats', async ({ page }) => {
      await page.goto(`/analysis/${analysisId}`);
      await page.click('text=LINDDUN');
      
      // Check for privacy categories
      await expect(page.locator('text=/Linking|Identifying|Non-repudiation/')).toBeVisible();
      await expect(page.locator('text=/Privacy.*Control|GDPR|Compliance/')).toBeVisible();
    });

    test('HAZOP shows deviation analysis', async ({ page }) => {
      await page.goto(`/analysis/${analysisId}`);
      await page.click('text=HAZOP');
      
      // Check for HAZOP elements
      await expect(page.locator('text=/Guide Word|Deviation|Safeguard/')).toBeVisible();
      await expect(page.locator('text=/NO.*MORE.*LESS|Process.*Parameter/')).toBeVisible();
    });

    test('OCTAVE shows organizational risk', async ({ page }) => {
      await page.goto(`/analysis/${analysisId}`);
      await page.click('text=OCTAVE');
      
      // Check for OCTAVE elements
      await expect(page.locator('text=/Critical Assets|Areas of Concern/')).toBeVisible();
      await expect(page.locator('text=/Organizational|Technical.*Risk/')).toBeVisible();
    });
  });

  test('framework results are cross-referenced', async ({ page, request }) => {
    // Create analysis with multiple frameworks
    const response = await request.post('http://localhost:8000/api/analysis/', {
      data: {
        project_id: '00000000-0000-0000-0000-000000000000',
        system_description: 'System for testing cross-framework references',
        frameworks: ['STPA_SEC', 'STRIDE', 'LINDDUN'],
      }
    });
    
    const data = await response.json();
    await page.goto(`/analysis/${data.id}`);
    
    // Wait for some results
    await new Promise(resolve => setTimeout(resolve, 8000));
    
    // Check that STRIDE references STPA-SEC control structure
    await page.click('text=STRIDE');
    await expect(page.locator('text=/control structure|STPA.*reference/i')).toBeVisible({ timeout: 20000 });
    
    // Check that LINDDUN considers STRIDE threats
    await page.click('text=LINDDUN');
    await expect(page.locator('text=/security.*threat|STRIDE.*finding/i')).toBeVisible({ timeout: 20000 });
  });

  test('can export results from all frameworks', async ({ page, request }) => {
    // Note: Export functionality to be implemented
    await page.goto('/');
    
    // For now, just verify the export button exists
    await expect(page.locator('button:has-text("Export")').or(page.locator('[aria-label*="export"]'))).toBeVisible();
  });
});