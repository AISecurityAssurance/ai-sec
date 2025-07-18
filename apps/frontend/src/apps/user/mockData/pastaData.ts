// PASTA (Process for Attack Simulation and Threat Analysis) mock data

export interface BusinessObjective {
  id: string;
  objective: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  impactArea: string;
  relatedAssets: string[];
}

export interface TechnicalScope {
  id: string;
  component: string;
  technology: string;
  interfaces: string[];
  dependencies: string[];
}

export interface ThreatActor {
  id: string;
  name: string;
  motivation: string;
  capability: 'nation-state' | 'organized-crime' | 'hacktivist' | 'insider' | 'opportunist';
  targetedAssets: string[];
  ttps: string[]; // Tactics, Techniques, and Procedures
}

export interface AttackScenario {
  id: string;
  name: string;
  description: string;
  threatActor: string;
  attackVector: string;
  vulnerability: string;
  impact: string;
  likelihood: 'very-high' | 'high' | 'medium' | 'low' | 'very-low';
  risk: 'critical' | 'high' | 'medium' | 'low';
}

export interface RiskAssessment {
  id: string;
  scenario: string;
  businessImpact: number; // 1-5 scale
  technicalImpact: number; // 1-5 scale
  likelihood: number; // 1-5 scale
  overallRisk: number; // calculated
  treatment: 'mitigate' | 'accept' | 'transfer' | 'avoid';
  mitigation?: string;
}

// Stage 1: Define Business Objectives
export const businessObjectives: BusinessObjective[] = [
  {
    id: 'BO-001',
    objective: 'Maintain 99.9% availability for online banking services',
    priority: 'critical',
    impactArea: 'Service Availability',
    relatedAssets: ['Web Application', 'API Gateway', 'Core Banking System']
  },
  {
    id: 'BO-002',
    objective: 'Protect customer financial data from unauthorized access',
    priority: 'critical',
    impactArea: 'Data Protection',
    relatedAssets: ['Customer Database', 'Transaction Processing', 'Authentication Service']
  },
  {
    id: 'BO-003',
    objective: 'Ensure compliance with PCI-DSS and financial regulations',
    priority: 'high',
    impactArea: 'Regulatory Compliance',
    relatedAssets: ['Payment Processing', 'Audit Logs', 'Data Storage']
  },
  {
    id: 'BO-004',
    objective: 'Prevent fraudulent transactions and money laundering',
    priority: 'critical',
    impactArea: 'Fraud Prevention',
    relatedAssets: ['Fraud Detection System', 'Transaction Monitoring', 'KYC System']
  }
];

// Stage 2: Define Technical Scope
export const technicalScope: TechnicalScope[] = [
  {
    id: 'TS-001',
    component: 'Web Application Frontend',
    technology: 'React/TypeScript',
    interfaces: ['REST API', 'WebSocket', 'OAuth2'],
    dependencies: ['CDN', 'API Gateway', 'Auth Service']
  },
  {
    id: 'TS-002',
    component: 'API Gateway',
    technology: 'Kong/Nginx',
    interfaces: ['HTTPS', 'mTLS', 'JWT'],
    dependencies: ['Load Balancer', 'Microservices', 'WAF']
  },
  {
    id: 'TS-003',
    component: 'Authentication Service',
    technology: 'OAuth2/OIDC',
    interfaces: ['SAML', 'MFA', 'Biometric'],
    dependencies: ['User Database', 'Token Store', 'HSM']
  },
  {
    id: 'TS-004',
    component: 'Core Banking Database',
    technology: 'PostgreSQL Cluster',
    interfaces: ['SQL', 'Encrypted Connections'],
    dependencies: ['Backup System', 'Replication', 'Key Management']
  }
];

// Stage 4: Threat Analysis
export const threatActors: ThreatActor[] = [
  {
    id: 'TA-001',
    name: 'APT Financial Group',
    motivation: 'Financial gain and data theft',
    capability: 'nation-state',
    targetedAssets: ['Customer Database', 'Transaction System', 'SWIFT Interface'],
    ttps: ['Spear phishing', 'Supply chain attacks', 'Zero-day exploits', 'Lateral movement']
  },
  {
    id: 'TA-002',
    name: 'Ransomware Operators',
    motivation: 'Ransom payments',
    capability: 'organized-crime',
    targetedAssets: ['Database Servers', 'Backup Systems', 'File Shares'],
    ttps: ['RaaS deployment', 'Data encryption', 'Double extortion', 'Backup deletion']
  },
  {
    id: 'TA-003',
    name: 'Malicious Insider',
    motivation: 'Revenge or financial gain',
    capability: 'insider',
    targetedAssets: ['Customer Data', 'Admin Credentials', 'Source Code'],
    ttps: ['Privilege abuse', 'Data exfiltration', 'Logic bombs', 'Credential theft']
  },
  {
    id: 'TA-004',
    name: 'Hacktivist Groups',
    motivation: 'Ideological or publicity',
    capability: 'hacktivist',
    targetedAssets: ['Public Website', 'Customer Portal', 'Social Media'],
    ttps: ['DDoS attacks', 'Website defacement', 'Data leaks', 'Social engineering']
  }
];

// Stage 6: Attack Modeling
export const attackScenarios: AttackScenario[] = [
  {
    id: 'AS-001',
    name: 'Supply Chain Compromise via Third-Party Integration',
    description: 'Attackers compromise a third-party payment processor to inject malicious code',
    threatActor: 'TA-001',
    attackVector: 'Third-party API integration',
    vulnerability: 'Insufficient vendor security assessment',
    impact: 'Customer payment data theft and financial fraud',
    likelihood: 'medium',
    risk: 'critical'
  },
  {
    id: 'AS-002',
    name: 'Ransomware Attack on Core Banking Systems',
    description: 'Ransomware deployed through phishing email to encrypt critical databases',
    threatActor: 'TA-002',
    attackVector: 'Phishing email with malicious attachment',
    vulnerability: 'Lack of email filtering and user awareness',
    impact: 'Complete service outage and data loss',
    likelihood: 'high',
    risk: 'critical'
  },
  {
    id: 'AS-003',
    name: 'Insider Data Exfiltration',
    description: 'Database administrator exports customer data for sale on dark web',
    threatActor: 'TA-003',
    attackVector: 'Privileged access abuse',
    vulnerability: 'Insufficient access controls and monitoring',
    impact: 'Mass customer data breach and regulatory fines',
    likelihood: 'medium',
    risk: 'high'
  },
  {
    id: 'AS-004',
    name: 'API Abuse for Account Takeover',
    description: 'Automated bot attacks exploit API rate limiting weakness',
    threatActor: 'TA-004',
    attackVector: 'API endpoint abuse',
    vulnerability: 'Weak rate limiting and bot detection',
    impact: 'Multiple customer account compromises',
    likelihood: 'high',
    risk: 'high'
  },
  {
    id: 'AS-005',
    name: 'MFA Bypass via SIM Swapping',
    description: 'Attackers perform SIM swap to bypass SMS-based MFA',
    threatActor: 'TA-001',
    attackVector: 'Social engineering of mobile carrier',
    vulnerability: 'Reliance on SMS for MFA',
    impact: 'High-value account takeovers',
    likelihood: 'medium',
    risk: 'high'
  }
];

// Stage 7: Risk and Impact Analysis
export const riskAssessments: RiskAssessment[] = [
  {
    id: 'RA-001',
    scenario: 'AS-001',
    businessImpact: 5,
    technicalImpact: 4,
    likelihood: 3,
    overallRisk: 12, // B*T*L / 5 = 12
    treatment: 'mitigate',
    mitigation: 'Implement vendor security assessment program and continuous monitoring'
  },
  {
    id: 'RA-002',
    scenario: 'AS-002',
    businessImpact: 5,
    technicalImpact: 5,
    likelihood: 4,
    overallRisk: 20,
    treatment: 'mitigate',
    mitigation: 'Deploy EDR, improve backups, and conduct security awareness training'
  },
  {
    id: 'RA-003',
    scenario: 'AS-003',
    businessImpact: 4,
    technicalImpact: 3,
    likelihood: 3,
    overallRisk: 7.2,
    treatment: 'mitigate',
    mitigation: 'Implement PAM, database activity monitoring, and separation of duties'
  },
  {
    id: 'RA-004',
    scenario: 'AS-004',
    businessImpact: 3,
    technicalImpact: 3,
    likelihood: 4,
    overallRisk: 7.2,
    treatment: 'mitigate',
    mitigation: 'Deploy advanced bot protection and implement adaptive rate limiting'
  },
  {
    id: 'RA-005',
    scenario: 'AS-005',
    businessImpact: 4,
    technicalImpact: 2,
    likelihood: 3,
    overallRisk: 4.8,
    treatment: 'mitigate',
    mitigation: 'Move to app-based MFA and implement risk-based authentication'
  }
];

// Helper functions
export function getScenariosByThreatActor(actorId: string) {
  return attackScenarios.filter(s => s.threatActor === actorId);
}

export function getRiskAssessmentByScenario(scenarioId: string) {
  return riskAssessments.find(r => r.scenario === scenarioId);
}

export function getCriticalRisks() {
  return attackScenarios.filter(s => s.risk === 'critical');
}

export function getHighPriorityObjectives() {
  return businessObjectives.filter(o => o.priority === 'critical' || o.priority === 'high');
}