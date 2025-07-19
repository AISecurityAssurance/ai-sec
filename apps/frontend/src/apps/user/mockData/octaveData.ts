// OCTAVE Analysis Mock Data for Modern Digital Banking Platform
// Operationally Critical Threat, Asset, and Vulnerability Evaluation

export interface OctaveAsset {
  id: string;
  name: string;
  type: 'information' | 'system' | 'service' | 'people' | 'facility';
  criticality: 'low' | 'medium' | 'high' | 'critical';
  owner: string;
  description: string;
  rationale: string;
  securityRequirements: {
    confidentiality: 'low' | 'medium' | 'high';
    integrity: 'low' | 'medium' | 'high';
    availability: 'low' | 'medium' | 'high';
  };
  containers: string[];
}

export interface OctaveThreat {
  id: string;
  assetId: string;
  source: 'internal-accidental' | 'internal-deliberate' | 'external-accidental' | 'external-deliberate' | 'system-problems' | 'natural-disasters';
  actor: string;
  means: string;
  motive: string;
  outcome: string;
  probability: 'very-low' | 'low' | 'medium' | 'high' | 'very-high';
  impact: {
    confidentiality: number; // 0-5
    integrity: number; // 0-5
    availability: number; // 0-5
    financial: number; // 0-5
    reputation: number; // 0-5
    compliance: number; // 0-5
  };
  currentControls: string[];
  controlGaps: string[];
}

export interface OctaveVulnerability {
  id: string;
  assetId: string;
  type: 'technical' | 'physical' | 'organizational';
  category: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  exploitability: 'low' | 'medium' | 'high';
  relatedThreats: string[];
  remediationEffort: 'low' | 'medium' | 'high';
  status: 'identified' | 'analyzing' | 'mitigating' | 'mitigated';
}

export interface OctaveRisk {
  id: string;
  assetId: string;
  threatId: string;
  vulnerabilityIds: string[];
  description: string;
  likelihood: 'very-low' | 'low' | 'medium' | 'high' | 'very-high';
  impact: 'negligible' | 'minor' | 'moderate' | 'major' | 'severe';
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  strategy: 'accept' | 'mitigate' | 'transfer' | 'avoid';
  mitigationPlan?: string;
  residualRisk?: 'low' | 'medium' | 'high';
  owner: string;
  reviewDate: string;
}

export interface OctaveProtectionStrategy {
  id: string;
  name: string;
  type: 'preventive' | 'detective' | 'corrective' | 'deterrent';
  description: string;
  implementation: string;
  coverage: string[]; // Asset IDs
  effectiveness: 'low' | 'medium' | 'high';
  cost: 'low' | 'medium' | 'high';
  timeframe: string;
  status: 'proposed' | 'approved' | 'implementing' | 'operational';
}

export const octaveAssets: OctaveAsset[] = [
  {
    id: 'ASSET-001',
    name: 'Customer Account Database',
    type: 'information',
    criticality: 'critical',
    owner: 'Chief Data Officer',
    description: 'Central repository of all customer account information, transaction history, and PII',
    rationale: 'Contains sensitive financial data for 10M+ customers, breach would result in severe regulatory and reputational damage',
    securityRequirements: {
      confidentiality: 'high',
      integrity: 'high',
      availability: 'high'
    },
    containers: ['Primary Data Center', 'DR Site', 'Cloud Backup']
  },
  {
    id: 'ASSET-002',
    name: 'Core Banking System',
    type: 'system',
    criticality: 'critical',
    owner: 'VP of Technology',
    description: 'Central system processing all banking transactions and account management',
    rationale: 'Processes $2B+ daily transactions, downtime directly impacts revenue and customer service',
    securityRequirements: {
      confidentiality: 'high',
      integrity: 'high',
      availability: 'high'
    },
    containers: ['Production Servers', 'Application Tier', 'Database Tier']
  },
  {
    id: 'ASSET-003',
    name: 'Mobile Banking Application',
    type: 'service',
    criticality: 'high',
    owner: 'Head of Digital Banking',
    description: 'Customer-facing mobile application for iOS and Android',
    rationale: '70% of customers use mobile as primary banking channel',
    securityRequirements: {
      confidentiality: 'high',
      integrity: 'high',
      availability: 'medium'
    },
    containers: ['App Stores', 'API Gateway', 'Mobile Backend']
  },
  {
    id: 'ASSET-004',
    name: 'Payment Processing Network',
    type: 'system',
    criticality: 'critical',
    owner: 'Payment Operations Manager',
    description: 'Network infrastructure for processing ACH, wire transfers, and card payments',
    rationale: 'Handles all payment types, integration with SWIFT, FedWire, and card networks',
    securityRequirements: {
      confidentiality: 'high',
      integrity: 'high',
      availability: 'high'
    },
    containers: ['Payment Gateway', 'HSM Cluster', 'Network Infrastructure']
  },
  {
    id: 'ASSET-005',
    name: 'Fraud Detection Models',
    type: 'information',
    criticality: 'high',
    owner: 'Chief Risk Officer',
    description: 'ML models and rules for detecting fraudulent transactions',
    rationale: 'Prevents $50M+ annual fraud losses, competitive advantage',
    securityRequirements: {
      confidentiality: 'high',
      integrity: 'high',
      availability: 'medium'
    },
    containers: ['ML Platform', 'Model Registry', 'Rules Engine']
  },
  {
    id: 'ASSET-006',
    name: 'Customer Service Representatives',
    type: 'people',
    criticality: 'medium',
    owner: 'Head of Customer Service',
    description: '500+ CSRs with access to customer data and transaction capabilities',
    rationale: 'Human element with broad system access, social engineering target',
    securityRequirements: {
      confidentiality: 'medium',
      integrity: 'medium',
      availability: 'low'
    },
    containers: ['Call Centers', 'Remote Workers', 'Branch Staff']
  },
  {
    id: 'ASSET-007',
    name: 'API Gateway Infrastructure',
    type: 'system',
    criticality: 'high',
    owner: 'Platform Engineering Lead',
    description: 'Central API gateway handling all external integrations',
    rationale: 'Single point of entry for partners, fintechs, and third-party services',
    securityRequirements: {
      confidentiality: 'high',
      integrity: 'high',
      availability: 'high'
    },
    containers: ['Load Balancers', 'API Management Platform', 'WAF']
  },
  {
    id: 'ASSET-008',
    name: 'Executive Leadership Team',
    type: 'people',
    criticality: 'high',
    owner: 'Chief Security Officer',
    description: 'C-suite executives with privileged access and decision authority',
    rationale: 'High-value targets for spear phishing and social engineering',
    securityRequirements: {
      confidentiality: 'high',
      integrity: 'high',
      availability: 'low'
    },
    containers: ['Executive Offices', 'Board Meetings', 'Remote Access']
  }
];

export const octaveThreats: OctaveThreat[] = [
  {
    id: 'THREAT-001',
    assetId: 'ASSET-001',
    source: 'external-deliberate',
    actor: 'Organized Crime Group',
    means: 'Advanced persistent threat using custom malware',
    motive: 'Financial gain through data theft and extortion',
    outcome: 'Mass customer data breach with ransom demand',
    probability: 'medium',
    impact: {
      confidentiality: 5,
      integrity: 3,
      availability: 4,
      financial: 5,
      reputation: 5,
      compliance: 5
    },
    currentControls: [
      'Network segmentation',
      'Encryption at rest',
      'DLP solutions',
      'SIEM monitoring'
    ],
    controlGaps: [
      'Limited threat hunting capability',
      'Gaps in east-west traffic inspection',
      'Incomplete data classification'
    ]
  },
  {
    id: 'THREAT-002',
    assetId: 'ASSET-002',
    source: 'internal-accidental',
    actor: 'System Administrator',
    means: 'Misconfiguration during maintenance',
    motive: 'Unintentional error',
    outcome: 'System outage affecting transaction processing',
    probability: 'high',
    impact: {
      confidentiality: 0,
      integrity: 2,
      availability: 5,
      financial: 4,
      reputation: 3,
      compliance: 2
    },
    currentControls: [
      'Change management process',
      'Testing environments',
      'Rollback procedures'
    ],
    controlGaps: [
      'Insufficient automation',
      'Limited configuration validation',
      'Manual deployment processes'
    ]
  },
  {
    id: 'THREAT-003',
    assetId: 'ASSET-003',
    source: 'external-deliberate',
    actor: 'Hacktivist Group',
    means: 'DDoS attack on mobile infrastructure',
    motive: 'Ideological protest against banking industry',
    outcome: 'Mobile banking unavailable for extended period',
    probability: 'medium',
    impact: {
      confidentiality: 0,
      integrity: 0,
      availability: 5,
      financial: 3,
      reputation: 4,
      compliance: 1
    },
    currentControls: [
      'CDN protection',
      'Rate limiting',
      'Geographic filtering'
    ],
    controlGaps: [
      'Limited surge capacity',
      'Incomplete DDoS playbooks',
      'Third-party dependencies'
    ]
  },
  {
    id: 'THREAT-004',
    assetId: 'ASSET-004',
    source: 'external-deliberate',
    actor: 'Nation-State Actor',
    means: 'Supply chain compromise of payment processor',
    motive: 'Economic warfare and intelligence gathering',
    outcome: 'Persistent access to payment flows and manipulation capability',
    probability: 'low',
    impact: {
      confidentiality: 5,
      integrity: 5,
      availability: 3,
      financial: 5,
      reputation: 5,
      compliance: 5
    },
    currentControls: [
      'Vendor risk assessments',
      'Code signing',
      'Network isolation'
    ],
    controlGaps: [
      'Limited supply chain visibility',
      'Insufficient vendor monitoring',
      'Complex integration points'
    ]
  },
  {
    id: 'THREAT-005',
    assetId: 'ASSET-005',
    source: 'internal-deliberate',
    actor: 'Disgruntled Data Scientist',
    means: 'Model poisoning and IP theft',
    motive: 'Revenge and competitive advantage for new employer',
    outcome: 'Degraded fraud detection and stolen algorithms',
    probability: 'medium',
    impact: {
      confidentiality: 5,
      integrity: 4,
      availability: 1,
      financial: 4,
      reputation: 3,
      compliance: 2
    },
    currentControls: [
      'Access controls',
      'Code repository monitoring',
      'Background checks'
    ],
    controlGaps: [
      'Model versioning gaps',
      'Insufficient behavioral monitoring',
      'Limited ML security tools'
    ]
  },
  {
    id: 'THREAT-006',
    assetId: 'ASSET-006',
    source: 'external-deliberate',
    actor: 'Social Engineering Attacker',
    means: 'Vishing and pretexting targeting CSRs',
    motive: 'Account takeover and fraud',
    outcome: 'Unauthorized customer data access and fraudulent transactions',
    probability: 'high',
    impact: {
      confidentiality: 4,
      integrity: 3,
      availability: 0,
      financial: 3,
      reputation: 3,
      compliance: 3
    },
    currentControls: [
      'Security awareness training',
      'Call verification procedures',
      'Transaction limits'
    ],
    controlGaps: [
      'Inconsistent verification',
      'Training effectiveness',
      'Real-time detection'
    ]
  },
  {
    id: 'THREAT-007',
    assetId: 'ASSET-007',
    source: 'external-deliberate',
    actor: 'Competitor-sponsored Attackers',
    means: 'API abuse and reverse engineering',
    motive: 'Competitive intelligence and service disruption',
    outcome: 'API keys compromised, rate limits bypassed, data scraping',
    probability: 'high',
    impact: {
      confidentiality: 3,
      integrity: 2,
      availability: 3,
      financial: 2,
      reputation: 2,
      compliance: 2
    },
    currentControls: [
      'API authentication',
      'Rate limiting',
      'Usage monitoring'
    ],
    controlGaps: [
      'Weak API key rotation',
      'Limited behavioral analysis',
      'Partner API oversight'
    ]
  },
  {
    id: 'THREAT-008',
    assetId: 'ASSET-008',
    source: 'external-deliberate',
    actor: 'Advanced Threat Group',
    means: 'Spear phishing with executive impersonation',
    motive: 'High-value wire transfer fraud',
    outcome: 'Fraudulent transfers authorized by compromised executive',
    probability: 'medium',
    impact: {
      confidentiality: 2,
      integrity: 5,
      availability: 0,
      financial: 5,
      reputation: 4,
      compliance: 3
    },
    currentControls: [
      'Email security gateway',
      'Multi-factor authentication',
      'Wire transfer procedures'
    ],
    controlGaps: [
      'Executive security training',
      'Out-of-band verification',
      'Privileged access management'
    ]
  }
];

export const octaveVulnerabilities: OctaveVulnerability[] = [
  {
    id: 'VULN-001',
    assetId: 'ASSET-001',
    type: 'technical',
    category: 'Access Control',
    description: 'Excessive database privileges for application accounts',
    severity: 'high',
    exploitability: 'medium',
    relatedThreats: ['THREAT-001'],
    remediationEffort: 'medium',
    status: 'mitigating'
  },
  {
    id: 'VULN-002',
    assetId: 'ASSET-001',
    type: 'organizational',
    category: 'Data Governance',
    description: 'Incomplete data classification and labeling',
    severity: 'medium',
    exploitability: 'low',
    relatedThreats: ['THREAT-001'],
    remediationEffort: 'high',
    status: 'analyzing'
  },
  {
    id: 'VULN-003',
    assetId: 'ASSET-002',
    type: 'technical',
    category: 'Change Management',
    description: 'Manual deployment processes prone to human error',
    severity: 'medium',
    exploitability: 'high',
    relatedThreats: ['THREAT-002'],
    remediationEffort: 'medium',
    status: 'mitigating'
  },
  {
    id: 'VULN-004',
    assetId: 'ASSET-003',
    type: 'technical',
    category: 'Infrastructure',
    description: 'Limited auto-scaling capacity for traffic surges',
    severity: 'medium',
    exploitability: 'medium',
    relatedThreats: ['THREAT-003'],
    remediationEffort: 'medium',
    status: 'identified'
  },
  {
    id: 'VULN-005',
    assetId: 'ASSET-004',
    type: 'organizational',
    category: 'Third-party Management',
    description: 'Insufficient visibility into vendor security practices',
    severity: 'high',
    exploitability: 'low',
    relatedThreats: ['THREAT-004'],
    remediationEffort: 'high',
    status: 'analyzing'
  },
  {
    id: 'VULN-006',
    assetId: 'ASSET-005',
    type: 'technical',
    category: 'Data Protection',
    description: 'Model artifacts not encrypted in development environments',
    severity: 'medium',
    exploitability: 'medium',
    relatedThreats: ['THREAT-005'],
    remediationEffort: 'low',
    status: 'mitigating'
  },
  {
    id: 'VULN-007',
    assetId: 'ASSET-006',
    type: 'organizational',
    category: 'Training',
    description: 'Inconsistent security awareness across locations',
    severity: 'medium',
    exploitability: 'high',
    relatedThreats: ['THREAT-006'],
    remediationEffort: 'medium',
    status: 'mitigating'
  },
  {
    id: 'VULN-008',
    assetId: 'ASSET-007',
    type: 'technical',
    category: 'Authentication',
    description: 'API keys stored in code repositories',
    severity: 'critical',
    exploitability: 'high',
    relatedThreats: ['THREAT-007'],
    remediationEffort: 'low',
    status: 'mitigated'
  },
  {
    id: 'VULN-009',
    assetId: 'ASSET-008',
    type: 'organizational',
    category: 'Process',
    description: 'Lack of out-of-band verification for high-value transfers',
    severity: 'high',
    exploitability: 'medium',
    relatedThreats: ['THREAT-008'],
    remediationEffort: 'low',
    status: 'mitigating'
  }
];

export const octaveRisks: OctaveRisk[] = [
  {
    id: 'RISK-001',
    assetId: 'ASSET-001',
    threatId: 'THREAT-001',
    vulnerabilityIds: ['VULN-001', 'VULN-002'],
    description: 'Customer database breach through APT exploitation',
    likelihood: 'medium',
    impact: 'severe',
    riskLevel: 'critical',
    strategy: 'mitigate',
    mitigationPlan: 'Implement zero-trust architecture, enhance monitoring, complete data classification',
    residualRisk: 'medium',
    owner: 'Chief Information Security Officer',
    reviewDate: '2024-04-01'
  },
  {
    id: 'RISK-002',
    assetId: 'ASSET-002',
    threatId: 'THREAT-002',
    vulnerabilityIds: ['VULN-003'],
    description: 'Core banking outage due to configuration error',
    likelihood: 'high',
    impact: 'major',
    riskLevel: 'high',
    strategy: 'mitigate',
    mitigationPlan: 'Automate deployments, implement infrastructure as code, enhance testing',
    residualRisk: 'low',
    owner: 'VP of Technology',
    reviewDate: '2024-03-15'
  },
  {
    id: 'RISK-003',
    assetId: 'ASSET-003',
    threatId: 'THREAT-003',
    vulnerabilityIds: ['VULN-004'],
    description: 'Mobile banking DDoS causing service unavailability',
    likelihood: 'medium',
    impact: 'moderate',
    riskLevel: 'medium',
    strategy: 'mitigate',
    mitigationPlan: 'Enhance CDN capabilities, implement surge capacity, create incident playbooks',
    residualRisk: 'low',
    owner: 'Head of Digital Banking',
    reviewDate: '2024-03-20'
  },
  {
    id: 'RISK-004',
    assetId: 'ASSET-004',
    threatId: 'THREAT-004',
    vulnerabilityIds: ['VULN-005'],
    description: 'Supply chain attack on payment infrastructure',
    likelihood: 'low',
    impact: 'severe',
    riskLevel: 'high',
    strategy: 'mitigate',
    mitigationPlan: 'Enhance vendor assessments, implement SBOM, increase monitoring',
    residualRisk: 'medium',
    owner: 'Chief Risk Officer',
    reviewDate: '2024-04-15'
  },
  {
    id: 'RISK-005',
    assetId: 'ASSET-005',
    threatId: 'THREAT-005',
    vulnerabilityIds: ['VULN-006'],
    description: 'Insider threat to fraud detection models',
    likelihood: 'medium',
    impact: 'major',
    riskLevel: 'high',
    strategy: 'mitigate',
    mitigationPlan: 'Implement ML security platform, enhance monitoring, encrypt all artifacts',
    residualRisk: 'low',
    owner: 'Chief Data Officer',
    reviewDate: '2024-03-25'
  },
  {
    id: 'RISK-006',
    assetId: 'ASSET-007',
    threatId: 'THREAT-007',
    vulnerabilityIds: ['VULN-008'],
    description: 'API abuse leading to data scraping',
    likelihood: 'high',
    impact: 'moderate',
    riskLevel: 'high',
    strategy: 'mitigate',
    mitigationPlan: 'Implement API security gateway, enhance rate limiting, add behavioral analysis',
    residualRisk: 'low',
    owner: 'Platform Engineering Lead',
    reviewDate: '2024-03-10'
  },
  {
    id: 'RISK-007',
    assetId: 'ASSET-008',
    threatId: 'THREAT-008',
    vulnerabilityIds: ['VULN-009'],
    description: 'Executive impersonation for wire fraud',
    likelihood: 'medium',
    impact: 'severe',
    riskLevel: 'high',
    strategy: 'mitigate',
    mitigationPlan: 'Implement callback procedures, enhance training, deploy PAM solution',
    residualRisk: 'low',
    owner: 'Chief Security Officer',
    reviewDate: '2024-04-05'
  }
];

export const octaveProtectionStrategies: OctaveProtectionStrategy[] = [
  {
    id: 'STRAT-001',
    name: 'Zero Trust Architecture',
    type: 'preventive',
    description: 'Implement zero trust principles across all systems',
    implementation: 'Phase 1: Network segmentation, Phase 2: Identity-based access, Phase 3: Continuous verification',
    coverage: ['ASSET-001', 'ASSET-002', 'ASSET-004', 'ASSET-007'],
    effectiveness: 'high',
    cost: 'high',
    timeframe: '18 months',
    status: 'implementing'
  },
  {
    id: 'STRAT-002',
    name: 'Advanced Threat Detection',
    type: 'detective',
    description: 'Deploy XDR platform with ML-based threat hunting',
    implementation: 'Integrate EDR, NDR, and cloud workload protection with SIEM',
    coverage: ['ASSET-001', 'ASSET-002', 'ASSET-003', 'ASSET-007'],
    effectiveness: 'high',
    cost: 'medium',
    timeframe: '6 months',
    status: 'approved'
  },
  {
    id: 'STRAT-003',
    name: 'Automated Incident Response',
    type: 'corrective',
    description: 'SOAR platform for automated containment and remediation',
    implementation: 'Deploy SOAR, create playbooks, integrate with security tools',
    coverage: ['ASSET-001', 'ASSET-002', 'ASSET-003', 'ASSET-004'],
    effectiveness: 'medium',
    cost: 'medium',
    timeframe: '9 months',
    status: 'proposed'
  },
  {
    id: 'STRAT-004',
    name: 'Security Champions Program',
    type: 'preventive',
    description: 'Embed security expertise in development teams',
    implementation: 'Train developers, establish secure coding practices, regular assessments',
    coverage: ['ASSET-002', 'ASSET-003', 'ASSET-007'],
    effectiveness: 'medium',
    cost: 'low',
    timeframe: '12 months',
    status: 'operational'
  },
  {
    id: 'STRAT-005',
    name: 'Privileged Access Management',
    type: 'preventive',
    description: 'Centralized PAM solution for all privileged accounts',
    implementation: 'Deploy PAM, migrate privileged accounts, implement just-in-time access',
    coverage: ['ASSET-001', 'ASSET-002', 'ASSET-008'],
    effectiveness: 'high',
    cost: 'medium',
    timeframe: '6 months',
    status: 'implementing'
  }
];

// Helper functions
export const getAssetById = (id: string) => 
  octaveAssets.find(asset => asset.id === id);

export const getThreatsByAsset = (assetId: string) =>
  octaveThreats.filter(threat => threat.assetId === assetId);

export const getVulnerabilitiesByAsset = (assetId: string) =>
  octaveVulnerabilities.filter(vuln => vuln.assetId === assetId);

export const getRisksByAsset = (assetId: string) =>
  octaveRisks.filter(risk => risk.assetId === assetId);

export const getCriticalRisks = () =>
  octaveRisks.filter(risk => risk.riskLevel === 'critical');

export const getHighValueAssets = () =>
  octaveAssets.filter(asset => asset.criticality === 'critical' || asset.criticality === 'high');

export const getThreatById = (id: string) =>
  octaveThreats.find(threat => threat.id === id);

export const getVulnerabilityById = (id: string) =>
  octaveVulnerabilities.find(vuln => vuln.id === id);

export const getStrategiesByAsset = (assetId: string) =>
  octaveProtectionStrategies.filter(strategy => strategy.coverage.includes(assetId));

// Risk calculation helpers
export const calculateOverallRisk = (probability: string, impact: any): string => {
  const probScore = ['very-low', 'low', 'medium', 'high', 'very-high'].indexOf(probability);
  const impactScore = Math.max(impact.financial, impact.reputation, impact.compliance);
  
  if (probScore >= 3 || impactScore >= 4) return 'critical';
  if (probScore >= 2 || impactScore >= 3) return 'high';
  if (probScore >= 1 || impactScore >= 2) return 'medium';
  return 'low';
};

export const riskMatrix = {
  likelihood: ['very-low', 'low', 'medium', 'high', 'very-high'],
  impact: ['negligible', 'minor', 'moderate', 'major', 'severe'],
  getRiskLevel: (likelihood: string, impact: string): string => {
    const likelihoodIndex = riskMatrix.likelihood.indexOf(likelihood);
    const impactIndex = riskMatrix.impact.indexOf(impact);
    
    if (likelihoodIndex >= 3 && impactIndex >= 3) return 'critical';
    if (likelihoodIndex >= 2 || impactIndex >= 3) return 'high';
    if (likelihoodIndex >= 1 || impactIndex >= 2) return 'medium';
    return 'low';
  }
};