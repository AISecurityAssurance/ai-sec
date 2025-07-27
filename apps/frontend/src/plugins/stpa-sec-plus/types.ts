/**
 * Type definitions for STPA-Sec+ Orchestrator
 */

// Base analysis framework types
export type AnalysisFramework = 
  | 'STPA-Sec'
  | 'STRIDE'
  | 'PASTA'
  | 'OCTAVE'
  | 'DREAD'
  | 'MAESTRO'
  | 'LINDDUN'
  | 'HAZOP'
  | 'NIST-CSF'
  | 'ISO27001'
  | 'CUSTOM';

// Import adapter interface
export interface AnalysisImportAdapter {
  format: string;
  version: string;
  
  validate(data: any): Promise<ValidationResult>;
  transform(data: any): Promise<StandardizedAnalysis>;
  mapToEntities(analysis: StandardizedAnalysis, entities: Entity[]): Promise<MappingResult>;
  extractRisks(analysis: StandardizedAnalysis): Promise<Risk[]>;
}

// Validation result
export interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

// Standardized analysis format
export interface StandardizedAnalysis {
  framework: AnalysisFramework;
  metadata: AnalysisMetadata;
  entities: EntityMapping[];
  relationships: RelationshipMapping[];
  threats: ThreatMapping[];
  controls: ControlMapping[];
  risks: RiskMapping[];
  originalData: any;
}

// Analysis metadata
export interface AnalysisMetadata {
  source: string;
  importDate: Date;
  version: string;
  confidence: number;
  author?: string;
  originalFile?: string;
}

// Entity mapping
export interface EntityMapping {
  originalId: string;
  name: string;
  type: string;
  originalType?: string;
  properties: Record<string, any>;
  confidence: number;
}

// Relationship mapping
export interface RelationshipMapping {
  originalId: string;
  source: string;
  sourceName?: string;
  target: string;
  targetName?: string;
  type: string;
  action?: string;
  properties: Record<string, any>;
  confidence: number;
}

// Threat mapping
export interface ThreatMapping {
  originalId: string;
  name: string;
  description: string;
  category: string;
  originalCategory?: string;
  severity: string;
  state?: string;
  affectedEntity?: string;
  affectedFlow?: string;
  properties: Record<string, any>;
  confidence: number;
}

// Control mapping
export interface ControlMapping {
  originalId: string;
  name: string;
  description: string;
  type: string;
  state?: string;
  threatId?: string;
  properties: Record<string, any>;
  confidence: number;
}

// Risk mapping
export interface RiskMapping {
  id: string;
  name: string;
  description?: string;
  entityId?: string;
  entityName?: string;
  score: number;
  category?: string;
  mitigated?: boolean;
  properties: Record<string, any>;
}

// System entities (existing in the system)
export interface Entity {
  id: string;
  name: string;
  type: string;
  description?: string;
  properties?: Record<string, any>;
}

export interface Risk {
  id: string;
  name: string;
  score: number;
  [key: string]: any;
}

// Mapping result
export interface MappingResult {
  mappings: Array<{
    imported: EntityMapping;
    system: Entity;
    confidence: number;
  }>;
  unmapped: EntityMapping[];
  suggestions: Array<{
    imported: EntityMapping;
    suggested: Entity;
    confidence: number;
    reason: string;
  }>;
}

// Analysis gap
export interface AnalysisGap {
  id: string;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  affectedEntities?: string[];
  recommendation: string;
  estimatedEffort: string;
  businessImpact: string;
  complianceImpact?: string[];
  suggestedFramework?: string;
}

// Cross-framework insight
export interface CrossFrameworkInsight {
  id: string;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  frameworks: string[];
  recommendation: string;
  businessValue: string;
  effort: 'low' | 'medium' | 'high';
  actionability: 'low' | 'medium' | 'high';
}

// Synthesis result
export interface SynthesisResult {
  timestamp: Date;
  analyses: StandardizedAnalysis[];
  gaps: AnalysisGap[];
  conflicts: any[];
  insights: CrossFrameworkInsight[];
  recommendations: any[];
  metrics: {
    unifiedRiskScore: number;
    completenessScore: number;
    confidenceLevel: number;
    coverageMap: any;
  };
}

// Analysis options
export interface AnalysisOptions {
  mode: 'import' | 'native' | 'synthesis' | 'hybrid';
  data?: any;
  config?: any;
}

// Analysis result
export interface AnalysisResult {
  success: boolean;
  data?: any;
  errors?: string[];
  warnings?: string[];
}

// Gap detection types
export interface GapDetectionConfig {
  includeCompliance?: boolean;
  includeCVE?: boolean;
  includeAI?: boolean;
  depth?: 'shallow' | 'deep';
}

// Conflict types
export interface Conflict {
  type: 'risk_score_mismatch' | 'control_effectiveness_disagreement' | 'threat_existence_conflict' | 'entity_classification_conflict' | 'severity_rating_conflict';
  entity?: string;
  frameworks: string[];
  details: any;
  severity: 'low' | 'medium' | 'high';
}

export interface ConflictResolution {
  conflict: Conflict;
  resolution: string;
  resolvedValue: any;
  confidence: number;
  rationale: string;
}

// Recommendation types
export interface Recommendation {
  priority: number;
  type: 'gap_remediation' | 'optimization' | 'strategic';
  action: string;
  rationale: string;
  impact: string;
  effort: string;
  framework?: string;
}

// Import adapter types
export interface AdapterConfig {
  format: string;
  version?: string;
  customMappings?: Record<string, any>;
}

// CVE integration types
export interface CVEData {
  cveId: string;
  description: string;
  cvssScore: number;
  affectedProducts: string[];
  publishedDate: Date;
  exploitAvailable?: boolean;
}

export interface ContextualCVERisk {
  cve: CVEData;
  affectedEntities: Entity[];
  contextualScore: number;
  missionImpact: 'low' | 'medium' | 'high' | 'critical';
  mitigationPriority: number;
}

// Compliance types
export interface ComplianceFramework {
  id: string;
  name: string;
  requirements: ComplianceRequirement[];
}

export interface ComplianceRequirement {
  id: string;
  description: string;
  category: string;
  controlMapping?: string[];
}

export interface ComplianceGap {
  framework: string;
  requirement: ComplianceRequirement;
  gap: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  remediationCost: number;
  remediationTime: string;
}

// Executive metrics
export interface ExecutiveMetrics {
  overallRiskScore: number;
  complianceScore: number;
  coverageScore: number;
  trendsAnalysis: {
    riskTrend: 'improving' | 'stable' | 'deteriorating';
    timeframe: string;
  };
  topRisks: Risk[];
  investmentROI: {
    implemented: number;
    potential: number;
    recommendations: string[];
  };
}

// Plugin capabilities
export interface PluginCapabilities {
  import: boolean;
  export: boolean;
  synthesis: boolean;
  native: boolean;
  realtime: boolean;
  compliance?: boolean;
  cve?: boolean;
}

// Analysis context
export interface AnalysisContext {
  analysisStore: any;
  entityStore: any;
  userContext: any;
}