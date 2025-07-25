# Analysis Table Architecture Notes

## Current State

We have two separate table implementations:

1. **Legacy AnalysisTable** (`/apps/user/components/AnalysisTable.tsx`)
   - Used by old analysis components (DreadAnalysis, StrideAnalysis, etc.)
   - Used by AnalysisPanel for STPA-Sec tables
   - Limited features (no scrolling, limited editing)
   - These components are NOT BEING USED in the main app

2. **Template AnalysisTable** (`/components/templates/AnalysisTable.tsx`)
   - Used by CollapsibleAnalysisContentWithTemplates
   - Full features (scrolling, editing, export, version sync)
   - This is what's actually rendered when users use the app

## How the App Works

The app uses `CollapsibleAnalysisSection` which checks if templates are available:

```typescript
const useTemplates = ['stpa-sec', 'dread', 'stride', 'pasta', 'maestro', 'linddun', 'hazop', 'octave'].includes(analysisId);
```

Since all analyses are in this list, it ALWAYS uses `CollapsibleAnalysisContentWithTemplates`, which uses the template version of AnalysisTable.

## Why We Have Legacy Code

The legacy components appear to be from an earlier iteration of the app. They're still referenced in:
- AnalysisPanel (for the old tab-based UI)
- Standalone windows that might use the old system

## Recommendation

Since the app is using the template system for all analyses, the legacy code is technical debt. However, we should NOT migrate it because:

1. It's not being used in the main flow
2. Migration would be complex (different interfaces)
3. It might break standalone windows if they're still used

Instead, when ready to clean up:
1. Verify standalone windows work with templates
2. Remove all legacy analysis components
3. Delete the legacy AnalysisTable

## The Scrolling Issue Was Fixed

The scrolling issue in the Detailed Unsafe Control Actions table was caused by conflicting pagination approaches in the template AnalysisTable. This was fixed by removing data slicing and using pure CSS scrolling.