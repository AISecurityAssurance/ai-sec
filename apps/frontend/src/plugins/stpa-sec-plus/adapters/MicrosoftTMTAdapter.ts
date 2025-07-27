/**
 * Microsoft Threat Modeling Tool Import Adapter
 * 
 * Transforms Microsoft TMT (.tm7) files into standardized STPA-Sec+ format
 */

import type { 
  AnalysisImportAdapter, 
  StandardizedAnalysis, 
  ValidationResult,
  EntityMapping,
  RelationshipMapping,
  ThreatMapping,
  ControlMapping 
} from '../types';

interface TMTElement {
  id: string;
  name: string;
  type: string;
  properties: {
    trustLevel?: string;
    dataClassification?: string;
    isEncrypted?: boolean;
    authenticatesSource?: boolean;
    authenticatesDestination?: boolean;
    [key: string]: any;
  };
}

interface TMTFlow {
  id: string;
  name: string;
  sourceId: string;
  targetId: string;
  properties: {
    protocol?: string;
    isEncrypted?: boolean;
    dataClassification?: string;
    [key: string]: any;
  };
}

interface TMTThreat {
  id: string;
  title: string;
  category: string; // STRIDE category
  description: string;
  state: string;
  priority: string;
  elementId: string;
  flowId?: string;
  mitigations?: TMTMitigation[];
}

interface TMTMitigation {
  id: string;
  title: string;
  description: string;
  state: string;
}

interface TMTData {
  metadata: {
    tool: string;
    version: string;
    author?: string;
    created?: string;
    modified?: string;
  };
  elements: TMTElement[];
  flows: TMTFlow[];
  threats: TMTThreat[];
}

export class MicrosoftTMTAdapter implements AnalysisImportAdapter {
  format = 'microsoft-tmt';
  version = '7.x';
  
  async validate(data: any): Promise<ValidationResult> {
    const errors: string[] = [];
    const warnings: string[] = [];
    
    // Check required structure
    if (!data || typeof data !== 'object') {
      errors.push('Invalid data format');
      return { isValid: false, errors, warnings };
    }
    
    // Check for required fields
    if (!data.elements || !Array.isArray(data.elements)) {
      errors.push('Missing or invalid elements array');
    }
    
    if (!data.flows || !Array.isArray(data.flows)) {
      errors.push('Missing or invalid flows array');
    }
    
    if (!data.threats || !Array.isArray(data.threats)) {
      warnings.push('No threats found in model');
    }
    
    // Validate elements
    if (data.elements) {
      data.elements.forEach((element: any, index: number) => {
        if (!element.id) {
          errors.push(`Element at index ${index} missing id`);
        }
        if (!element.name) {
          warnings.push(`Element ${element.id} missing name`);
        }
        if (!element.type) {
          errors.push(`Element ${element.id} missing type`);
        }
      });
    }
    
    // Validate flows
    if (data.flows) {
      data.flows.forEach((flow: any, index: number) => {
        if (!flow.sourceId || !flow.targetId) {
          errors.push(`Flow at index ${index} missing source or target`);
        }
      });
    }
    
    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }
  
  async transform(data: TMTData): Promise<StandardizedAnalysis> {
    return {
      framework: 'STRIDE',
      metadata: {
        source: data.metadata.tool || 'Microsoft Threat Modeling Tool',
        importDate: new Date(),
        version: data.metadata.version || 'unknown',
        confidence: 0.85, // High confidence for structured TMT data
        author: data.metadata.author,
        originalFile: 'imported.tm7'
      },
      
      entities: this.transformEntities(data.elements),
      relationships: this.transformFlows(data.flows, data.elements),
      threats: this.transformThreats(data.threats),
      controls: this.extractMitigations(data.threats),
      risks: this.calculateRisks(data),
      
      originalData: data
    };
  }
  
  async mapToEntities(analysis: StandardizedAnalysis, systemEntities: any[]): Promise<any> {
    const mappingResults = {
      mappings: [] as any[],
      unmapped: [] as any[],
      suggestions: [] as any[]
    };
    
    analysis.entities.forEach(importedEntity => {
      const bestMatch = this.findBestEntityMatch(importedEntity, systemEntities);
      
      if (bestMatch.confidence > 0.7) {
        mappingResults.mappings.push({
          imported: importedEntity,
          system: bestMatch.entity,
          confidence: bestMatch.confidence
        });
      } else if (bestMatch.confidence > 0.4) {
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
  
  private transformEntities(elements: TMTElement[]): EntityMapping[] {
    return elements.map(element => ({
      originalId: element.id,
      name: element.name,
      type: this.mapElementType(element.type),
      originalType: element.type,
      properties: {
        trustLevel: element.properties.trustLevel,
        dataClassification: element.properties.dataClassification,
        isEncrypted: element.properties.isEncrypted,
        authenticatesSource: element.properties.authenticatesSource,
        authenticatesDestination: element.properties.authenticatesDestination,
        tmtProperties: element.properties
      },
      confidence: this.calculateEntityConfidence(element)
    }));
  }
  
  private transformFlows(flows: TMTFlow[], elements: TMTElement[]): RelationshipMapping[] {
    return flows.map(flow => {
      const source = elements.find(e => e.id === flow.sourceId);
      const target = elements.find(e => e.id === flow.targetId);
      
      return {
        originalId: flow.id,
        source: flow.sourceId,
        sourceName: source?.name || 'Unknown',
        target: flow.targetId,
        targetName: target?.name || 'Unknown',
        type: 'dataflow', // TMT primarily models data flows
        action: flow.name || 'Data Flow',
        properties: {
          protocol: flow.properties.protocol,
          isEncrypted: flow.properties.isEncrypted,
          dataClassification: flow.properties.dataClassification,
          tmtProperties: flow.properties
        },
        confidence: this.calculateFlowConfidence(flow)
      };
    });
  }
  
  private transformThreats(threats: TMTThreat[]): ThreatMapping[] {
    return threats.map(threat => ({
      originalId: threat.id,
      name: threat.title,
      description: threat.description,
      category: this.mapSTRIDECategory(threat.category),
      originalCategory: threat.category,
      severity: this.mapPriority(threat.priority),
      state: threat.state,
      affectedEntity: threat.elementId,
      affectedFlow: threat.flowId,
      properties: {
        tmtThreat: threat
      },
      confidence: 0.9 // High confidence for TMT threats
    }));
  }
  
  private extractMitigations(threats: TMTThreat[]): ControlMapping[] {
    const mitigations: ControlMapping[] = [];
    
    threats.forEach(threat => {
      if (threat.mitigations) {
        threat.mitigations.forEach(mitigation => {
          mitigations.push({
            originalId: mitigation.id,
            name: mitigation.title,
            description: mitigation.description,
            type: 'mitigation',
            state: mitigation.state,
            threatId: threat.id,
            properties: {
              tmtMitigation: mitigation
            },
            confidence: 0.85
          });
        });
      }
    });
    
    return mitigations;
  }
  
  private calculateRisks(data: TMTData): any[] {
    const risks: any[] = [];
    
    // Calculate risks based on threats and their priorities
    data.threats.forEach(threat => {
      const element = data.elements.find(e => e.id === threat.elementId);
      const flow = data.flows.find(f => f.id === threat.flowId);
      
      risks.push({
        id: `risk-${threat.id}`,
        name: threat.title,
        description: threat.description,
        entityId: threat.elementId,
        entityName: element?.name,
        flowId: threat.flowId,
        flowName: flow?.name,
        score: this.calculateRiskScore(threat),
        category: threat.category,
        mitigated: threat.state === 'Mitigated',
        properties: {
          priority: threat.priority,
          state: threat.state
        }
      });
    });
    
    return risks;
  }
  
  private mapElementType(tmtType: string): string {
    const typeMapping: Record<string, string> = {
      'Process': 'software',
      'External Interactor': 'external_entity',
      'Data Store': 'datastore',
      'Data Flow': 'dataflow',
      'Trust Boundary': 'trust_boundary',
      'Web Application': 'software',
      'Database': 'datastore',
      'Human User': 'human',
      'External Service': 'external_service'
    };
    
    return typeMapping[tmtType] || 'unknown';
  }
  
  private mapSTRIDECategory(category: string): string {
    // TMT uses full STRIDE names
    const categoryMapping: Record<string, string> = {
      'Spoofing': 'spoofing',
      'Tampering': 'tampering',
      'Repudiation': 'repudiation',
      'Information Disclosure': 'information_disclosure',
      'Denial of Service': 'denial_of_service',
      'Elevation of Privilege': 'elevation_of_privilege'
    };
    
    return categoryMapping[category] || category.toLowerCase();
  }
  
  private mapPriority(priority: string): string {
    const priorityMapping: Record<string, string> = {
      'Critical': 'critical',
      'High': 'high',
      'Medium': 'medium',
      'Low': 'low',
      'Info': 'info'
    };
    
    return priorityMapping[priority] || 'medium';
  }
  
  private calculateRiskScore(threat: TMTThreat): number {
    const priorityScores: Record<string, number> = {
      'Critical': 10,
      'High': 8,
      'Medium': 5,
      'Low': 2,
      'Info': 1
    };
    
    const baseScore = priorityScores[threat.priority] || 5;
    
    // Adjust based on state
    if (threat.state === 'Mitigated') {
      return baseScore * 0.2; // 80% reduction for mitigated threats
    } else if (threat.state === 'Not Started') {
      return baseScore * 1.2; // 20% increase for unaddressed threats
    }
    
    return baseScore;
  }
  
  private calculateEntityConfidence(element: TMTElement): number {
    let confidence = 0.5; // Base confidence
    
    // Increase confidence based on data completeness
    if (element.name) confidence += 0.1;
    if (element.properties.trustLevel) confidence += 0.1;
    if (element.properties.dataClassification) confidence += 0.1;
    if (element.properties.isEncrypted !== undefined) confidence += 0.1;
    if (element.properties.authenticatesSource !== undefined) confidence += 0.1;
    
    return Math.min(confidence, 1.0);
  }
  
  private calculateFlowConfidence(flow: TMTFlow): number {
    let confidence = 0.5; // Base confidence
    
    // Increase confidence based on data completeness
    if (flow.name) confidence += 0.1;
    if (flow.properties.protocol) confidence += 0.15;
    if (flow.properties.isEncrypted !== undefined) confidence += 0.15;
    if (flow.properties.dataClassification) confidence += 0.1;
    
    return Math.min(confidence, 1.0);
  }
  
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
      
      // Property matching
      const propMatch = this.calculatePropertyMatch(
        importedEntity.properties,
        systemEntity.properties || {}
      );
      confidence += propMatch * 0.3;
      if (propMatch > 0.5) reasons.push('properties align');
      
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
    // Simple Levenshtein distance-based similarity
    const maxLen = Math.max(str1.length, str2.length);
    if (maxLen === 0) return 1;
    
    const distance = this.levenshteinDistance(str1, str2);
    return 1 - (distance / maxLen);
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
      'external_entity': ['external', 'third_party', 'external_service'],
      'datastore': ['database', 'storage', 'cache', 'repository'],
      'human': ['user', 'person', 'actor', 'human']
    };
    
    const importedCompatible = compatibilityMap[importedType] || [importedType];
    const systemCompatible = compatibilityMap[systemType] || [systemType];
    
    return importedCompatible.some(t1 => 
      systemCompatible.some(t2 => t1 === t2)
    );
  }
  
  private calculatePropertyMatch(imported: any, system: any): number {
    const importedKeys = Object.keys(imported || {});
    const systemKeys = Object.keys(system || {});
    
    if (importedKeys.length === 0 && systemKeys.length === 0) return 1;
    if (importedKeys.length === 0 || systemKeys.length === 0) return 0;
    
    let matches = 0;
    let comparisons = 0;
    
    // Check common properties
    const commonProps = ['dataClassification', 'trustLevel', 'criticality', 'encryption'];
    
    commonProps.forEach(prop => {
      if (imported[prop] && system[prop]) {
        comparisons++;
        if (imported[prop] === system[prop]) {
          matches++;
        }
      }
    });
    
    return comparisons > 0 ? matches / comparisons : 0;
  }
}