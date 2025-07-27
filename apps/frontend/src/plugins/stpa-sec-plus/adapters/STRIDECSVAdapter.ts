/**
 * STRIDE CSV Import Adapter
 * 
 * Transforms generic STRIDE threat modeling CSV exports into standardized format
 */

import type { 
  AnalysisImportAdapter, 
  StandardizedAnalysis, 
  ValidationResult,
  EntityMapping,
  ThreatMapping,
  ControlMapping 
} from '../types';

interface STRIDERow {
  threat: string;
  category: string; // S, T, R, I, D, E
  asset: string;
  description?: string;
  likelihood?: string;
  impact?: string;
  risk?: string;
  mitigation?: string;
  status?: string;
}

export class STRIDECSVAdapter implements AnalysisImportAdapter {
  format = 'stride-csv';
  version = '1.0';
  
  async validate(data: any): Promise<ValidationResult> {
    const errors: string[] = [];
    const warnings: string[] = [];
    
    // Check if data is string (CSV content)
    if (typeof data !== 'string') {
      errors.push('Data must be CSV string');
      return { isValid: false, errors, warnings };
    }
    
    // Parse CSV
    const rows = this.parseCSV(data);
    
    if (rows.length === 0) {
      errors.push('No data rows found in CSV');
      return { isValid: false, errors, warnings };
    }
    
    // Check required columns
    const requiredColumns = ['threat', 'category', 'asset'];
    const headers = Object.keys(rows[0]);
    
    requiredColumns.forEach(col => {
      if (!headers.includes(col)) {
        errors.push(`Missing required column: ${col}`);
      }
    });
    
    // Validate STRIDE categories
    const validCategories = ['S', 'T', 'R', 'I', 'D', 'E', 
                           'Spoofing', 'Tampering', 'Repudiation', 
                           'Information Disclosure', 'Denial of Service', 
                           'Elevation of Privilege'];
    
    rows.forEach((row, index) => {
      if (row.category && !validCategories.includes(row.category)) {
        warnings.push(`Row ${index + 1}: Invalid STRIDE category '${row.category}'`);
      }
    });
    
    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }
  
  async transform(data: string): Promise<StandardizedAnalysis> {
    const rows = this.parseCSV(data);
    const entities = new Map<string, EntityMapping>();
    const threats: ThreatMapping[] = [];
    const controls: ControlMapping[] = [];
    
    // Extract unique assets as entities
    rows.forEach(row => {
      if (row.asset && !entities.has(row.asset)) {
        entities.set(row.asset, {
          originalId: `asset-${row.asset}`,
          name: row.asset,
          type: this.inferEntityType(row.asset),
          properties: {
            source: 'stride-csv'
          },
          confidence: 0.7
        });
      }
      
      // Create threat mapping
      if (row.threat) {
        threats.push({
          originalId: `threat-${threats.length + 1}`,
          name: row.threat,
          description: row.description || row.threat,
          category: this.normalizeSTRIDECategory(row.category),
          originalCategory: row.category,
          severity: this.calculateSeverity(row.likelihood, row.impact, row.risk),
          state: row.status || 'identified',
          affectedEntity: `asset-${row.asset}`,
          properties: {
            likelihood: row.likelihood,
            impact: row.impact,
            risk: row.risk
          },
          confidence: 0.8
        });
        
        // Create mitigation as control if present
        if (row.mitigation) {
          controls.push({
            originalId: `control-${controls.length + 1}`,
            name: row.mitigation,
            description: row.mitigation,
            type: 'mitigation',
            state: row.status || 'proposed',
            threatId: `threat-${threats.length}`,
            properties: {},
            confidence: 0.75
          });
        }
      }
    });
    
    return {
      framework: 'STRIDE',
      metadata: {
        source: 'STRIDE CSV Import',
        importDate: new Date(),
        version: '1.0',
        confidence: 0.75,
        originalFile: 'stride-analysis.csv'
      },
      entities: Array.from(entities.values()),
      relationships: [], // STRIDE CSV typically doesn't include relationships
      threats,
      controls,
      risks: this.calculateRisks(threats, entities),
      originalData: { rows }
    };
  }
  
  async mapToEntities(analysis: StandardizedAnalysis, systemEntities: any[]): Promise<any> {
    // Similar to Microsoft TMT adapter
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
  
  // Parse CSV string into array of objects
  private parseCSV(csvString: string): STRIDERow[] {
    const lines = csvString.trim().split('\n');
    if (lines.length < 2) return [];
    
    // Extract headers (normalize to lowercase)
    const headers = lines[0].split(',').map(h => h.trim().toLowerCase());
    
    // Parse data rows
    const rows: STRIDERow[] = [];
    for (let i = 1; i < lines.length; i++) {
      const values = this.parseCSVLine(lines[i]);
      if (values.length !== headers.length) continue;
      
      const row: any = {};
      headers.forEach((header, index) => {
        row[header] = values[index].trim();
      });
      
      rows.push(row as STRIDERow);
    }
    
    return rows;
  }
  
  // Parse a single CSV line handling quoted values
  private parseCSVLine(line: string): string[] {
    const result = [];
    let current = '';
    let inQuotes = false;
    
    for (let i = 0; i < line.length; i++) {
      const char = line[i];
      
      if (char === '"') {
        inQuotes = !inQuotes;
      } else if (char === ',' && !inQuotes) {
        result.push(current);
        current = '';
      } else {
        current += char;
      }
    }
    
    result.push(current);
    return result;
  }
  
  // Infer entity type from name
  private inferEntityType(assetName: string): string {
    const name = assetName.toLowerCase();
    
    if (name.includes('user') || name.includes('admin') || name.includes('operator')) {
      return 'human';
    }
    if (name.includes('database') || name.includes('db') || name.includes('storage')) {
      return 'datastore';
    }
    if (name.includes('api') || name.includes('service') || name.includes('server')) {
      return 'software';
    }
    if (name.includes('network') || name.includes('firewall') || name.includes('router')) {
      return 'network';
    }
    if (name.includes('external') || name.includes('third-party')) {
      return 'external_entity';
    }
    
    return 'unknown';
  }
  
  // Normalize STRIDE category
  private normalizeSTRIDECategory(category: string): string {
    const mapping: Record<string, string> = {
      'S': 'spoofing',
      'T': 'tampering',
      'R': 'repudiation',
      'I': 'information_disclosure',
      'D': 'denial_of_service',
      'E': 'elevation_of_privilege',
      'Spoofing': 'spoofing',
      'Tampering': 'tampering',
      'Repudiation': 'repudiation',
      'Information Disclosure': 'information_disclosure',
      'Denial of Service': 'denial_of_service',
      'Elevation of Privilege': 'elevation_of_privilege'
    };
    
    return mapping[category] || category.toLowerCase();
  }
  
  // Calculate severity from likelihood and impact
  private calculateSeverity(likelihood?: string, impact?: string, risk?: string): string {
    // If risk is directly provided, use it
    if (risk) {
      const riskLower = risk.toLowerCase();
      if (riskLower.includes('critical') || riskLower.includes('very high')) return 'critical';
      if (riskLower.includes('high')) return 'high';
      if (riskLower.includes('medium') || riskLower.includes('moderate')) return 'medium';
      if (riskLower.includes('low')) return 'low';
    }
    
    // Otherwise calculate from likelihood and impact
    const likelihoodScore = this.scoreFromString(likelihood);
    const impactScore = this.scoreFromString(impact);
    const combinedScore = (likelihoodScore + impactScore) / 2;
    
    if (combinedScore >= 4) return 'critical';
    if (combinedScore >= 3) return 'high';
    if (combinedScore >= 2) return 'medium';
    return 'low';
  }
  
  // Convert string ratings to numeric scores
  private scoreFromString(value?: string): number {
    if (!value) return 2.5; // Default to medium
    
    const valueLower = value.toLowerCase();
    if (valueLower.includes('very high') || valueLower.includes('critical')) return 5;
    if (valueLower.includes('high')) return 4;
    if (valueLower.includes('medium') || valueLower.includes('moderate')) return 3;
    if (valueLower.includes('low')) return 2;
    if (valueLower.includes('very low') || valueLower.includes('negligible')) return 1;
    
    return 2.5;
  }
  
  // Calculate risks from threats
  private calculateRisks(threats: ThreatMapping[], entities: Map<string, EntityMapping>): any[] {
    const risks: any[] = [];
    
    threats.forEach(threat => {
      const entity = entities.get(threat.affectedEntity?.replace('asset-', '') || '');
      
      risks.push({
        id: `risk-${threat.originalId}`,
        name: threat.name,
        description: threat.description,
        entityId: threat.affectedEntity,
        entityName: entity?.name,
        score: this.severityToScore(threat.severity),
        category: threat.category,
        mitigated: threat.state === 'mitigated',
        properties: threat.properties
      });
    });
    
    return risks;
  }
  
  // Convert severity to numeric score
  private severityToScore(severity: string): number {
    const scores: Record<string, number> = {
      'critical': 10,
      'high': 8,
      'medium': 5,
      'low': 2,
      'info': 1
    };
    
    return scores[severity] || 5;
  }
  
  // Find best entity match
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
      confidence += nameSimilarity * 0.5;
      if (nameSimilarity > 0.8) reasons.push('name match');
      
      // Type compatibility
      if (importedEntity.type === systemEntity.type) {
        confidence += 0.3;
        reasons.push('type match');
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
  
  // Simple string similarity
  private calculateStringSimilarity(str1: string, str2: string): number {
    if (str1 === str2) return 1;
    
    const longer = str1.length > str2.length ? str1 : str2;
    const shorter = str1.length > str2.length ? str2 : str1;
    
    if (longer.length === 0) return 1;
    
    const editDistance = this.levenshteinDistance(longer, shorter);
    return (longer.length - editDistance) / longer.length;
  }
  
  // Levenshtein distance
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
}