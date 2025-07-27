/**
 * Conflict Resolver
 * 
 * Resolves conflicts between different security analyses and frameworks
 */

import type { StandardizedAnalysis, Conflict, ConflictResolution } from '../types';

export class ConflictResolver {
  // Main conflict resolution function
  async resolveConflicts(analyses: StandardizedAnalysis[]): Promise<ConflictResolution[]> {
    const conflicts = this.detectConflicts(analyses);
    const resolutions: ConflictResolution[] = [];
    
    for (const conflict of conflicts) {
      const resolution = await this.resolveConflict(conflict, analyses);
      resolutions.push(resolution);
    }
    
    return resolutions;
  }
  
  // Detect all types of conflicts
  private detectConflicts(analyses: StandardizedAnalysis[]): Conflict[] {
    const conflicts: Conflict[] = [];
    
    // Risk score conflicts
    conflicts.push(...this.detectRiskScoreConflicts(analyses));
    
    // Control effectiveness conflicts
    conflicts.push(...this.detectControlEffectivenessConflicts(analyses));
    
    // Threat existence conflicts
    conflicts.push(...this.detectThreatExistenceConflicts(analyses));
    
    // Entity classification conflicts
    conflicts.push(...this.detectEntityClassificationConflicts(analyses));
    
    // Severity rating conflicts
    conflicts.push(...this.detectSeverityRatingConflicts(analyses));
    
    return conflicts;
  }
  
  // Detect risk score conflicts
  private detectRiskScoreConflicts(analyses: StandardizedAnalysis[]): Conflict[] {
    const conflicts: Conflict[] = [];
    const risksByEntity = new Map<string, Array<{framework: string, risk: any}>>();
    
    // Group risks by entity
    analyses.forEach(analysis => {
      analysis.risks.forEach(risk => {
        const key = risk.entityId || risk.name;
        if (!risksByEntity.has(key)) {
          risksByEntity.set(key, []);
        }
        risksByEntity.get(key)!.push({
          framework: analysis.framework,
          risk
        });
      });
    });
    
    // Find conflicts
    risksByEntity.forEach((risks, entity) => {
      if (risks.length > 1) {
        const scores = risks.map(r => r.risk.score);
        const maxScore = Math.max(...scores);
        const minScore = Math.min(...scores);
        const variance = this.calculateVariance(scores);
        
        // Significant difference threshold
        if (maxScore - minScore > 3 || variance > 2) {
          conflicts.push({
            type: 'risk_score_mismatch',
            entity,
            frameworks: risks.map(r => r.framework),
            details: {
              scores: risks.map(r => ({
                framework: r.framework,
                score: r.risk.score,
                name: r.risk.name
              })),
              difference: maxScore - minScore,
              variance
            },
            severity: this.calculateConflictSeverity(maxScore - minScore)
          });
        }
      }
    });
    
    return conflicts;
  }
  
  // Detect control effectiveness conflicts
  private detectControlEffectivenessConflicts(analyses: StandardizedAnalysis[]): Conflict[] {
    const conflicts: Conflict[] = [];
    const controlsByName = new Map<string, Array<{framework: string, control: any}>>();
    
    // Group controls by name
    analyses.forEach(analysis => {
      analysis.controls.forEach(control => {
        const key = this.normalizeControlName(control.name);
        if (!controlsByName.has(key)) {
          controlsByName.set(key, []);
        }
        controlsByName.get(key)!.push({
          framework: analysis.framework,
          control
        });
      });
    });
    
    // Find effectiveness conflicts
    controlsByName.forEach((controls, name) => {
      if (controls.length > 1) {
        const effectivenessRatings = controls.map(c => 
          c.control.properties?.effectiveness || c.control.state
        ).filter(e => e);
        
        if (effectivenessRatings.length > 1 && !this.areEffectivenessRatingsConsistent(effectivenessRatings)) {
          conflicts.push({
            type: 'control_effectiveness_disagreement',
            entity: name,
            frameworks: controls.map(c => c.framework),
            details: {
              ratings: controls.map(c => ({
                framework: c.framework,
                effectiveness: c.control.properties?.effectiveness || c.control.state,
                controlName: c.control.name
              }))
            },
            severity: 'medium'
          });
        }
      }
    });
    
    return conflicts;
  }
  
  // Detect threat existence conflicts
  private detectThreatExistenceConflicts(analyses: StandardizedAnalysis[]): Conflict[] {
    const conflicts: Conflict[] = [];
    const threatsByType = new Map<string, Set<string>>();
    const frameworksByThreat = new Map<string, Set<string>>();
    
    // Collect all threat types by framework
    analyses.forEach(analysis => {
      analysis.threats.forEach(threat => {
        const threatType = this.normalizeThreatType(threat);
        
        if (!threatsByType.has(analysis.framework)) {
          threatsByType.set(analysis.framework, new Set());
        }
        threatsByType.get(analysis.framework)!.add(threatType);
        
        if (!frameworksByThreat.has(threatType)) {
          frameworksByThreat.set(threatType, new Set());
        }
        frameworksByThreat.get(threatType)!.add(analysis.framework);
      });
    });
    
    // Find threats identified by some frameworks but not others
    frameworksByThreat.forEach((frameworks, threatType) => {
      const identifyingFrameworks = Array.from(frameworks);
      const allFrameworks = analyses.map(a => a.framework);
      const missingFrameworks = allFrameworks.filter(f => !frameworks.has(f));
      
      // If a threat is identified by some but not all frameworks
      if (missingFrameworks.length > 0 && identifyingFrameworks.length > 0) {
        // Only flag as conflict if it's a significant threat
        const isSignificant = this.isSignificantThreat(threatType, analyses);
        
        if (isSignificant) {
          conflicts.push({
            type: 'threat_existence_conflict',
            entity: threatType,
            frameworks: allFrameworks,
            details: {
              identifiedBy: identifyingFrameworks,
              notIdentifiedBy: missingFrameworks,
              threatType
            },
            severity: 'medium'
          });
        }
      }
    });
    
    return conflicts;
  }
  
  // Detect entity classification conflicts
  private detectEntityClassificationConflicts(analyses: StandardizedAnalysis[]): Conflict[] {
    const conflicts: Conflict[] = [];
    const entitiesByName = new Map<string, Array<{framework: string, entity: any}>>();
    
    // Group entities by name
    analyses.forEach(analysis => {
      analysis.entities.forEach(entity => {
        const key = entity.name.toLowerCase();
        if (!entitiesByName.has(key)) {
          entitiesByName.set(key, []);
        }
        entitiesByName.get(key)!.push({
          framework: analysis.framework,
          entity
        });
      });
    });
    
    // Find classification conflicts
    entitiesByName.forEach((entities, name) => {
      if (entities.length > 1) {
        const types = entities.map(e => e.entity.type);
        const uniqueTypes = [...new Set(types)];
        
        if (uniqueTypes.length > 1) {
          conflicts.push({
            type: 'entity_classification_conflict',
            entity: name,
            frameworks: entities.map(e => e.framework),
            details: {
              classifications: entities.map(e => ({
                framework: e.framework,
                type: e.entity.type,
                confidence: e.entity.confidence
              }))
            },
            severity: 'low'
          });
        }
      }
    });
    
    return conflicts;
  }
  
  // Detect severity rating conflicts
  private detectSeverityRatingConflicts(analyses: StandardizedAnalysis[]): Conflict[] {
    const conflicts: Conflict[] = [];
    const threatsBySimilarity = new Map<string, Array<{framework: string, threat: any}>>();
    
    // Group similar threats
    analyses.forEach(analysis => {
      analysis.threats.forEach(threat => {
        const similarKey = this.getSimilarThreatKey(threat);
        if (!threatsBySimilarity.has(similarKey)) {
          threatsBySimilarity.set(similarKey, []);
        }
        threatsBySimilarity.get(similarKey)!.push({
          framework: analysis.framework,
          threat
        });
      });
    });
    
    // Find severity conflicts
    threatsBySimilarity.forEach((threats, key) => {
      if (threats.length > 1) {
        const severities = threats.map(t => t.threat.severity);
        const uniqueSeverities = [...new Set(severities)];
        
        if (uniqueSeverities.length > 1 && this.hasSeverityConflict(uniqueSeverities)) {
          conflicts.push({
            type: 'severity_rating_conflict',
            entity: key,
            frameworks: threats.map(t => t.framework),
            details: {
              severities: threats.map(t => ({
                framework: t.framework,
                severity: t.threat.severity,
                threatName: t.threat.name
              }))
            },
            severity: 'medium'
          });
        }
      }
    });
    
    return conflicts;
  }
  
  // Resolve a single conflict
  private async resolveConflict(conflict: Conflict, analyses: StandardizedAnalysis[]): Promise<ConflictResolution> {
    switch (conflict.type) {
      case 'risk_score_mismatch':
        return this.resolveRiskScoreConflict(conflict, analyses);
        
      case 'control_effectiveness_disagreement':
        return this.resolveControlEffectivenessConflict(conflict, analyses);
        
      case 'threat_existence_conflict':
        return this.resolveThreatExistenceConflict(conflict, analyses);
        
      case 'entity_classification_conflict':
        return this.resolveEntityClassificationConflict(conflict, analyses);
        
      case 'severity_rating_conflict':
        return this.resolveSeverityRatingConflict(conflict, analyses);
        
      default:
        return this.defaultResolution(conflict);
    }
  }
  
  // Resolve risk score conflicts
  private resolveRiskScoreConflict(conflict: Conflict, analyses: StandardizedAnalysis[]): ConflictResolution {
    const scores = conflict.details.scores.map((s: any) => s.score);
    
    // Use weighted average based on framework confidence
    const weightedScores = conflict.details.scores.map((s: any) => {
      const analysis = analyses.find(a => a.framework === s.framework);
      const confidence = analysis?.metadata.confidence || 0.5;
      return {
        score: s.score,
        weight: confidence,
        framework: s.framework
      };
    });
    
    const totalWeight = weightedScores.reduce((sum, ws) => sum + ws.weight, 0);
    const weightedAverage = weightedScores.reduce(
      (sum, ws) => sum + (ws.score * ws.weight), 
      0
    ) / totalWeight;
    
    // Consider the highest score if it comes from a specialized framework
    const specializedFrameworks = ['DREAD', 'FAIR', 'OCTAVE'];
    const specializedScores = weightedScores.filter(ws => 
      specializedFrameworks.includes(ws.framework)
    );
    
    let resolvedScore = weightedAverage;
    let rationale = `Weighted average of ${scores.length} risk assessments`;
    
    if (specializedScores.length > 0) {
      const maxSpecialized = Math.max(...specializedScores.map(s => s.score));
      if (maxSpecialized > weightedAverage * 1.2) {
        resolvedScore = maxSpecialized;
        rationale = `Using specialized risk framework assessment`;
      }
    }
    
    return {
      conflict,
      resolution: 'weighted_consensus',
      resolvedValue: Math.round(resolvedScore * 10) / 10,
      confidence: this.calculateResolutionConfidence(scores),
      rationale
    };
  }
  
  // Resolve control effectiveness conflicts
  private resolveControlEffectivenessConflict(conflict: Conflict, analyses: StandardizedAnalysis[]): ConflictResolution {
    const ratings = conflict.details.ratings;
    
    // Map effectiveness to numeric values
    const effectivenessMap: Record<string, number> = {
      'high': 3,
      'effective': 3,
      'implemented': 3,
      'medium': 2,
      'partial': 2,
      'proposed': 1,
      'low': 1,
      'ineffective': 0,
      'not_implemented': 0
    };
    
    // Calculate consensus
    const numericRatings = ratings.map((r: any) => 
      effectivenessMap[r.effectiveness?.toLowerCase()] || 1
    );
    
    const avgRating = numericRatings.reduce((sum, r) => sum + r, 0) / numericRatings.length;
    
    // Map back to effectiveness label
    let resolvedEffectiveness = 'medium';
    if (avgRating >= 2.5) resolvedEffectiveness = 'high';
    else if (avgRating <= 1) resolvedEffectiveness = 'low';
    
    // Check for recent assessments
    const recentAssessments = ratings.filter((r: any) => {
      const analysis = analyses.find(a => a.framework === r.framework);
      const daysSinceImport = analysis ? 
        (Date.now() - analysis.metadata.importDate.getTime()) / (1000 * 60 * 60 * 24) : 
        999;
      return daysSinceImport < 90;
    });
    
    if (recentAssessments.length > 0) {
      // Prefer recent assessments
      const recentAvg = recentAssessments
        .map((r: any) => effectivenessMap[r.effectiveness?.toLowerCase()] || 1)
        .reduce((sum, r) => sum + r, 0) / recentAssessments.length;
      
      if (recentAvg >= 2.5) resolvedEffectiveness = 'high';
      else if (recentAvg <= 1) resolvedEffectiveness = 'low';
      else resolvedEffectiveness = 'medium';
    }
    
    return {
      conflict,
      resolution: 'consensus',
      resolvedValue: resolvedEffectiveness,
      confidence: 0.7,
      rationale: `Consensus from ${ratings.length} assessments, prioritizing recent evaluations`
    };
  }
  
  // Resolve threat existence conflicts
  private resolveThreatExistenceConflict(conflict: Conflict, analyses: StandardizedAnalysis[]): ConflictResolution {
    const identifiedBy = conflict.details.identifiedBy.length;
    const notIdentifiedBy = conflict.details.notIdentifiedBy.length;
    const total = identifiedBy + notIdentifiedBy;
    
    // Threat exists if identified by majority or by specialized framework
    const specializedFrameworks = ['STRIDE', 'PASTA', 'OCTAVE'];
    const identifiedBySpecialized = conflict.details.identifiedBy.some((f: string) => 
      specializedFrameworks.includes(f)
    );
    
    let threatExists = identifiedBy > notIdentifiedBy;
    let confidence = identifiedBy / total;
    let rationale = `Identified by ${identifiedBy} of ${total} frameworks`;
    
    if (identifiedBySpecialized && identifiedBy >= 1) {
      threatExists = true;
      confidence = Math.max(confidence, 0.75);
      rationale = `Identified by specialized threat modeling framework`;
    }
    
    // Check framework suitability
    const threatType = conflict.details.threatType;
    const suitableFrameworks = this.getFrameworksSuitableForThreat(threatType);
    const identifiedBySuitable = conflict.details.identifiedBy.filter((f: string) => 
      suitableFrameworks.includes(f)
    ).length;
    
    if (identifiedBySuitable > 0) {
      threatExists = true;
      confidence = Math.max(confidence, 0.8);
      rationale = `Identified by framework specialized for this threat type`;
    }
    
    return {
      conflict,
      resolution: threatExists ? 'threat_confirmed' : 'threat_rejected',
      resolvedValue: threatExists,
      confidence,
      rationale
    };
  }
  
  // Resolve entity classification conflicts
  private resolveEntityClassificationConflict(conflict: Conflict, analyses: StandardizedAnalysis[]): ConflictResolution {
    const classifications = conflict.details.classifications;
    
    // Prefer classification with highest confidence
    const highestConfidence = classifications.reduce((max: any, c: any) => 
      c.confidence > (max?.confidence || 0) ? c : max
    , null);
    
    // Check for consensus
    const typeCounts = new Map<string, number>();
    classifications.forEach((c: any) => {
      typeCounts.set(c.type, (typeCounts.get(c.type) || 0) + 1);
    });
    
    const mostCommon = Array.from(typeCounts.entries())
      .reduce((max, [type, count]) => count > max[1] ? [type, count] : max, ['', 0]);
    
    let resolvedType = highestConfidence.type;
    let confidence = highestConfidence.confidence;
    let rationale = `Highest confidence classification`;
    
    // If there's a clear majority, use that
    if (mostCommon[1] > classifications.length / 2) {
      resolvedType = mostCommon[0];
      confidence = 0.8;
      rationale = `Majority consensus (${mostCommon[1]} of ${classifications.length})`;
    }
    
    return {
      conflict,
      resolution: 'classification_resolved',
      resolvedValue: resolvedType,
      confidence,
      rationale
    };
  }
  
  // Resolve severity rating conflicts
  private resolveSeverityRatingConflict(conflict: Conflict, analyses: StandardizedAnalysis[]): ConflictResolution {
    const severities = conflict.details.severities;
    
    // Map severities to numeric values
    const severityMap: Record<string, number> = {
      'critical': 4,
      'high': 3,
      'medium': 2,
      'low': 1,
      'info': 0
    };
    
    // Calculate weighted average based on framework expertise
    const weightedSeverities = severities.map((s: any) => {
      const analysis = analyses.find(a => a.framework === s.framework);
      const weight = this.getFrameworkWeight(s.framework, 'severity');
      
      return {
        severity: severityMap[s.severity] || 2,
        weight,
        framework: s.framework
      };
    });
    
    const totalWeight = weightedSeverities.reduce((sum, ws) => sum + ws.weight, 0);
    const weightedAverage = weightedSeverities.reduce(
      (sum, ws) => sum + (ws.severity * ws.weight), 
      0
    ) / totalWeight;
    
    // Map back to severity label
    let resolvedSeverity = 'medium';
    if (weightedAverage >= 3.5) resolvedSeverity = 'critical';
    else if (weightedAverage >= 2.5) resolvedSeverity = 'high';
    else if (weightedAverage >= 1.5) resolvedSeverity = 'medium';
    else resolvedSeverity = 'low';
    
    // Conservative approach: if any framework rates as critical, consider it high at minimum
    const hasCritical = severities.some((s: any) => s.severity === 'critical');
    if (hasCritical && resolvedSeverity === 'medium') {
      resolvedSeverity = 'high';
    }
    
    return {
      conflict,
      resolution: 'weighted_severity',
      resolvedValue: resolvedSeverity,
      confidence: this.calculateSeverityConfidence(severities),
      rationale: `Weighted consensus from ${severities.length} assessments`
    };
  }
  
  // Default resolution for unknown conflict types
  private defaultResolution(conflict: Conflict): ConflictResolution {
    return {
      conflict,
      resolution: 'unresolved',
      resolvedValue: null,
      confidence: 0,
      rationale: 'No resolution strategy available for this conflict type'
    };
  }
  
  // Helper methods
  private calculateVariance(values: number[]): number {
    const mean = values.reduce((sum, v) => sum + v, 0) / values.length;
    const squaredDiffs = values.map(v => Math.pow(v - mean, 2));
    return Math.sqrt(squaredDiffs.reduce((sum, v) => sum + v, 0) / values.length);
  }
  
  private calculateConflictSeverity(difference: number): 'low' | 'medium' | 'high' {
    if (difference > 5) return 'high';
    if (difference > 3) return 'medium';
    return 'low';
  }
  
  private normalizeControlName(name: string): string {
    return name.toLowerCase()
      .replace(/[^a-z0-9]/g, '')
      .replace(/control|mitigation|safeguard/g, '');
  }
  
  private areEffectivenessRatingsConsistent(ratings: string[]): boolean {
    const normalized = ratings.map(r => {
      const lower = r.toLowerCase();
      if (['high', 'effective', 'implemented'].includes(lower)) return 'high';
      if (['medium', 'partial', 'proposed'].includes(lower)) return 'medium';
      if (['low', 'ineffective', 'not_implemented'].includes(lower)) return 'low';
      return 'unknown';
    });
    
    const unique = [...new Set(normalized)];
    return unique.length === 1;
  }
  
  private normalizeThreatType(threat: any): string {
    // Create a normalized threat identifier
    const category = threat.category || 'unknown';
    const target = threat.affectedEntity || threat.affectedFlow || 'system';
    return `${category}-${target}`.toLowerCase();
  }
  
  private isSignificantThreat(threatType: string, analyses: StandardizedAnalysis[]): boolean {
    // Check if threat appears as high/critical in any analysis
    return analyses.some(a => 
      a.threats.some(t => {
        const normalized = this.normalizeThreatType(t);
        return normalized === threatType && 
               ['high', 'critical'].includes(t.severity);
      })
    );
  }
  
  private getSimilarThreatKey(threat: any): string {
    // Create key for grouping similar threats
    const category = threat.category || 'unknown';
    const target = threat.affectedEntity || 'unknown';
    const keywords = this.extractKeywords(threat.name + ' ' + threat.description);
    return `${category}-${target}-${keywords.join('-')}`.toLowerCase();
  }
  
  private extractKeywords(text: string): string[] {
    const stopWords = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'];
    const words = text.toLowerCase()
      .replace(/[^a-z0-9\s]/g, '')
      .split(/\s+/)
      .filter(w => w.length > 3 && !stopWords.includes(w));
    
    // Return top 3 most relevant words
    return words.slice(0, 3).sort();
  }
  
  private hasSeverityConflict(severities: string[]): boolean {
    const hasLowOrMedium = severities.some(s => ['low', 'medium'].includes(s));
    const hasHighOrCritical = severities.some(s => ['high', 'critical'].includes(s));
    return hasLowOrMedium && hasHighOrCritical;
  }
  
  private calculateResolutionConfidence(scores: number[]): number {
    // Higher variance means lower confidence
    const variance = this.calculateVariance(scores);
    const normalizedVariance = Math.min(variance / 5, 1); // Normalize to 0-1
    return 1 - (normalizedVariance * 0.5); // Max 50% confidence reduction
  }
  
  private getFrameworksSuitableForThreat(threatType: string): string[] {
    const suitabilityMap: Record<string, string[]> = {
      'spoofing': ['STRIDE', 'PASTA'],
      'tampering': ['STRIDE', 'PASTA'],
      'repudiation': ['STRIDE'],
      'information_disclosure': ['STRIDE', 'LINDDUN'],
      'denial_of_service': ['STRIDE', 'HAZOP'],
      'elevation_of_privilege': ['STRIDE'],
      'privacy': ['LINDDUN'],
      'ai_ml': ['MAESTRO'],
      'supply_chain': ['OCTAVE', 'PASTA']
    };
    
    for (const [key, frameworks] of Object.entries(suitabilityMap)) {
      if (threatType.includes(key)) {
        return frameworks;
      }
    }
    
    return ['STRIDE', 'PASTA']; // Default suitable frameworks
  }
  
  private getFrameworkWeight(framework: string, aspect: string): number {
    const weights: Record<string, Record<string, number>> = {
      'STRIDE': { severity: 0.8, risk: 0.7, control: 0.7 },
      'PASTA': { severity: 0.9, risk: 0.9, control: 0.6 },
      'DREAD': { severity: 1.0, risk: 1.0, control: 0.5 },
      'OCTAVE': { severity: 0.7, risk: 0.9, control: 0.8 },
      'LINDDUN': { severity: 0.8, risk: 0.7, control: 0.7 },
      'MAESTRO': { severity: 0.8, risk: 0.8, control: 0.8 },
      'HAZOP': { severity: 0.9, risk: 0.8, control: 0.9 }
    };
    
    return weights[framework]?.[aspect] || 0.5;
  }
  
  private calculateSeverityConfidence(severities: any[]): number {
    const unique = [...new Set(severities.map((s: any) => s.severity))];
    
    // High agreement means high confidence
    if (unique.length === 1) return 0.95;
    if (unique.length === 2) {
      // Check if they're adjacent (e.g., medium and high)
      const severityOrder = ['info', 'low', 'medium', 'high', 'critical'];
      const indices = unique.map(s => severityOrder.indexOf(s));
      const distance = Math.abs(indices[0] - indices[1]);
      if (distance === 1) return 0.8; // Adjacent severities
    }
    
    // Low confidence for highly divergent ratings
    return 0.6;
  }
}