// HAZOP Analysis Mock Data for Modern Digital Banking Platform
// Hazard and Operability Study - Systematic examination of process nodes

export interface HazopNode {
  id: string;
  name: string;
  type: 'process' | 'data-flow' | 'interface' | 'storage' | 'service';
  description: string;
  parameters: string[];
  normalOperation: string;
}

export interface HazopDeviation {
  id: string;
  nodeId: string;
  parameter: string;
  guideWord: 'No' | 'More' | 'Less' | 'As well as' | 'Part of' | 'Reverse' | 'Other than' | 'Early' | 'Late' | 'Before' | 'After';
  deviation: string;
  causes: string[];
  consequences: string[];
  safeguards: string[];
  recommendations: string[];
  severity: 'low' | 'medium' | 'high' | 'critical';
  likelihood: 'rare' | 'unlikely' | 'possible' | 'likely' | 'almost certain';
  riskRating: 'low' | 'medium' | 'high' | 'critical';
  status: 'open' | 'in-review' | 'mitigated' | 'accepted';
}

export interface HazopAction {
  id: string;
  deviationId: string;
  action: string;
  responsible: string;
  dueDate: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  status: 'pending' | 'in-progress' | 'completed' | 'overdue';
}

export const hazopNodes: HazopNode[] = [
  {
    id: 'NODE-001',
    name: 'Customer Authentication',
    type: 'process',
    description: 'Process for verifying customer identity during login',
    parameters: ['Authentication Flow', 'Credential Validation', 'Session Management', 'MFA Token'],
    normalOperation: 'Customer provides credentials, system validates against stored hash, MFA token verified, session established'
  },
  {
    id: 'NODE-002',
    name: 'Payment Processing',
    type: 'process',
    description: 'Core payment processing and transaction execution',
    parameters: ['Transaction Amount', 'Processing Time', 'Authorization', 'Data Flow'],
    normalOperation: 'Transaction initiated, validated, authorized, processed, and confirmed within 2-3 seconds'
  },
  {
    id: 'NODE-003',
    name: 'Account Data Storage',
    type: 'storage',
    description: 'Primary database for customer account information',
    parameters: ['Data Integrity', 'Access Control', 'Replication', 'Backup Frequency'],
    normalOperation: 'Data stored encrypted, replicated across 3 zones, backed up every hour, access logged'
  },
  {
    id: 'NODE-004',
    name: 'API Gateway',
    type: 'interface',
    description: 'Central API gateway for mobile and web applications',
    parameters: ['Request Rate', 'Response Time', 'Authentication', 'Data Format'],
    normalOperation: 'Handles 10k requests/second, authenticates all requests, validates format, routes to services'
  },
  {
    id: 'NODE-005',
    name: 'Fraud Detection Service',
    type: 'service',
    description: 'Real-time fraud detection and prevention system',
    parameters: ['Detection Algorithm', 'Response Time', 'False Positive Rate', 'Alert Generation'],
    normalOperation: 'Analyzes transactions in <100ms, maintains <0.1% false positive rate, generates alerts for suspicious activity'
  },
  {
    id: 'NODE-006',
    name: 'Customer Data Flow',
    type: 'data-flow',
    description: 'Flow of customer PII through the system',
    parameters: ['Data Encryption', 'Transfer Protocol', 'Data Validation', 'Flow Rate'],
    normalOperation: 'All PII encrypted in transit using TLS 1.3, validated at each hop, rate limited per customer'
  },
  {
    id: 'NODE-007',
    name: 'Loan Approval Process',
    type: 'process',
    description: 'Automated loan approval and decisioning system',
    parameters: ['Credit Check', 'Decision Time', 'Approval Criteria', 'Documentation'],
    normalOperation: 'Credit check completed in 5 seconds, decision in 30 seconds, documents generated automatically'
  },
  {
    id: 'NODE-008',
    name: 'Mobile App Backend',
    type: 'interface',
    description: 'Backend services specifically for mobile banking app',
    parameters: ['Session Timeout', 'Biometric Auth', 'Push Notifications', 'Offline Capability'],
    normalOperation: '5-minute session timeout, biometric required for sensitive operations, encrypted push notifications'
  }
];

export const hazopDeviations: HazopDeviation[] = [
  // Customer Authentication Deviations
  {
    id: 'DEV-001',
    nodeId: 'NODE-001',
    parameter: 'Authentication Flow',
    guideWord: 'No',
    deviation: 'No authentication performed',
    causes: [
      'Authentication service down',
      'Network connectivity issues',
      'Service misconfiguration',
      'DDoS attack on auth service'
    ],
    consequences: [
      'Customers unable to access accounts',
      'Complete service outage',
      'Revenue loss from transaction inability',
      'Customer frustration and complaints'
    ],
    safeguards: [
      'Redundant authentication services',
      'Health checks and auto-failover',
      'DDoS protection',
      'Cached authentication tokens'
    ],
    recommendations: [
      'Implement circuit breaker pattern',
      'Add authentication service redundancy',
      'Create offline authentication capability',
      'Improve monitoring and alerting'
    ],
    severity: 'critical',
    likelihood: 'unlikely',
    riskRating: 'high',
    status: 'in-review'
  },
  {
    id: 'DEV-002',
    nodeId: 'NODE-001',
    parameter: 'MFA Token',
    guideWord: 'Other than',
    deviation: 'Invalid or manipulated MFA tokens accepted',
    causes: [
      'Token validation vulnerability',
      'Time synchronization issues',
      'Replay attack',
      'Compromised token generation'
    ],
    consequences: [
      'Unauthorized account access',
      'Financial fraud',
      'Regulatory compliance violations',
      'Loss of customer trust'
    ],
    safeguards: [
      'Token expiration and one-time use',
      'Time window validation',
      'Rate limiting on attempts',
      'Anomaly detection'
    ],
    recommendations: [
      'Implement FIDO2 standards',
      'Add token binding to device',
      'Enhance replay attack prevention',
      'Regular security audits'
    ],
    severity: 'critical',
    likelihood: 'rare',
    riskRating: 'medium',
    status: 'open'
  },
  {
    id: 'DEV-003',
    nodeId: 'NODE-001',
    parameter: 'Session Management',
    guideWord: 'More',
    deviation: 'Sessions persist longer than intended',
    causes: [
      'Session timeout not enforced',
      'Bug in session cleanup',
      'Redis cache not expiring keys',
      'Clock synchronization issues'
    ],
    consequences: [
      'Unauthorized access from shared devices',
      'Session hijacking vulnerability',
      'Compliance violations (PCI-DSS)',
      'Increased attack surface'
    ],
    safeguards: [
      'Absolute session timeout',
      'Activity-based timeout',
      'Server-side session validation',
      'Regular session cleanup jobs'
    ],
    recommendations: [
      'Implement sliding window timeout',
      'Add session binding to IP/device',
      'Monitor long-running sessions',
      'Automated session audit'
    ],
    severity: 'high',
    likelihood: 'possible',
    riskRating: 'high',
    status: 'mitigated'
  },

  // Payment Processing Deviations
  {
    id: 'DEV-004',
    nodeId: 'NODE-002',
    parameter: 'Transaction Amount',
    guideWord: 'More',
    deviation: 'Transaction amount exceeds limits',
    causes: [
      'Limit validation failure',
      'Integer overflow',
      'Concurrent modification',
      'Malicious input manipulation'
    ],
    consequences: [
      'Unauthorized large transfers',
      'Account overdraft',
      'Money laundering risk',
      'Regulatory scrutiny'
    ],
    safeguards: [
      'Multiple limit checks',
      'Database constraints',
      'Real-time balance validation',
      'Transaction monitoring'
    ],
    recommendations: [
      'Implement hard limits in database',
      'Add cryptographic amount signing',
      'Enhanced concurrent control',
      'Real-time limit adjustment'
    ],
    severity: 'critical',
    likelihood: 'unlikely',
    riskRating: 'high',
    status: 'mitigated'
  },
  {
    id: 'DEV-005',
    nodeId: 'NODE-002',
    parameter: 'Processing Time',
    guideWord: 'Late',
    deviation: 'Transaction processing delayed significantly',
    causes: [
      'Database locks',
      'Network latency',
      'Third-party service delays',
      'System overload'
    ],
    consequences: [
      'Duplicate transaction attempts',
      'Customer uncertainty',
      'Timeout errors',
      'Inconsistent account state'
    ],
    safeguards: [
      'Idempotency keys',
      'Transaction status tracking',
      'Async processing option',
      'Queue management'
    ],
    recommendations: [
      'Implement saga pattern',
      'Add processing time SLAs',
      'Create fast-path for small transactions',
      'Improve database query optimization'
    ],
    severity: 'medium',
    likelihood: 'likely',
    riskRating: 'medium',
    status: 'in-review'
  },

  // Account Data Storage Deviations
  {
    id: 'DEV-006',
    nodeId: 'NODE-003',
    parameter: 'Data Integrity',
    guideWord: 'Part of',
    deviation: 'Partial data corruption or loss',
    causes: [
      'Hardware failure',
      'Software bug in database',
      'Incomplete transaction commit',
      'Replication lag issues'
    ],
    consequences: [
      'Incorrect account balances',
      'Missing transaction history',
      'Audit trail gaps',
      'Customer data inconsistency'
    ],
    safeguards: [
      'ACID compliance',
      'Regular integrity checks',
      'Point-in-time recovery',
      'Multi-region replication'
    ],
    recommendations: [
      'Implement blockchain audit trail',
      'Add real-time integrity monitoring',
      'Enhance backup testing',
      'Create data reconciliation service'
    ],
    severity: 'critical',
    likelihood: 'rare',
    riskRating: 'medium',
    status: 'open'
  },
  {
    id: 'DEV-007',
    nodeId: 'NODE-003',
    parameter: 'Access Control',
    guideWord: 'No',
    deviation: 'No access control enforcement',
    causes: [
      'IAM service failure',
      'Policy misconfiguration',
      'Privilege escalation bug',
      'Bypassed authentication'
    ],
    consequences: [
      'Unauthorized data access',
      'Data breach risk',
      'Compliance violations',
      'Insider threat exposure'
    ],
    safeguards: [
      'Defense in depth',
      'Network segmentation',
      'Encryption at rest',
      'Access logging'
    ],
    recommendations: [
      'Implement zero-trust architecture',
      'Add database firewall',
      'Enhance privilege management',
      'Regular access reviews'
    ],
    severity: 'critical',
    likelihood: 'unlikely',
    riskRating: 'high',
    status: 'mitigated'
  },

  // API Gateway Deviations
  {
    id: 'DEV-008',
    nodeId: 'NODE-004',
    parameter: 'Request Rate',
    guideWord: 'More',
    deviation: 'Request rate exceeds capacity',
    causes: [
      'DDoS attack',
      'Viral marketing campaign',
      'Bot activity',
      'Load balancer failure'
    ],
    consequences: [
      'Service degradation',
      'Complete outage',
      'Cascading failures',
      'SLA violations'
    ],
    safeguards: [
      'Rate limiting',
      'Auto-scaling',
      'CDN caching',
      'DDoS protection'
    ],
    recommendations: [
      'Implement adaptive rate limiting',
      'Add request prioritization',
      'Enhance caching strategy',
      'Create surge capacity'
    ],
    severity: 'high',
    likelihood: 'possible',
    riskRating: 'high',
    status: 'in-review'
  },
  {
    id: 'DEV-009',
    nodeId: 'NODE-004',
    parameter: 'Data Format',
    guideWord: 'Other than',
    deviation: 'Malformed or malicious data accepted',
    causes: [
      'Insufficient input validation',
      'New API version issues',
      'Injection attacks',
      'Schema evolution problems'
    ],
    consequences: [
      'Security vulnerabilities',
      'Service crashes',
      'Data corruption',
      'Downstream service failures'
    ],
    safeguards: [
      'Schema validation',
      'Input sanitization',
      'WAF protection',
      'API versioning'
    ],
    recommendations: [
      'Implement strict schema enforcement',
      'Add payload encryption',
      'Enhance WAF rules',
      'Create data validation service'
    ],
    severity: 'high',
    likelihood: 'likely',
    riskRating: 'high',
    status: 'open'
  },

  // Fraud Detection Service Deviations
  {
    id: 'DEV-010',
    nodeId: 'NODE-005',
    parameter: 'Detection Algorithm',
    guideWord: 'Less',
    deviation: 'Reduced detection accuracy',
    causes: [
      'Model drift',
      'New fraud patterns',
      'Training data issues',
      'Feature extraction failures'
    ],
    consequences: [
      'Increased fraud losses',
      'Undetected money laundering',
      'Regulatory penalties',
      'Reputation damage'
    ],
    safeguards: [
      'Model performance monitoring',
      'Regular retraining',
      'Multiple model ensemble',
      'Human review queue'
    ],
    recommendations: [
      'Implement continuous learning',
      'Add adversarial testing',
      'Enhance feature engineering',
      'Create fraud pattern library'
    ],
    severity: 'high',
    likelihood: 'possible',
    riskRating: 'high',
    status: 'in-review'
  },
  {
    id: 'DEV-011',
    nodeId: 'NODE-005',
    parameter: 'False Positive Rate',
    guideWord: 'More',
    deviation: 'Excessive false positives',
    causes: [
      'Over-sensitive rules',
      'Model overfitting',
      'Seasonal patterns',
      'System integration issues'
    ],
    consequences: [
      'Customer frustration',
      'Legitimate transactions blocked',
      'Increased support costs',
      'Customer attrition'
    ],
    safeguards: [
      'Threshold tuning',
      'Customer profiling',
      'Whitelist management',
      'Quick review process'
    ],
    recommendations: [
      'Implement adaptive thresholds',
      'Add customer feedback loop',
      'Enhance rule explainability',
      'Create self-service unblock'
    ],
    severity: 'medium',
    likelihood: 'likely',
    riskRating: 'medium',
    status: 'mitigated'
  },

  // Customer Data Flow Deviations
  {
    id: 'DEV-012',
    nodeId: 'NODE-006',
    parameter: 'Data Encryption',
    guideWord: 'No',
    deviation: 'Unencrypted data transmission',
    causes: [
      'TLS configuration error',
      'Certificate expiration',
      'Downgrade attack',
      'Legacy system integration'
    ],
    consequences: [
      'Data interception risk',
      'PII exposure',
      'Compliance violations',
      'Man-in-the-middle attacks'
    ],
    safeguards: [
      'Certificate monitoring',
      'TLS policy enforcement',
      'Network segmentation',
      'VPN backup'
    ],
    recommendations: [
      'Implement certificate pinning',
      'Add encryption monitoring',
      'Enforce TLS 1.3 minimum',
      'Create encryption audit trail'
    ],
    severity: 'critical',
    likelihood: 'unlikely',
    riskRating: 'high',
    status: 'mitigated'
  },

  // Loan Approval Process Deviations
  {
    id: 'DEV-013',
    nodeId: 'NODE-007',
    parameter: 'Approval Criteria',
    guideWord: 'Other than',
    deviation: 'Incorrect approval criteria applied',
    causes: [
      'Configuration error',
      'Rule engine bug',
      'Data quality issues',
      'Integration failures'
    ],
    consequences: [
      'Bad loans approved',
      'Good customers rejected',
      'Regulatory violations',
      'Financial losses'
    ],
    safeguards: [
      'Manual review sampling',
      'Approval limits',
      'Rule validation',
      'Audit trails'
    ],
    recommendations: [
      'Implement A/B testing for rules',
      'Add explainable AI',
      'Enhance data quality checks',
      'Create rule simulation environment'
    ],
    severity: 'high',
    likelihood: 'possible',
    riskRating: 'high',
    status: 'open'
  },

  // Mobile App Backend Deviations
  {
    id: 'DEV-014',
    nodeId: 'NODE-008',
    parameter: 'Biometric Auth',
    guideWord: 'As well as',
    deviation: 'Multiple authentication methods active simultaneously',
    causes: [
      'State management bug',
      'Race condition',
      'Feature flag misconfiguration',
      'Version compatibility issues'
    ],
    consequences: [
      'Security bypass potential',
      'Confused user experience',
      'Audit complications',
      'Compliance issues'
    ],
    safeguards: [
      'Mutual exclusion logic',
      'State validation',
      'Version checking',
      'Clear auth flow'
    ],
    recommendations: [
      'Implement auth state machine',
      'Add mutual exclusion enforcement',
      'Enhance testing coverage',
      'Create auth flow documentation'
    ],
    severity: 'medium',
    likelihood: 'unlikely',
    riskRating: 'medium',
    status: 'accepted'
  },
  {
    id: 'DEV-015',
    nodeId: 'NODE-008',
    parameter: 'Push Notifications',
    guideWord: 'Reverse',
    deviation: 'Notifications sent to wrong devices',
    causes: [
      'Device token mix-up',
      'Database corruption',
      'Concurrent updates',
      'Platform API changes'
    ],
    consequences: [
      'Privacy breach',
      'Sensitive data exposure',
      'Customer complaints',
      'Regulatory scrutiny'
    ],
    safeguards: [
      'Token validation',
      'Encryption of content',
      'Device binding checks',
      'Delivery confirmation'
    ],
    recommendations: [
      'Implement end-to-end encryption',
      'Add device verification',
      'Enhance token management',
      'Create notification audit log'
    ],
    severity: 'high',
    likelihood: 'rare',
    riskRating: 'medium',
    status: 'in-review'
  }
];

export const hazopActions: HazopAction[] = [
  {
    id: 'ACT-001',
    deviationId: 'DEV-001',
    action: 'Implement authentication service redundancy across all regions',
    responsible: 'Infrastructure Team',
    dueDate: '2024-03-15',
    priority: 'high',
    status: 'in-progress'
  },
  {
    id: 'ACT-002',
    deviationId: 'DEV-001',
    action: 'Design and implement offline authentication capability',
    responsible: 'Security Architecture',
    dueDate: '2024-04-01',
    priority: 'medium',
    status: 'pending'
  },
  {
    id: 'ACT-003',
    deviationId: 'DEV-004',
    action: 'Add cryptographic signing to all transaction amounts',
    responsible: 'Payment Team',
    dueDate: '2024-02-28',
    priority: 'urgent',
    status: 'in-progress'
  },
  {
    id: 'ACT-004',
    deviationId: 'DEV-006',
    action: 'Implement blockchain-based audit trail for critical data',
    responsible: 'Data Team',
    dueDate: '2024-05-01',
    priority: 'medium',
    status: 'pending'
  },
  {
    id: 'ACT-005',
    deviationId: 'DEV-008',
    action: 'Deploy adaptive rate limiting with ML-based thresholds',
    responsible: 'Platform Team',
    dueDate: '2024-03-01',
    priority: 'high',
    status: 'completed'
  },
  {
    id: 'ACT-006',
    deviationId: 'DEV-009',
    action: 'Upgrade WAF rules and implement deep packet inspection',
    responsible: 'Security Operations',
    dueDate: '2024-02-15',
    priority: 'urgent',
    status: 'completed'
  },
  {
    id: 'ACT-007',
    deviationId: 'DEV-010',
    action: 'Implement continuous learning pipeline for fraud models',
    responsible: 'ML Team',
    dueDate: '2024-04-15',
    priority: 'high',
    status: 'pending'
  },
  {
    id: 'ACT-008',
    deviationId: 'DEV-012',
    action: 'Enforce TLS 1.3 minimum and implement certificate pinning',
    responsible: 'Network Security',
    dueDate: '2024-02-01',
    priority: 'urgent',
    status: 'overdue'
  }
];

export const getDeviationsByNode = (nodeId: string) => 
  hazopDeviations.filter(dev => dev.nodeId === nodeId);

export const getActionsByDeviation = (deviationId: string) =>
  hazopActions.filter(action => action.deviationId === deviationId);

export const getCriticalDeviations = () =>
  hazopDeviations.filter(dev => dev.riskRating === 'critical');

export const getOpenActions = () =>
  hazopActions.filter(action => action.status === 'pending' || action.status === 'in-progress');

export const getNodeById = (nodeId: string) =>
  hazopNodes.find(node => node.id === nodeId);

export const hazopGuideWords = [
  { word: 'No', description: 'Complete negation of intention' },
  { word: 'More', description: 'Quantitative increase' },
  { word: 'Less', description: 'Quantitative decrease' },
  { word: 'As well as', description: 'Qualitative increase' },
  { word: 'Part of', description: 'Qualitative decrease' },
  { word: 'Reverse', description: 'Logical opposite' },
  { word: 'Other than', description: 'Complete substitution' },
  { word: 'Early', description: 'Relative to clock time' },
  { word: 'Late', description: 'Relative to clock time' },
  { word: 'Before', description: 'Relating to order or sequence' },
  { word: 'After', description: 'Relating to order or sequence' }
];

export const riskMatrix = {
  severity: ['low', 'medium', 'high', 'critical'],
  likelihood: ['rare', 'unlikely', 'possible', 'likely', 'almost certain'],
  getRating: (severity: string, likelihood: string): string => {
    const severityIndex = riskMatrix.severity.indexOf(severity);
    const likelihoodIndex = riskMatrix.likelihood.indexOf(likelihood);
    
    if (severityIndex >= 3 || likelihoodIndex >= 3) return 'critical';
    if (severityIndex >= 2 || likelihoodIndex >= 2) return 'high';
    if (severityIndex >= 1 || likelihoodIndex >= 1) return 'medium';
    return 'low';
  }
};