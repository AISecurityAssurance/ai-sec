/**
 * Unified Risk Scorer
 * 
 * Calculates unified risk scores across multiple security analysis frameworks
 */

import type { SynthesisResult, StandardizedAnalysis, ExecutiveMetrics, AnalysisFramework } from '../types';

export class UnifiedRiskScorer {
  // Framework weights for different aspects
  private frameworkWeights: Record<string, { technical: number; systemic: number; business: number; coverage: number }> = {
    'STPA-Sec': { technical: 0.9, systemic: 1.0, business: 0.6, coverage: 0.9 },
    'STRIDE': { technical: 1.0, systemic: 0.7, business: 0.5, coverage: 0.8 },
    'PASTA': { technical: 0.7, systemic: 0.8, business: 1.0, coverage: 0.8 },
    'OCTAVE': { technical: 0.6, systemic: 0.9, business: 0.9, coverage: 0.7 },
    'DREAD': { technical: 0.8, systemic: 0.6, business: 0.7, coverage: 0.6 },
    'MAESTRO': { technical: 0.9, systemic: 0.8, business: 0.7, coverage: 0.8 },
    'LINDDUN': { technical: 0.7, systemic: 0.6, business: 0.8, coverage: 0.7 },
    'HAZOP': { technical: 0.8, systemic: 0.9, business: 0.6, coverage: 0.7 },
    'NIST-CSF': { technical: 0.7, systemic: 0.8, business: 0.8, coverage: 0.9 },
    'ISO27001': { technical: 0.7, systemic: 0.8, business: 0.8, coverage: 0.9 },
    'CUSTOM': { technical: 0.5, systemic: 0.5, business: 0.5, coverage: 0.5 }
  };
  
  // Main unified risk calculation
  async calculateUnifiedRisk(synthesis: SynthesisResult): Promise<ExecutiveMetrics> {
    const analyses = synthesis.analyses;
    
    // Calculate component scores
    const technicalRisk = this.calculateTechnicalRisk(analyses);
    const systemicRisk = this.calculateSystemicRisk(analyses);
    const businessRisk = this.calculateBusinessRisk(analyses);
    
    // Calculate unified score
    const unifiedScore = this.combineRiskScores({
      technical: technicalRisk,
      systemic: systemicRisk,
      business: businessRisk
    });
    
    // Calculate compliance score
    const complianceScore = this.calculateComplianceScore(analyses, synthesis.gaps);
    
    // Calculate coverage score
    const coverageScore = this.calculateCoverageScore(analyses);
    
    // Analyze trends
    const trendsAnalysis = this.analyzeTrends(synthesis);
    
    // Identify top risks
    const topRisks = this.identifyTopRisks(analyses);
    
    // Calculate ROI
    const investmentROI = this.calculateROI(synthesis);
    
    return {
      overallRiskScore: Math.round(unifiedScore),
      complianceScore: Math.round(complianceScore * 100),
      coverageScore: Math.round(coverageScore * 100),
      trendsAnalysis,
      topRisks,
      investmentROI
    };
  }
  
  // Calculate technical risk score
  private calculateTechnicalRisk(analyses: StandardizedAnalysis[]): number {
    if (analyses.length === 0) return 0;
    
    const technicalScores = analyses.map(analysis => {
      const weight = this.frameworkWeights[analysis.framework]?.technical || 0.5;
      const risks = analysis.risks;
      
      if (risks.length === 0) return 0;
      
      // Calculate average risk score for this analysis
      const avgRisk = risks.reduce((sum, risk) => sum + (risk.score || 0), 0) / risks.length;
      
      // Adjust for unmitigated threats
      const unmitigatedCount = analysis.threats.filter(t => 
        !this.isThreatMitigated(t, analysis.controls)
      ).length;
      const mitigationFactor = 1 + (unmitigatedCount * 0.1); // 10% increase per unmitigated threat
      
      return avgRisk * weight * mitigationFactor;
    });
    
    // Weighted average
    const totalWeight = analyses.reduce((sum, a) => 
      sum + (this.frameworkWeights[a.framework]?.technical || 0.5), 0
    );
    
    return technicalScores.reduce((sum, score) => sum + score, 0) / totalWeight;
  }
  
  // Calculate systemic risk score
  private calculateSystemicRisk(analyses: StandardizedAnalysis[]): number {
    if (analyses.length === 0) return 0;
    
    // Factors for systemic risk
    const factors = {
      cascadingFailures: this.assessCascadingFailureRisk(analyses),
      singlePointsOfFailure: this.assessSinglePointsOfFailure(analyses),
      interdependencies: this.assessInterdependencyRisk(analyses),
      emergentBehaviors: this.assessEmergentBehaviorRisk(analyses)
    };
    
    // Weight factors based on framework capabilities
    const weightedFactors = analyses.map(analysis => {
      const weight = this.frameworkWeights[analysis.framework]?.systemic || 0.5;
      const frameworkScore = this.calculateFrameworkSystemicScore(analysis, factors);
      return frameworkScore * weight;
    });
    
    const totalWeight = analyses.reduce((sum, a) => 
      sum + (this.frameworkWeights[a.framework]?.systemic || 0.5), 0
    );
    
    return weightedFactors.reduce((sum, score) => sum + score, 0) / totalWeight;
  }
  
  // Calculate business risk score
  private calculateBusinessRisk(analyses: StandardizedAnalysis[]): number {
    if (analyses.length === 0) return 0;
    
    const businessScores = analyses.map(analysis => {
      const weight = this.frameworkWeights[analysis.framework]?.business || 0.5;
      
      // Factors for business risk
      const factors = {
        financialImpact: this.assessFinancialImpact(analysis),
        reputationalImpact: this.assessReputationalImpact(analysis),
        operationalImpact: this.assessOperationalImpact(analysis),
        regulatoryImpact: this.assessRegulatoryImpact(analysis)
      };
      
      // Combine factors
      const businessScore = Object.values(factors).reduce((sum, f) => sum + f, 0) / 4;
      
      return businessScore * weight;
    });
    
    const totalWeight = analyses.reduce((sum, a) => 
      sum + (this.frameworkWeights[a.framework]?.business || 0.5), 0
    );
    
    return businessScores.reduce((sum, score) => sum + score, 0) / totalWeight;
  }
  
  // Combine risk scores into unified score
  private combineRiskScores(scores: {technical: number, systemic: number, business: number}): number {
    // Use weighted combination with emphasis on highest risk
    const weights = {
      technical: 0.35,
      systemic: 0.35,
      business: 0.30
    };
    
    // Calculate weighted average
    const weightedAvg = (scores.technical * weights.technical) +
                       (scores.systemic * weights.systemic) +
                       (scores.business * weights.business);
    
    // Apply non-linear scaling to emphasize high risks
    const maxComponent = Math.max(scores.technical, scores.systemic, scores.business);
    const scalingFactor = 1 + ((maxComponent / 10) * 0.2); // Up to 20% increase for high risks
    
    return Math.min(weightedAvg * scalingFactor, 10); // Cap at 10
  }
  
  // Calculate compliance score
  private calculateComplianceScore(analyses: StandardizedAnalysis[], gaps: any[]): number {
    // Base compliance from control implementation
    const controlCompliance = this.assessControlCompliance(analyses);
    
    // Deduct for compliance gaps
    const complianceGaps = gaps.filter(g => g.type === 'compliance_gap');
    const gapPenalty = complianceGaps.reduce((penalty, gap) => {
      const severityPenalty = {
        'critical': 0.2,
        'high': 0.15,
        'medium': 0.1,
        'low': 0.05
      };
      return penalty + (severityPenalty[gap.severity] || 0.1);
    }, 0);
    
    // Calculate framework coverage for compliance
    const requiredFrameworks = this.getRequiredComplianceFrameworks(analyses);
    const presentFrameworks = new Set(analyses.map(a => a.framework));
    const frameworkCoverage = requiredFrameworks.filter(f => presentFrameworks.has(f as AnalysisFramework)).length / 
                             requiredFrameworks.length;
    
    // Combine factors
    const baseScore = (controlCompliance * 0.6) + (frameworkCoverage * 0.4);
    return Math.max(baseScore - gapPenalty, 0);
  }
  
  // Calculate coverage score
  private calculateCoverageScore(analyses: StandardizedAnalysis[]): number {
    const coverageDomains = {
      technical: this.hasTechnicalCoverage(analyses),
      business: this.hasBusinessCoverage(analyses),
      privacy: this.hasPrivacyCoverage(analyses),
      ai_ml: this.hasAICoverage(analyses),
      supply_chain: this.hasSupplyChainCoverage(analyses),
      physical: this.hasPhysicalCoverage(analyses),
      human: this.hasHumanFactorCoverage(analyses),
      compliance: this.hasComplianceCoverage(analyses)
    };
    
    const coveredDomains = Object.values(coverageDomains).filter(covered => covered).length;
    const totalDomains = Object.keys(coverageDomains).length;
    
    // Additional credit for depth of coverage
    const depthBonus = this.calculateCoverageDepth(analyses) * 0.2;
    
    return Math.min((coveredDomains / totalDomains) + depthBonus, 1);
  }
  
  // Analyze trends
  private analyzeTrends(synthesis: SynthesisResult): any {
    // This would typically compare with historical data
    // For now, analyze based on current state
    
    const riskScore = synthesis.metrics.unifiedRiskScore;
    const hasUnmitigatedCritical = synthesis.gaps.some(g => 
      g.severity === 'critical' && g.type === 'unmitigated_threat'
    );
    const improvementPotential = synthesis.recommendations.filter(r => 
      r.impact && r.impact.includes('reduction')
    ).length;
    
    let trend: 'improving' | 'stable' | 'deteriorating' = 'stable';
    let timeframe = '30 days';
    
    if (hasUnmitigatedCritical || riskScore > 7) {
      trend = 'deteriorating';
    } else if (improvementPotential > 5) {
      trend = 'improving';
    }
    
    return {
      riskTrend: trend,
      timeframe,
      factors: [
        riskScore > 7 ? 'High overall risk score' : null,
        hasUnmitigatedCritical ? 'Critical unmitigated threats' : null,
        improvementPotential > 5 ? 'Multiple improvement opportunities' : null
      ].filter(f => f !== null)
    };
  }
  
  // Identify top risks
  private identifyTopRisks(analyses: StandardizedAnalysis[]): any[] {
    const allRisks: any[] = [];
    
    analyses.forEach(analysis => {
      analysis.risks.forEach(risk => {
        allRisks.push({
          ...risk,
          framework: analysis.framework,
          adjustedScore: this.adjustRiskScore(risk, analysis)
        });
      });
    });
    
    // Sort by adjusted score and take top 10
    return allRisks
      .sort((a, b) => b.adjustedScore - a.adjustedScore)
      .slice(0, 10)
      .map(risk => ({
        id: risk.id,
        name: risk.name,
        score: risk.adjustedScore,
        category: risk.category,
        framework: risk.framework,
        mitigated: risk.mitigated || false
      }));
  }
  
  // Calculate ROI
  private calculateROI(synthesis: SynthesisResult): any {
    // Estimate implemented controls cost
    const implementedControls = synthesis.analyses
      .flatMap(a => a.controls)
      .filter(c => c.state === 'implemented' || c.properties?.effectiveness === 'high');
    
    const implementedCost = implementedControls.length * 50000; // Rough estimate
    
    // Estimate risk reduction value
    const riskReduction = this.estimateRiskReduction(synthesis);
    const riskReductionValue = riskReduction * 1000000; // Value of 1 point risk reduction
    
    // Potential improvements
    const potentialControls = synthesis.recommendations
      .filter(r => r.type === 'gap_remediation')
      .length;
    
    const potentialCost = potentialControls * 75000; // Higher cost for new controls
    const potentialReduction = potentialControls * 0.5; // 0.5 point reduction per control
    const potentialValue = potentialReduction * 1000000;
    
    return {
      implemented: Math.round(riskReductionValue / implementedCost * 100) / 100,
      potential: Math.round(potentialValue / potentialCost * 100) / 100,
      recommendations: [
        `Current security ROI: ${Math.round(riskReductionValue / implementedCost * 100)}%`,
        `Potential ROI from recommendations: ${Math.round(potentialValue / potentialCost * 100)}%`,
        potentialControls > 0 ? `Implement ${potentialControls} recommended controls` : null
      ].filter(r => r !== null)
    };
  }
  
  // Helper methods for risk assessment
  private isThreatMitigated(threat: any, controls: any[]): boolean {
    return controls.some(c => 
      c.threatId === threat.originalId ||
      c.properties?.mitigates?.includes(threat.originalId) ||
      (c.state === 'implemented' && c.properties?.protectedEntity === threat.affectedEntity)
    );
  }
  
  private assessCascadingFailureRisk(analyses: StandardizedAnalysis[]): number {
    // Look for highly connected entities
    const connectionCounts = new Map<string, number>();
    
    analyses.forEach(a => {
      a.relationships.forEach(r => {
        connectionCounts.set(r.source, (connectionCounts.get(r.source) || 0) + 1);
        connectionCounts.set(r.target, (connectionCounts.get(r.target) || 0) + 1);
      });
    });
    
    // High connection count increases cascading risk
    const highlyConnected = Array.from(connectionCounts.values())
      .filter(count => count > 5).length;
    
    return Math.min(highlyConnected * 0.5, 10);
  }
  
  private assessSinglePointsOfFailure(analyses: StandardizedAnalysis[]): number {
    let spofCount = 0;
    
    analyses.forEach(a => {
      // Entities with single control
      const entityControls = new Map<string, number>();
      a.controls.forEach(c => {
        const entity = c.properties?.protectedEntity;
        if (entity) {
          entityControls.set(entity, (entityControls.get(entity) || 0) + 1);
        }
      });
      
      spofCount += Array.from(entityControls.values())
        .filter(count => count === 1).length;
    });
    
    return Math.min(spofCount * 0.8, 10);
  }
  
  private assessInterdependencyRisk(analyses: StandardizedAnalysis[]): number {
    // Analyze relationship density
    const totalEntities = new Set<string>();
    let totalRelationships = 0;
    
    analyses.forEach(a => {
      a.entities.forEach(e => totalEntities.add(e.originalId));
      totalRelationships += a.relationships.length;
    });
    
    const density = totalEntities.size > 0 ? 
      totalRelationships / totalEntities.size : 0;
    
    // Higher density means higher interdependency risk
    return Math.min(density * 2, 10);
  }
  
  private assessEmergentBehaviorRisk(analyses: StandardizedAnalysis[]): number {
    // Look for complex control loops and feedback mechanisms
    const hasSTPA = analyses.some(a => a.framework === 'STPA-Sec');
    const hasHAZOP = analyses.some(a => a.framework === 'HAZOP');
    
    if (!hasSTPA && !hasHAZOP) {
      // High risk if systemic analysis frameworks are missing
      return 7;
    }
    
    // Lower risk if proper systemic analysis was done
    return 3;
  }
  
  private calculateFrameworkSystemicScore(analysis: StandardizedAnalysis, factors: any): number {
    // Frameworks have different strengths in identifying systemic risks
    const frameworkStrengths = {
      'STPA-Sec': { cascading: 1.0, spof: 0.9, interdep: 1.0, emergent: 1.0 },
      'HAZOP': { cascading: 0.9, spof: 0.8, interdep: 0.8, emergent: 0.9 },
      'OCTAVE': { cascading: 0.7, spof: 0.8, interdep: 0.7, emergent: 0.6 },
      'STRIDE': { cascading: 0.5, spof: 0.7, interdep: 0.5, emergent: 0.4 }
    };
    
    const strengths = frameworkStrengths[analysis.framework] || 
                     { cascading: 0.5, spof: 0.5, interdep: 0.5, emergent: 0.5 };
    
    return (factors.cascadingFailures * strengths.cascading +
            factors.singlePointsOfFailure * strengths.spof +
            factors.interdependencies * strengths.interdep +
            factors.emergentBehaviors * strengths.emergent) / 4;
  }
  
  private assessFinancialImpact(analysis: StandardizedAnalysis): number {
    // Estimate based on affected assets and threat severity
    const highValueAssets = analysis.entities.filter(e => 
      e.properties?.businessValue === 'high' ||
      e.properties?.criticality === 'critical'
    ).length;
    
    const criticalThreats = analysis.threats.filter(t => 
      t.severity === 'critical' && !this.isThreatMitigated(t, analysis.controls)
    ).length;
    
    return Math.min((highValueAssets * 1.5) + (criticalThreats * 2), 10);
  }
  
  private assessReputationalImpact(analysis: StandardizedAnalysis): number {
    // Look for privacy and data breach risks
    const privacyThreats = analysis.threats.filter(t => 
      t.category === 'information_disclosure' ||
      t.category === 'privacy' ||
      t.description.toLowerCase().includes('breach')
    ).length;
    
    const customerFacingEntities = analysis.entities.filter(e => 
      e.properties?.exposure === 'external' ||
      e.name.toLowerCase().includes('customer') ||
      e.name.toLowerCase().includes('user')
    ).length;
    
    return Math.min((privacyThreats * 2) + (customerFacingEntities * 0.5), 10);
  }
  
  private assessOperationalImpact(analysis: StandardizedAnalysis): number {
    // DoS and availability risks
    const availabilityThreats = analysis.threats.filter(t => 
      t.category === 'denial_of_service' ||
      t.description.toLowerCase().includes('availability')
    ).length;
    
    const criticalProcesses = analysis.entities.filter(e => 
      e.type === 'process' && e.properties?.criticality === 'high'
    ).length;
    
    return Math.min((availabilityThreats * 1.5) + (criticalProcesses * 1), 10);
  }
  
  private assessRegulatoryImpact(analysis: StandardizedAnalysis): number {
    // Compliance-related risks
    const complianceEntities = analysis.entities.filter(e => 
      e.properties?.dataClassification === 'pii' ||
      e.properties?.dataClassification === 'phi' ||
      e.properties?.dataClassification === 'pci'
    ).length;
    
    const unmitigatedCompliance = analysis.threats.filter(t => 
      t.properties?.complianceImpact && 
      !this.isThreatMitigated(t, analysis.controls)
    ).length;
    
    return Math.min((complianceEntities * 1) + (unmitigatedCompliance * 2), 10);
  }
  
  private assessControlCompliance(analyses: StandardizedAnalysis[]): number {
    let totalControls = 0;
    let implementedControls = 0;
    
    analyses.forEach(a => {
      totalControls += a.controls.length;
      implementedControls += a.controls.filter(c => 
        c.state === 'implemented' || 
        c.properties?.effectiveness === 'high'
      ).length;
    });
    
    return totalControls > 0 ? implementedControls / totalControls : 0;
  }
  
  private getRequiredComplianceFrameworks(analyses: StandardizedAnalysis[]): string[] {
    const required: string[] = [];
    const dataTypes = new Set<string>();
    
    analyses.forEach(a => {
      a.entities.forEach(e => {
        if (e.properties?.dataClassification) {
          dataTypes.add(e.properties.dataClassification);
        }
      });
    });
    
    // Map data types to required frameworks
    if (dataTypes.has('pii') || dataTypes.has('personal')) {
      required.push('LINDDUN', 'STRIDE');
    }
    if (dataTypes.has('phi') || dataTypes.has('health')) {
      required.push('PASTA', 'OCTAVE');
    }
    if (dataTypes.has('pci') || dataTypes.has('payment')) {
      required.push('OCTAVE', 'DREAD');
    }
    
    // Always require basic frameworks
    required.push('STRIDE', 'PASTA');
    
    return [...new Set(required)];
  }
  
  // Coverage assessment helpers
  private hasTechnicalCoverage(analyses: StandardizedAnalysis[]): boolean {
    return analyses.some(a => ['STRIDE', 'STPA-Sec', 'HAZOP'].includes(a.framework));
  }
  
  private hasBusinessCoverage(analyses: StandardizedAnalysis[]): boolean {
    return analyses.some(a => ['PASTA', 'OCTAVE'].includes(a.framework));
  }
  
  private hasPrivacyCoverage(analyses: StandardizedAnalysis[]): boolean {
    return analyses.some(a => a.framework === 'LINDDUN');
  }
  
  private hasAICoverage(analyses: StandardizedAnalysis[]): boolean {
    return analyses.some(a => a.framework === 'MAESTRO');
  }
  
  private hasSupplyChainCoverage(analyses: StandardizedAnalysis[]): boolean {
    return analyses.some(a => 
      a.threats.some(t => 
        t.category === 'supply_chain' ||
        t.description.toLowerCase().includes('third-party')
      )
    );
  }
  
  private hasPhysicalCoverage(analyses: StandardizedAnalysis[]): boolean {
    return analyses.some(a => 
      a.entities.some(e => e.type === 'physical_asset') ||
      a.threats.some(t => t.category === 'physical')
    );
  }
  
  private hasHumanFactorCoverage(analyses: StandardizedAnalysis[]): boolean {
    return analyses.some(a => 
      a.entities.some(e => e.type === 'human') ||
      a.threats.some(t => 
        t.category === 'social_engineering' ||
        t.description.toLowerCase().includes('insider')
      )
    );
  }
  
  private hasComplianceCoverage(analyses: StandardizedAnalysis[]): boolean {
    return analyses.some(a => 
      a.controls.some(c => 
        c.properties?.complianceMapping ||
        c.name.toLowerCase().includes('compliance')
      )
    );
  }
  
  private calculateCoverageDepth(analyses: StandardizedAnalysis[]): number {
    // More frameworks covering same domain = deeper coverage
    const domainCoverage = new Map<string, number>();
    
    analyses.forEach(a => {
      const domains = this.getFrameworkDomains(a.framework);
      domains.forEach(domain => {
        domainCoverage.set(domain, (domainCoverage.get(domain) || 0) + 1);
      });
    });
    
    // Average coverage depth
    const depths = Array.from(domainCoverage.values());
    const avgDepth = depths.length > 0 ? 
      depths.reduce((sum, d) => sum + d, 0) / depths.length : 0;
    
    return Math.min(avgDepth / 3, 1); // Normalize to 0-1
  }
  
  private getFrameworkDomains(framework: string): string[] {
    const domainMap = {
      'STRIDE': ['technical', 'threats'],
      'PASTA': ['business', 'process', 'threats'],
      'OCTAVE': ['business', 'operational', 'assets'],
      'STPA-Sec': ['technical', 'systemic', 'control'],
      'LINDDUN': ['privacy', 'data'],
      'MAESTRO': ['ai_ml', 'technical'],
      'HAZOP': ['operational', 'systemic'],
      'DREAD': ['risk', 'prioritization']
    };
    
    return domainMap[framework] || ['general'];
  }
  
  private adjustRiskScore(risk: any, analysis: StandardizedAnalysis): number {
    let adjustedScore = risk.score || 5;
    
    // Adjust based on framework confidence
    adjustedScore *= analysis.metadata.confidence;
    
    // Adjust based on mitigation status
    if (risk.mitigated) {
      adjustedScore *= 0.3; // 70% reduction for mitigated risks
    }
    
    // Adjust based on data recency
    const daysSinceImport = (Date.now() - analysis.metadata.importDate.getTime()) / 
                           (1000 * 60 * 60 * 24);
    if (daysSinceImport > 180) {
      adjustedScore *= 0.8; // 20% reduction for stale data
    }
    
    return adjustedScore;
  }
  
  private estimateRiskReduction(synthesis: SynthesisResult): number {
    // Estimate how much risk has been reduced by implemented controls
    let totalReduction = 0;
    
    synthesis.analyses.forEach(analysis => {
      const mitigatedThreats = analysis.threats.filter(t => 
        this.isThreatMitigated(t, analysis.controls)
      );
      
      // Each mitigated threat reduces risk
      mitigatedThreats.forEach(threat => {
        const severityReduction = {
          'critical': 2,
          'high': 1.5,
          'medium': 1,
          'low': 0.5
        };
        totalReduction += severityReduction[threat.severity] || 1;
      });
    });
    
    // Normalize to 0-10 scale
    return Math.min(totalReduction / 5, 10);
  }
}