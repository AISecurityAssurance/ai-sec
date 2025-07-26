/**
 * Generic CSV Import Adapter
 * 
 * Flexible CSV adapter that can handle various security analysis CSV formats
 */

import { 
  AnalysisImportAdapter, 
  StandardizedAnalysis, 
  ValidationResult,
  EntityMapping,
  ThreatMapping,
  ControlMapping,
  RiskMapping
} from '../types';

interface CSVMapping {
  // Column mappings
  entityColumns?: {
    name?: string;
    type?: string;
    description?: string;
    [key: string]: string | undefined;
  };
  threatColumns?: {
    name?: string;
    description?: string;
    severity?: string;
    category?: string;
    affectedEntity?: string;
    [key: string]: string | undefined;
  };
  controlColumns?: {
    name?: string;
    description?: string;
    type?: string;
    effectiveness?: string;
    [key: string]: string | undefined;
  };
  riskColumns?: {
    name?: string;
    score?: string;
    impact?: string;
    likelihood?: string;
    [key: string]: string | undefined;
  };
}

export class GenericCSVAdapter implements AnalysisImportAdapter {
  format = 'generic-csv';
  version = '1.0';
  private mapping: CSVMapping = {};
  
  constructor(mapping?: CSVMapping) {
    if (mapping) {
      this.mapping = mapping;
    } else {
      // Default mappings for common column names
      this.mapping = {
        entityColumns: {
          name: 'name,asset,entity,component',
          type: 'type,category,class',
          description: 'description,details'
        },
        threatColumns: {
          name: 'threat,title,name',
          description: 'description,details,summary',
          severity: 'severity,priority,risk_level',
          category: 'category,type,classification',
          affectedEntity: 'asset,entity,target,affected'
        },
        controlColumns: {
          name: 'control,mitigation,countermeasure,name',
          description: 'description,details,implementation',
          type: 'type,category,control_type',
          effectiveness: 'effectiveness,status,implementation_status'
        },
        riskColumns: {
          name: 'risk,title,name',
          score: 'score,risk_score,rating',
          impact: 'impact,consequence,severity',
          likelihood: 'likelihood,probability,frequency'
        }
      };
    }
  }
  
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
    
    // Check if we can identify any meaningful columns
    const headers = Object.keys(rows[0]);
    const identifiedColumns = this.identifyColumns(headers);
    
    if (identifiedColumns.entityColumns === 0 && 
        identifiedColumns.threatColumns === 0 && 
        identifiedColumns.controlColumns === 0) {
      warnings.push('Could not identify standard security columns. Using best-effort mapping.');
    }
    
    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }
  
  async transform(data: string): Promise<StandardizedAnalysis> {
    const rows = this.parseCSV(data);
    const headers = Object.keys(rows[0] || {});
    
    // Auto-detect column types
    const columnTypes = this.detectColumnTypes(headers, rows);
    
    // Extract data based on detected columns
    const entities = this.extractEntities(rows, columnTypes);
    const threats = this.extractThreats(rows, columnTypes);
    const controls = this.extractControls(rows, columnTypes);
    const risks = this.extractRisks(rows, columnTypes);
    
    // Try to infer relationships
    const relationships = this.inferRelationships(entities, threats, rows);
    
    return {
      framework: 'CUSTOM',
      metadata: {
        source: 'Generic CSV Import',
        importDate: new Date(),
        version: '1.0',
        confidence: 0.6, // Lower confidence for generic import
        originalFile: 'analysis.csv'
      },
      entities,
      relationships,
      threats,
      controls,
      risks,
      originalData: { rows, columnTypes }
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
      
      // Lower confidence thresholds for generic import
      if (bestMatch.confidence > 0.6) {
        mappingResults.mappings.push({
          imported: importedEntity,
          system: bestMatch.entity,
          confidence: bestMatch.confidence
        });
      } else if (bestMatch.confidence > 0.3) {
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
  private parseCSV(csvString: string): any[] {
    const lines = csvString.trim().split('\n');
    if (lines.length < 2) return [];
    
    // Extract headers
    const headers = this.parseCSVLine(lines[0]).map(h => 
      h.trim().toLowerCase().replace(/[^a-z0-9_]/g, '_')
    );
    
    // Parse data rows
    const rows: any[] = [];
    for (let i = 1; i < lines.length; i++) {
      const values = this.parseCSVLine(lines[i]);
      if (values.length !== headers.length) continue;
      
      const row: any = {};
      headers.forEach((header, index) => {
        row[header] = values[index].trim();
      });
      
      // Skip empty rows
      if (Object.values(row).some(v => v !== '')) {
        rows.push(row);
      }
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
  
  // Identify column types based on headers
  private identifyColumns(headers: string[]): any {
    const result = {
      entityColumns: 0,
      threatColumns: 0,
      controlColumns: 0,
      riskColumns: 0
    };
    
    headers.forEach(header => {
      const headerLower = header.toLowerCase();
      
      // Check for entity indicators
      if (this.matchesPattern(headerLower, this.mapping.entityColumns)) {
        result.entityColumns++;
      }
      
      // Check for threat indicators
      if (this.matchesPattern(headerLower, this.mapping.threatColumns)) {
        result.threatColumns++;
      }
      
      // Check for control indicators
      if (this.matchesPattern(headerLower, this.mapping.controlColumns)) {
        result.controlColumns++;
      }
      
      // Check for risk indicators
      if (this.matchesPattern(headerLower, this.mapping.riskColumns)) {
        result.riskColumns++;
      }
    });
    
    return result;
  }
  
  // Match header against patterns
  private matchesPattern(header: string, patterns?: any): boolean {
    if (!patterns) return false;
    
    return Object.values(patterns).some(pattern => {
      if (typeof pattern === 'string') {
        const options = pattern.split(',');
        return options.some(opt => header.includes(opt));
      }
      return false;
    });
  }
  
  // Detect column types from data
  private detectColumnTypes(headers: string[], rows: any[]): any {
    const columnTypes: any = {
      entities: {},
      threats: {},
      controls: {},
      risks: {},
      relationships: {}
    };
    
    headers.forEach(header => {
      // Check entity columns
      if (this.isEntityColumn(header)) {
        columnTypes.entities[header] = this.detectEntityColumnType(header);
      }
      
      // Check threat columns
      if (this.isThreatColumn(header)) {
        columnTypes.threats[header] = this.detectThreatColumnType(header);
      }
      
      // Check control columns
      if (this.isControlColumn(header)) {
        columnTypes.controls[header] = this.detectControlColumnType(header);
      }
      
      // Check risk columns
      if (this.isRiskColumn(header)) {
        columnTypes.risks[header] = this.detectRiskColumnType(header);
      }
      
      // Check for relationship indicators
      if (this.isRelationshipColumn(header, rows)) {
        columnTypes.relationships[header] = 'relationship';
      }
    });
    
    return columnTypes;
  }
  
  // Column detection helpers
  private isEntityColumn(header: string): boolean {
    const patterns = ['asset', 'entity', 'component', 'system', 'application', 'service'];
    return patterns.some(p => header.includes(p));
  }
  
  private isThreatColumn(header: string): boolean {
    const patterns = ['threat', 'vulnerability', 'attack', 'risk'];
    return patterns.some(p => header.includes(p));
  }
  
  private isControlColumn(header: string): boolean {
    const patterns = ['control', 'mitigation', 'countermeasure', 'safeguard'];
    return patterns.some(p => header.includes(p));
  }
  
  private isRiskColumn(header: string): boolean {
    const patterns = ['risk', 'score', 'rating', 'level', 'priority'];
    return patterns.some(p => header.includes(p));
  }
  
  private isRelationshipColumn(header: string, rows: any[]): boolean {
    // Check if column contains references to other entities
    const patterns = ['from', 'to', 'source', 'target', 'flow'];
    if (patterns.some(p => header.includes(p))) return true;
    
    // Check if values look like references
    const sampleValues = rows.slice(0, 10).map(r => r[header]);
    const refPattern = /^[A-Z]{2,}-\d+$|^\w+\.\w+$/; // Common ID patterns
    return sampleValues.some(v => refPattern.test(v));
  }
  
  // Detect specific column types
  private detectEntityColumnType(header: string): string {
    if (header.includes('name') || header.includes('title')) return 'name';
    if (header.includes('type') || header.includes('category')) return 'type';
    if (header.includes('desc')) return 'description';
    return 'property';
  }
  
  private detectThreatColumnType(header: string): string {
    if (header.includes('name') || header.includes('title')) return 'name';
    if (header.includes('severity') || header.includes('priority')) return 'severity';
    if (header.includes('category') || header.includes('type')) return 'category';
    return 'property';
  }
  
  private detectControlColumnType(header: string): string {
    if (header.includes('name') || header.includes('title')) return 'name';
    if (header.includes('type')) return 'type';
    if (header.includes('status') || header.includes('effectiveness')) return 'effectiveness';
    return 'property';
  }
  
  private detectRiskColumnType(header: string): string {
    if (header.includes('score') || header.includes('rating')) return 'score';
    if (header.includes('impact')) return 'impact';
    if (header.includes('likelihood') || header.includes('probability')) return 'likelihood';
    return 'property';
  }
  
  // Extract entities from rows
  private extractEntities(rows: any[], columnTypes: any): EntityMapping[] {
    const entities: EntityMapping[] = [];
    const entityColumns = columnTypes.entities;
    
    if (Object.keys(entityColumns).length === 0) {
      // No entity columns detected, try to extract from all data
      return this.extractEntitiesFromGenericData(rows);
    }
    
    // Group rows by entity if possible
    const entityGroups = this.groupRowsByEntity(rows, entityColumns);
    
    entityGroups.forEach((group, entityName) => {
      entities.push({
        originalId: `entity-${entities.length + 1}`,
        name: entityName,
        type: this.inferEntityType(group[0], entityColumns),
        properties: this.extractProperties(group[0], entityColumns),
        confidence: 0.6
      });
    });
    
    return entities;
  }
  
  // Extract entities from generic data
  private extractEntitiesFromGenericData(rows: any[]): EntityMapping[] {
    const entities: EntityMapping[] = [];
    const seen = new Set<string>();
    
    rows.forEach(row => {
      // Look for columns that might contain entity names
      Object.entries(row).forEach(([key, value]) => {
        if (typeof value === 'string' && value.length > 2 && value.length < 100) {
          if (this.looksLikeEntityName(key, value) && !seen.has(value)) {
            seen.add(value);
            entities.push({
              originalId: `entity-${entities.length + 1}`,
              name: value,
              type: 'unknown',
              properties: { sourceColumn: key },
              confidence: 0.4
            });
          }
        }
      });
    });
    
    return entities;
  }
  
  // Check if value looks like an entity name
  private looksLikeEntityName(column: string, value: string): boolean {
    // Column name heuristics
    const goodColumns = ['asset', 'entity', 'system', 'component', 'name'];
    if (goodColumns.some(c => column.includes(c))) return true;
    
    // Value heuristics
    const hasLetters = /[a-zA-Z]/.test(value);
    const notJustNumbers = !/^\d+$/.test(value);
    const reasonableLength = value.length >= 3 && value.length <= 50;
    const notBoolean = !['true', 'false', 'yes', 'no'].includes(value.toLowerCase());
    
    return hasLetters && notJustNumbers && reasonableLength && notBoolean;
  }
  
  // Group rows by entity
  private groupRowsByEntity(rows: any[], entityColumns: any): Map<string, any[]> {
    const groups = new Map<string, any[]>();
    
    rows.forEach(row => {
      // Find the name column
      let entityName = '';
      Object.entries(entityColumns).forEach(([col, type]) => {
        if (type === 'name' && row[col]) {
          entityName = row[col];
        }
      });
      
      if (entityName) {
        if (!groups.has(entityName)) {
          groups.set(entityName, []);
        }
        groups.get(entityName)!.push(row);
      }
    });
    
    return groups;
  }
  
  // Infer entity type
  private inferEntityType(row: any, entityColumns: any): string {
    // Check if there's a type column
    for (const [col, colType] of Object.entries(entityColumns)) {
      if (colType === 'type' && row[col]) {
        return this.normalizeEntityType(row[col] as string);
      }
    }
    
    // Infer from name or other properties
    const name = row[Object.keys(row)[0]] || '';
    return this.inferEntityTypeFromName(name);
  }
  
  private normalizeEntityType(type: string): string {
    const typeMap: Record<string, string> = {
      'application': 'software',
      'app': 'software',
      'service': 'software',
      'database': 'datastore',
      'db': 'datastore',
      'user': 'human',
      'person': 'human',
      'network': 'network',
      'system': 'system'
    };
    
    return typeMap[type.toLowerCase()] || 'unknown';
  }
  
  private inferEntityTypeFromName(name: string): string {
    const nameLower = name.toLowerCase();
    
    if (nameLower.includes('user') || nameLower.includes('admin')) return 'human';
    if (nameLower.includes('database') || nameLower.includes('db')) return 'datastore';
    if (nameLower.includes('api') || nameLower.includes('service')) return 'software';
    if (nameLower.includes('network')) return 'network';
    
    return 'unknown';
  }
  
  // Extract properties
  private extractProperties(row: any, columns: any): any {
    const properties: any = {};
    
    Object.entries(columns).forEach(([col, type]) => {
      if (type === 'property' && row[col]) {
        properties[col] = row[col];
      }
    });
    
    return properties;
  }
  
  // Extract threats
  private extractThreats(rows: any[], columnTypes: any): ThreatMapping[] {
    const threats: ThreatMapping[] = [];
    const threatColumns = columnTypes.threats;
    
    if (Object.keys(threatColumns).length === 0) {
      return []; // No threat data detected
    }
    
    rows.forEach((row, index) => {
      const threatName = this.extractThreatName(row, threatColumns);
      if (threatName) {
        threats.push({
          originalId: `threat-${index + 1}`,
          name: threatName,
          description: this.extractThreatDescription(row, threatColumns) || threatName,
          category: this.extractThreatCategory(row, threatColumns),
          severity: this.extractThreatSeverity(row, threatColumns),
          affectedEntity: this.extractAffectedEntity(row, threatColumns),
          properties: this.extractProperties(row, threatColumns),
          confidence: 0.6
        });
      }
    });
    
    return threats;
  }
  
  // Extract threat properties
  private extractThreatName(row: any, columns: any): string {
    for (const [col, type] of Object.entries(columns)) {
      if (type === 'name' && row[col]) {
        return row[col] as string;
      }
    }
    return '';
  }
  
  private extractThreatDescription(row: any, columns: any): string {
    for (const [col, type] of Object.entries(columns)) {
      if ((type === 'description' || col.includes('desc')) && row[col]) {
        return row[col] as string;
      }
    }
    return '';
  }
  
  private extractThreatCategory(row: any, columns: any): string {
    for (const [col, type] of Object.entries(columns)) {
      if (type === 'category' && row[col]) {
        return row[col] as string;
      }
    }
    return 'unknown';
  }
  
  private extractThreatSeverity(row: any, columns: any): string {
    for (const [col, type] of Object.entries(columns)) {
      if (type === 'severity' && row[col]) {
        return this.normalizeSeverity(row[col] as string);
      }
    }
    return 'medium';
  }
  
  private extractAffectedEntity(row: any, columns: any): string {
    // Look for entity reference columns
    for (const [col, value] of Object.entries(row)) {
      if (col.includes('asset') || col.includes('entity') || col.includes('target')) {
        return value as string;
      }
    }
    return '';
  }
  
  private normalizeSeverity(severity: string): string {
    const severityLower = severity.toLowerCase();
    
    if (severityLower.includes('critical') || severityLower.includes('very high')) return 'critical';
    if (severityLower.includes('high')) return 'high';
    if (severityLower.includes('medium') || severityLower.includes('moderate')) return 'medium';
    if (severityLower.includes('low')) return 'low';
    
    // Check numeric values
    const numValue = parseFloat(severity);
    if (!isNaN(numValue)) {
      if (numValue >= 9) return 'critical';
      if (numValue >= 7) return 'high';
      if (numValue >= 4) return 'medium';
      return 'low';
    }
    
    return 'medium';
  }
  
  // Extract controls
  private extractControls(rows: any[], columnTypes: any): ControlMapping[] {
    const controls: ControlMapping[] = [];
    const controlColumns = columnTypes.controls;
    
    if (Object.keys(controlColumns).length === 0) {
      return []; // No control data detected
    }
    
    rows.forEach((row, index) => {
      const controlName = this.extractControlName(row, controlColumns);
      if (controlName) {
        controls.push({
          originalId: `control-${index + 1}`,
          name: controlName,
          description: this.extractControlDescription(row, controlColumns) || controlName,
          type: this.extractControlType(row, controlColumns),
          state: this.extractControlState(row, controlColumns),
          properties: this.extractProperties(row, controlColumns),
          confidence: 0.6
        });
      }
    });
    
    return controls;
  }
  
  // Extract control properties
  private extractControlName(row: any, columns: any): string {
    for (const [col, type] of Object.entries(columns)) {
      if (type === 'name' && row[col]) {
        return row[col] as string;
      }
    }
    return '';
  }
  
  private extractControlDescription(row: any, columns: any): string {
    for (const [col, type] of Object.entries(columns)) {
      if ((type === 'description' || col.includes('desc')) && row[col]) {
        return row[col] as string;
      }
    }
    return '';
  }
  
  private extractControlType(row: any, columns: any): string {
    for (const [col, type] of Object.entries(columns)) {
      if (type === 'type' && row[col]) {
        return row[col] as string;
      }
    }
    return 'control';
  }
  
  private extractControlState(row: any, columns: any): string {
    for (const [col, type] of Object.entries(columns)) {
      if (type === 'effectiveness' && row[col]) {
        return row[col] as string;
      }
    }
    return 'proposed';
  }
  
  // Extract risks
  private extractRisks(rows: any[], columnTypes: any): RiskMapping[] {
    const risks: RiskMapping[] = [];
    const riskColumns = columnTypes.risks;
    
    // If we have threats, convert them to risks
    if (Object.keys(riskColumns).length === 0 && columnTypes.threats) {
      return this.convertThreatsToRisks(rows, columnTypes);
    }
    
    rows.forEach((row, index) => {
      const riskScore = this.extractRiskScore(row, riskColumns);
      if (riskScore > 0) {
        risks.push({
          id: `risk-${index + 1}`,
          name: this.extractRiskName(row, riskColumns) || `Risk ${index + 1}`,
          score: riskScore,
          properties: this.extractProperties(row, riskColumns)
        });
      }
    });
    
    return risks;
  }
  
  // Convert threats to risks
  private convertThreatsToRisks(rows: any[], columnTypes: any): RiskMapping[] {
    const risks: RiskMapping[] = [];
    const threats = this.extractThreats(rows, columnTypes);
    
    threats.forEach(threat => {
      risks.push({
        id: `risk-${threat.originalId}`,
        name: threat.name,
        description: threat.description,
        score: this.severityToScore(threat.severity),
        category: threat.category,
        properties: threat.properties
      });
    });
    
    return risks;
  }
  
  private severityToScore(severity: string): number {
    const scores: Record<string, number> = {
      'critical': 10,
      'high': 8,
      'medium': 5,
      'low': 2
    };
    
    return scores[severity] || 5;
  }
  
  // Extract risk properties
  private extractRiskName(row: any, columns: any): string {
    for (const [col, type] of Object.entries(columns)) {
      if (type === 'name' && row[col]) {
        return row[col] as string;
      }
    }
    
    // Try to find any name-like column
    for (const [col, value] of Object.entries(row)) {
      if (col.includes('name') || col.includes('title')) {
        return value as string;
      }
    }
    
    return '';
  }
  
  private extractRiskScore(row: any, columns: any): number {
    // Direct score column
    for (const [col, type] of Object.entries(columns)) {
      if (type === 'score' && row[col]) {
        const score = parseFloat(row[col]);
        if (!isNaN(score)) return score;
      }
    }
    
    // Calculate from impact and likelihood
    let impact = 0;
    let likelihood = 0;
    
    for (const [col, type] of Object.entries(columns)) {
      if (type === 'impact' && row[col]) {
        impact = this.qualitativeToScore(row[col]);
      }
      if (type === 'likelihood' && row[col]) {
        likelihood = this.qualitativeToScore(row[col]);
      }
    }
    
    if (impact > 0 && likelihood > 0) {
      return (impact + likelihood) / 2;
    }
    
    return 0;
  }
  
  private qualitativeToScore(value: string): number {
    const valueLower = value.toLowerCase();
    
    if (valueLower.includes('very high') || valueLower.includes('critical')) return 10;
    if (valueLower.includes('high')) return 8;
    if (valueLower.includes('medium') || valueLower.includes('moderate')) return 5;
    if (valueLower.includes('low')) return 2;
    if (valueLower.includes('very low') || valueLower.includes('negligible')) return 1;
    
    // Try numeric
    const num = parseFloat(value);
    if (!isNaN(num) && num >= 0 && num <= 10) return num;
    
    return 5; // Default to medium
  }
  
  // Infer relationships
  private inferRelationships(entities: EntityMapping[], threats: ThreatMapping[], rows: any[]): any[] {
    const relationships: any[] = [];
    
    // Try to find relationship columns
    const relColumns = this.findRelationshipColumns(rows);
    
    if (relColumns.length > 0) {
      rows.forEach((row, index) => {
        relColumns.forEach(col => {
          const sourceEntity = this.findEntityByName(entities, row[col.source]);
          const targetEntity = this.findEntityByName(entities, row[col.target]);
          
          if (sourceEntity && targetEntity) {
            relationships.push({
              originalId: `rel-${index}-${col.source}-${col.target}`,
              source: sourceEntity.originalId,
              target: targetEntity.originalId,
              type: 'relationship',
              action: col.action || 'relates to',
              properties: {},
              confidence: 0.5
            });
          }
        });
      });
    }
    
    return relationships;
  }
  
  // Find relationship columns
  private findRelationshipColumns(rows: any[]): any[] {
    const columns = Object.keys(rows[0] || {});
    const relColumns: any[] = [];
    
    // Look for paired columns (from/to, source/target)
    const pairs = [
      { source: 'from', target: 'to' },
      { source: 'source', target: 'target' },
      { source: 'sender', target: 'receiver' }
    ];
    
    pairs.forEach(pair => {
      const sourceCol = columns.find(c => c.includes(pair.source));
      const targetCol = columns.find(c => c.includes(pair.target));
      
      if (sourceCol && targetCol) {
        relColumns.push({
          source: sourceCol,
          target: targetCol,
          action: 'flows to'
        });
      }
    });
    
    return relColumns;
  }
  
  // Find entity by name
  private findEntityByName(entities: EntityMapping[], name: string): EntityMapping | undefined {
    if (!name) return undefined;
    return entities.find(e => e.name === name);
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
      confidence += nameSimilarity * 0.6; // Higher weight for generic import
      if (nameSimilarity > 0.7) reasons.push('name match');
      
      // Type compatibility (if known)
      if (importedEntity.type !== 'unknown' && systemEntity.type) {
        if (importedEntity.type === systemEntity.type) {
          confidence += 0.3;
          reasons.push('type match');
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
}