// Comprehensive STPA-Sec mock data based on the generation files

export interface Loss {
  id: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  category: string;
  stakeholders: string[];
}

export interface Hazard {
  id: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  relatedLosses: string[];
  systemState: string;
  worstCase: string;
}

export interface Controller {
  id: string;
  name: string;
  type: 'human' | 'software' | 'organizational';
  responsibilities: string[];
  processModel: string[];
}

export interface ControlAction {
  id: string;
  controllerId: string;
  action: string;
  targetProcess: string;
  constraints: string[];
}

export interface UCA {
  id: string;
  controlActionId: string;
  type: 'not-provided' | 'provided' | 'wrong-timing' | 'wrong-duration';
  description: string;
  hazards: string[];
  context: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
}

export interface CausalScenario {
  id: string;
  ucaId: string;
  description: string;
  causalFactors: string[];
  strideCategory: string;
  d4Score: {
    detectability: number;
    difficulty: number;
    damage: number;
    deniability: number;
  };
  mitigations: string[];
  confidence: number;
}

// Step 1: System Engineering Foundation
export const losses: Loss[] = [
  {
    id: 'L1',
    description: 'Financial data breach leading to customer financial loss',
    severity: 'critical',
    category: 'Financial',
    stakeholders: ['Customers', 'Bank', 'Regulators']
  },
  {
    id: 'L2',
    description: 'Service unavailability affecting customer transactions',
    severity: 'high',
    category: 'Operational',
    stakeholders: ['Customers', 'Bank Operations']
  },
  {
    id: 'L3',
    description: 'Regulatory compliance violations resulting in fines',
    severity: 'high',
    category: 'Compliance',
    stakeholders: ['Bank', 'Regulators', 'Shareholders']
  },
  {
    id: 'L4',
    description: 'Loss of customer trust and reputation damage',
    severity: 'high',
    category: 'Reputational',
    stakeholders: ['Bank', 'Customers', 'Shareholders']
  },
  {
    id: 'L5',
    description: 'Intellectual property theft affecting competitive advantage',
    severity: 'medium',
    category: 'Strategic',
    stakeholders: ['Bank', 'Shareholders']
  }
];

export const hazards: Hazard[] = [
  {
    id: 'H1',
    description: 'System allows unauthorized access to customer financial data',
    severity: 'critical',
    relatedLosses: ['L1', 'L4'],
    systemState: 'Authentication system compromised or bypassed',
    worstCase: 'Attacker gains access to entire customer database'
  },
  {
    id: 'H2',
    description: 'Transaction processing system accepts fraudulent transactions',
    severity: 'high',
    relatedLosses: ['L1', 'L3'],
    systemState: 'Transaction validation controls ineffective',
    worstCase: 'Large-scale fraudulent transfers processed'
  },
  {
    id: 'H3',
    description: 'Critical services become unavailable during peak usage',
    severity: 'high',
    relatedLosses: ['L2', 'L4'],
    systemState: 'System overloaded or under DoS attack',
    worstCase: 'Complete service outage during critical business hours'
  },
  {
    id: 'H4',
    description: 'Audit logs can be tampered with or deleted',
    severity: 'high',
    relatedLosses: ['L3'],
    systemState: 'Logging system lacks integrity protection',
    worstCase: 'Regulatory investigation cannot determine breach scope'
  },
  {
    id: 'H5',
    description: 'Sensitive data transmitted without encryption',
    severity: 'critical',
    relatedLosses: ['L1', 'L3', 'L5'],
    systemState: 'TLS/encryption not enforced on all channels',
    worstCase: 'Man-in-the-middle attack captures all data'
  }
];

// Step 2: Control Structure
export const controllers: Controller[] = [
  {
    id: 'C1',
    name: 'Authentication Service',
    type: 'software',
    responsibilities: ['Verify user credentials', 'Issue session tokens', 'Enforce access policies'],
    processModel: ['User credentials database', 'Session state', 'Access control rules']
  },
  {
    id: 'C2',
    name: 'Transaction Processor',
    type: 'software',
    responsibilities: ['Validate transactions', 'Apply business rules', 'Execute transfers'],
    processModel: ['Account balances', 'Transaction limits', 'Fraud patterns']
  },
  {
    id: 'C3',
    name: 'Security Operations Team',
    type: 'human',
    responsibilities: ['Monitor security events', 'Respond to incidents', 'Update security policies'],
    processModel: ['Threat intelligence', 'System status', 'Incident history']
  },
  {
    id: 'C4',
    name: 'API Gateway',
    type: 'software',
    responsibilities: ['Route requests', 'Enforce rate limits', 'Apply security filters'],
    processModel: ['Request patterns', 'Rate limit counters', 'Blocked IP list']
  }
];

export const controlActions: ControlAction[] = [
  {
    id: 'CA1',
    controllerId: 'C1',
    action: 'Grant Authentication',
    targetProcess: 'User Session Management',
    constraints: ['Valid credentials required', 'Account not locked', 'MFA completed if required']
  },
  {
    id: 'CA2',
    controllerId: 'C2',
    action: 'Approve Transaction',
    targetProcess: 'Fund Transfer System',
    constraints: ['Sufficient balance', 'Within daily limit', 'Passes fraud checks']
  },
  {
    id: 'CA3',
    controllerId: 'C3',
    action: 'Block Suspicious IP',
    targetProcess: 'Firewall Configuration',
    constraints: ['Confirmed malicious activity', 'Not critical service IP', 'Documented reason']
  },
  {
    id: 'CA4',
    controllerId: 'C4',
    action: 'Apply Rate Limit',
    targetProcess: 'Request Processing',
    constraints: ['Threshold exceeded', 'Not whitelisted source', 'Within policy parameters']
  }
];

// Step 3: Unsafe Control Actions
export const ucas: UCA[] = [
  // CA1: Grant Authentication - All 4 types
  {
    id: 'UCA1-1',
    controlActionId: 'CA1',
    type: 'not-provided',
    description: 'Authentication not granted to legitimate user',
    hazards: ['H3'],
    context: 'System overload, false positive in fraud detection, or service outage',
    severity: 'high'
  },
  {
    id: 'UCA1-2',
    controlActionId: 'CA1',
    type: 'provided',
    description: 'Authentication granted with invalid or stolen credentials',
    hazards: ['H1'],
    context: 'Credential stuffing attack, insider threat, or compromised credentials',
    severity: 'critical'
  },
  {
    id: 'UCA1-3',
    controlActionId: 'CA1',
    type: 'wrong-timing',
    description: 'Authentication granted after session should have expired',
    hazards: ['H1', 'H4'],
    context: 'Session timeout not enforced or clock synchronization issues',
    severity: 'high'
  },
  {
    id: 'UCA1-4',
    controlActionId: 'CA1',
    type: 'wrong-duration',
    description: 'Authentication session active for excessive duration',
    hazards: ['H1'],
    context: 'No session timeout or improper session management',
    severity: 'medium'
  },

  // CA2: Approve Transaction - All 4 types
  {
    id: 'UCA2-1',
    controlActionId: 'CA2',
    type: 'not-provided',
    description: 'Transaction not approved for legitimate request',
    hazards: ['H2', 'H3'],
    context: 'False positive in fraud detection or system unavailability',
    severity: 'medium'
  },
  {
    id: 'UCA2-2',
    controlActionId: 'CA2',
    type: 'provided',
    description: 'Transaction approved despite fraud indicators',
    hazards: ['H2'],
    context: 'Fraud detection bypassed, rules outdated, or insider threat',
    severity: 'critical'
  },
  {
    id: 'UCA2-3',
    controlActionId: 'CA2',
    type: 'wrong-timing',
    description: 'Transaction approved after account closure or freeze',
    hazards: ['H2', 'H4'],
    context: 'Race condition or synchronization failure',
    severity: 'high'
  },
  {
    id: 'UCA2-4',
    controlActionId: 'CA2',
    type: 'wrong-duration',
    description: 'Transaction processing takes excessive time',
    hazards: ['H3'],
    context: 'System overload or deadlock conditions',
    severity: 'medium'
  },

  // CA3: Block Suspicious IP - All 4 types
  {
    id: 'UCA3-1',
    controlActionId: 'CA3',
    type: 'not-provided',
    description: 'Malicious IP not blocked when detected',
    hazards: ['H1', 'H5'],
    context: 'Detection failure or manual intervention required but not available',
    severity: 'high'
  },
  {
    id: 'UCA3-2',
    controlActionId: 'CA3',
    type: 'provided',
    description: 'Legitimate IP blocked incorrectly',
    hazards: ['H3'],
    context: 'False positive or misconfigured rules',
    severity: 'medium'
  },
  {
    id: 'UCA3-3',
    controlActionId: 'CA3',
    type: 'wrong-timing',
    description: 'Suspicious IP blocked too late after breach',
    hazards: ['H1', 'H5'],
    context: 'Delayed incident detection or response',
    severity: 'critical'
  },
  {
    id: 'UCA3-4',
    controlActionId: 'CA3',
    type: 'wrong-duration',
    description: 'IP block expires too soon allowing re-attack',
    hazards: ['H1'],
    context: 'Improper timeout configuration',
    severity: 'medium'
  },

  // CA4: Apply Rate Limit - All 4 types
  {
    id: 'UCA4-1',
    controlActionId: 'CA4',
    type: 'not-provided',
    description: 'Rate limit not applied during DDoS attack',
    hazards: ['H3'],
    context: 'Rate limiting disabled or threshold too high',
    severity: 'high'
  },
  {
    id: 'UCA4-2',
    controlActionId: 'CA4',
    type: 'provided',
    description: 'Rate limit applied to legitimate high-volume user',
    hazards: ['H3'],
    context: 'Legitimate business surge or whitelisting failure',
    severity: 'medium'
  },
  {
    id: 'UCA4-3',
    controlActionId: 'CA4',
    type: 'wrong-timing',
    description: 'Rate limit applied after service already degraded',
    hazards: ['H3'],
    context: 'Reactive instead of proactive limiting',
    severity: 'high'
  },
  {
    id: 'UCA4-4',
    controlActionId: 'CA4',
    type: 'wrong-duration',
    description: 'Rate limit applied for excessive duration',
    hazards: ['H3'],
    context: 'No automatic reset or manual intervention required',
    severity: 'medium'
  }
];

// Step 4: Causal Scenarios - Comprehensive coverage for critical UCAs
export const causalScenarios: CausalScenario[] = [
  // Authentication scenarios
  {
    id: 'CS1',
    ucaId: 'UCA1-2',
    description: 'Attacker uses credential stuffing with previously breached passwords',
    causalFactors: [
      'No password complexity enforcement',
      'MFA not required for all accounts',
      'No detection of multiple failed attempts',
      'Password reuse across services'
    ],
    strideCategory: 'Spoofing',
    d4Score: {
      detectability: 3,
      difficulty: 2,
      damage: 5,
      deniability: 4
    },
    mitigations: [
      'Implement mandatory MFA',
      'Deploy credential stuffing detection',
      'Force password reset for suspicious activity',
      'Implement device fingerprinting'
    ],
    confidence: 85
  },
  {
    id: 'CS2',
    ucaId: 'UCA1-3',
    description: 'Session hijacking through expired session reuse',
    causalFactors: [
      'Session tokens not invalidated server-side',
      'Clock drift between servers',
      'Session state not synchronized',
      'Token validation logic flawed'
    ],
    strideCategory: 'Spoofing',
    d4Score: {
      detectability: 2,
      difficulty: 3,
      damage: 4,
      deniability: 3
    },
    mitigations: [
      'Server-side session invalidation',
      'Time synchronization (NTP)',
      'Distributed session management',
      'Short-lived tokens with refresh'
    ],
    confidence: 80
  },
  
  // Transaction scenarios
  {
    id: 'CS3',
    ucaId: 'UCA2-2',
    description: 'Insider manipulates fraud rules to allow malicious transactions',
    causalFactors: [
      'Insufficient segregation of duties',
      'Fraud rule changes not reviewed',
      'No anomaly detection on rule modifications',
      'Excessive privileges for operations staff'
    ],
    strideCategory: 'Tampering',
    d4Score: {
      detectability: 2,
      difficulty: 4,
      damage: 5,
      deniability: 2
    },
    mitigations: [
      'Implement dual control for rule changes',
      'Automated testing of rule modifications',
      'Anomaly detection on configuration changes',
      'Principle of least privilege enforcement'
    ],
    confidence: 90
  },
  {
    id: 'CS4',
    ucaId: 'UCA2-3',
    description: 'Race condition allows transaction on frozen account',
    causalFactors: [
      'Lack of distributed locking',
      'Eventual consistency delays',
      'Missing transaction ordering',
      'Cache invalidation issues'
    ],
    strideCategory: 'Tampering',
    d4Score: {
      detectability: 1,
      difficulty: 4,
      damage: 4,
      deniability: 1
    },
    mitigations: [
      'Implement distributed locks',
      'Strong consistency for critical operations',
      'Transaction sequencing',
      'Real-time cache synchronization'
    ],
    confidence: 75
  },
  
  // IP blocking scenarios
  {
    id: 'CS5',
    ucaId: 'UCA3-3',
    description: 'APT establishes persistence before detection',
    causalFactors: [
      'Limited visibility into encrypted traffic',
      'Insufficient endpoint monitoring',
      'Alert fatigue in SOC',
      'Lack of threat hunting capability'
    ],
    strideCategory: 'Information Disclosure',
    d4Score: {
      detectability: 1,
      difficulty: 5,
      damage: 5,
      deniability: 5
    },
    mitigations: [
      'Deploy advanced EDR solutions',
      'Implement SSL inspection',
      'Automated alert correlation',
      'Regular threat hunting exercises'
    ],
    confidence: 75
  },
  
  // Rate limiting scenarios
  {
    id: 'CS6',
    ucaId: 'UCA4-1',
    description: 'DDoS attack overwhelms service before rate limiting engages',
    causalFactors: [
      'Rate limit thresholds too high',
      'Detection algorithms too slow',
      'Geographic distribution not considered',
      'Botnet detection failures'
    ],
    strideCategory: 'Denial of Service',
    d4Score: {
      detectability: 4,
      difficulty: 2,
      damage: 4,
      deniability: 5
    },
    mitigations: [
      'Dynamic rate limit adjustment',
      'Machine learning for anomaly detection',
      'Geographic rate limiting',
      'Cloud-based DDoS protection'
    ],
    confidence: 85
  }
];

// Helper function to link all data
export function getRelatedData(id: string, type: 'loss' | 'hazard' | 'uca' | 'scenario') {
  const result = {
    losses: [] as Loss[],
    hazards: [] as Hazard[],
    ucas: [] as UCA[],
    scenarios: [] as CausalScenario[]
  };

  switch (type) {
    case 'loss':
      result.hazards = hazards.filter(h => h.relatedLosses.includes(id));
      result.ucas = ucas.filter(u => 
        result.hazards.some(h => u.hazards.includes(h.id))
      );
      result.scenarios = causalScenarios.filter(s => 
        result.ucas.some(u => s.ucaId === u.id)
      );
      break;
    
    case 'hazard':
      result.losses = losses.filter(l => 
        hazards.find(h => h.id === id)?.relatedLosses.includes(l.id)
      );
      result.ucas = ucas.filter(u => u.hazards.includes(id));
      result.scenarios = causalScenarios.filter(s => 
        result.ucas.some(u => s.ucaId === u.id)
      );
      break;
    
    case 'uca':
      const uca = ucas.find(u => u.id === id);
      if (uca) {
        result.hazards = hazards.filter(h => uca.hazards.includes(h.id));
        result.losses = losses.filter(l => 
          result.hazards.some(h => h.relatedLosses.includes(l.id))
        );
        result.scenarios = causalScenarios.filter(s => s.ucaId === id);
      }
      break;
    
    case 'scenario':
      const scenario = causalScenarios.find(s => s.id === id);
      if (scenario) {
        const uca = ucas.find(u => u.id === scenario.ucaId);
        if (uca) {
          result.ucas = [uca];
          result.hazards = hazards.filter(h => uca.hazards.includes(h.id));
          result.losses = losses.filter(l => 
            result.hazards.some(h => h.relatedLosses.includes(l.id))
          );
        }
      }
      break;
  }

  return result;
}