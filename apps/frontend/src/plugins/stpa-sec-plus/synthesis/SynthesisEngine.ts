/**
 * STPA-Sec+ Synthesis Engine
 * 
 * Core engine that synthesizes insights across multiple security analysis frameworks
 */

import type { StandardizedAnalysis, SynthesisResult, AnalysisGap, CrossFrameworkInsight } from '../types';

export class STPASecPlusSynthesisEngine {
  private analyses: Map<string, StandardizedAnalysis> = new Map();
  private synthesisHistory: SynthesisResult[] = [];
  
  // Add an analysis to the synthesis pool
  async addAnalysis(analysis: StandardizedAnalysis): Promise<void> {
    const key = `${analysis.framework}-${analysis.metadata.source}`;
    this.this.analyses.set(key, analysis);
  }
  
  // Main synthesis function
  async synthesize(): Promise<SynthesisResult> {
    const analysesArray = Array.from(this.this.analyses.values());
    
    // Detect gaps across frameworks
    const gaps = this.detectGaps(analysesArray);
    
    // Find conflicts between analyses
    const conflicts = this.detectConflicts(analysesArray);
    
    // Generate cross-framework insights
    const insights = this.generateInsights(analysesArray);
    
    // Generate recommendations
    const recommendations = this.generateRecommendations(gaps, insights);
    
    // Calculate metrics
    const metrics = {
      unifiedRiskScore: this.calculateUnifiedRisk(analysesArray),
      completenessScore: this.calculateCompleteness(analysesArray),
      confidenceLevel: this.calculateConfidence(analysesArray),
      coverageMap: this.calculateCoverageMap(analysesArray)
    };
    
    const result: SynthesisResult = {
      timestamp: new Date(),
      analyses: analysesArray,
      gaps,
      conflicts,
      insights,
      recommendations,
      metrics
    };
    
    this.synthesisHistory.push(result);
    
    return result;
  }
  
  // Detect gaps in analysis coverage
  private detectGaps(analyses: StandardizedAnalysis[]): AnalysisGap[] {
    const gaps: AnalysisGap[] = [];
    const frameworks = new Set(this.analyses.map(a => a.framework));
    
    // Check for missing privacy analysis
    if (this.hasPersonalDataFlows(analyses) && !frameworks.has('LINDDUN')) {
      gaps.push({
        id: 'gap-privacy-001',
        type: 'missing_privacy_analysis',
        severity: 'high',
        description: 'Personal data flows detected without privacy threat modeling',
        affectedEntities: this.getPersonalDataEntities(analyses),
        recommendation: 'Conduct LINDDUN privacy threat modeling',
        estimatedEffort: '2-3 days',
        businessImpact: 'GDPR/CCPA compliance risk, potential fines up to $20M',
        complianceImpact: ['GDPR', 'CCPA', 'HIPAA']
      });
    }
    
    // Check for missing AI/ML security
    if (this.hasAIComponents(analyses) && !frameworks.has('MAESTRO')) {
      gaps.push({
        id: 'gap-ai-001',
        type: 'missing_ai_security',
        severity: 'critical',
        description: 'AI/ML components without specialized security analysis',
        affectedEntities: this.getAIEntities(analyses),
        recommendation: 'Apply MAESTRO framework for AI security',
        estimatedEffort: '3-5 days',
        businessImpact: 'AI manipulation, model theft, adversarial attacks'
      });
    }
    
    // Check for missing deviation analysis
    if (this.hasComplexControlFlows(analyses) && !frameworks.has('HAZOP')) {
      gaps.push({
        id: 'gap-deviation-001',
        type: 'missing_deviation_analysis',
        severity: 'medium',
        description: 'Complex control flows without systematic deviation analysis',
        affectedEntities: this.getControlFlowEntities(analyses),
        recommendation: 'Apply HAZOP guide words to critical control actions',
        estimatedEffort: '2-3 days',
        businessImpact: 'Unidentified failure modes and edge cases'
      });
    }
    
    // Check for missing business context
    if (!frameworks.has('PASTA') && this.needsBusinessContext(analyses)) {
      gaps.push({
        id: 'gap-business-001',
        type: 'missing_business_context',
        severity: 'medium',
        description: 'Technical security analysis without business risk context',
        recommendation: 'Add PASTA business-driven threat modeling',
        estimatedEffort: '1-2 days',
        businessImpact: 'Misaligned security investments'
      });
    }
    
    // Check for quantitative risk assessment
    if (!frameworks.has('DREAD') && !this.hasQuantitativeScoring(analyses)) {
      gaps.push({
        id: 'gap-quantitative-001',
        type: 'missing_quantitative_assessment',
        severity: 'low',
        description: 'No standardized quantitative risk scoring',
        recommendation: 'Apply DREAD or similar scoring methodology',
        estimatedEffort: '1 day',
        businessImpact: 'Difficulty prioritizing mitigations'
      });
    }
    
    return gaps;
  }
  
  // Detect conflicts between analyses
  private detectConflicts(analyses: StandardizedAnalysis[]): any[] {
    const conflicts = [];
    
    // Check for risk score conflicts
    const riskConflicts = this.detectRiskScoreConflicts(analyses);
    conflicts.push(...riskConflicts);
    
    // Check for control effectiveness disagreements
    const controlConflicts = this.detectControlConflicts(analyses);
    conflicts.push(...controlConflicts);
    
    // Check for threat existence conflicts
    const threatConflicts = this.detectThreatConflicts(analyses);
    conflicts.push(...threatConflicts);
    
    return conflicts;
  }
  
  // Generate cross-framework insights
  private generateInsights(analyses: StandardizedAnalysis[]): CrossFrameworkInsight[] {
    const insights: CrossFrameworkInsight[] = [];
    
    // Hidden dependency detection
    const hiddenDeps = this.detectHiddenDependencies(analyses);
    insights.push(...hiddenDeps);
    
    // Attack path correlation
    const attackPaths = this.correlateAttackPaths(analyses);
    insights.push(...attackPaths);
    
    // Control coverage analysis
    const controlGaps = this.analyzeControlCoverage(analyses);
    insights.push(...controlGaps);
    
    // Compliance mapping
    const complianceInsights = this.mapComplianceRequirements(analyses);
    insights.push(...complianceInsights);
    
    return insights;
  }
  
  // Generate actionable recommendations
  private generateRecommendations(gaps: AnalysisGap[], insights: CrossFrameworkInsight[]): any[] {
    const recommendations = [];
    
    // Priority 1: Address critical gaps
    gaps
      .filter(g => g.severity === 'critical')
      .forEach(gap => {
        recommendations.push({
          priority: 1,
          type: 'gap_remediation',
          action: gap.recommendation,
          rationale: gap.description,
          impact: gap.businessImpact,
          effort: gap.estimatedEffort,
          framework: this.suggestFramework(gap)
        });
      });
    
    // Priority 2: Leverage insights for quick wins
    insights
      .filter(i => i.actionability === 'high' && i.effort === 'low')
      .forEach(insight => {
        recommendations.push({
          priority: 2,
          type: 'optimization',
          action: insight.recommendation,
          rationale: insight.description,
          impact: insight.businessValue,
          effort: insight.effort
        });
      });
    
    // Priority 3: Strategic improvements
    this.generateStrategicRecommendations(analyses).forEach(rec => {
      recommendations.push({
        priority: 3,
        type: 'strategic',
        ...rec
      });
    });
    
    return recommendations.sort((a, b) => a.priority - b.priority);
  }
  
  // Calculate unified risk score across all analyses
  private calculateUnifiedRisk(analyses: StandardizedAnalysis[]): number {
    if (this.analyses.length === 0) return 0;
    
    // Weight different frameworks based on their strengths
    const frameworkWeights = {
      'STPA-Sec': 0.25,  // Systems thinking
      'STRIDE': 0.20,    // Technical threats
      'PASTA': 0.20,     // Business impact
      'DREAD': 0.15,     // Prioritization
      'MAESTRO': 0.10,   // AI-specific
      'LINDDUN': 0.10    // Privacy
    };
    
    let weightedSum = 0;
    let totalWeight = 0;
    
    this.analyses.forEach(analysis => {
      const weight = frameworkWeights[analysis.framework] || 0.1;
      const avgRisk = this.calculateAverageRisk(analysis);
      weightedSum += avgRisk * weight;
      totalWeight += weight;
    });
    
    return totalWeight > 0 ? weightedSum / totalWeight : 0;
  }
  
  // Calculate completeness of analysis
  private calculateCompleteness(analyses: StandardizedAnalysis[]): number {
    const requiredFrameworks = ['STPA-Sec', 'STRIDE', 'PASTA'];
    const recommendedFrameworks = ['DREAD', 'LINDDUN', 'HAZOP'];
    
    const frameworks = new Set(this.analyses.map(a => a.framework));
    
    let score = 0;
    let maxScore = 0;
    
    // Required frameworks worth more
    requiredFrameworks.forEach(fw => {
      maxScore += 2;
      if (frameworks.has(fw)) score += 2;
    });
    
    // Recommended frameworks
    recommendedFrameworks.forEach(fw => {
      maxScore += 1;
      if (frameworks.has(fw)) score += 1;
    });
    
    return maxScore > 0 ? score / maxScore : 0;
  }
  
  // Calculate confidence in synthesis
  private calculateConfidence(analyses: StandardizedAnalysis[]): number {
    if (this.analyses.length === 0) return 0;
    
    // Factors affecting confidence:
    // 1. Data quality of imported analyses
    const avgDataQuality = this.analyses.reduce((sum, a) => sum + a.metadata.confidence, 0) / this.analyses.length;
    
    // 2. Coverage overlap (more overlap = higher confidence)
    const overlapScore = this.calculateOverlapScore(analyses);
    
    // 3. Conflict resolution success
    const conflictScore = this.calculateConflictResolutionScore(analyses);
    
    // 4. Recency of data
    const recencyScore = this.calculateRecencyScore(analyses);
    
    // Weighted average
    return (avgDataQuality * 0.3) + (overlapScore * 0.3) + (conflictScore * 0.2) + (recencyScore * 0.2);
  }
  
  // Helper methods for gap detection
  private hasPersonalDataFlows(analyses: StandardizedAnalysis[]): boolean {
    return this.analyses.some(a => 
      a.entities.some(e => 
        e.properties?.dataClassification?.includes('personal') ||
        e.properties?.dataClassification?.includes('pii')
      ) ||
      a.relationships.some(r => 
        r.properties?.dataTypes?.includes('personal')
      )
    );
  }
  
  private hasAIComponents(analyses: StandardizedAnalysis[]): boolean {
    return this.analyses.some(a =>
      a.entities.some(e =>
        e.type === 'ai' ||
        e.type === 'ml_model' ||
        e.properties?.technology?.toLowerCase().includes('ai') ||
        e.properties?.technology?.toLowerCase().includes('machine learning')
      )
    );
  }
  
  private hasComplexControlFlows(analyses: StandardizedAnalysis[]): boolean {
    return this.analyses.some(a => {
      const controlRelationships = a.relationships.filter(r => r.type === 'control');
      return controlRelationships.length > 10; // Threshold for complexity
    });
  }
  
  private needsBusinessContext(analyses: StandardizedAnalysis[]): boolean {
    // Check if we have technical analysis but no business context
    const hasTechnical = this.analyses.some(a => ['STRIDE', 'STPA-Sec'].includes(a.framework));
    const hasBusiness = this.analyses.some(a => ['PASTA', 'OCTAVE'].includes(a.framework));
    return hasTechnical && !hasBusiness;
  }
  
  private hasQuantitativeScoring(analyses: StandardizedAnalysis[]): boolean {
    return this.analyses.some(a =>
      a.risks.some(r => typeof r.score === 'number')
    );
  }
  
  // Get affected entities for gaps
  private getPersonalDataEntities(analyses: StandardizedAnalysis[]): string[] {
    const entities = new Set<string>();
    this.analyses.forEach(a => {
      a.entities
        .filter(e => 
          e.properties?.dataClassification?.includes('personal') ||
          e.properties?.dataClassification?.includes('pii')
        )
        .forEach(e => entities.add(e.name));
    });
    return Array.from(entities);
  }
  
  private getAIEntities(analyses: StandardizedAnalysis[]): string[] {
    const entities = new Set<string>();
    this.analyses.forEach(a => {
      a.entities
        .filter(e =>
          e.type === 'ai' ||
          e.type === 'ml_model' ||
          e.properties?.technology?.toLowerCase().includes('ai')
        )
        .forEach(e => entities.add(e.name));
    });
    return Array.from(entities);
  }
  
  private getControlFlowEntities(analyses: StandardizedAnalysis[]): string[] {
    const entities = new Set<string>();
    this.analyses.forEach(a => {
      a.relationships
        .filter(r => r.type === 'control')
        .forEach(r => {
          entities.add(r.source);
          entities.add(r.target);
        });
    });
    return Array.from(entities);
  }
  
  // Conflict detection helpers
  private detectRiskScoreConflicts(analyses: StandardizedAnalysis[]): any[] {
    const conflicts = [];
    const risksByEntity = new Map<string, Array<{framework: string, score: number}>>();
    
    // Group risks by entity
    this.analyses.forEach(analysis => {
      analysis.risks.forEach(risk => {
        const key = risk.entityId || risk.name;
        if (!risksByEntity.has(key)) {
          risksByEntity.set(key, []);
        }
        risksByEntity.get(key)!.push({
          framework: analysis.framework,
          score: risk.score
        });
      });
    });
    
    // Find conflicts
    risksByEntity.forEach((risks, entity) => {
      if (risks.length > 1) {
        const scores = risks.map(r => r.score);
        const maxScore = Math.max(...scores);
        const minScore = Math.min(...scores);
        
        if (maxScore - minScore > 3) { // Significant difference
          conflicts.push({
            type: 'risk_score_mismatch',
            entity,
            frameworks: risks.map(r => r.framework),
            scores: risks,
            difference: maxScore - minScore,
            severity: 'medium'
          });
        }
      }
    });
    
    return conflicts;
  }
  
  private detectControlConflicts(analyses: StandardizedAnalysis[]): any[] {
    // Implementation for control effectiveness conflicts
    return [];
  }
  
  private detectThreatConflicts(analyses: StandardizedAnalysis[]): any[] {
    // Implementation for threat existence conflicts
    return [];
  }
  
  // Insight generation helpers
  private detectHiddenDependencies(analyses: StandardizedAnalysis[]): CrossFrameworkInsight[] {
    const insights: CrossFrameworkInsight[] = [];
    
    // Look for dependencies found in one framework but not others
    const dependenciesByFramework = new Map<string, Set<string>>();
    
    this.analyses.forEach(analysis => {
      const deps = new Set<string>();
      analysis.relationships.forEach(rel => {
        deps.add(`${rel.source}->${rel.target}`);
      });
      dependenciesByFramework.set(analysis.framework, deps);
    });
    
    // Find unique dependencies
    dependenciesByFramework.forEach((deps, framework) => {
      deps.forEach(dep => {
        let foundInOthers = false;
        dependenciesByFramework.forEach((otherDeps, otherFramework) => {
          if (framework !== otherFramework && otherDeps.has(dep)) {
            foundInOthers = true;
          }
        });
        
        if (!foundInOthers && deps.size > 0) {
          insights.push({
            id: `hidden-dep-${dep}`,
            type: 'hidden_dependency',
            severity: 'medium',
            description: `Dependency ${dep} only identified in ${framework} analysis`,
            frameworks: [framework],
            recommendation: `Validate ${dep} dependency in other frameworks`,
            businessValue: 'Prevent cascade failures',
            effort: 'low',
            actionability: 'high'
          });
        }
      });
    });
    
    return insights;
  }
  
  private correlateAttackPaths(analyses: StandardizedAnalysis[]): CrossFrameworkInsight[] {
    // Implementation for attack path correlation
    return [];
  }
  
  private analyzeControlCoverage(analyses: StandardizedAnalysis[]): CrossFrameworkInsight[] {
    // Implementation for control coverage analysis
    return [];
  }
  
  private mapComplianceRequirements(analyses: StandardizedAnalysis[]): CrossFrameworkInsight[] {
    // Implementation for compliance mapping
    return [];
  }
  
  // Strategic recommendation generation
  private generateStrategicRecommendations(analyses: StandardizedAnalysis[]): any[] {
    const recommendations = [];
    
    // Continuous monitoring recommendation
    if (this.shouldRecommendContinuousMonitoring(analyses)) {
      recommendations.push({
        action: 'Implement continuous security analysis',
        rationale: 'Static analysis becomes outdated quickly',
        impact: 'Real-time threat detection and response',
        effort: 'medium'
      });
    }
    
    // Framework consolidation
    if (this.shouldRecommendConsolidation(analyses)) {
      recommendations.push({
        action: 'Consolidate to STPA-Sec+ native analysis',
        rationale: 'Multiple overlapping frameworks create maintenance burden',
        impact: 'Reduced analysis time by 50%',
        effort: 'high'
      });
    }
    
    return recommendations;
  }
  
  // Helper calculation methods
  private calculateAverageRisk(analysis: StandardizedAnalysis): number {
    if (analysis.risks.length === 0) return 0;
    const sum = analysis.risks.reduce((total, risk) => total + (risk.score || 0), 0);
    return sum / analysis.risks.length;
  }
  
  private calculateOverlapScore(analyses: StandardizedAnalysis[]): number {
    // Calculate how much the analyses overlap in coverage
    if (this.analyses.length < 2) return 1;
    
    // Simple implementation - check entity overlap
    const allEntities = new Set<string>();
    const entityCounts = new Map<string, number>();
    
    this.analyses.forEach(analysis => {
      analysis.entities.forEach(entity => {
        const key = entity.name;
        allEntities.add(key);
        entityCounts.set(key, (entityCounts.get(key) || 0) + 1);
      });
    });
    
    // Calculate overlap ratio
    let overlapCount = 0;
    entityCounts.forEach(count => {
      if (count > 1) overlapCount++;
    });
    
    return allEntities.size > 0 ? overlapCount / allEntities.size : 0;
  }
  
  private calculateConflictResolutionScore(analyses: StandardizedAnalysis[]): number {
    // Placeholder - would calculate based on resolved vs unresolved conflicts
    return 0.8;
  }
  
  private calculateRecencyScore(analyses: StandardizedAnalysis[]): number {
    const now = new Date();
    const avgAge = this.analyses.reduce((sum, a) => {
      const age = now.getTime() - a.metadata.importDate.getTime();
      return sum + age;
    }, 0) / this.analyses.length;
    
    const daysOld = avgAge / (1000 * 60 * 60 * 24);
    
    // Score based on age
    if (daysOld < 30) return 1.0;
    if (daysOld < 90) return 0.8;
    if (daysOld < 180) return 0.6;
    if (daysOld < 365) return 0.4;
    return 0.2;
  }
  
  private calculateCoverageMap(analyses: StandardizedAnalysis[]): any {
    const coverage = {
      technical: 0,
      business: 0,
      privacy: 0,
      compliance: 0,
      ai_ml: 0,
      quantitative: 0
    };
    
    const frameworks = new Set(this.analyses.map(a => a.framework));
    
    // Technical coverage
    if (frameworks.has('STRIDE') || frameworks.has('STPA-Sec')) coverage.technical = 1;
    
    // Business coverage
    if (frameworks.has('PASTA') || frameworks.has('OCTAVE')) coverage.business = 1;
    
    // Privacy coverage
    if (frameworks.has('LINDDUN')) coverage.privacy = 1;
    
    // AI/ML coverage
    if (frameworks.has('MAESTRO')) coverage.ai_ml = 1;
    
    // Quantitative coverage
    if (frameworks.has('DREAD')) coverage.quantitative = 1;
    
    return coverage;
  }
  
  private suggestFramework(gap: AnalysisGap): string {
    const typeToFramework = {
      'missing_privacy_analysis': 'LINDDUN',
      'missing_ai_security': 'MAESTRO',
      'missing_deviation_analysis': 'HAZOP',
      'missing_business_context': 'PASTA',
      'missing_quantitative_assessment': 'DREAD'
    };
    
    return typeToFramework[gap.type] || 'STPA-Sec';
  }
  
  private shouldRecommendContinuousMonitoring(analyses: StandardizedAnalysis[]): boolean {
    // Recommend if analyses are getting stale
    const recencyScore = this.calculateRecencyScore(analyses);
    return recencyScore < 0.6;
  }
  
  private shouldRecommendConsolidation(analyses: StandardizedAnalysis[]): boolean {
    // Recommend if too many overlapping frameworks
    return this.analyses.length > 5;
  }
  
  // Run comprehensive native STPA-Sec+ analysis
  async runComprehensiveAnalysis(systemData: any, config: any): Promise<any> {
    // This would implement the full STPA-Sec+ methodology
    // For now, return a placeholder
    return {
      framework: 'STPA-Sec+',
      status: 'completed',
      coverage: config.frameworks,
      results: {}
    };
  }
}