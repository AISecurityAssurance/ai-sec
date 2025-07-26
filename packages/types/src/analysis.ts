// Analysis Types

export interface Project {
  id: string;
  name: string;
  description: string;
  createdAt: Date;
  updatedAt: Date;
  files: ProjectFile[];
  analyses: Analysis[];
}

export interface ProjectFile {
  id: string;
  path: string;
  content: string;
  type: 'code' | 'documentation' | 'specification' | 'diagram';
  language?: string;
  size: number;
  lastModified: Date;
}

export interface Analysis {
  id: string;
  projectId: string;
  type: AnalysisType;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  startedAt: Date;
  completedAt?: Date;
  results?: AnalysisResults;
  error?: string;
}

export type AnalysisType = 'stpa-sec' | 'stpa-sec-plus' | 'stride' | 'pasta' | 'maestro' | 'combined';

// STPA-Sec Types
export interface STPASecAnalysis {
  losses: Loss[];
  hazards: Hazard[];
  controlStructure: ControlStructure;
  unsafeControlActions: UnsafeControlAction[];
  lossSenarios: LossScenario[];
  mitigations: Mitigation[];
}

export interface Loss {
  id: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  category: string;
}

export interface Hazard {
  id: string;
  description: string;
  relatedLosses: string[]; // Loss IDs
  severity: 'low' | 'medium' | 'high' | 'critical';
}

export interface ControlStructure {
  controllers: Controller[];
  controlledProcesses: ControlledProcess[];
  connections: Connection[];
}

export interface Controller {
  id: string;
  name: string;
  type: string;
  processModel?: string;
  trustBoundary?: string;
}

export interface ControlledProcess {
  id: string;
  name: string;
  type: string;
  state?: string;
}

export interface Connection {
  id: string;
  from: string; // Controller or Process ID
  to: string; // Controller or Process ID
  type: 'control' | 'feedback';
  label: string;
}

export interface UnsafeControlAction {
  id: string;
  controlAction: string;
  controllerId: string;
  type: 'not_provided' | 'provided_incorrectly' | 'wrong_timing' | 'wrong_duration';
  context: string;
  hazards: string[]; // Hazard IDs
  strideCategories?: STRIDECategory[];
}

export interface LossScenario {
  id: string;
  ucaId: string;
  description: string;
  causalFactors: string[];
  attackVector?: string;
  likelihood: 'low' | 'medium' | 'high';
  impact: 'low' | 'medium' | 'high';
}

export interface Mitigation {
  id: string;
  scenarioId: string;
  type: 'preventive' | 'detective' | 'corrective';
  description: string;
  implementation?: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
}

// STRIDE Types
export type STRIDECategory = 'spoofing' | 'tampering' | 'repudiation' | 'information_disclosure' | 'denial_of_service' | 'elevation_of_privilege';

export interface STRIDEThreat {
  id: string;
  category: STRIDECategory;
  component: string;
  description: string;
  impact: string;
  likelihood: 'low' | 'medium' | 'high';
  mitigations: string[];
}

export interface STRIDEAnalysis {
  threats: STRIDEThreat[];
  dataFlows: DataFlow[];
  trustBoundaries: TrustBoundary[];
}

export interface DataFlow {
  id: string;
  from: string;
  to: string;
  data: string;
  protocol?: string;
  encrypted?: boolean;
}

export interface TrustBoundary {
  id: string;
  name: string;
  components: string[];
}

// Combined Analysis Results
export interface AnalysisResults {
  stpaSec?: STPASecAnalysis;
  stride?: STRIDEAnalysis;
  summary: AnalysisSummary;
  recommendations: Recommendation[];
}

export interface AnalysisSummary {
  totalFindings: number;
  criticalFindings: number;
  highFindings: number;
  mediumFindings: number;
  lowFindings: number;
  coverageScore: number;
  confidenceScore: number;
}

export interface Recommendation {
  id: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  category: string;
  title: string;
  description: string;
  relatedFindings: string[];
  estimatedEffort?: 'low' | 'medium' | 'high';
  implementationGuidance?: string;
}

// Analysis Plugin System
export interface AnalysisPlugin {
  id: string;
  name: string;
  version: string;
  description: string;
  capabilities?: PluginCapabilities;
  initialize(context: AnalysisContext): Promise<void>;
  analyze(options: AnalysisOptions): Promise<AnalysisResult>;
}

export interface PluginCapabilities {
  import?: boolean;
  export?: boolean;
  synthesis?: boolean;
  native?: boolean;
  realtime?: boolean;
  compliance?: boolean;
  cve?: boolean;
}

export interface AnalysisContext {
  analysisStore: any;
  entityStore?: any;
  userContext?: any;
}

export interface AnalysisOptions {
  mode: 'import' | 'native' | 'synthesis' | 'hybrid';
  data?: any;
  config?: any;
}

export interface AnalysisResult {
  success: boolean;
  data?: any;
  errors?: string[];
  warnings?: string[];
}