// Additional PASTA data for complete 7-stage implementation

// Stage 3: Application Decomposition
export interface ApplicationComponent {
  id: string;
  name: string;
  type: 'frontend' | 'backend' | 'database' | 'infrastructure' | 'external';
  dataFlows: DataFlow[];
  trustBoundaries: string[];
  assets: string[];
}

export interface DataFlow {
  from: string;
  to: string;
  data: string;
  protocol: string;
  authentication: string;
  encryption: boolean;
}

export const applicationComponents: ApplicationComponent[] = [
  {
    id: 'AC-001',
    name: 'Customer Web Portal',
    type: 'frontend',
    dataFlows: [
      { from: 'Browser', to: 'CDN', data: 'Static Assets', protocol: 'HTTPS', authentication: 'None', encryption: true },
      { from: 'Browser', to: 'API Gateway', data: 'User Requests', protocol: 'HTTPS', authentication: 'JWT', encryption: true }
    ],
    trustBoundaries: ['Internet', 'DMZ'],
    assets: ['Customer PII', 'Session Tokens', 'Transaction Data']
  },
  {
    id: 'AC-002',
    name: 'API Gateway',
    type: 'infrastructure',
    dataFlows: [
      { from: 'Web Portal', to: 'Auth Service', data: 'Auth Requests', protocol: 'HTTPS', authentication: 'mTLS', encryption: true },
      { from: 'Mobile App', to: 'Transaction Service', data: 'Transactions', protocol: 'HTTPS', authentication: 'OAuth2', encryption: true }
    ],
    trustBoundaries: ['DMZ', 'Internal Network'],
    assets: ['API Keys', 'Rate Limit Rules', 'Routing Configuration']
  },
  {
    id: 'AC-003',
    name: 'Transaction Processing Engine',
    type: 'backend',
    dataFlows: [
      { from: 'API Gateway', to: 'Core Banking', data: 'Transaction Requests', protocol: 'HTTPS', authentication: 'Certificate', encryption: true },
      { from: 'Fraud Detection', to: 'Transaction DB', data: 'Risk Scores', protocol: 'TCP', authentication: 'Service Account', encryption: true }
    ],
    trustBoundaries: ['Internal Network', 'Secure Zone'],
    assets: ['Transaction Logic', 'Business Rules', 'Transaction History']
  },
  {
    id: 'AC-004',
    name: 'Customer Database',
    type: 'database',
    dataFlows: [
      { from: 'Auth Service', to: 'DB Cluster', data: 'User Queries', protocol: 'PostgreSQL', authentication: 'Certificate', encryption: true },
      { from: 'Backup Service', to: 'Backup Storage', data: 'Database Dumps', protocol: 'SSH', authentication: 'Key-based', encryption: true }
    ],
    trustBoundaries: ['Secure Zone'],
    assets: ['Customer Data', 'Account Information', 'Transaction Records']
  }
];

// Stage 5: Vulnerability & Weakness Analysis
export interface Vulnerability {
  id: string;
  component: string;
  category: 'design' | 'implementation' | 'configuration' | 'operational';
  description: string;
  cwe: string;
  cvss: number;
  exploitability: 'low' | 'medium' | 'high';
  remediation: string;
  status: 'open' | 'in-progress' | 'remediated' | 'accepted';
}

export const vulnerabilities: Vulnerability[] = [
  {
    id: 'VUL-001',
    component: 'API Gateway',
    category: 'configuration',
    description: 'Insufficient rate limiting on authentication endpoints',
    cwe: 'CWE-307',
    cvss: 7.5,
    exploitability: 'high',
    remediation: 'Implement adaptive rate limiting based on user behavior',
    status: 'open'
  },
  {
    id: 'VUL-002',
    component: 'Web Portal',
    category: 'implementation',
    description: 'Client-side encryption keys stored in localStorage',
    cwe: 'CWE-522',
    cvss: 6.5,
    exploitability: 'medium',
    remediation: 'Use secure key storage mechanisms or server-side encryption',
    status: 'in-progress'
  },
  {
    id: 'VUL-003',
    component: 'Transaction Processing',
    category: 'design',
    description: 'Race condition in concurrent transaction processing',
    cwe: 'CWE-362',
    cvss: 8.1,
    exploitability: 'low',
    remediation: 'Implement distributed locking mechanism',
    status: 'remediated'
  },
  {
    id: 'VUL-004',
    component: 'Customer Database',
    category: 'operational',
    description: 'Database backups not encrypted at rest',
    cwe: 'CWE-311',
    cvss: 7.2,
    exploitability: 'low',
    remediation: 'Enable encryption for all backup storage',
    status: 'open'
  },
  {
    id: 'VUL-005',
    component: 'Authentication Service',
    category: 'design',
    description: 'SMS-based MFA vulnerable to SIM swapping',
    cwe: 'CWE-287',
    cvss: 7.8,
    exploitability: 'medium',
    remediation: 'Migrate to TOTP or FIDO2-based authentication',
    status: 'in-progress'
  }
];

// Attack Trees for Stage 6
export interface AttackTree {
  id: string;
  goal: string;
  root: AttackNode;
}

export interface AttackNode {
  id: string;
  description: string;
  type: 'AND' | 'OR' | 'LEAF';
  probability?: number;
  impact?: number;
  children?: AttackNode[];
}

export const attackTrees: AttackTree[] = [
  {
    id: 'AT-001',
    goal: 'Steal Customer Financial Data',
    root: {
      id: 'node-1',
      description: 'Access Customer Database',
      type: 'OR',
      children: [
        {
          id: 'node-1.1',
          description: 'SQL Injection Attack',
          type: 'AND',
          children: [
            {
              id: 'node-1.1.1',
              description: 'Find vulnerable endpoint',
              type: 'LEAF',
              probability: 0.7
            },
            {
              id: 'node-1.1.2',
              description: 'Bypass WAF rules',
              type: 'LEAF',
              probability: 0.4
            }
          ]
        },
        {
          id: 'node-1.2',
          description: 'Compromise Admin Account',
          type: 'AND',
          children: [
            {
              id: 'node-1.2.1',
              description: 'Phish admin credentials',
              type: 'LEAF',
              probability: 0.3
            },
            {
              id: 'node-1.2.2',
              description: 'Bypass MFA',
              type: 'LEAF',
              probability: 0.2
            }
          ]
        }
      ]
    }
  }
];

// Threat Intelligence Feeds for Stage 4
export interface ThreatIntelligence {
  id: string;
  source: string;
  date: string;
  ioc: string; // Indicator of Compromise
  threatActor: string;
  relevance: 'low' | 'medium' | 'high';
  description: string;
}

export const threatIntelligence: ThreatIntelligence[] = [
  {
    id: 'TI-001',
    source: 'Financial ISAC',
    date: '2024-01-15',
    ioc: '185.220.101.45',
    threatActor: 'TA-001',
    relevance: 'high',
    description: 'APT group targeting banking APIs with custom malware'
  },
  {
    id: 'TI-002',
    source: 'CISA Alert',
    date: '2024-01-20',
    ioc: 'evilbank.phishing.com',
    threatActor: 'TA-004',
    relevance: 'medium',
    description: 'Phishing campaign mimicking major banks'
  },
  {
    id: 'TI-003',
    source: 'Vendor Advisory',
    date: '2024-01-22',
    ioc: 'CVE-2024-1234',
    threatActor: 'Multiple',
    relevance: 'high',
    description: 'Critical vulnerability in authentication framework'
  }
];

// Risk Heat Map Data for Stage 7
export interface RiskHeatMap {
  component: string;
  risks: {
    confidentiality: number;
    integrity: number;
    availability: number;
    overall: number;
  };
}

export const riskHeatMap: RiskHeatMap[] = [
  {
    component: 'Customer Database',
    risks: { confidentiality: 5, integrity: 4, availability: 3, overall: 4.8 }
  },
  {
    component: 'Transaction Processing',
    risks: { confidentiality: 4, integrity: 5, availability: 4, overall: 4.5 }
  },
  {
    component: 'API Gateway',
    risks: { confidentiality: 3, integrity: 3, availability: 5, overall: 3.8 }
  },
  {
    component: 'Authentication Service',
    risks: { confidentiality: 5, integrity: 4, availability: 4, overall: 4.5 }
  },
  {
    component: 'Web Portal',
    risks: { confidentiality: 3, integrity: 3, availability: 3, overall: 3.0 }
  }
];