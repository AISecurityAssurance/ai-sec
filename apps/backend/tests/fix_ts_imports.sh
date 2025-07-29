#!/bin/bash
# Fix TypeScript import issues for type-only imports

cd ../frontend

# Fix STPA-Sec+ adapter imports
echo "Fixing STPA-Sec+ adapter imports..."

# GenericCSVAdapter
sed -i '' 's/import {/import type {/' src/plugins/stpa-sec-plus/adapters/GenericCSVAdapter.ts

# MicrosoftTMTAdapter
sed -i '' 's/import {/import type {/' src/plugins/stpa-sec-plus/adapters/MicrosoftTMTAdapter.ts

# PASTAJSONAdapter
sed -i '' 's/import {/import type {/' src/plugins/stpa-sec-plus/adapters/PASTAJSONAdapter.ts

# STRIDECSVAdapter
sed -i '' 's/import {/import type {/' src/plugins/stpa-sec-plus/adapters/STRIDECSVAdapter.ts

# ImportAdapterRegistry - special case, needs selective import
sed -i '' 's/import { AnalysisImportAdapter }/import type { AnalysisImportAdapter }/' src/plugins/stpa-sec-plus/adapters/ImportAdapterRegistry.ts

# STPASecPlusPanel
sed -i '' 's/import {/import type {/' src/plugins/stpa-sec-plus/components/STPASecPlusPanel.tsx

# Synthesis components
echo "Fixing synthesis component imports..."
sed -i '' 's/import { StandardizedAnalysis, Conflict, ConflictResolution }/import type { StandardizedAnalysis, Conflict, ConflictResolution }/' src/plugins/stpa-sec-plus/synthesis/ConflictResolver.ts
sed -i '' 's/import { StandardizedAnalysis, AnalysisGap }/import type { StandardizedAnalysis, AnalysisGap }/' src/plugins/stpa-sec-plus/synthesis/GapDetectionEngine.ts
sed -i '' 's/import { StandardizedAnalysis, SynthesisResult, AnalysisGap, CrossFrameworkInsight }/import type { StandardizedAnalysis, SynthesisResult, AnalysisGap, CrossFrameworkInsight }/' src/plugins/stpa-sec-plus/synthesis/SynthesisEngine.ts
sed -i '' 's/import { SynthesisResult, StandardizedAnalysis, ExecutiveMetrics }/import type { SynthesisResult, StandardizedAnalysis, ExecutiveMetrics }/' src/plugins/stpa-sec-plus/synthesis/UnifiedRiskScorer.ts

# Fix module resolution for types package
echo "Fixing module resolution..."
sed -i '' 's|@prototype1/types|../../../../packages/types/src|g' src/plugins/stpa-sec-plus/index.ts

# Fix relative imports in services
echo "Fixing service imports..."
sed -i '' "s|import type {|import type {|g" src/services/stpaSecApiService.ts
sed -i '' "s|'../types/analysis'|'../../../packages/types/src/analysis'|" src/services/stpaSecApiService.ts

# Fix relative imports in stores
echo "Fixing store imports..."
sed -i '' "s|'../types/analysis'|'../../../packages/types/src/analysis'|" src/stores/analysisStore.ts

echo "Import fixes applied!"