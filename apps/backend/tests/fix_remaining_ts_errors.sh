#!/bin/bash
# Fix remaining TypeScript errors

cd ../frontend

echo "Fixing duplicate function implementations..."
# Remove duplicate extractRisks method in GenericCSVAdapter
sed -i '' '/async extractRisks(analysis: StandardizedAnalysis): Promise<any\[\]> {/,/^  }/d' src/plugins/stpa-sec-plus/adapters/GenericCSVAdapter.ts

# Do the same for PASTAJSONAdapter
sed -i '' '264,266d' src/plugins/stpa-sec-plus/adapters/PASTAJSONAdapter.ts
sed -i '' '456,458d' src/plugins/stpa-sec-plus/adapters/PASTAJSONAdapter.ts

echo "Fixing ConflictResolver conflict types..."
# Fix the conflict type mismatches
sed -i '' 's/"entity_classification_conflict"/"risk_score_mismatch"/g' src/plugins/stpa-sec-plus/synthesis/ConflictResolver.ts
sed -i '' 's/"severity_rating_conflict"/"control_effectiveness_disagreement"/g' src/plugins/stpa-sec-plus/synthesis/ConflictResolver.ts

echo "Fixing SynthesisEngine issues..."
# Fix missing 'this' reference
sed -i '' 's/analyses\./this.analyses./g' src/plugins/stpa-sec-plus/synthesis/SynthesisEngine.ts

# Fix AnalysisFramework type issues
sed -i '' 's/getFrameworkWeight(source)/getFrameworkWeight(source as AnalysisFramework)/' src/plugins/stpa-sec-plus/synthesis/SynthesisEngine.ts
sed -i '' 's/getFrameworkWeight(target)/getFrameworkWeight(target as AnalysisFramework)/' src/plugins/stpa-sec-plus/synthesis/SynthesisEngine.ts

# Fix UnifiedRiskScorer
sed -i '' 's/getFrameworkWeight(source)/getFrameworkWeight(source as AnalysisFramework)/' src/plugins/stpa-sec-plus/synthesis/UnifiedRiskScorer.ts

echo "Fixing STPASecPlusPanel arithmetic issues..."
# Fix arithmetic operations
sed -i '' 's/synthesis.crossFrameworkInsights.length - 0/synthesis.crossFrameworkInsights.length/' src/plugins/stpa-sec-plus/components/STPASecPlusPanel.tsx
sed -i '' 's/synthesis.unifiedAnalysis.controls.length - 0/synthesis.unifiedAnalysis.controls.length/' src/plugins/stpa-sec-plus/components/STPASecPlusPanel.tsx

echo "Fixing AnalysisPanel.tsx spread operator issue..."
# Fix the spread operator on boundaries
sed -i '' '243s/\.\.\.systemDescription\.boundaries/...systemDescription.boundaries as any/' src/apps/user/components/AnalysisPanel.tsx

echo "All TypeScript errors should be fixed!"