// Unified Analysis Data Schema
// Defines the database structure for all analysis frameworks

export interface AnalysisProject {
  id: string;
  name: string;
  description: string;
  systemDescription: string;
  createdAt: Date;
  updatedAt: Date;
  owner: string;
  collaborators: string[];
  status: 'draft' | 'in-progress' | 'review' | 'completed';
}

// Base interfaces for common patterns
export interface BaseEntity {
  id: string;
  name?: string;
  description: string;
  createdAt: Date;
  updatedAt: Date;
  projectId: string;
}

export interface RiskEntity extends BaseEntity {
  likelihood: 'very-low' | 'low' | 'medium' | 'high' | 'very-high';
  impact: 'very-low' | 'low' | 'medium' | 'high' | 'very-high' | 'critical';
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'identified' | 'analyzed' | 'mitigated' | 'accepted' | 'closed';
}

export interface ThreatEntity extends RiskEntity {
  category: string;
  threatActor?: string;
  attackVector?: string;
  mitigations: string[];
}

// STRIDE Schema
export interface STRIDEAnalysis {
  id: string;
  projectId: string;
  dataFlows: DataFlow[];
  components: Component[];
  threats: STRIDEThreat[];
  mitigations: Mitigation[];
}

export interface DataFlow {
  id: string;
  source: string;
  destination: string;
  protocol: string;
  data: string[];
  trustBoundary?: string;
}

export interface Component {
  id: string;
  name: string;
  type: 'process' | 'datastore' | 'external-entity' | 'data-flow';
  trustLevel: 'untrusted' | 'semi-trusted' | 'trusted';
}

export interface STRIDEThreat extends ThreatEntity {
  category: 'Spoofing' | 'Tampering' | 'Repudiation' | 'Information Disclosure' | 'Denial of Service' | 'Elevation of Privilege';
  component: string;
  dataFlow?: string;
}

// PASTA Schema
export interface PASTAAnalysis {
  id: string;
  projectId: string;
  stages: {
    businessObjectives: BusinessObjective[];
    technicalScope: TechnicalComponent[];
    applicationDecomposition: ApplicationComponent[];
    threatAnalysis: ThreatScenario[];
    vulnerabilityAnalysis: Vulnerability[];
    attackModeling: AttackScenario[];
    riskManagement: RiskAssessment[];
  };
}

export interface BusinessObjective extends BaseEntity {
  priority: 'low' | 'medium' | 'high' | 'critical';
  successCriteria: string[];
}

export interface TechnicalComponent extends Component {
  technologies: string[];
  interfaces: string[];
}

export interface ApplicationComponent extends BaseEntity {
  type: 'frontend' | 'backend' | 'api' | 'database' | 'service';
  technologies: string[];
  dataHandled: string[];
}

export interface ThreatScenario extends ThreatEntity {
  threatActor: string;
  motivation: string;
  capabilities: string[];
}

export interface AttackScenario extends BaseEntity {
  threatScenarioId: string;
  vulnerabilities: string[];
  attackPath: string[];
  ttps: string[];
}

export interface RiskAssessment extends RiskEntity {
  attackScenarioId: string;
  businessImpact: string;
  riskScore: number;
  treatment: 'mitigate' | 'transfer' | 'accept' | 'avoid';
}

export interface Vulnerability extends RiskEntity {
  component: string;
  cwe?: string;
  cvss?: number;
  exploitability: 'low' | 'medium' | 'high';
}

// DREAD Schema
export interface DREADAnalysis {
  id: string;
  projectId: string;
  threats: DREADThreat[];
}

export interface DREADThreat extends BaseEntity {
  scores: {
    damage: 1 | 2 | 3;
    reproducibility: 1 | 2 | 3;
    exploitability: 1 | 2 | 3;
    affectedUsers: 1 | 2 | 3;
    discoverability: 1 | 2 | 3;
    total: number;
  };
  riskLevel: 'Low' | 'Medium' | 'High' | 'Critical';
}

// STPA-Sec Schema (already defined in stpaSecTypes.ts)

// MAESTRO Schema
export interface MAESTROAnalysis {
  id: string;
  projectId: string;
  agents: AIAgent[];
  threats: AIThreat[];
  controls: AIControl[];
}

export interface AIAgent extends BaseEntity {
  type: 'AI Assistant' | 'ML Model' | 'Decision Engine' | 'Automation Agent';
  purpose: string;
  dataAccess: string[];
  capabilities: string[];
  trustLevel: 'untrusted' | 'partially-trusted' | 'trusted' | 'critical';
}

export interface AIThreat extends ThreatEntity {
  agentId: string;
  category: 'Adversarial' | 'Data Poisoning' | 'Model Theft' | 'Privacy Breach' | 'Bias' | 'Hallucination';
  detectionDifficulty: 'easy' | 'moderate' | 'hard' | 'very hard';
}

export interface AIControl extends BaseEntity {
  type: 'preventive' | 'detective' | 'corrective';
  effectiveness: 'low' | 'medium' | 'high';
  coverage: string[]; // Agent IDs
}

// LINDDUN Schema
export interface LINDDUNAnalysis {
  id: string;
  projectId: string;
  dataFlows: PersonalDataFlow[];
  threats: PrivacyThreat[];
  controls: PrivacyControl[];
}

export interface PersonalDataFlow extends DataFlow {
  dataTypes: string[];
  purpose: string;
  retention: string;
  encryption: 'none' | 'transit' | 'rest' | 'both';
}

export interface PrivacyThreat extends ThreatEntity {
  category: 'Linkability' | 'Identifiability' | 'Non-repudiation' | 'Detectability' | 'Disclosure' | 'Unawareness' | 'Non-compliance';
  dataFlow: string;
  gdprArticles?: string[];
}

export interface PrivacyControl extends BaseEntity {
  type: 'technical' | 'organizational' | 'legal';
  addresses: string[]; // Threat IDs
  implementation: string;
}

// HAZOP Schema
export interface HAZOPAnalysis {
  id: string;
  projectId: string;
  nodes: ProcessNode[];
  deviations: Deviation[];
  actions: ActionItem[];
}

export interface ProcessNode extends BaseEntity {
  type: 'process' | 'data-flow' | 'interface' | 'storage' | 'service';
  parameters: string[];
  normalOperation: string;
}

export interface Deviation extends RiskEntity {
  nodeId: string;
  parameter: string;
  guideWord: 'No' | 'More' | 'Less' | 'As well as' | 'Part of' | 'Reverse' | 'Other than' | 'Early' | 'Late' | 'Before' | 'After';
  causes: string[];
  consequences: string[];
  safeguards: string[];
}

export interface ActionItem extends BaseEntity {
  deviationId: string;
  action: string;
  responsible: string;
  dueDate: Date;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  status: 'pending' | 'in-progress' | 'completed' | 'overdue';
}

// OCTAVE Schema
export interface OCTAVEAnalysis {
  id: string;
  projectId: string;
  assets: CriticalAsset[];
  threats: AssetThreat[];
  vulnerabilities: AssetVulnerability[];
  risks: AssetRisk[];
  strategies: ProtectionStrategy[];
}

export interface CriticalAsset extends BaseEntity {
  type: 'information' | 'system' | 'service' | 'people' | 'facility';
  criticality: 'low' | 'medium' | 'high' | 'critical';
  owner: string;
  securityRequirements: {
    confidentiality: string;
    integrity: string;
    availability: string;
  };
}

export interface AssetThreat extends ThreatEntity {
  assetId: string;
  source: 'internal-accidental' | 'internal-deliberate' | 'external-accidental' | 'external-deliberate' | 'system-problems' | 'natural-disasters';
  actor: string;
}

export interface AssetVulnerability extends RiskEntity {
  assetId: string;
  type: 'technical' | 'physical' | 'organizational';
  exploitedBy: string[]; // Threat IDs
}

export interface AssetRisk extends RiskEntity {
  assetId: string;
  threatId: string;
  vulnerabilityId: string;
  strategy: 'mitigate' | 'transfer' | 'accept' | 'avoid';
}

export interface ProtectionStrategy extends BaseEntity {
  type: 'preventive' | 'detective' | 'corrective' | 'deterrent';
  effectiveness: 'low' | 'medium' | 'high';
  cost: 'low' | 'medium' | 'high';
  timeframe: string;
  status: 'proposed' | 'approved' | 'implementing' | 'operational';
}

// Unified Mitigation/Control Schema
export interface Mitigation extends BaseEntity {
  type: 'preventive' | 'detective' | 'corrective' | 'compensating';
  addresses: {
    framework: string;
    threatIds: string[];
  }[];
  implementation: string;
  cost: 'low' | 'medium' | 'high' | 'very-high';
  effectiveness: 'low' | 'medium' | 'high' | 'very-high';
  status: 'proposed' | 'approved' | 'in-progress' | 'implemented' | 'verified';
  owner?: string;
  dueDate?: Date;
}

// Database Tables Structure
export interface UnifiedAnalysisDatabase {
  // Core tables
  projects: AnalysisProject[];
  
  // Framework-specific tables
  strideAnalyses: STRIDEAnalysis[];
  pastaAnalyses: PASTAAnalysis[];
  dreadAnalyses: DREADAnalysis[];
  stpaSecAnalyses: any[]; // Imported from stpaSecTypes
  maestroAnalyses: MAESTROAnalysis[];
  linddunAnalyses: LINDDUNAnalysis[];
  hazopAnalyses: HAZOPAnalysis[];
  octaveAnalyses: OCTAVEAnalysis[];
  
  // Shared tables
  mitigations: Mitigation[];
  
  // Relationship tables
  projectAnalyses: {
    projectId: string;
    analysisType: string;
    analysisId: string;
  }[];
  
  // Cross-analysis mappings
  threatMappings: {
    sourceFramework: string;
    sourceId: string;
    targetFramework: string;
    targetId: string;
    mappingType: 'equivalent' | 'related' | 'partial';
  }[];
}

// LLM Integration Types
export interface AnalysisPrompt {
  framework: string;
  systemContext: string;
  previousAnalyses?: {
    framework: string;
    summary: any;
  }[];
  focusAreas?: string[];
  constraints?: string[];
}

export interface AnalysisResult {
  framework: string;
  confidence: number;
  data: any; // Framework-specific data
  explanations: {
    section: string;
    reasoning: string;
  }[];
  suggestedNextSteps: string[];
}