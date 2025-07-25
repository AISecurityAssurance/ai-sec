// STPA-Sec Data Types for Database Storage and LLM Population
// This defines the complete data structure for STPA-Sec analysis

export interface StpaSecAnalysis {
  id: string;
  projectId: string;
  name: string;
  description: string;
  createdAt: Date;
  updatedAt: Date;
  
  // Core STPA-Sec components
  systemDescription: SystemDescription;
  losses: Loss[];
  hazards: Hazard[];
  controllers: Controller[];
  controlActions: ControlAction[];
  ucas: UCA[];
  causalScenarios: CausalScenario[];
  mitigations: Mitigation[];
}

export interface SystemDescription {
  id: string;
  purpose: string;
  boundaries: string[];
  assumptions: string[];
  constraints: string[];
  operationalContext: string;
}

export interface Loss {
  id: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  category: string;
  stakeholders: string[];
  estimatedCost?: number;
  regulatoryImpact?: string;
}

export interface Hazard {
  id: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  relatedLosses: string[]; // Loss IDs
  systemState: string;
  worstCase: string;
  environmentalConditions?: string;
  preconditions?: string[];
}

export interface Controller {
  id: string;
  name: string;
  type: 'human' | 'software' | 'hardware' | 'organizational';
  responsibilities: string[];
  processModel: string[]; // What the controller needs to know
  controlAlgorithm?: string; // How it makes decisions
  limitations?: string[];
}

export interface ControlAction {
  id: string;
  controllerId: string; // Controller ID
  action: string;
  targetProcess: string;
  constraints: string[]; // When it should/shouldn't be provided
  feedbackRequired?: string[];
  timing?: {
    minDelay?: number;
    maxDelay?: number;
    unit: 'ms' | 's' | 'min' | 'hour';
  };
}

export interface UCA {
  id: string;
  controlActionId: string; // Control Action ID
  type: 'not-provided' | 'provided' | 'wrong-timing' | 'wrong-duration';
  description: string;
  hazards: string[]; // Hazard IDs
  context: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  
  // STRIDE integration
  strideCategories?: ('spoofing' | 'tampering' | 'repudiation' | 'info-disclosure' | 'dos' | 'elevation')[];
  
  // Additional context
  systemMode?: string; // Normal, degraded, emergency, etc.
  environmentalFactors?: string[];
  assumptionsViolated?: string[];
}

export interface CausalScenario {
  id: string;
  ucaId: string; // UCA ID
  description: string;
  
  // Categorized causal factors
  causalFactors: {
    controller: string[]; // Controller inadequacies
    feedback: string[]; // Inadequate feedback
    communication: string[]; // Communication issues
    processModel: string[]; // Incorrect process model
    externalDisturbances: string[]; // Environmental factors
  };
  
  // Security perspective
  strideCategory?: string;
  attackVector?: string;
  threatActor?: string;
  
  // Risk assessment
  likelihood: 'very-low' | 'low' | 'medium' | 'high' | 'very-high';
  detectability: 'very-easy' | 'easy' | 'moderate' | 'hard' | 'very-hard';
  
  // D4 Score for security scenarios
  d4Score?: {
    detectability: number; // 1-5
    difficulty: number; // 1-5
    damage: number; // 1-5
    deniability: number; // 1-5
  };
  
  prerequisites: string[];
  indicators: string[];
  confidence: number; // 0-100
}

export interface Mitigation {
  id: string;
  name: string;
  description: string;
  type: 'preventive' | 'detective' | 'corrective' | 'compensating';
  
  // What it addresses
  addressesUCAs: string[]; // UCA IDs
  addressesScenarios: string[]; // Scenario IDs
  
  // Implementation details
  implementation: string;
  cost: 'low' | 'medium' | 'high' | 'very-high';
  complexity: 'low' | 'medium' | 'high' | 'very-high';
  effectiveness: 'low' | 'medium' | 'high' | 'very-high';
  
  // Dependencies and constraints
  dependencies: string[];
  constraints: string[];
  sideEffects?: string[];
  
  // Status tracking
  status: 'proposed' | 'approved' | 'in-progress' | 'implemented' | 'verified';
  priority: 'low' | 'medium' | 'high' | 'critical';
  owner?: string;
  dueDate?: Date;
}

// Helper types for analysis results
export interface UCAHeatMapData {
  controlAction: string;
  ucaType: string;
  count: number;
  averageSeverity: number;
  ucas: UCA[];
}

export interface RiskSummary {
  totalUCAs: number;
  criticalUCAs: number;
  highRiskScenarios: number;
  proposedMitigations: number;
  implementedMitigations: number;
  residualRisk: 'low' | 'medium' | 'high' | 'critical';
}

// Database schema helpers
export interface StpaSecTables {
  analyses: StpaSecAnalysis[];
  losses: Loss[];
  hazards: Hazard[];
  controllers: Controller[];
  controlActions: ControlAction[];
  ucas: UCA[];
  causalScenarios: CausalScenario[];
  mitigations: Mitigation[];
  
  // Relationship tables
  hazardLosses: { hazardId: string; lossId: string; }[];
  ucaHazards: { ucaId: string; hazardId: string; }[];
  scenarioMitigations: { scenarioId: string; mitigationId: string; }[];
}

// LLM prompt structure for analysis generation
export interface StpaSecPromptContext {
  systemDescription: string;
  existingAnalyses?: {
    stride?: any;
    pasta?: any;
    // Other analyses that can inform STPA-Sec
  };
  focusAreas?: string[];
  riskTolerance?: 'low' | 'medium' | 'high';
  complianceRequirements?: string[];
}