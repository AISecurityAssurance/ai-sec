# STPA-Sec+ Orchestrator Usage Example

## Quick Start Guide

### 1. Enable STPA-Sec+ in the Analysis Panel

In the Input Selection Panel, check the "STPA-Sec+ Orchestrator" option:

```typescript
// The plugin is automatically registered when the app loads
// Users just need to enable it in the UI
```

### 2. Import Existing Analyses

#### Option A: Via UI
1. Click on the STPA-Sec+ Orchestrator in the analysis panel
2. Select "Import & Synthesize" mode
3. Click "Choose File" and select your analysis file:
   - Microsoft Threat Modeling Tool (.tm7)
   - STRIDE CSV export
   - PASTA JSON file
   - Generic security CSV

#### Option B: Programmatically
```typescript
import { STPASecPlusPlugin } from './plugins/stpa-sec-plus';

// Initialize the plugin
const plugin = new STPASecPlusPlugin();
await plugin.initialize({ analysisStore: store });

// Import a Microsoft TMT file
const tmtAnalysis = await plugin.analyze({
  mode: 'import',
  data: tmtFileContent,
  config: {
    format: 'microsoft-tmt',
    file: 'threat-model.tm7'
  }
});

// Import a STRIDE CSV
const strideAnalysis = await plugin.analyze({
  mode: 'import',
  data: csvContent,
  config: {
    format: 'stride-csv',
    file: 'stride-analysis.csv'
  }
});
```

### 3. Run Synthesis

After importing multiple analyses, run the synthesis:

```typescript
// Synthesize all imported analyses
const synthesis = await plugin.analyze({
  mode: 'synthesis',
  config: {
    includeCompliance: true,
    includeCVE: true,
    depth: 'full'
  }
});

// Review the results
console.log('Unified Risk Score:', synthesis.data.unifiedRisk);
console.log('Gaps Found:', synthesis.data.gaps.length);
console.log('Insights:', synthesis.data.insights);
```

### 4. Review Results in the UI

#### Overview Tab
- **Unified Risk Score**: Combined risk assessment across all frameworks
- **Completeness Score**: How comprehensive your analysis coverage is
- **Confidence Level**: Reliability of the synthesis results
- **Coverage Map**: Visual representation of security domain coverage

#### Gaps Tab
- Lists all identified gaps sorted by severity
- Each gap includes:
  - Description of what's missing
  - Business impact
  - Recommended framework to fill the gap
  - Estimated effort
  - Affected entities

#### Insights Tab
- Cross-framework insights that individual analyses might miss
- Hidden dependencies
- Correlated attack paths
- Actionable recommendations with business value

#### Recommendations Tab
- Prioritized list of security improvements
- ROI calculations for each recommendation
- Implementation guidance

### 5. Fill Gaps with Targeted Analysis

```typescript
// Run hybrid analysis to fill identified gaps
const hybridAnalysis = await plugin.analyze({
  mode: 'hybrid',
  data: {
    imports: previousAnalyses,
    system: systemModel
  },
  config: {
    targetGaps: ['missing_privacy_analysis', 'missing_ai_security'],
    frameworks: ['LINDDUN', 'MAESTRO']
  }
});
```

## Common Use Cases

### Use Case 1: Consolidating Multiple Security Assessments

```typescript
// Import all existing analyses
const analyses = [];
for (const file of securityAssessmentFiles) {
  const result = await plugin.analyze({
    mode: 'import',
    data: file.content,
    config: { format: detectFormat(file.name) }
  });
  analyses.push(result);
}

// Run synthesis
const synthesis = await plugin.analyze({
  mode: 'synthesis'
});

// Generate executive report
const executiveMetrics = synthesis.data.insights
  .filter(i => i.type === 'executive_summary')[0];
```

### Use Case 2: Compliance Gap Analysis

```typescript
// Focus on compliance gaps
const complianceAnalysis = await plugin.analyze({
  mode: 'synthesis',
  config: {
    focusAreas: ['compliance'],
    frameworks: ['GDPR', 'PCI-DSS', 'HIPAA']
  }
});

// Get specific compliance gaps
const gdprGaps = complianceAnalysis.data.gaps
  .filter(g => g.complianceImpact?.includes('GDPR'));
```

### Use Case 3: Risk Prioritization

```typescript
// Get unified risk scores for all entities
const riskPrioritization = await plugin.analyze({
  mode: 'synthesis',
  config: {
    outputFormat: 'risk_matrix',
    includeContextualScoring: true
  }
});

// Top 10 risks across all frameworks
const topRisks = riskPrioritization.data.unifiedRisk.topRisks;
```

## Advanced Features

### Custom Import Adapters

```typescript
// Register a custom adapter for proprietary format
import { ImportAdapterRegistry } from './plugins/stpa-sec-plus/adapters';

const customAdapter = {
  format: 'my-custom-format',
  version: '1.0',
  async validate(data) { /* validation logic */ },
  async transform(data) { /* transform to standardized format */ },
  async mapToEntities(analysis, entities) { /* entity mapping */ },
  async extractRisks(analysis) { /* risk extraction */ }
};

registry.registerAdapter('my-custom-format', customAdapter);
```

### Real-time Analysis Updates

```typescript
// Connect to external security tools for real-time updates
const realtimeConfig = {
  mode: 'synthesis',
  config: {
    realtime: true,
    sources: [
      { type: 'api', url: 'https://security-tool.com/api', key: 'xxx' },
      { type: 'webhook', endpoint: '/webhooks/security-updates' }
    ],
    updateInterval: 3600 // 1 hour
  }
};
```

### Export Synthesis Results

```typescript
// Export results in various formats
const exportFormats = ['json', 'pdf', 'excel', 'powerpoint'];

for (const format of exportFormats) {
  const exported = await plugin.export({
    data: synthesis.data,
    format: format,
    template: format === 'powerpoint' ? 'executive' : 'detailed'
  });
  
  // Save or send the exported file
  await saveFile(`synthesis-report.${format}`, exported);
}
```

## Best Practices

### 1. Start with Import
- Import all existing security analyses first
- Let STPA-Sec+ identify gaps before running new analyses
- This avoids duplicate effort

### 2. Review Conflicts
- Always review conflict resolutions
- High-confidence conflicts may indicate real disagreements between teams
- Use manual override when domain expertise suggests different resolution

### 3. Iterative Refinement
- Run synthesis after each new analysis
- Track confidence scores over time
- Focus on filling high-priority gaps first

### 4. Executive Communication
- Use the unified risk score for executive dashboards
- Present ROI calculations to justify security investments
- Show coverage improvements over time

### 5. Integration
- Connect STPA-Sec+ to your CI/CD pipeline
- Automate imports from security scanning tools
- Set up alerts for new critical gaps

## Troubleshooting

### Import Failures
```typescript
// Check validation errors
if (!result.success) {
  console.error('Import failed:', result.errors);
  console.warn('Warnings:', result.warnings);
}

// Try generic adapter for unknown formats
const fallbackResult = await plugin.analyze({
  mode: 'import',
  data: content,
  config: { format: 'generic-csv' }
});
```

### Low Confidence Scores
- Import more analyses to increase coverage
- Ensure recent analysis data (< 90 days old)
- Check for entity mapping issues
- Review and resolve conflicts

### Performance Issues
- Use batch import for multiple files
- Enable caching for synthesis results
- Limit synthesis depth for quick previews

## API Reference

See [STPA-Sec+ API Documentation](./api/stpa-sec-plus.md) for complete API details.