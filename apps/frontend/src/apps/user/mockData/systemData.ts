// System description and stakeholder data for STPA-Sec Step 1

export interface SystemDescription {
  id: string;
  name: string;
  missionStatement: {
    purpose: string;
    method: string;
    goals: string[];
    constraints: string[];
  };
  fullDescription: string;
  boundaries: {
    included: string[];
    excluded: string[];
  };
  assumptions: string[];
  context: string;
  lastUpdated: Date;
}

export interface Stakeholder {
  id: string;
  name: string;
  role: string;
  type: 'primary' | 'secondary' | 'adversary';
  interests: string[];
  securityConcerns: string[];
  influenceLevel: 'high' | 'medium' | 'low';
  accessLevel: string;
  responsibilities: string[];
}

export const systemDescription: SystemDescription = {
  id: 'SYS-001',
  name: 'Digital Banking Platform',
  missionStatement: {
    purpose: 'enable secure financial transactions',
    method: 'providing digital banking services through web and mobile applications',
    goals: [
      'Process customer transactions accurately and timely',
      'Protect customer financial data and privacy',
      'Maintain regulatory compliance',
      'Provide 24/7 service availability'
    ],
    constraints: [
      'Must comply with PCI-DSS standards',
      'Must implement strong customer authentication (SCA)',
      'Must maintain audit trails for all transactions',
      'Must protect against money laundering (AML requirements)',
      'Must ensure data residency compliance'
    ]
  },
  fullDescription: `A system to enable secure financial transactions by means of providing digital banking services through web and mobile applications in order to process customer transactions accurately and timely, protect customer financial data and privacy, maintain regulatory compliance, and provide 24/7 service availability, while complying with PCI-DSS standards, implementing strong customer authentication, maintaining audit trails, protecting against money laundering, and ensuring data residency compliance.

The Digital Banking Platform consists of:
- Customer-facing web and mobile applications
- Core banking APIs and microservices
- Transaction processing engine
- Authentication and authorization services
- Payment gateway integrations
- Account management system
- Fraud detection and prevention system
- Data analytics and reporting engine
- Customer support interfaces`,
  boundaries: {
    included: [
      'Web application frontend',
      'Mobile applications (iOS/Android)',
      'API gateway and microservices',
      'Authentication service (including MFA)',
      'Core banking database',
      'Transaction processing engine',
      'Fraud detection system',
      'Audit logging service',
      'Internal admin interfaces'
    ],
    excluded: [
      'Third-party payment processors',
      'External credit bureaus',
      'Customer devices',
      'Internet infrastructure',
      'Physical bank branches',
      'ATM networks',
      'SWIFT network',
      'Partner bank systems'
    ]
  },
  assumptions: [
    'Customers have secure devices with updated software',
    'Network communications use TLS 1.3 or higher',
    'Third-party services maintain their own security',
    'Regulatory requirements remain relatively stable',
    'Employees follow security policies and procedures',
    'Physical data centers have adequate security controls'
  ],
  context: 'Operating in a highly regulated financial environment with sophisticated threat actors including organized crime, nation-states, and insider threats. The system processes millions of transactions daily with zero tolerance for financial loss or data breaches.',
  lastUpdated: new Date('2024-01-15')
};

export const stakeholders: Stakeholder[] = [
  {
    id: 'STK-001',
    name: 'Banking Customers',
    role: 'End users of the banking platform',
    type: 'primary',
    interests: [
      'Access to funds and account information',
      'Transaction processing',
      'Privacy and data protection',
      'Service availability',
      'Low fees and good user experience'
    ],
    securityConcerns: [
      'Unauthorized access to accounts',
      'Financial fraud and theft',
      'Identity theft',
      'Privacy breaches',
      'Service disruptions'
    ],
    influenceLevel: 'high',
    accessLevel: 'Authenticated access to own accounts only',
    responsibilities: [
      'Protect login credentials',
      'Report suspicious activity',
      'Keep contact information updated',
      'Use secure devices and networks'
    ]
  },
  {
    id: 'STK-002',
    name: 'Bank Operations Team',
    role: 'Internal staff managing daily operations',
    type: 'primary',
    interests: [
      'System stability and performance',
      'Operational efficiency',
      'Compliance with procedures',
      'Incident resolution',
      'Clear reporting and metrics'
    ],
    securityConcerns: [
      'Insider threats',
      'Operational errors leading to vulnerabilities',
      'Social engineering attacks',
      'Privilege escalation',
      'Data leakage'
    ],
    influenceLevel: 'high',
    accessLevel: 'Privileged access to operational systems',
    responsibilities: [
      'Monitor system health',
      'Respond to incidents',
      'Maintain service levels',
      'Follow security procedures',
      'Report anomalies'
    ]
  },
  {
    id: 'STK-003',
    name: 'Security Operations Center (SOC)',
    role: 'Security monitoring and incident response',
    type: 'primary',
    interests: [
      'Threat detection and prevention',
      'Incident response capability',
      'Security posture improvement',
      'Compliance verification',
      'Threat intelligence'
    ],
    securityConcerns: [
      'Advanced persistent threats',
      'Zero-day exploits',
      'Coordinated attacks',
      'Alert fatigue',
      'False positives'
    ],
    influenceLevel: 'high',
    accessLevel: 'Read access to all logs, limited write access',
    responsibilities: [
      'Monitor security events 24/7',
      'Investigate alerts',
      'Coordinate incident response',
      'Maintain security tools',
      'Produce threat reports'
    ]
  },
  {
    id: 'STK-004',
    name: 'Regulatory Bodies',
    role: 'Financial regulators and compliance auditors',
    type: 'secondary',
    interests: [
      'Regulatory compliance',
      'Consumer protection',
      'Financial system stability',
      'Anti-money laundering',
      'Data protection compliance'
    ],
    securityConcerns: [
      'Compliance violations',
      'Inadequate controls',
      'Audit trail tampering',
      'Data sovereignty issues',
      'Systemic risks'
    ],
    influenceLevel: 'high',
    accessLevel: 'Audit access to compliance data',
    responsibilities: [
      'Define regulations',
      'Conduct audits',
      'Impose penalties',
      'Issue guidance',
      'Investigate violations'
    ]
  },
  {
    id: 'STK-005',
    name: 'Third-Party Service Providers',
    role: 'External vendors and partners',
    type: 'secondary',
    interests: [
      'Service integration',
      'API reliability',
      'Business continuity',
      'Contract compliance',
      'Revenue from services'
    ],
    securityConcerns: [
      'Supply chain attacks',
      'API vulnerabilities',
      'Data exposure',
      'Service dependencies',
      'Vendor lock-in risks'
    ],
    influenceLevel: 'medium',
    accessLevel: 'Limited API access with specific scopes',
    responsibilities: [
      'Maintain service security',
      'Provide secure APIs',
      'Report security incidents',
      'Comply with agreements',
      'Protect shared data'
    ]
  },
  {
    id: 'STK-006',
    name: 'Organized Cybercriminals',
    role: 'Sophisticated threat actors seeking financial gain',
    type: 'adversary',
    interests: [
      'Financial theft',
      'Data theft for resale',
      'Ransomware deployment',
      'Money laundering',
      'Cryptojacking'
    ],
    securityConcerns: [
      'Detection and attribution',
      'Law enforcement action',
      'Defensive improvements',
      'Honeypots and deception',
      'Loss of infrastructure'
    ],
    influenceLevel: 'high',
    accessLevel: 'Attempting unauthorized access',
    responsibilities: [] // Adversaries don't have legitimate responsibilities
  },
  {
    id: 'STK-007',
    name: 'Nation-State Actors',
    role: 'State-sponsored groups with strategic objectives',
    type: 'adversary',
    interests: [
      'Economic espionage',
      'Disruption of financial systems',
      'Intelligence gathering',
      'Strategic advantage',
      'Testing cyber capabilities'
    ],
    securityConcerns: [
      'Attribution',
      'Diplomatic consequences',
      'Escalation',
      'Exposure of techniques',
      'Retaliation'
    ],
    influenceLevel: 'high',
    accessLevel: 'Attempting persistent unauthorized access',
    responsibilities: []
  },
  {
    id: 'STK-008',
    name: 'Malicious Insiders',
    role: 'Employees or contractors with malicious intent',
    type: 'adversary',
    interests: [
      'Financial gain',
      'Revenge or grievance',
      'Selling access or data',
      'Sabotage',
      'Espionage'
    ],
    securityConcerns: [
      'Detection by monitoring',
      'Access revocation',
      'Legal consequences',
      'Behavioral analytics',
      'Segregation of duties'
    ],
    influenceLevel: 'medium',
    accessLevel: 'Legitimate access being abused',
    responsibilities: []
  }
];

// Helper functions
export function getStakeholdersByType(type: 'primary' | 'secondary' | 'adversary') {
  return stakeholders.filter(s => s.type === type);
}

export function getMissionStatementString(mission: SystemDescription['missionStatement']) {
  return `A system to ${mission.purpose} by means of ${mission.method} in order to ${mission.goals.join(', ')}, while ${mission.constraints.join(', ')}.`;
}