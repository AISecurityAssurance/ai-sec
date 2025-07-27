/**
 * PASTA JSON Import Adapter
 * 
 * Process for Attack Simulation and Threat Analysis (PASTA) import adapter
 * Handles the 7-stage PASTA methodology output
 */

import type { 
  AnalysisImportAdapter, 
  StandardizedAnalysis, 
  ValidationResult,
  EntityMapping,
  ThreatMapping,
  ControlMapping,
  RiskMapping
} from '../types';

interface PASTAData {
  metadata: {
    version: string;
    created: string;
    author?: string;
    organization?: string;
  };
  
  // Stage 1: Define Business Objectives
  businessObjectives: {
    objectives: Array<{
      id: string;
      name: string;
      description: string;
      priority: string;
      businessValue: number;
    }>;
    complianceRequirements: string[];
  };
  
  // Stage 2: Define Technical Scope
  technicalScope: {
    applications: Array<{
      id: string;
      name: string;
      type: string;
      criticality: string;
      technologies: string[];
    }>;
    infrastructure: Array<{
      id: string;
      name: string;
      type: string;
      location: string;
    }>;
    dataAssets: Array<{
      id: string;
      name: string;
      classification: string;
      owner: string;
    }>;
  };
  
  // Stage 3: Application Decomposition
  decomposition: {
    components: Array<{
      id: string;
      applicationId: string;
      name: string;
      type: string;
      trustLevel: string;
    }>;
    dataFlows: Array<{
      id: string;
      source: string;
      target: string;
      protocol: string;
      dataTypes: string[];
    }>;
  };
  
  // Stage 4: Threat Analysis
  threatAnalysis: {
    threatAgents: Array<{
      id: string;
      name: string;
      type: string;
      motivation: string;
      capability: string;
    }>;
    threats: Array<{
      id: string;
      name: string;
      description: string;
      agentId: string;
      targetId: string;
      likelihood: string;
      ttp?: string; // Tactics, Techniques, Procedures
    }>;
  };
  
  // Stage 5: Vulnerability & Weakness Analysis
  vulnerabilities: Array<{
    id: string;
    name: string;
    description: string;
    componentId: string;
    cve?: string;
    cvss?: number;
    exploitability: string;
  }>;
  
  // Stage 6: Attack Modeling
  attackScenarios: Array<{
    id: string;
    name: string;
    description: string;
    threatId: string;
    vulnerabilityIds: string[];
    impact: string;
    likelihood: string;
    attackVector: string;
  }>;
  
  // Stage 7: Risk & Impact Analysis
  riskAnalysis: {
    risks: Array<{
      id: string;
      scenarioId: string;
      businessImpact: string;
      technicalImpact: string;
      riskScore: number;
      residualRisk?: number;
    }>;
    controls: Array<{
      id: string;
      name: string;
      type: string;
      riskIds: string[];
      effectiveness: string;
      implementationCost: string;
    }>;
  };
}

export class PASTAJSONAdapter implements AnalysisImportAdapter {
  format = 'pasta-json';
  version = '1.0';
  
  async validate(data: any): Promise<ValidationResult> {
    const errors: string[] = [];
    const warnings: string[] = [];
    
    // Check basic structure
    if (!data || typeof data !== 'object') {
      errors.push('Invalid PASTA JSON format');
      return { isValid: false, errors, warnings };
    }
    
    // Check required sections
    const requiredSections = [
      'businessObjectives',
      'technicalScope',
      'decomposition',
      'threatAnalysis',
      'vulnerabilities',
      'attackScenarios',
      'riskAnalysis'
    ];
    
    requiredSections.forEach(section => {
      if (!data[section]) {
        errors.push(`Missing required section: ${section}`);
      }
    });
    
    // Validate business objectives
    if (data.businessObjectives) {
      if (!data.businessObjectives.objectives || !Array.isArray(data.businessObjectives.objectives)) {
        errors.push('Invalid business objectives format');
      } else if (data.businessObjectives.objectives.length === 0) {
        warnings.push('No business objectives defined');
      }
    }
    
    // Validate technical scope
    if (data.technicalScope) {
      if (!data.technicalScope.applications || !Array.isArray(data.technicalScope.applications)) {
        errors.push('Invalid applications format in technical scope');
      }
    }
    
    // Validate threat analysis
    if (data.threatAnalysis) {
      if (!data.threatAnalysis.threats || !Array.isArray(data.threatAnalysis.threats)) {
        errors.push('Invalid threats format');
      } else if (data.threatAnalysis.threats.length === 0) {
        warnings.push('No threats identified');
      }
    }
    
    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }
  
  async transform(data: PASTAData): Promise<StandardizedAnalysis> {
    const entities = this.extractEntities(data);
    const relationships = this.extractRelationships(data);
    const threats = this.extractThreats(data);
    const controls = this.extractControls(data);
    const risks = this.extractRisks(data);
    
    return {
      framework: 'PASTA',
      metadata: {
        source: 'PASTA JSON Import',
        importDate: new Date(),
        version: data.metadata?.version || '1.0',
        confidence: 0.9, // High confidence for comprehensive PASTA data
        author: data.metadata?.author,
        originalFile: 'pasta-analysis.json'
      },
      entities,
      relationships,
      threats,
      controls,
      risks,
      originalData: data
    };
  }
  
  async mapToEntities(analysis: StandardizedAnalysis, systemEntities: any[]): Promise<any> {
    // Similar mapping logic as other adapters
    const mappingResults = {
      mappings: [] as any[],
      unmapped: [] as any[],
      suggestions: [] as any[]
    };
    
    analysis.entities.forEach(importedEntity => {
      const bestMatch = this.findBestEntityMatch(importedEntity, systemEntities);
      
      if (bestMatch.confidence > 0.75) {
        mappingResults.mappings.push({
          imported: importedEntity,
          system: bestMatch.entity,
          confidence: bestMatch.confidence
        });
      } else if (bestMatch.confidence > 0.5) {
        mappingResults.suggestions.push({
          imported: importedEntity,
          suggested: bestMatch.entity,
          confidence: bestMatch.confidence,
          reason: bestMatch.reason
        });
      } else {
        mappingResults.unmapped.push(importedEntity);
      }
    });
    
    return mappingResults;
  }
  
  async extractRisks(analysis: StandardizedAnalysis): Promise<any[]> {
    return analysis.risks;
  }
  
  // Extract entities from PASTA data
  private extractEntities(data: PASTAData): EntityMapping[] {
    const entities: EntityMapping[] = [];
    
    // Extract applications as entities
    data.technicalScope.applications.forEach(app => {
      entities.push({
        originalId: app.id,
        name: app.name,
        type: 'software',
        originalType: app.type,
        properties: {
          criticality: app.criticality,
          technologies: app.technologies,
          pastaType: 'application'
        },
        confidence: 0.95
      });
    });
    
    // Extract infrastructure as entities
    data.technicalScope.infrastructure.forEach(infra => {
      entities.push({
        originalId: infra.id,
        name: infra.name,
        type: this.mapInfrastructureType(infra.type),
        originalType: infra.type,
        properties: {
          location: infra.location,
          pastaType: 'infrastructure'
        },
        confidence: 0.9
      });
    });
    
    // Extract data assets as entities
    data.technicalScope.dataAssets.forEach(asset => {
      entities.push({
        originalId: asset.id,
        name: asset.name,
        type: 'datastore',
        properties: {
          classification: asset.classification,
          owner: asset.owner,
          pastaType: 'data_asset'
        },
        confidence: 0.9
      });
    });
    
    // Extract components from decomposition
    data.decomposition.components.forEach(component => {
      entities.push({
        originalId: component.id,
        name: component.name,
        type: this.mapComponentType(component.type),
        originalType: component.type,
        properties: {
          applicationId: component.applicationId,
          trustLevel: component.trustLevel,
          pastaType: 'component'
        },
        confidence: 0.85
      });
    });
    
    // Extract threat agents as adversaries
    data.threatAnalysis.threatAgents.forEach(agent => {
      entities.push({
        originalId: agent.id,
        name: agent.name,
        type: 'adversary',
        properties: {
          agentType: agent.type,
          motivation: agent.motivation,
          capability: agent.capability,
          pastaType: 'threat_agent'
        },
        confidence: 0.85
      });
    });
    
    return entities;
  }
  
  // Extract relationships from PASTA data
  private extractRelationships(data: PASTAData): any[] {
    const relationships: any[] = [];
    
    // Data flows as relationships
    data.decomposition.dataFlows.forEach(flow => {
      relationships.push({
        originalId: flow.id,
        source: flow.source,
        target: flow.target,
        type: 'dataflow',
        action: 'transfers data',
        properties: {
          protocol: flow.protocol,
          dataTypes: flow.dataTypes
        },
        confidence: 0.9
      });
    });
    
    // Component to application relationships
    data.decomposition.components.forEach(component => {
      relationships.push({
        originalId: `rel-${component.id}-${component.applicationId}`,
        source: component.id,
        target: component.applicationId,
        type: 'composition',
        action: 'is part of',
        properties: {},
        confidence: 0.95
      });
    });
    
    return relationships;
  }
  
  // Extract threats from PASTA data
  private extractThreats(data: PASTAData): ThreatMapping[] {
    const threats: ThreatMapping[] = [];
    
    // Threats from threat analysis
    data.threatAnalysis.threats.forEach(threat => {
      threats.push({
        originalId: threat.id,
        name: threat.name,
        description: threat.description,
        category: 'targeted_threat', // PASTA focuses on targeted threats
        severity: this.calculateThreatSeverity(threat.likelihood, data),
        affectedEntity: threat.targetId,
        properties: {
          agentId: threat.agentId,
          likelihood: threat.likelihood,
          ttp: threat.ttp
        },
        confidence: 0.85
      });
    });
    
    // Attack scenarios as composite threats
    data.attackScenarios.forEach(scenario => {
      threats.push({
        originalId: scenario.id,
        name: scenario.name,
        description: scenario.description,
        category: 'attack_scenario',
        severity: this.calculateScenarioSeverity(scenario.impact, scenario.likelihood),
        properties: {
          threatId: scenario.threatId,
          vulnerabilityIds: scenario.vulnerabilityIds,
          attackVector: scenario.attackVector,
          impact: scenario.impact,
          likelihood: scenario.likelihood
        },
        confidence: 0.9
      });
    });
    
    return threats;
  }
  
  // Extract controls from PASTA data
  private extractControls(data: PASTAData): ControlMapping[] {
    const controls: ControlMapping[] = [];
    
    data.riskAnalysis.controls.forEach(control => {
      controls.push({
        originalId: control.id,
        name: control.name,
        description: `${control.type} control for risks: ${control.riskIds.join(', ')}`,
        type: this.mapControlType(control.type),
        properties: {
          riskIds: control.riskIds,
          effectiveness: control.effectiveness,
          implementationCost: control.implementationCost
        },
        confidence: 0.85
      });
    });
    
    return controls;
  }
  
  // Extract risks from PASTA data
  private extractRisks(data: PASTAData): RiskMapping[] {
    const risks: RiskMapping[] = [];
    
    data.riskAnalysis.risks.forEach(risk => {
      const scenario = data.attackScenarios.find(s => s.id === risk.scenarioId);
      
      risks.push({
        id: risk.id,
        name: scenario?.name || `Risk ${risk.id}`,
        description: `Business Impact: ${risk.businessImpact}, Technical Impact: ${risk.technicalImpact}`,
        score: risk.riskScore,
        category: 'business_risk',
        properties: {
          scenarioId: risk.scenarioId,
          businessImpact: risk.businessImpact,
          technicalImpact: risk.technicalImpact,
          residualRisk: risk.residualRisk
        }
      });
    });
    
    return risks;
  }
  
  // Type mapping helpers
  private mapInfrastructureType(type: string): string {
    const mapping: Record<string, string> = {
      'server': 'physical_asset',
      'network': 'network',
      'cloud': 'cloud_service',
      'database': 'datastore',
      'firewall': 'network',
      'load_balancer': 'network'
    };
    
    return mapping[type.toLowerCase()] || 'infrastructure';
  }
  
  private mapComponentType(type: string): string {
    const mapping: Record<string, string> = {
      'web_app': 'software',
      'api': 'software',
      'service': 'software',
      'database': 'datastore',
      'cache': 'datastore',
      'queue': 'software'
    };
    
    return mapping[type.toLowerCase()] || 'component';
  }
  
  private mapControlType(type: string): string {
    const mapping: Record<string, string> = {
      'preventive': 'preventive',
      'detective': 'detective',
      'corrective': 'corrective',
      'compensating': 'compensating'
    };
    
    return mapping[type.toLowerCase()] || 'control';
  }
  
  // Severity calculation helpers
  private calculateThreatSeverity(likelihood: string, data: PASTAData): string {
    const likelihoodScore = this.likelihoodToScore(likelihood);
    
    // In PASTA, severity also considers threat agent capability
    if (likelihoodScore >= 4) return 'critical';
    if (likelihoodScore >= 3) return 'high';
    if (likelihoodScore >= 2) return 'medium';
    return 'low';
  }
  
  private calculateScenarioSeverity(impact: string, likelihood: string): string {
    const impactScore = this.impactToScore(impact);
    const likelihoodScore = this.likelihoodToScore(likelihood);
    const combined = (impactScore + likelihoodScore) / 2;
    
    if (combined >= 4) return 'critical';
    if (combined >= 3) return 'high';
    if (combined >= 2) return 'medium';
    return 'low';
  }
  
  private likelihoodToScore(likelihood: string): number {
    const scores: Record<string, number> = {
      'very_high': 5,
      'high': 4,
      'medium': 3,
      'low': 2,
      'very_low': 1
    };
    
    return scores[likelihood.toLowerCase()] || 3;
  }
  
  private impactToScore(impact: string): number {
    const scores: Record<string, number> = {
      'catastrophic': 5,
      'severe': 4,
      'moderate': 3,
      'minor': 2,
      'negligible': 1
    };
    
    return scores[impact.toLowerCase()] || 3;
  }
  
  // Entity matching helper
  private findBestEntityMatch(importedEntity: EntityMapping, systemEntities: any[]): any {
    let bestMatch = {
      entity: null,
      confidence: 0,
      reason: ''
    };
    
    systemEntities.forEach(systemEntity => {
      let confidence = 0;
      const reasons = [];
      
      // Name similarity
      const nameSimilarity = this.calculateStringSimilarity(
        importedEntity.name.toLowerCase(),
        systemEntity.name.toLowerCase()
      );
      confidence += nameSimilarity * 0.4;
      if (nameSimilarity > 0.8) reasons.push('name match');
      
      // Type compatibility
      if (this.areTypesCompatible(importedEntity.type, systemEntity.type)) {
        confidence += 0.3;
        reasons.push('type compatible');
      }
      
      // Property matching for PASTA-specific properties
      if (importedEntity.properties.criticality && systemEntity.properties?.criticality) {
        if (importedEntity.properties.criticality === systemEntity.properties.criticality) {
          confidence += 0.2;
          reasons.push('criticality match');
        }
      }
      
      if (confidence > bestMatch.confidence) {
        bestMatch = {
          entity: systemEntity,
          confidence,
          reason: reasons.join(', ')
        };
      }
    });
    
    return bestMatch;
  }
  
  private calculateStringSimilarity(str1: string, str2: string): number {
    if (str1 === str2) return 1;
    
    const longer = str1.length > str2.length ? str1 : str2;
    const shorter = str1.length > str2.length ? str2 : str1;
    
    if (longer.length === 0) return 1;
    
    const editDistance = this.levenshteinDistance(longer, shorter);
    return (longer.length - editDistance) / longer.length;
  }
  
  private levenshteinDistance(str1: string, str2: string): number {
    const matrix: number[][] = [];
    
    for (let i = 0; i <= str2.length; i++) {
      matrix[i] = [i];
    }
    
    for (let j = 0; j <= str1.length; j++) {
      matrix[0][j] = j;
    }
    
    for (let i = 1; i <= str2.length; i++) {
      for (let j = 1; j <= str1.length; j++) {
        if (str2.charAt(i - 1) === str1.charAt(j - 1)) {
          matrix[i][j] = matrix[i - 1][j - 1];
        } else {
          matrix[i][j] = Math.min(
            matrix[i - 1][j - 1] + 1,
            matrix[i][j - 1] + 1,
            matrix[i - 1][j] + 1
          );
        }
      }
    }
    
    return matrix[str2.length][str1.length];
  }
  
  private areTypesCompatible(importedType: string, systemType: string): boolean {
    const compatibilityMap: Record<string, string[]> = {
      'software': ['software', 'application', 'service', 'component'],
      'adversary': ['adversary', 'threat_actor', 'attacker'],
      'datastore': ['database', 'storage', 'data_asset', 'repository'],
      'network': ['network', 'infrastructure', 'firewall', 'router'],
      'cloud_service': ['cloud', 'iaas', 'paas', 'saas']
    };
    
    const importedCompatible = compatibilityMap[importedType] || [importedType];
    const systemCompatible = compatibilityMap[systemType] || [systemType];
    
    return importedCompatible.some(t1 => 
      systemCompatible.some(t2 => t1 === t2)
    );
  }
}