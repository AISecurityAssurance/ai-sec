# STPA-Sec Demo Analyses

This directory contains pre-packaged demo analyses that can be loaded without running AI agents.

## Available Demos

### banking-analysis
A comprehensive STPA-Sec Step 1 analysis of a digital banking platform including:
- Mission analysis
- Loss identification  
- Hazard identification
- Security constraints
- System boundaries
- Stakeholder analysis
- Validation report

## Running a Demo

To load the banking demo:

```bash
./ai-sec demo --name banking-analysis
```

This will:
1. Create a new analysis database
2. Load the pre-packaged results
3. Generate reports and display summary
4. Save outputs to the configured output directory

## Demo Structure

Each demo contains:
- `analysis-config.yaml` - Configuration used for the analysis
- `system-description.txt` - Original system description
- `results/` - Pre-computed analysis results
  - `mission_analyst.json`
  - `loss_identification.json`
  - `hazard_identification.json`
  - `security_constraints.json`
  - `system_boundaries.json`
  - `stakeholder_analyst.json`
  - `validation.json`
- `step1_analysis_report.md` - Generated markdown report

## Benefits

- Quick demonstration without API keys
- Consistent results for testing
- Example of expected output quality
- Baseline for comparing AI-generated analyses