// DREAD Risk Assessment mock data

export interface DreadThreat {
  id: string;
  threat: string;
  category: string;
  asset: string;
  scores: {
    damage: number; // 1-3: 1=Low, 2=Medium, 3=High
    reproducibility: number; // 1-3: 1=Difficult, 2=Moderate, 3=Easy
    exploitability: number; // 1-3: 1=Difficult, 2=Moderate, 3=Easy
    affectedUsers: number; // 1-3: 1=Few, 2=Some, 3=Many
    discoverability: number; // 1-3: 1=Difficult, 2=Moderate, 3=Easy
  };
  totalScore: number; // Sum of all scores (5-15)
  riskLevel: 'Low' | 'Medium' | 'High' | 'Critical';
  description: string;
  mitigation: string;
  status: 'identified' | 'mitigating' | 'mitigated' | 'accepted';
}

export interface DreadCategory {
  name: string;
  description: string;
  threats: DreadThreat[];
}

// DREAD scoring thresholds
const getRiskLevel = (score: number): 'Low' | 'Medium' | 'High' | 'Critical' => {
  if (score <= 6) return 'Low';
  if (score <= 9) return 'Medium';
  if (score <= 12) return 'High';
  return 'Critical';
};

// Mock DREAD threats for Digital Banking Platform
export const dreadThreats: DreadThreat[] = [
  {
    id: 'DT-001',
    threat: 'SQL Injection in Login Form',
    category: 'Input Validation',
    asset: 'Authentication Service',
    scores: {
      damage: 3, // High - Could access all user accounts
      reproducibility: 3, // Easy - Standard SQL injection techniques
      exploitability: 2, // Moderate - Requires some SQL knowledge
      affectedUsers: 3, // Many - All users potentially affected
      discoverability: 3 // Easy - Automated scanners can find it
    },
    totalScore: 14,
    riskLevel: 'Critical',
    description: 'Unvalidated user input in login form allows SQL injection attacks that could compromise the entire user database',
    mitigation: 'Implement parameterized queries, input validation, and WAF rules',
    status: 'mitigating'
  },
  {
    id: 'DT-002',
    threat: 'Weak Password Policy',
    category: 'Authentication',
    asset: 'User Accounts',
    scores: {
      damage: 2, // Medium - Individual accounts compromised
      reproducibility: 3, // Easy - Password attacks are automated
      exploitability: 3, // Easy - Many tools available
      affectedUsers: 2, // Some - Depends on user behavior
      discoverability: 3 // Easy - Can test password policy
    },
    totalScore: 13,
    riskLevel: 'Critical',
    description: 'Weak password requirements allow brute force and dictionary attacks',
    mitigation: 'Enforce strong password policy, implement account lockout, add MFA',
    status: 'identified'
  },
  {
    id: 'DT-003',
    threat: 'Unencrypted Data in Transit',
    category: 'Cryptography',
    asset: 'API Communications',
    scores: {
      damage: 3, // High - Sensitive financial data exposed
      reproducibility: 2, // Moderate - Requires network position
      exploitability: 2, // Moderate - Needs MITM capability
      affectedUsers: 3, // Many - All API users affected
      discoverability: 2 // Moderate - Network analysis required
    },
    totalScore: 12,
    riskLevel: 'High',
    description: 'Some internal API calls use HTTP instead of HTTPS',
    mitigation: 'Enforce TLS 1.3 for all communications, implement certificate pinning',
    status: 'mitigating'
  },
  {
    id: 'DT-004',
    threat: 'Session Fixation Vulnerability',
    category: 'Session Management',
    asset: 'Web Application',
    scores: {
      damage: 2, // Medium - Account takeover
      reproducibility: 2, // Moderate - Requires user interaction
      exploitability: 2, // Moderate - Social engineering needed
      affectedUsers: 2, // Some - Targeted attacks
      discoverability: 2 // Moderate - Not obvious
    },
    totalScore: 10,
    riskLevel: 'High',
    description: 'Session IDs not regenerated after login allowing fixation attacks',
    mitigation: 'Regenerate session IDs on login, implement session timeout',
    status: 'identified'
  },
  {
    id: 'DT-005',
    threat: 'Insufficient Logging of Transactions',
    category: 'Auditing',
    asset: 'Transaction System',
    scores: {
      damage: 2, // Medium - Compliance issues, forensics impact
      reproducibility: 3, // Easy - Always present
      exploitability: 1, // Difficult - Indirect threat
      affectedUsers: 2, // Some - Fraud victims
      discoverability: 2 // Moderate - Audit would find it
    },
    totalScore: 10,
    riskLevel: 'High',
    description: 'Transaction logs lack sufficient detail for fraud investigation',
    mitigation: 'Implement comprehensive logging with tamper protection',
    status: 'identified'
  },
  {
    id: 'DT-006',
    threat: 'XSS in User Profile Fields',
    category: 'Input Validation',
    asset: 'User Profile Management',
    scores: {
      damage: 2, // Medium - Session hijacking, defacement
      reproducibility: 3, // Easy - Standard XSS payloads
      exploitability: 3, // Easy - Basic web knowledge
      affectedUsers: 1, // Few - Only profile viewers
      discoverability: 3 // Easy - Common vulnerability
    },
    totalScore: 12,
    riskLevel: 'High',
    description: 'User-controlled fields not properly sanitized allowing stored XSS',
    mitigation: 'Implement output encoding, CSP headers, input sanitization',
    status: 'mitigated'
  },
  {
    id: 'DT-007',
    threat: 'API Rate Limiting Bypass',
    category: 'Access Control',
    asset: 'API Gateway',
    scores: {
      damage: 1, // Low - DoS impact
      reproducibility: 2, // Moderate - Distributed attacks
      exploitability: 2, // Moderate - Requires resources
      affectedUsers: 3, // Many - Service availability
      discoverability: 2 // Moderate - Testing reveals it
    },
    totalScore: 10,
    riskLevel: 'High',
    description: 'Rate limiting can be bypassed using distributed IPs',
    mitigation: 'Implement user-based rate limiting, CAPTCHA, anomaly detection',
    status: 'mitigating'
  },
  {
    id: 'DT-008',
    threat: 'Insecure Direct Object References',
    category: 'Access Control',
    asset: 'Account Management API',
    scores: {
      damage: 3, // High - Access to other accounts
      reproducibility: 2, // Moderate - Requires valid session
      exploitability: 2, // Moderate - Parameter manipulation
      affectedUsers: 3, // Many - All accounts at risk
      discoverability: 2 // Moderate - Testing required
    },
    totalScore: 12,
    riskLevel: 'High',
    description: 'Account IDs in API calls not validated against session user',
    mitigation: 'Implement proper authorization checks, use indirect references',
    status: 'identified'
  },
  {
    id: 'DT-009',
    threat: 'Weak Cryptographic Key Management',
    category: 'Cryptography',
    asset: 'Encryption Keys',
    scores: {
      damage: 3, // High - All encrypted data compromised
      reproducibility: 1, // Difficult - Requires system access
      exploitability: 1, // Difficult - Privileged access needed
      affectedUsers: 3, // Many - All encrypted data
      discoverability: 1 // Difficult - Internal issue
    },
    totalScore: 9,
    riskLevel: 'Medium',
    description: 'Encryption keys stored in configuration files',
    mitigation: 'Implement HSM, key rotation, secure key storage',
    status: 'identified'
  },
  {
    id: 'DT-010',
    threat: 'Missing Security Headers',
    category: 'Configuration',
    asset: 'Web Application',
    scores: {
      damage: 1, // Low - Enables other attacks
      reproducibility: 3, // Easy - Always present
      exploitability: 2, // Moderate - Part of attack chain
      affectedUsers: 2, // Some - Web users
      discoverability: 3 // Easy - Header inspection
    },
    totalScore: 11,
    riskLevel: 'High',
    description: 'Missing X-Frame-Options, CSP, and other security headers',
    mitigation: 'Configure all security headers properly',
    status: 'mitigated'
  }
];

// Group threats by category
export const threatCategories: DreadCategory[] = [
  {
    name: 'Input Validation',
    description: 'Threats related to improper input validation and sanitization',
    threats: dreadThreats.filter(t => t.category === 'Input Validation')
  },
  {
    name: 'Authentication',
    description: 'Threats related to authentication mechanisms',
    threats: dreadThreats.filter(t => t.category === 'Authentication')
  },
  {
    name: 'Cryptography',
    description: 'Threats related to encryption and cryptographic controls',
    threats: dreadThreats.filter(t => t.category === 'Cryptography')
  },
  {
    name: 'Access Control',
    description: 'Threats related to authorization and access control',
    threats: dreadThreats.filter(t => t.category === 'Access Control')
  },
  {
    name: 'Session Management',
    description: 'Threats related to session handling',
    threats: dreadThreats.filter(t => t.category === 'Session Management')
  },
  {
    name: 'Auditing',
    description: 'Threats related to logging and monitoring',
    threats: dreadThreats.filter(t => t.category === 'Auditing')
  },
  {
    name: 'Configuration',
    description: 'Threats related to security configuration',
    threats: dreadThreats.filter(t => t.category === 'Configuration')
  }
];

// Helper functions
export function getHighestRiskThreats() {
  return dreadThreats
    .filter(t => t.riskLevel === 'Critical' || t.riskLevel === 'High')
    .sort((a, b) => b.totalScore - a.totalScore);
}

export function getThreatsByStatus(status: DreadThreat['status']) {
  return dreadThreats.filter(t => t.status === status);
}

export function getAverageRiskScore() {
  const total = dreadThreats.reduce((sum, t) => sum + t.totalScore, 0);
  return (total / dreadThreats.length).toFixed(1);
}

export function getRiskDistribution() {
  const distribution = {
    Critical: 0,
    High: 0,
    Medium: 0,
    Low: 0
  };
  
  dreadThreats.forEach(t => {
    distribution[t.riskLevel]++;
  });
  
  return distribution;
}