// MAESTRO Analysis Mock Data - Multi-Agent Evaluated Securely Through Rigorous Oversight
// For AI/ML components in the Modern Digital Banking Platform

export interface MaestroAgent {
  id: string;
  name: string;
  type: 'AI Assistant' | 'ML Model' | 'Decision Engine' | 'Automation Agent';
  purpose: string;
  dataAccess: string[];
  capabilities: string[];
  interactions: string[];
  trustLevel: 'untrusted' | 'partially-trusted' | 'trusted' | 'critical';
}

export interface MaestroThreat {
  id: string;
  agentId: string;
  category: 'Adversarial' | 'Data Poisoning' | 'Model Theft' | 'Privacy Breach' | 'Bias' | 'Hallucination';
  threat: string;
  scenario: string;
  likelihood: 'low' | 'medium' | 'high';
  impact: 'low' | 'medium' | 'high' | 'critical';
  detectionDifficulty: 'easy' | 'moderate' | 'hard' | 'very hard';
  mitigations: string[];
  monitoringRequired: string[];
}

export interface MaestroControl {
  id: string;
  name: string;
  type: 'preventive' | 'detective' | 'corrective';
  description: string;
  implementation: string;
  effectiveness: 'low' | 'medium' | 'high';
  coverage: string[];
}

export const maestroAgents: MaestroAgent[] = [
  {
    id: 'MA-001',
    name: 'Customer Service Chatbot',
    type: 'AI Assistant',
    purpose: 'Handle customer inquiries and basic banking operations',
    dataAccess: ['Customer profiles', 'Account balances', 'Transaction history', 'Product information'],
    capabilities: [
      'Natural language understanding',
      'Account balance queries',
      'Transaction disputes initiation',
      'Product recommendations',
      'Appointment scheduling'
    ],
    interactions: ['Customer Portal', 'Mobile App', 'Customer Database', 'Transaction System'],
    trustLevel: 'partially-trusted'
  },
  {
    id: 'MA-002',
    name: 'Fraud Detection Model',
    type: 'ML Model',
    purpose: 'Real-time detection of fraudulent transactions',
    dataAccess: ['Transaction data', 'Customer behavior patterns', 'Device fingerprints', 'Location data'],
    capabilities: [
      'Pattern recognition',
      'Anomaly detection',
      'Risk scoring',
      'Real-time decision making',
      'Adaptive learning'
    ],
    interactions: ['Transaction Processing', 'Risk Management System', 'Alert System', 'Customer Notifications'],
    trustLevel: 'critical'
  },
  {
    id: 'MA-003',
    name: 'Credit Risk Assessor',
    type: 'Decision Engine',
    purpose: 'Automated credit scoring and loan approval decisions',
    dataAccess: ['Credit history', 'Income data', 'Employment records', 'Banking relationships'],
    capabilities: [
      'Credit scoring',
      'Risk assessment',
      'Loan approval recommendations',
      'Interest rate calculation',
      'Compliance checking'
    ],
    interactions: ['Loan Origination System', 'Credit Bureaus', 'Compliance System', 'Decision Audit Trail'],
    trustLevel: 'trusted'
  },
  {
    id: 'MA-004',
    name: 'Investment Advisor Bot',
    type: 'AI Assistant',
    purpose: 'Provide personalized investment recommendations',
    dataAccess: ['Portfolio data', 'Market data', 'Risk profile', 'Financial goals'],
    capabilities: [
      'Portfolio analysis',
      'Market trend analysis',
      'Risk assessment',
      'Recommendation generation',
      'Performance tracking'
    ],
    interactions: ['Trading Platform', 'Market Data Feeds', 'Portfolio Management System', 'Compliance Engine'],
    trustLevel: 'partially-trusted'
  },
  {
    id: 'MA-005',
    name: 'AML Transaction Monitor',
    type: 'ML Model',
    purpose: 'Detect money laundering patterns and suspicious activities',
    dataAccess: ['Transaction networks', 'Customer relationships', 'Geographic data', 'Sanctions lists'],
    capabilities: [
      'Network analysis',
      'Pattern matching',
      'Sanctions screening',
      'Risk categorization',
      'Case prioritization'
    ],
    interactions: ['Transaction System', 'Case Management', 'Regulatory Reporting', 'Investigation Tools'],
    trustLevel: 'critical'
  }
];

export const maestroThreats: MaestroThreat[] = [
  // Customer Service Chatbot Threats
  {
    id: 'MT-001',
    agentId: 'MA-001',
    category: 'Adversarial',
    threat: 'Prompt injection attacks to reveal sensitive data',
    scenario: 'Attacker crafts prompts to make chatbot disclose other customers\' information',
    likelihood: 'high',
    impact: 'high',
    detectionDifficulty: 'moderate',
    mitigations: [
      'Input sanitization and validation',
      'Strict output filtering',
      'Context isolation between conversations',
      'Regular prompt injection testing'
    ],
    monitoringRequired: [
      'Unusual query patterns',
      'Attempts to access unauthorized data',
      'Output anomaly detection'
    ]
  },
  {
    id: 'MT-002',
    agentId: 'MA-001',
    category: 'Hallucination',
    threat: 'Chatbot provides incorrect financial advice',
    scenario: 'AI generates plausible but incorrect information about products or regulations',
    likelihood: 'medium',
    impact: 'high',
    detectionDifficulty: 'hard',
    mitigations: [
      'Retrieval-augmented generation (RAG)',
      'Response verification against knowledge base',
      'Confidence scoring with disclaimers',
      'Human oversight for complex queries'
    ],
    monitoringRequired: [
      'Response accuracy metrics',
      'Customer complaint tracking',
      'Confidence score distribution'
    ]
  },

  // Fraud Detection Model Threats
  {
    id: 'MT-003',
    agentId: 'MA-002',
    category: 'Data Poisoning',
    threat: 'Adversarial training data corrupts fraud detection',
    scenario: 'Attackers inject crafted transactions to train model to ignore specific fraud patterns',
    likelihood: 'low',
    impact: 'critical',
    detectionDifficulty: 'very hard',
    mitigations: [
      'Training data validation and anomaly detection',
      'Ensemble models with different training sets',
      'Regular model performance monitoring',
      'Rollback capabilities'
    ],
    monitoringRequired: [
      'Model drift detection',
      'False negative rate changes',
      'Training data distribution shifts'
    ]
  },
  {
    id: 'MT-004',
    agentId: 'MA-002',
    category: 'Adversarial',
    threat: 'Evasion attacks bypass fraud detection',
    scenario: 'Criminals use adversarial examples to make fraudulent transactions appear legitimate',
    likelihood: 'medium',
    impact: 'high',
    detectionDifficulty: 'hard',
    mitigations: [
      'Adversarial training',
      'Multiple model consensus',
      'Rule-based safety nets',
      'Continuous model updates'
    ],
    monitoringRequired: [
      'Edge case transaction patterns',
      'Model confidence distribution',
      'Manual review sampling'
    ]
  },

  // Credit Risk Assessor Threats
  {
    id: 'MT-005',
    agentId: 'MA-003',
    category: 'Bias',
    threat: 'Discriminatory lending decisions',
    scenario: 'Model exhibits bias against protected groups due to historical data patterns',
    likelihood: 'high',
    impact: 'critical',
    detectionDifficulty: 'moderate',
    mitigations: [
      'Bias testing and fairness metrics',
      'Regular algorithmic audits',
      'Diverse training data',
      'Explainable AI techniques'
    ],
    monitoringRequired: [
      'Demographic approval rates',
      'Fairness metrics tracking',
      'Regulatory compliance checks'
    ]
  },
  {
    id: 'MT-006',
    agentId: 'MA-003',
    category: 'Model Theft',
    threat: 'Reverse engineering of credit scoring algorithm',
    scenario: 'Competitors or criminals extract model logic through API queries',
    likelihood: 'medium',
    impact: 'medium',
    detectionDifficulty: 'moderate',
    mitigations: [
      'API rate limiting',
      'Query pattern detection',
      'Model output perturbation',
      'Legal protections'
    ],
    monitoringRequired: [
      'API usage patterns',
      'Systematic query detection',
      'Unusual access patterns'
    ]
  },

  // Investment Advisor Bot Threats
  {
    id: 'MT-007',
    agentId: 'MA-004',
    category: 'Hallucination',
    threat: 'Incorrect investment recommendations',
    scenario: 'AI provides advice based on misunderstood market conditions or regulations',
    likelihood: 'medium',
    impact: 'high',
    detectionDifficulty: 'moderate',
    mitigations: [
      'Human-in-the-loop for significant recommendations',
      'Regulatory compliance checking',
      'Conservative recommendation boundaries',
      'Clear disclaimers and limitations'
    ],
    monitoringRequired: [
      'Recommendation outcome tracking',
      'Compliance violations',
      'Customer satisfaction metrics'
    ]
  },
  {
    id: 'MT-008',
    agentId: 'MA-004',
    category: 'Privacy Breach',
    threat: 'Cross-customer information leakage',
    scenario: 'AI inadvertently reveals investment strategies of other customers',
    likelihood: 'low',
    impact: 'high',
    detectionDifficulty: 'hard',
    mitigations: [
      'Strict data segregation',
      'Differential privacy techniques',
      'Output sanitization',
      'Regular privacy audits'
    ],
    monitoringRequired: [
      'Output content analysis',
      'Data access patterns',
      'Privacy breach indicators'
    ]
  },

  // AML Transaction Monitor Threats
  {
    id: 'MT-009',
    agentId: 'MA-005',
    category: 'Adversarial',
    threat: 'Money laundering pattern evasion',
    scenario: 'Criminals structure transactions to avoid detection patterns',
    likelihood: 'high',
    impact: 'critical',
    detectionDifficulty: 'very hard',
    mitigations: [
      'Adaptive learning algorithms',
      'Network analysis techniques',
      'Human expert review',
      'Cross-institution intelligence sharing'
    ],
    monitoringRequired: [
      'Novel transaction patterns',
      'False negative analysis',
      'Regulatory feedback loops'
    ]
  },
  {
    id: 'MT-010',
    agentId: 'MA-005',
    category: 'Data Poisoning',
    threat: 'Sanctions list manipulation',
    scenario: 'Attackers compromise data feeds to remove sanctioned entities',
    likelihood: 'low',
    impact: 'critical',
    detectionDifficulty: 'moderate',
    mitigations: [
      'Multiple data source validation',
      'Cryptographic data verification',
      'Historical data comparison',
      'Manual spot checks'
    ],
    monitoringRequired: [
      'Data source integrity',
      'Unusual list changes',
      'Verification failures'
    ]
  },
  // Additional Comprehensive Threats for Demo
  
  // More Fraud Detection Threats
  {
    id: 'MT-011',
    agentId: 'MA-002',
    category: 'Adversarial',
    threat: 'Evasion attacks to bypass fraud detection',
    scenario: 'Attackers use adversarial examples to make fraudulent transactions appear legitimate',
    likelihood: 'high',
    impact: 'critical',
    detectionDifficulty: 'very hard',
    mitigations: [
      'Adversarial training',
      'Input preprocessing and normalization',
      'Ensemble models with diverse architectures',
      'Anomaly detection layers'
    ],
    monitoringRequired: [
      'Model confidence distributions',
      'False negative rate trends',
      'Transaction pattern analysis'
    ]
  },
  {
    id: 'MT-012',
    agentId: 'MA-002',
    category: 'Bias',
    threat: 'Discriminatory fraud flagging based on demographics',
    scenario: 'Model unfairly targets certain demographic groups leading to service denial',
    likelihood: 'medium',
    impact: 'high',
    detectionDifficulty: 'moderate',
    mitigations: [
      'Fairness-aware training',
      'Regular bias audits',
      'Demographic parity constraints',
      'Human review for edge cases'
    ],
    monitoringRequired: [
      'Demographic disparity metrics',
      'False positive rates by group',
      'Customer complaint analysis'
    ]
  },
  
  // More Credit Scoring Threats
  {
    id: 'MT-013',
    agentId: 'MA-003',
    category: 'Privacy Breach',
    threat: 'Model inversion attacks revealing training data',
    scenario: 'Attackers extract sensitive customer financial data from model parameters',
    likelihood: 'low',
    impact: 'critical',
    detectionDifficulty: 'very hard',
    mitigations: [
      'Differential privacy in training',
      'Model parameter encryption',
      'Access control and monitoring',
      'Regular security audits'
    ],
    monitoringRequired: [
      'Model query patterns',
      'Unusual API access attempts',
      'Parameter extraction attempts'
    ]
  },
  {
    id: 'MT-014',
    agentId: 'MA-003',
    category: 'Adversarial',
    threat: 'Credit score manipulation through synthetic data',
    scenario: 'Attackers create synthetic financial histories to manipulate credit scores',
    likelihood: 'medium',
    impact: 'high',
    detectionDifficulty: 'hard',
    mitigations: [
      'Data authenticity verification',
      'Cross-reference with external sources',
      'Synthetic data detection models',
      'Manual review triggers'
    ],
    monitoringRequired: [
      'Data source validation',
      'Unusual score improvements',
      'Synthetic pattern detection'
    ]
  },
  
  // More Investment Advisor Threats
  {
    id: 'MT-015',
    agentId: 'MA-004',
    category: 'Bias',
    threat: 'Biased investment recommendations favoring certain sectors',
    scenario: 'Model systematically recommends investments that benefit specific industries',
    likelihood: 'medium',
    impact: 'medium',
    detectionDifficulty: 'moderate',
    mitigations: [
      'Portfolio diversity requirements',
      'Regular recommendation audits',
      'Multi-objective optimization',
      'Transparency reports'
    ],
    monitoringRequired: [
      'Recommendation distribution',
      'Portfolio performance tracking',
      'Sector allocation patterns'
    ]
  },
  {
    id: 'MT-016',
    agentId: 'MA-004',
    category: 'Adversarial',
    threat: 'Market manipulation through coordinated attacks',
    scenario: 'Attackers manipulate model inputs to cause specific investment recommendations',
    likelihood: 'low',
    impact: 'critical',
    detectionDifficulty: 'hard',
    mitigations: [
      'Market data validation',
      'Anomaly detection in inputs',
      'Human oversight for large trades',
      'Multi-source data verification'
    ],
    monitoringRequired: [
      'Input data anomalies',
      'Recommendation volatility',
      'Market impact analysis'
    ]
  },
  
  // More AML Monitor Threats
  {
    id: 'MT-017',
    agentId: 'MA-005',
    category: 'Privacy Breach',
    threat: 'Unauthorized access to transaction monitoring data',
    scenario: 'Attackers gain access to sensitive transaction patterns and customer relationships',
    likelihood: 'medium',
    impact: 'high',
    detectionDifficulty: 'moderate',
    mitigations: [
      'Strict access controls',
      'Data encryption at rest and in transit',
      'Audit logging',
      'Zero-trust architecture'
    ],
    monitoringRequired: [
      'Access patterns',
      'Data exfiltration attempts',
      'Privilege escalation'
    ]
  },
  {
    id: 'MT-018',
    agentId: 'MA-005',
    category: 'Hallucination',
    threat: 'False positive money laundering alerts',
    scenario: 'Model generates excessive false alerts overwhelming compliance teams',
    likelihood: 'high',
    impact: 'medium',
    detectionDifficulty: 'easy',
    mitigations: [
      'Alert tuning and optimization',
      'Machine learning feedback loops',
      'Risk-based alert prioritization',
      'Continuous model refinement'
    ],
    monitoringRequired: [
      'False positive rates',
      'Alert volume trends',
      'Investigation outcomes'
    ]
  },
  
  // Additional cross-cutting threats
  {
    id: 'MT-019',
    agentId: 'MA-001',
    category: 'Data Poisoning',
    threat: 'Contaminated conversation logs corrupt chatbot training',
    scenario: 'Attackers inject malicious conversations to influence future model behavior',
    likelihood: 'medium',
    impact: 'high',
    detectionDifficulty: 'hard',
    mitigations: [
      'Training data validation',
      'Anomaly detection in conversations',
      'Human review of training samples',
      'Incremental learning controls'
    ],
    monitoringRequired: [
      'Training data quality metrics',
      'Conversation pattern analysis',
      'Model drift detection'
    ]
  },
  {
    id: 'MT-020',
    agentId: 'MA-003',
    category: 'Hallucination',
    threat: 'Unreliable creditworthiness assessments',
    scenario: 'Model provides inconsistent or arbitrary credit decisions',
    likelihood: 'medium',
    impact: 'high',
    detectionDifficulty: 'moderate',
    mitigations: [
      'Decision consistency checks',
      'Explainable AI requirements',
      'Human review for borderline cases',
      'Model calibration'
    ],
    monitoringRequired: [
      'Decision consistency metrics',
      'Appeal rates',
      'Model explanation quality'
    ]
  }
];

export const maestroControls: MaestroControl[] = [
  {
    id: 'MC-001',
    name: 'AI Red Team Testing',
    type: 'detective',
    description: 'Regular adversarial testing of AI systems by security experts',
    implementation: 'Quarterly red team exercises with rotating scenarios',
    effectiveness: 'high',
    coverage: ['MA-001', 'MA-002', 'MA-004']
  },
  {
    id: 'MC-002',
    name: 'Model Versioning and Rollback',
    type: 'corrective',
    description: 'Ability to quickly revert to previous model versions if issues detected',
    implementation: 'Git-based model registry with automated deployment pipelines',
    effectiveness: 'high',
    coverage: ['MA-002', 'MA-003', 'MA-005']
  },
  {
    id: 'MC-003',
    name: 'Differential Privacy',
    type: 'preventive',
    description: 'Mathematical guarantees on individual privacy in training and inference',
    implementation: 'Epsilon-differential privacy with noise injection',
    effectiveness: 'medium',
    coverage: ['MA-001', 'MA-003', 'MA-004']
  },
  {
    id: 'MC-004',
    name: 'Multi-Model Consensus',
    type: 'preventive',
    description: 'Multiple independent models must agree for high-risk decisions',
    implementation: 'Ensemble voting with diversity requirements',
    effectiveness: 'high',
    coverage: ['MA-002', 'MA-003', 'MA-005']
  },
  {
    id: 'MC-005',
    name: 'Explainability Dashboard',
    type: 'detective',
    description: 'Real-time visibility into AI decision-making processes',
    implementation: 'SHAP/LIME integration with monitoring dashboards',
    effectiveness: 'medium',
    coverage: ['MA-003', 'MA-004', 'MA-005']
  },
  {
    id: 'MC-006',
    name: 'Behavioral Drift Detection',
    type: 'detective',
    description: 'Continuous monitoring for changes in model behavior',
    implementation: 'Statistical process control with automated alerts',
    effectiveness: 'high',
    coverage: ['MA-001', 'MA-002', 'MA-003', 'MA-004', 'MA-005']
  }
];

export const getAgentById = (id: string) => maestroAgents.find(agent => agent.id === id);

export const getThreatsByAgent = (agentId: string) => maestroThreats.filter(threat => threat.agentId === agentId);

export const getThreatsByCategory = (category: string) => maestroThreats.filter(threat => threat.category === category);

export const getControlsByAgent = (agentId: string) => maestroControls.filter(control => control.coverage.includes(agentId));

export const getCriticalThreats = () => maestroThreats.filter(threat => threat.impact === 'critical');

export const maestroCategories = [
  { name: 'Adversarial', description: 'Attacks designed to fool or manipulate AI systems', icon: '⚔️' },
  { name: 'Data Poisoning', description: 'Corruption of training or reference data', icon: '☠️' },
  { name: 'Model Theft', description: 'Extraction or reverse engineering of models', icon: '🔓' },
  { name: 'Privacy Breach', description: 'Unauthorized disclosure of private information', icon: '👁️' },
  { name: 'Bias', description: 'Unfair or discriminatory behavior', icon: '⚖️' },
  { name: 'Hallucination', description: 'Generation of false or misleading information', icon: '🌀' }
];