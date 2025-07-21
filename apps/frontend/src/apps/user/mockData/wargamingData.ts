export interface WargamingScenario {
  id: string;
  name: string;
  type: 'red-team' | 'blue-team' | 'purple-team' | 'tabletop';
  description: string;
  objectives: string[];
  scope: string[];
  participants: string[];
  duration: string;
  tactics?: string[];
  defenses?: string[];
  findings?: string[];
  improvements?: string[];
}

export const redTeamScenarios: WargamingScenario[] = [
  {
    id: 'RT1',
    name: 'APT Campaign Simulation',
    type: 'red-team',
    description: 'Simulate a nation-state APT targeting customer financial data',
    objectives: [
      'Test detection capabilities against advanced threats',
      'Evaluate incident response procedures',
      'Identify gaps in security monitoring',
      'Assess data exfiltration prevention'
    ],
    scope: [
      'External network penetration',
      'Phishing campaigns',
      'Lateral movement',
      'Data exfiltration attempts'
    ],
    participants: ['External Red Team', 'SOC Team', 'Incident Response Team'],
    duration: '3 weeks',
    tactics: [
      'Spear phishing with custom implants',
      'Living off the land techniques',
      'Domain controller targeting',
      'Encrypted C2 channels'
    ],
    findings: [
      'Email filtering missed 30% of phishing attempts',
      'Lateral movement detected after 5 days',
      'Insufficient PowerShell logging',
      'Data loss prevention gaps identified'
    ]
  },
  {
    id: 'RT2',
    name: 'Insider Threat Exercise',
    type: 'red-team',
    description: 'Simulate malicious insider with database administrator privileges',
    objectives: [
      'Test privileged access management controls',
      'Evaluate data access monitoring',
      'Assess insider threat detection',
      'Validate separation of duties'
    ],
    scope: [
      'Database access abuse',
      'Privilege escalation attempts',
      'Data exfiltration via approved channels',
      'Log manipulation'
    ],
    participants: ['Internal Security Team', 'Database Team', 'Compliance'],
    duration: '2 weeks',
    tactics: [
      'Gradual data collection',
      'Use of legitimate tools',
      'Business hours activity only',
      'Small batch exfiltration'
    ],
    findings: [
      'Bulk data exports not flagged',
      'Database activity monitoring gaps',
      'Weak segregation of duties',
      'Insufficient behavioral analytics'
    ]
  },
  {
    id: 'RT3',
    name: 'Ransomware Attack Simulation',
    type: 'red-team',
    description: 'Test defenses against modern ransomware tactics',
    objectives: [
      'Evaluate ransomware prevention controls',
      'Test backup and recovery procedures',
      'Assess network segmentation',
      'Validate incident response playbooks'
    ],
    scope: [
      'Initial compromise vectors',
      'Ransomware deployment',
      'Backup targeting',
      'Recovery processes'
    ],
    participants: ['Red Team', 'IT Operations', 'Business Continuity Team'],
    duration: '1 week',
    tactics: [
      'Supply chain compromise scenario',
      'RDP brute force',
      'PSExec deployment',
      'Shadow copy deletion'
    ],
    findings: [
      'Network segmentation prevented lateral spread',
      'Offline backups successfully protected',
      'Detection occurred within 2 hours',
      'Recovery time exceeded RTO by 50%'
    ]
  }
];

export const blueTeamScenarios: WargamingScenario[] = [
  {
    id: 'BT1',
    name: 'Incident Response Tabletop',
    type: 'blue-team',
    description: 'Walk through response to major data breach scenario',
    objectives: [
      'Test incident response procedures',
      'Evaluate communication protocols',
      'Assess decision-making processes',
      'Identify resource gaps'
    ],
    scope: [
      'Initial detection and triage',
      'Containment strategies',
      'Evidence collection',
      'Communication procedures'
    ],
    participants: ['SOC', 'IR Team', 'Legal', 'PR', 'Executive Team'],
    duration: '4 hours',
    defenses: [
      'SIEM correlation rules',
      'EDR automated response',
      'Network isolation procedures',
      'Forensic collection tools'
    ],
    improvements: [
      'Need executive communication templates',
      'Automate containment procedures',
      'Improve evidence chain of custody',
      'Enhance external communication plan'
    ]
  },
  {
    id: 'BT2',
    name: 'DDoS Defense Exercise',
    type: 'blue-team',
    description: 'Test response to large-scale DDoS attack',
    objectives: [
      'Validate DDoS mitigation services',
      'Test traffic analysis capabilities',
      'Assess service failover procedures',
      'Evaluate customer communication'
    ],
    scope: [
      'Attack detection and classification',
      'Mitigation service activation',
      'Service continuity measures',
      'Stakeholder communication'
    ],
    participants: ['Network Team', 'SOC', 'DDoS Service Provider', 'Customer Service'],
    duration: '2 hours',
    defenses: [
      'Traffic scrubbing services',
      'Rate limiting rules',
      'Geographic blocking',
      'CDN absorption'
    ],
    improvements: [
      'Reduce mitigation activation time',
      'Improve attack classification accuracy',
      'Enhance customer status page',
      'Automate traffic rerouting'
    ]
  }
];

export const purpleTeamScenarios: WargamingScenario[] = [
  {
    id: 'PT1',
    name: 'Authentication Bypass Workshop',
    type: 'purple-team',
    description: 'Collaborative exercise to improve authentication security',
    objectives: [
      'Identify authentication weaknesses',
      'Develop detection strategies',
      'Implement security improvements',
      'Knowledge transfer between teams'
    ],
    scope: [
      'MFA bypass techniques',
      'Session hijacking',
      'Password attack methods',
      'Federation vulnerabilities'
    ],
    participants: ['Red Team', 'Blue Team', 'Identity Team', 'Development Team'],
    duration: '3 days',
    tactics: [
      'MFA fatigue attacks',
      'Session token manipulation',
      'Password spraying',
      'SAML assertion attacks'
    ],
    defenses: [
      'Adaptive authentication',
      'Impossible travel detection',
      'Session anomaly monitoring',
      'Risk-based authentication'
    ],
    improvements: [
      'Implement number matching for MFA',
      'Deploy impossible travel alerts',
      'Enhance session monitoring',
      'Add risk scoring to auth flow'
    ]
  },
  {
    id: 'PT2',
    name: 'Cloud Security Assessment',
    type: 'purple-team',
    description: 'Joint assessment of cloud infrastructure security',
    objectives: [
      'Evaluate cloud security posture',
      'Test cloud-native detection',
      'Improve cloud IR procedures',
      'Develop cloud security metrics'
    ],
    scope: [
      'IAM configuration review',
      'Storage bucket security',
      'Network security controls',
      'Workload protection'
    ],
    participants: ['Cloud Team', 'Security Team', 'DevOps', 'Compliance'],
    duration: '1 week',
    tactics: [
      'Misconfiguration exploitation',
      'Credential compromise',
      'Resource enumeration',
      'Data exfiltration paths'
    ],
    defenses: [
      'Cloud security posture management',
      'Identity governance',
      'Network micro-segmentation',
      'Data loss prevention'
    ],
    improvements: [
      'Implement CSPM tooling',
      'Enhance least privilege model',
      'Deploy cloud workload protection',
      'Improve secret management'
    ]
  }
];

export const tabletopScenarios: WargamingScenario[] = [
  {
    id: 'TT1',
    name: 'Supply Chain Compromise',
    type: 'tabletop',
    description: 'Strategic exercise on responding to third-party breach',
    objectives: [
      'Test vendor risk procedures',
      'Evaluate supply chain visibility',
      'Assess third-party communication',
      'Review contractual obligations'
    ],
    scope: [
      'Vendor breach notification',
      'Impact assessment',
      'Customer notification decisions',
      'Remediation strategies'
    ],
    participants: ['CISO', 'Legal', 'Vendor Management', 'Risk Management', 'PR'],
    duration: '3 hours',
    findings: [
      'Need better vendor inventory',
      'Unclear notification thresholds',
      'Gaps in vendor security requirements',
      'Insufficient vendor monitoring'
    ],
    improvements: [
      'Implement vendor risk scoring',
      'Standardize security requirements',
      'Enhance continuous monitoring',
      'Develop notification playbooks'
    ]
  },
  {
    id: 'TT2',
    name: 'Regulatory Investigation Response',
    type: 'tabletop',
    description: 'Practice responding to regulatory security audit',
    objectives: [
      'Test regulatory response procedures',
      'Evaluate evidence collection',
      'Assess documentation quality',
      'Review communication protocols'
    ],
    scope: [
      'Initial regulatory contact',
      'Document production',
      'Interview preparation',
      'Remediation planning'
    ],
    participants: ['Legal', 'Compliance', 'Security', 'IT', 'Executive Team'],
    duration: '4 hours',
    findings: [
      'Documentation gaps identified',
      'Need litigation hold procedures',
      'Unclear escalation paths',
      'Evidence collection delays'
    ],
    improvements: [
      'Improve security documentation',
      'Implement legal hold automation',
      'Define clear RACI matrix',
      'Create evidence collection runbooks'
    ]
  }
];

export const allWargamingScenarios = [
  ...redTeamScenarios,
  ...blueTeamScenarios,
  ...purpleTeamScenarios,
  ...tabletopScenarios
];