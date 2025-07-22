// STRIDE Analysis Mock Data for Modern Digital Banking Platform

export interface StrideThreat {
  id: string;
  component: string;
  threatType: 'Spoofing' | 'Tampering' | 'Repudiation' | 'Information Disclosure' | 'Denial of Service' | 'Elevation of Privilege';
  description: string;
  asset: string;
  attackVector: string;
  likelihood: 'low' | 'medium' | 'high';
  impact: 'low' | 'medium' | 'high';
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  mitigations: string[];
  status: 'identified' | 'mitigating' | 'mitigated' | 'accepted';
}

export const strideThreats: StrideThreat[] = [
  // Spoofing
  {
    id: 'STR-001',
    component: 'Web Banking Portal',
    threatType: 'Spoofing',
    description: 'Attacker creates phishing site mimicking bank login',
    asset: 'Customer Credentials',
    attackVector: 'Social engineering via email/SMS with fake login links',
    likelihood: 'high',
    impact: 'high',
    riskLevel: 'critical',
    mitigations: [
      'Implement FIDO2/WebAuthn for phishing-resistant authentication',
      'Deploy DMARC/SPF/DKIM for email authentication',
      'Regular security awareness training for customers',
      'Browser-based phishing detection'
    ],
    status: 'mitigating'
  },
  {
    id: 'STR-002',
    component: 'Mobile Banking App',
    threatType: 'Spoofing',
    description: 'Malicious app impersonates legitimate banking app',
    asset: 'Customer Trust',
    attackVector: 'Third-party app stores or sideloading',
    likelihood: 'medium',
    impact: 'high',
    riskLevel: 'high',
    mitigations: [
      'App attestation and certificate pinning',
      'Runtime application self-protection (RASP)',
      'Regular monitoring of app stores for fake apps',
      'Customer education on official app sources'
    ],
    status: 'mitigating'
  },
  {
    id: 'STR-003',
    component: 'API Gateway',
    threatType: 'Spoofing',
    description: 'API client spoofing using stolen API keys',
    asset: 'API Access Control',
    attackVector: 'Compromised developer machines or repositories',
    likelihood: 'medium',
    impact: 'medium',
    riskLevel: 'medium',
    mitigations: [
      'Implement OAuth 2.0 with short-lived tokens',
      'API key rotation policies',
      'Mutual TLS for high-value operations',
      'Anomaly detection for API usage patterns'
    ],
    status: 'identified'
  },

  // Tampering
  {
    id: 'STR-004',
    component: 'Transaction Processing System',
    threatType: 'Tampering',
    description: 'Man-in-the-middle attack modifying transaction amounts',
    asset: 'Transaction Integrity',
    attackVector: 'Network interception or compromised intermediary',
    likelihood: 'low',
    impact: 'high',
    riskLevel: 'high',
    mitigations: [
      'End-to-end encryption for all transactions',
      'Digital signatures for transaction authorization',
      'Real-time fraud detection system',
      'Transaction limits and velocity checks'
    ],
    status: 'mitigated'
  },
  {
    id: 'STR-005',
    component: 'Customer Database',
    threatType: 'Tampering',
    description: 'Unauthorized modification of customer account details',
    asset: 'Customer Data Integrity',
    attackVector: 'SQL injection or insider threat',
    likelihood: 'medium',
    impact: 'high',
    riskLevel: 'high',
    mitigations: [
      'Parameterized queries and input validation',
      'Database activity monitoring',
      'Segregation of duties for data modifications',
      'Audit trails with tamper-proof logging'
    ],
    status: 'mitigating'
  },
  {
    id: 'STR-006',
    component: 'Mobile App',
    threatType: 'Tampering',
    description: 'Runtime manipulation of app code or memory',
    asset: 'Application Logic',
    attackVector: 'Jailbroken/rooted devices or debugging tools',
    likelihood: 'medium',
    impact: 'medium',
    riskLevel: 'medium',
    mitigations: [
      'Anti-tampering and obfuscation techniques',
      'Jailbreak/root detection',
      'Code integrity checks',
      'Sensitive operations server-side only'
    ],
    status: 'mitigating'
  },

  // Repudiation
  {
    id: 'STR-007',
    component: 'Payment Gateway',
    threatType: 'Repudiation',
    description: 'Customer denies authorizing legitimate transaction',
    asset: 'Transaction Non-repudiation',
    attackVector: 'Shared credentials or social engineering',
    likelihood: 'medium',
    impact: 'medium',
    riskLevel: 'medium',
    mitigations: [
      'Strong customer authentication (SCA)',
      'Comprehensive audit logging',
      'Transaction confirmation via multiple channels',
      'Biometric authorization for high-value transactions'
    ],
    status: 'mitigated'
  },
  {
    id: 'STR-008',
    component: 'Admin Portal',
    threatType: 'Repudiation',
    description: 'Employee denies making critical configuration changes',
    asset: 'Administrative Accountability',
    attackVector: 'Shared admin accounts or weak access controls',
    likelihood: 'low',
    impact: 'high',
    riskLevel: 'medium',
    mitigations: [
      'Individual admin accounts with MFA',
      'Privileged access management (PAM)',
      'Video recording of admin sessions',
      'Change approval workflow'
    ],
    status: 'mitigating'
  },

  // Information Disclosure
  {
    id: 'STR-009',
    component: 'Web Application',
    threatType: 'Information Disclosure',
    description: 'Sensitive data exposed through error messages',
    asset: 'System Information',
    attackVector: 'Forced errors or edge case inputs',
    likelihood: 'high',
    impact: 'medium',
    riskLevel: 'high',
    mitigations: [
      'Generic error messages for users',
      'Detailed logging server-side only',
      'Security headers implementation',
      'Regular penetration testing'
    ],
    status: 'identified'
  },
  {
    id: 'STR-010',
    component: 'Data Analytics Platform',
    threatType: 'Information Disclosure',
    description: 'Customer PII exposed through analytics dashboards',
    asset: 'Customer Privacy',
    attackVector: 'Insufficient data anonymization or access controls',
    likelihood: 'medium',
    impact: 'high',
    riskLevel: 'high',
    mitigations: [
      'Data anonymization and pseudonymization',
      'Role-based access control for analytics',
      'Privacy-preserving analytics techniques',
      'Regular privacy impact assessments'
    ],
    status: 'mitigating'
  },
  {
    id: 'STR-011',
    component: 'API Endpoints',
    threatType: 'Information Disclosure',
    description: 'Excessive data returned in API responses',
    asset: 'Customer Financial Data',
    attackVector: 'Direct API access or response manipulation',
    likelihood: 'medium',
    impact: 'medium',
    riskLevel: 'medium',
    mitigations: [
      'API response filtering based on permissions',
      'Field-level encryption for sensitive data',
      'API rate limiting and throttling',
      'GraphQL query depth limiting'
    ],
    status: 'identified'
  },

  // Denial of Service
  {
    id: 'STR-012',
    component: 'Online Banking Platform',
    threatType: 'Denial of Service',
    description: 'DDoS attack overwhelming web servers',
    asset: 'Service Availability',
    attackVector: 'Botnet or amplification attacks',
    likelihood: 'high',
    impact: 'high',
    riskLevel: 'critical',
    mitigations: [
      'DDoS mitigation service (CloudFlare, Akamai)',
      'Auto-scaling infrastructure',
      'Geographic load distribution',
      'Rate limiting per user/IP'
    ],
    status: 'mitigated'
  },
  {
    id: 'STR-013',
    component: 'Transaction Processing',
    threatType: 'Denial of Service',
    description: 'Resource exhaustion through complex transactions',
    asset: 'Processing Capacity',
    attackVector: 'Crafted transactions requiring excessive computation',
    likelihood: 'medium',
    impact: 'high',
    riskLevel: 'high',
    mitigations: [
      'Transaction complexity limits',
      'Queue management with priorities',
      'Circuit breakers for downstream services',
      'Horizontal scaling capabilities'
    ],
    status: 'mitigating'
  },

  // Elevation of Privilege
  {
    id: 'STR-014',
    component: 'Customer Portal',
    threatType: 'Elevation of Privilege',
    description: 'Privilege escalation from customer to admin role',
    asset: 'Access Control System',
    attackVector: 'Authorization bypass or JWT manipulation',
    likelihood: 'low',
    impact: 'high',
    riskLevel: 'high',
    mitigations: [
      'Principle of least privilege',
      'Regular permission audits',
      'Signed and encrypted JWTs',
      'Server-side authorization checks'
    ],
    status: 'mitigated'
  },
  {
    id: 'STR-015',
    component: 'Internal Systems',
    threatType: 'Elevation of Privilege',
    description: 'Lateral movement from compromised employee workstation',
    asset: 'Internal Network',
    attackVector: 'Malware or stolen credentials',
    likelihood: 'medium',
    impact: 'high',
    riskLevel: 'high',
    mitigations: [
      'Network segmentation and zero trust',
      'Endpoint detection and response (EDR)',
      'Privileged account management',
      'Just-in-time access provisioning'
    ],
    status: 'mitigating'
  }
];

export const getStrideByType = (type: StrideThreat['threatType']) => {
  return strideThreats.filter(threat => threat.threatType === type);
};

export const getCriticalStrideThreats = () => {
  return strideThreats.filter(threat => threat.riskLevel === 'critical');
};

export const getStrideByComponent = (component: string) => {
  return strideThreats.filter(threat => threat.component === component);
};

export const strideComponents = [
  'Web Banking Portal',
  'Mobile Banking App',
  'API Gateway',
  'Transaction Processing System',
  'Customer Database',
  'Payment Gateway',
  'Admin Portal',
  'Data Analytics Platform',
  'Internal Systems'
];

export const strideThreatTypes = [
  { type: 'Spoofing', description: 'Pretending to be something or someone else', icon: '🎭' },
  { type: 'Tampering', description: 'Modifying data or code', icon: '🔨' },
  { type: 'Repudiation', description: 'Claiming to not have performed an action', icon: '🚫' },
  { type: 'Information Disclosure', description: 'Exposing information to unauthorized users', icon: '📢' },
  { type: 'Denial of Service', description: 'Deny or degrade service availability', icon: '🚧' },
  { type: 'Elevation of Privilege', description: 'Gain unauthorized capabilities', icon: '⬆️' }
];

// Component Threat Summary
export const componentThreats = strideComponents.map(component => {
  const threats = getStrideByComponent(component);
  const summary = {
    component,
    spoofing: threats.filter(t => t.threatType === 'Spoofing').length,
    tampering: threats.filter(t => t.threatType === 'Tampering').length,
    repudiation: threats.filter(t => t.threatType === 'Repudiation').length,
    informationDisclosure: threats.filter(t => t.threatType === 'Information Disclosure').length,
    denialOfService: threats.filter(t => t.threatType === 'Denial of Service').length,
    elevationOfPrivilege: threats.filter(t => t.threatType === 'Elevation of Privilege').length,
    total: threats.length
  };
  return summary;
});

// Threat Category Summary
export const threatCategorySummary = {
  spoofing: strideThreats.filter(t => t.threatType === 'Spoofing').length,
  tampering: strideThreats.filter(t => t.threatType === 'Tampering').length,
  repudiation: strideThreats.filter(t => t.threatType === 'Repudiation').length,
  informationDisclosure: strideThreats.filter(t => t.threatType === 'Information Disclosure').length,
  denialOfService: strideThreats.filter(t => t.threatType === 'Denial of Service').length,
  elevationOfPrivilege: strideThreats.filter(t => t.threatType === 'Elevation of Privilege').length
};

// Risk Matrix Data
export const riskMatrix = {
  'High': {
    'Critical': strideThreats.filter(t => t.likelihood === 'high' && t.impact === 'high' && t.riskLevel === 'critical').map(t => t.id),
    'High': strideThreats.filter(t => t.likelihood === 'high' && t.impact === 'high' && t.riskLevel === 'high').map(t => t.id),
    'Medium': strideThreats.filter(t => t.likelihood === 'high' && t.impact === 'medium').map(t => t.id),
    'Low': strideThreats.filter(t => t.likelihood === 'high' && t.impact === 'low').map(t => t.id)
  },
  'Medium': {
    'Critical': strideThreats.filter(t => t.likelihood === 'medium' && t.impact === 'high' && t.riskLevel === 'critical').map(t => t.id),
    'High': strideThreats.filter(t => t.likelihood === 'medium' && t.impact === 'high' && t.riskLevel === 'high').map(t => t.id),
    'Medium': strideThreats.filter(t => t.likelihood === 'medium' && t.impact === 'medium').map(t => t.id),
    'Low': strideThreats.filter(t => t.likelihood === 'medium' && t.impact === 'low').map(t => t.id)
  },
  'Low': {
    'Critical': strideThreats.filter(t => t.likelihood === 'low' && t.impact === 'high' && t.riskLevel === 'critical').map(t => t.id),
    'High': strideThreats.filter(t => t.likelihood === 'low' && t.impact === 'high' && t.riskLevel === 'high').map(t => t.id),
    'Medium': strideThreats.filter(t => t.likelihood === 'low' && t.impact === 'medium').map(t => t.id),
    'Low': strideThreats.filter(t => t.likelihood === 'low' && t.impact === 'low').map(t => t.id)
  }
};