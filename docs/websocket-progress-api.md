# WebSocket Progress API Documentation

## Overview
The frontend expects WebSocket messages to update the analysis progress in real-time.

## Message Types

### 1. Analysis Update
Updates the overall analysis status.

```json
{
  "type": "analysis_update",
  "analysis_id": "uuid-here",
  "status": "in_progress", // or "completed", "failed"
  "progress": 45, // percentage 0-100
  "message": "Processing STPA-SEC framework...",
  "framework": "stpa-sec" // current framework being processed
}
```

### 2. Section Update
Updates individual analysis steps/sections.

```json
{
  "type": "section_update",
  "analysis_id": "uuid-here",
  "framework": "stpa-sec",
  "section_id": "system-modeling", // matches step IDs in frontend
  "status": "in_progress", // or "completed", "failed"
  "content": {}, // optional: actual analysis results
  "error": null // optional: error message if failed
}
```

## Expected Flow

1. User submits analysis request
2. Backend creates analysis and returns `{ id: "analysis-uuid" }`
3. Frontend subscribes to WebSocket channel for that analysis ID
4. Backend sends progress updates as it processes each framework and step
5. Frontend updates the progress indicator in real-time

## Framework Steps

Each framework has specific steps that should be reported:

### STPA-SEC
- `stpa-sec-system-modeling`
- `stpa-sec-hazard-analysis`
- `stpa-sec-control-structure`
- `stpa-sec-unsafe-actions`
- `stpa-sec-loss-scenarios`

### STRIDE
- `stride-data-flow`
- `stride-threat-modeling`
- `stride-threat-categorization`
- `stride-mitigation`

### PASTA
- `pasta-business-objectives`
- `pasta-tech-scope`
- `pasta-app-decomposition`
- `pasta-threat-analysis`
- `pasta-vulnerability-analysis`
- `pasta-attack-modeling`
- `pasta-risk-analysis`

(etc. for other frameworks...)

## Example Sequence

```javascript
// 1. Start analysis
{ type: "analysis_update", status: "in_progress", progress: 0, message: "Starting security analysis..." }

// 2. Process first framework
{ type: "analysis_update", framework: "stpa-sec", progress: 10, message: "Analyzing system with STPA-SEC..." }

// 3. Update specific steps
{ type: "section_update", framework: "stpa-sec", section_id: "system-modeling", status: "in_progress" }
{ type: "section_update", framework: "stpa-sec", section_id: "system-modeling", status: "completed" }

// 4. Continue through all steps...

// 5. Complete analysis
{ type: "analysis_update", status: "completed", progress: 100, message: "Analysis complete" }
```

## Notes
- The frontend expects section IDs in the format: `{framework}-{step-name}`
- Send updates frequently to show smooth progress
- Include error details if any step fails
- The frontend will automatically close the progress dialog when status is "completed"