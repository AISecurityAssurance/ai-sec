/**
 * STPA-Sec+ Analysis Orchestrator Plugin
 * 
 * This plugin provides intelligent synthesis across multiple security analysis frameworks,
 * allowing users to import existing analyses and generate unified insights.
 */

import { AnalysisPlugin, AnalysisResult, AnalysisOptions } from '@prototype1/types';
import { STPASecPlusSynthesisEngine } from './synthesis/SynthesisEngine';
import { ImportAdapterRegistry } from './adapters/ImportAdapterRegistry';
import { GapDetectionEngine } from './synthesis/GapDetectionEngine';
import { ConflictResolver } from './synthesis/ConflictResolver';
import { UnifiedRiskScorer } from './synthesis/UnifiedRiskScorer';

export class STPASecPlusPlugin implements AnalysisPlugin {
  id = 'stpa-sec-plus';
  name = 'STPA-Sec+ Orchestrator';
  version = '1.0.0';
  description = 'Intelligent synthesis layer for all security analyses';
  
  // Plugin capabilities
  capabilities = {
    import: true,
    export: true,
    synthesis: true,
    native: true,
    realtime: true,
    compliance: true,
    cve: true
  };
  
  // Supported frameworks for orchestration
  supportedFrameworks = [
    'STPA-Sec',
    'STRIDE', 
    'PASTA',
    'OCTAVE',
    'DREAD',
    'MAESTRO',
    'LINDDUN',
    'HAZOP',
    'NIST-CSF',
    'ISO27001'
  ];
  
  // Supported import formats
  supportedImports = [
    'microsoft-tmt',      // Microsoft Threat Modeling Tool
    'stride-csv',         // Generic STRIDE CSV
    'pasta-json',         // PASTA JSON export
    'octave-xml',         // OCTAVE Allegro
    'nist-csf-xlsx',      // NIST CSF Excel
    'iso27001-xlsx',      // ISO 27001 checklist
    'custom-json',        // Generic JSON
    'api-integration'     // Real-time API sync
  ];
  
  private synthesisEngine: STPASecPlusSynthesisEngine;
  private adapterRegistry: ImportAdapterRegistry;
  private gapDetector: GapDetectionEngine;
  private conflictResolver: ConflictResolver;
  private riskScorer: UnifiedRiskScorer;
  
  // Initialize plugin
  async initialize(context: any): Promise<void> {
    this.synthesisEngine = new STPASecPlusSynthesisEngine();
    this.adapterRegistry = new ImportAdapterRegistry();
    this.gapDetector = new GapDetectionEngine();
    this.conflictResolver = new ConflictResolver();
    this.riskScorer = new UnifiedRiskScorer();
    
    // Load built-in adapters
    await this.adapterRegistry.loadBuiltInAdapters();
    
    // Register with analysis store
    context.analysisStore.registerPlugin(this);
  }
  
  // Main analysis function
  async analyze(options: AnalysisOptions): Promise<AnalysisResult> {
    const { mode, data, config } = options;
    
    switch (mode) {
      case 'import':
        return this.importExternalAnalysis(data, config);
        
      case 'native':
        return this.runNativeAnalysis(data, config);
        
      case 'synthesis':
        return this.synthesizeAnalyses(config);
        
      case 'hybrid':
        return this.runHybridAnalysis(data, config);
        
      default:
        throw new Error(`Unsupported analysis mode: ${mode}`);
    }
  }
  
  // Import external analysis
  private async importExternalAnalysis(data: any, config: any): Promise<AnalysisResult> {
    const { format, file, apiConfig } = config;
    
    // Get appropriate adapter
    const adapter = this.adapterRegistry.getAdapter(format);
    if (!adapter) {
      throw new Error(`No adapter found for format: ${format}`);
    }
    
    // Validate data
    const validation = await adapter.validate(data);
    if (!validation.isValid) {
      return {
        success: false,
        errors: validation.errors,
        warnings: validation.warnings
      };
    }
    
    // Transform to standardized format
    const standardized = await adapter.transform(data);
    
    // Map to existing system model
    const mapping = await this.mapToSystemModel(standardized);
    
    // Store analysis
    await this.synthesisEngine.addAnalysis(standardized);
    
    // Run initial synthesis
    const synthesis = await this.synthesisEngine.synthesize();
    
    return {
      success: true,
      data: {
        imported: standardized,
        mapping,
        synthesis,
        gaps: synthesis.gaps,
        insights: synthesis.insights
      }
    };
  }
  
  // Run native STPA-Sec+ analysis
  private async runNativeAnalysis(data: any, config: any): Promise<AnalysisResult> {
    const { frameworks, depth } = config;
    
    // Run comprehensive STPA-Sec+ analysis
    const results = await this.synthesisEngine.runComprehensiveAnalysis(data, {
      frameworks: frameworks || this.supportedFrameworks,
      depth: depth || 'full',
      includeCompliance: true,
      includeCVE: true
    });
    
    return {
      success: true,
      data: results
    };
  }
  
  // Synthesize across all imported analyses
  private async synthesizeAnalyses(config: any): Promise<AnalysisResult> {
    const synthesis = await this.synthesisEngine.synthesize();
    
    // Detect gaps
    const gaps = await this.gapDetector.detectGaps(synthesis.analyses);
    
    // Resolve conflicts
    const conflicts = await this.conflictResolver.resolveConflicts(synthesis.analyses);
    
    // Calculate unified risk score
    const unifiedRisk = await this.riskScorer.calculateUnifiedRisk(synthesis);
    
    // Generate executive insights
    const insights = this.generateExecutiveInsights(synthesis, gaps, conflicts);
    
    return {
      success: true,
      data: {
        synthesis,
        gaps,
        conflicts,
        unifiedRisk,
        insights,
        recommendations: this.generateRecommendations(gaps, conflicts)
      }
    };
  }
  
  // Hybrid analysis - import + native
  private async runHybridAnalysis(data: any, config: any): Promise<AnalysisResult> {
    // First import existing analyses
    const importResults = await this.importExternalAnalysis(data.imports, config);
    
    // Then run native analysis to fill gaps
    const gaps = importResults.data.gaps;
    const gapFillingConfig = {
      frameworks: this.identifyMissingFrameworks(gaps),
      targetedAnalysis: true
    };
    
    const nativeResults = await this.runNativeAnalysis(data.system, gapFillingConfig);
    
    // Final synthesis
    const finalSynthesis = await this.synthesizeAnalyses(config);
    
    return {
      success: true,
      data: {
        imported: importResults.data,
        native: nativeResults.data,
        synthesis: finalSynthesis.data
      }
    };
  }
  
  // Map imported analysis to system model
  private async mapToSystemModel(standardized: any): Promise<any> {
    // Use ML/heuristics to map entities
    const entityMappings = await this.mapEntities(standardized.entities);
    const relationshipMappings = await this.mapRelationships(standardized.relationships);
    
    return {
      entityMappings,
      relationshipMappings,
      confidence: this.calculateMappingConfidence(entityMappings, relationshipMappings),
      unmapped: this.identifyUnmapped(entityMappings, relationshipMappings)
    };
  }
  
  // Map entities using similarity algorithms
  private async mapEntities(importedEntities: any[]): Promise<any[]> {
    // Implementation would use:
    // - Name similarity (Levenshtein distance)
    // - Type compatibility
    // - Property matching
    // - Context analysis
    return [];
  }
  
  // Map relationships
  private async mapRelationships(importedRelationships: any[]): Promise<any[]> {
    // Implementation would use:
    // - Source/target entity mappings
    // - Action/type similarity
    // - Protocol matching
    return [];
  }
  
  // Calculate mapping confidence
  private calculateMappingConfidence(entityMappings: any[], relationshipMappings: any[]): number {
    const entityConfidence = entityMappings.reduce((sum, m) => sum + m.confidence, 0) / entityMappings.length;
    const relationshipConfidence = relationshipMappings.reduce((sum, m) => sum + m.confidence, 0) / relationshipMappings.length;
    
    return (entityConfidence + relationshipConfidence) / 2;
  }
  
  // Identify unmapped elements
  private identifyUnmapped(entityMappings: any[], relationshipMappings: any[]): any {
    return {
      entities: entityMappings.filter(m => m.confidence < 0.5),
      relationships: relationshipMappings.filter(m => m.confidence < 0.5)
    };
  }
  
  // Generate executive insights
  private generateExecutiveInsights(synthesis: any, gaps: any[], conflicts: any[]): any[] {
    const insights = [];
    
    // Critical gap insights
    const criticalGaps = gaps.filter(g => g.severity === 'critical');
    if (criticalGaps.length > 0) {
      insights.push({
        type: 'critical_gap',
        title: `${criticalGaps.length} Critical Security Gaps Identified`,
        description: 'Missing analyses that could lead to compliance violations or breaches',
        businessImpact: this.calculateGapImpact(criticalGaps),
        recommendation: 'Immediate action required'
      });
    }
    
    // Conflict insights
    const unresolvedConflicts = conflicts.filter(c => !c.resolved);
    if (unresolvedConflicts.length > 0) {
      insights.push({
        type: 'analysis_conflict',
        title: 'Conflicting Risk Assessments Detected',
        description: 'Different frameworks disagree on risk levels',
        affectedAreas: this.identifyConflictAreas(unresolvedConflicts),
        recommendation: 'Manual review recommended'
      });
    }
    
    // Positive insights
    const coverage = this.calculateCoverage(synthesis);
    if (coverage > 0.8) {
      insights.push({
        type: 'positive',
        title: 'Comprehensive Security Coverage',
        description: `${Math.round(coverage * 100)}% of security domains covered`,
        strengths: this.identifyStrengths(synthesis)
      });
    }
    
    return insights;
  }
  
  // Generate recommendations
  private generateRecommendations(gaps: any[], conflicts: any[]): any[] {
    const recommendations = [];
    
    // Gap-based recommendations
    gaps.forEach(gap => {
      recommendations.push({
        priority: this.calculatePriority(gap),
        action: gap.recommendation,
        effort: gap.estimatedEffort,
        impact: gap.businessImpact,
        framework: gap.suggestedFramework
      });
    });
    
    // Sort by priority
    return recommendations.sort((a, b) => b.priority - a.priority);
  }
  
  // Helper methods
  private identifyMissingFrameworks(gaps: any[]): string[] {
    const missing = new Set<string>();
    gaps.forEach(gap => {
      if (gap.suggestedFramework) {
        missing.add(gap.suggestedFramework);
      }
    });
    return Array.from(missing);
  }
  
  private calculateGapImpact(gaps: any[]): string {
    // Business impact calculation logic
    const totalImpact = gaps.reduce((sum, gap) => {
      return sum + (gap.financialImpact || 0);
    }, 0);
    
    if (totalImpact > 1000000) return `$${(totalImpact / 1000000).toFixed(1)}M potential loss`;
    if (totalImpact > 1000) return `$${(totalImpact / 1000).toFixed(0)}K potential loss`;
    return 'Moderate financial impact';
  }
  
  private identifyConflictAreas(conflicts: any[]): string[] {
    const areas = new Set<string>();
    conflicts.forEach(conflict => {
      areas.add(conflict.area);
    });
    return Array.from(areas);
  }
  
  private calculateCoverage(synthesis: any): number {
    const totalDomains = 10; // Security domains
    const coveredDomains = synthesis.coveredDomains?.length || 0;
    return coveredDomains / totalDomains;
  }
  
  private identifyStrengths(synthesis: any): string[] {
    // Identify areas of strong coverage
    return synthesis.frameworks
      .filter(f => f.coverage > 0.8)
      .map(f => `${f.name}: ${Math.round(f.coverage * 100)}% coverage`);
  }
  
  private calculatePriority(gap: any): number {
    const severityScore = {
      critical: 10,
      high: 7,
      medium: 4,
      low: 1
    };
    
    const effortScore = {
      '1 day': 3,
      '2-3 days': 2,
      '1 week': 1,
      '2+ weeks': 0
    };
    
    return (severityScore[gap.severity] || 0) + (effortScore[gap.estimatedEffort] || 0);
  }
}

// Export plugin
export default STPASecPlusPlugin;