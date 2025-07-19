// LINDDUN Privacy Analysis Mock Data for Modern Digital Banking Platform
// Linkability, Identifiability, Non-repudiation, Detectability, Disclosure of information, Unawareness, Non-compliance

export interface LinddunThreat {
  id: string;
  category: 'Linkability' | 'Identifiability' | 'Non-repudiation' | 'Detectability' | 'Disclosure' | 'Unawareness' | 'Non-compliance';
  dataFlow: string;
  asset: string;
  threat: string;
  scenario: string;
  privacyImpact: 'low' | 'medium' | 'high' | 'critical';
  likelihood: 'low' | 'medium' | 'high';
  affectedParties: string[];
  mitigations: string[];
  gdprArticles?: string[];
  status: 'identified' | 'mitigating' | 'mitigated' | 'accepted';
}

export interface DataFlow {
  id: string;
  name: string;
  source: string;
  destination: string;
  dataTypes: string[];
  purpose: string;
  retention: string;
  encryption: 'none' | 'transit' | 'rest' | 'both';
  accessControl: string;
}

export interface PrivacyControl {
  id: string;
  name: string;
  type: 'technical' | 'organizational' | 'legal';
  description: string;
  effectiveness: 'low' | 'medium' | 'high';
  implementation: string;
  applicableTo: string[];
}

export const dataFlows: DataFlow[] = [
  {
    id: 'DF-001',
    name: 'Customer Registration',
    source: 'Web/Mobile App',
    destination: 'Customer Database',
    dataTypes: ['Name', 'Email', 'Phone', 'Address', 'SSN', 'Date of Birth'],
    purpose: 'Account creation and KYC compliance',
    retention: '7 years after account closure',
    encryption: 'both',
    accessControl: 'Role-based with audit logging'
  },
  {
    id: 'DF-002',
    name: 'Transaction Processing',
    source: 'Customer',
    destination: 'Transaction System',
    dataTypes: ['Account numbers', 'Transaction amounts', 'Merchant info', 'Location', 'Device ID'],
    purpose: 'Payment processing and fraud detection',
    retention: '5 years for compliance',
    encryption: 'both',
    accessControl: 'Strict need-to-know basis'
  },
  {
    id: 'DF-003',
    name: 'Fraud Analytics',
    source: 'Transaction System',
    destination: 'ML Models',
    dataTypes: ['Transaction patterns', 'Device fingerprints', 'Behavioral biometrics', 'Location history'],
    purpose: 'Fraud detection and prevention',
    retention: '2 years rolling window',
    encryption: 'transit',
    accessControl: 'Data science team only'
  },
  {
    id: 'DF-004',
    name: 'Marketing Analytics',
    source: 'Customer Database',
    destination: 'Analytics Platform',
    dataTypes: ['Demographics', 'Product usage', 'Channel preferences', 'Response rates'],
    purpose: 'Personalized marketing and product development',
    retention: '3 years',
    encryption: 'rest',
    accessControl: 'Marketing team with anonymization'
  },
  {
    id: 'DF-005',
    name: 'Third-party Credit Check',
    source: 'Loan Application',
    destination: 'Credit Bureaus',
    dataTypes: ['SSN', 'Income', 'Employment', 'Credit history requests'],
    purpose: 'Credit risk assessment',
    retention: 'As per credit bureau policies',
    encryption: 'transit',
    accessControl: 'API with consent verification'
  }
];

export const linddunThreats: LinddunThreat[] = [
  // Linkability
  {
    id: 'LT-001',
    category: 'Linkability',
    dataFlow: 'DF-003',
    asset: 'Transaction History',
    threat: 'Cross-device tracking links user activities',
    scenario: 'Device fingerprints and behavioral patterns allow linking anonymous sessions to identified users',
    privacyImpact: 'high',
    likelihood: 'high',
    affectedParties: ['Customers', 'Family members'],
    mitigations: [
      'Implement device ID rotation',
      'Use differential privacy for analytics',
      'Separate authentication from analytics tracking',
      'Provide opt-out mechanisms'
    ],
    gdprArticles: ['Art. 5(1)(c) - Data minimization', 'Art. 25 - Privacy by design'],
    status: 'identified'
  },
  {
    id: 'LT-002',
    category: 'Linkability',
    dataFlow: 'DF-004',
    asset: 'Customer Profiles',
    threat: 'Marketing profiles linked across products and channels',
    scenario: 'Comprehensive customer profiles created by linking data from multiple banking products',
    privacyImpact: 'medium',
    likelihood: 'high',
    affectedParties: ['Customers'],
    mitigations: [
      'Implement purpose limitation controls',
      'Use pseudonymization for analytics',
      'Regular profile data reviews',
      'Granular consent management'
    ],
    gdprArticles: ['Art. 5(1)(b) - Purpose limitation', 'Art. 6 - Lawfulness'],
    status: 'mitigating'
  },

  // Identifiability
  {
    id: 'LT-003',
    category: 'Identifiability',
    dataFlow: 'DF-001',
    asset: 'Customer PII',
    threat: 'Re-identification from anonymized datasets',
    scenario: 'Supposedly anonymized transaction data can be re-identified using auxiliary information',
    privacyImpact: 'critical',
    likelihood: 'medium',
    affectedParties: ['Customers', 'Beneficiaries'],
    mitigations: [
      'Use k-anonymity with k≥5',
      'Implement l-diversity for sensitive attributes',
      'Regular re-identification risk assessments',
      'Limit data granularity in exports'
    ],
    gdprArticles: ['Art. 32 - Security of processing', 'Art. 5(1)(f) - Integrity'],
    status: 'mitigating'
  },
  {
    id: 'LT-004',
    category: 'Identifiability',
    dataFlow: 'DF-005',
    asset: 'Credit Check Data',
    threat: 'Third-party data broker aggregation',
    scenario: 'Credit bureaus aggregate data from multiple banks creating comprehensive profiles',
    privacyImpact: 'high',
    likelihood: 'high',
    affectedParties: ['Customers', 'Co-applicants'],
    mitigations: [
      'Minimize shared data fields',
      'Implement data sharing agreements',
      'Regular third-party audits',
      'Customer data portability rights'
    ],
    gdprArticles: ['Art. 26 - Joint controllers', 'Art. 28 - Processors'],
    status: 'identified'
  },

  // Non-repudiation
  {
    id: 'LT-005',
    category: 'Non-repudiation',
    dataFlow: 'DF-002',
    asset: 'Transaction Logs',
    threat: 'Permanent transaction records without right to deletion',
    scenario: 'Legal requirements prevent deletion of transaction history even upon customer request',
    privacyImpact: 'medium',
    likelihood: 'high',
    affectedParties: ['Customers', 'Merchants'],
    mitigations: [
      'Clear retention policy communication',
      'Partial anonymization after legal period',
      'Segregated archive storage',
      'Transparent data lifecycle management'
    ],
    gdprArticles: ['Art. 17 - Right to erasure', 'Art. 5(1)(e) - Storage limitation'],
    status: 'accepted'
  },

  // Detectability
  {
    id: 'LT-006',
    category: 'Detectability',
    dataFlow: 'DF-003',
    asset: 'Behavioral Patterns',
    threat: 'Customer behavior profiling and prediction',
    scenario: 'ML models detect and predict customer financial behaviors and life events',
    privacyImpact: 'high',
    likelihood: 'high',
    affectedParties: ['Customers'],
    mitigations: [
      'Explainable AI requirements',
      'Opt-in for behavioral analysis',
      'Regular model bias audits',
      'Transparent profiling notices'
    ],
    gdprArticles: ['Art. 22 - Automated decision-making', 'Art. 13 - Information to be provided'],
    status: 'mitigating'
  },
  {
    id: 'LT-007',
    category: 'Detectability',
    dataFlow: 'DF-004',
    asset: 'Marketing Preferences',
    threat: 'Inference of sensitive characteristics',
    scenario: 'Marketing analytics infer protected characteristics from banking behavior',
    privacyImpact: 'critical',
    likelihood: 'medium',
    affectedParties: ['Customers', 'Household members'],
    mitigations: [
      'Prohibit sensitive attribute inference',
      'Regular fairness testing',
      'Strict purpose limitation',
      'Ethics review board'
    ],
    gdprArticles: ['Art. 9 - Special categories of data', 'Art. 5(1)(a) - Fairness'],
    status: 'mitigating'
  },

  // Disclosure
  {
    id: 'LT-008',
    category: 'Disclosure',
    dataFlow: 'DF-001',
    asset: 'Customer Database',
    threat: 'Data breach exposing full customer records',
    scenario: 'Cyberattack or insider threat leads to mass customer data exposure',
    privacyImpact: 'critical',
    likelihood: 'low',
    affectedParties: ['All customers', 'Employees'],
    mitigations: [
      'Encryption at rest with HSM',
      'Database activity monitoring',
      'Privileged access management',
      'Incident response plan'
    ],
    gdprArticles: ['Art. 32 - Security', 'Art. 33 - Breach notification'],
    status: 'mitigated'
  },
  {
    id: 'LT-009',
    category: 'Disclosure',
    dataFlow: 'DF-005',
    asset: 'Income Data',
    threat: 'Unauthorized employee access to financial records',
    scenario: 'Employees access customer financial data for personal reasons',
    privacyImpact: 'high',
    likelihood: 'medium',
    affectedParties: ['High-net-worth customers', 'Public figures'],
    mitigations: [
      'Need-to-know access controls',
      'VIP customer data segregation',
      'Access logging and monitoring',
      'Regular access reviews'
    ],
    gdprArticles: ['Art. 5(1)(f) - Confidentiality', 'Art. 32 - Security measures'],
    status: 'mitigating'
  },

  // Unawareness
  {
    id: 'LT-010',
    category: 'Unawareness',
    dataFlow: 'DF-003',
    asset: 'Fraud Detection Models',
    threat: 'Hidden profiling for risk assessment',
    scenario: 'Customers unaware of extensive behavioral profiling for fraud and credit decisions',
    privacyImpact: 'medium',
    likelihood: 'high',
    affectedParties: ['All customers'],
    mitigations: [
      'Clear privacy notices',
      'Profiling transparency dashboard',
      'Regular privacy communications',
      'Easy-to-understand explanations'
    ],
    gdprArticles: ['Art. 12 - Transparent information', 'Art. 13-14 - Information provisions'],
    status: 'identified'
  },
  {
    id: 'LT-011',
    category: 'Unawareness',
    dataFlow: 'DF-004',
    asset: 'Marketing Lists',
    threat: 'Invisible data sharing with partners',
    scenario: 'Customer data shared with insurance and investment subsidiaries without clear consent',
    privacyImpact: 'high',
    likelihood: 'medium',
    affectedParties: ['Customers'],
    mitigations: [
      'Explicit consent mechanisms',
      'Data sharing transparency report',
      'Preference center with granular controls',
      'Regular consent renewal'
    ],
    gdprArticles: ['Art. 7 - Conditions for consent', 'Art. 13(1)(e) - Recipients'],
    status: 'mitigating'
  },

  // Non-compliance
  {
    id: 'LT-012',
    category: 'Non-compliance',
    dataFlow: 'DF-001',
    asset: 'International Transfers',
    threat: 'Cross-border data transfers without adequate protection',
    scenario: 'Customer data processed in countries without adequate data protection laws',
    privacyImpact: 'critical',
    likelihood: 'medium',
    affectedParties: ['EU customers', 'International customers'],
    mitigations: [
      'Standard contractual clauses',
      'Data localization for EU customers',
      'Transfer impact assessments',
      'Binding corporate rules'
    ],
    gdprArticles: ['Chapter V - International transfers', 'Art. 46 - Appropriate safeguards'],
    status: 'mitigating'
  },
  {
    id: 'LT-013',
    category: 'Non-compliance',
    dataFlow: 'DF-002',
    asset: 'Children\'s Data',
    threat: 'Processing minors\' data without parental consent',
    scenario: 'Teen banking apps collect data without proper age verification or parental consent',
    privacyImpact: 'critical',
    likelihood: 'low',
    affectedParties: ['Minor customers', 'Parents'],
    mitigations: [
      'Age verification mechanisms',
      'Parental consent workflows',
      'Limited data collection for minors',
      'Special protection measures'
    ],
    gdprArticles: ['Art. 8 - Child\'s consent', 'Art. 12 - Transparent information'],
    status: 'mitigated'
  }
];

export const privacyControls: PrivacyControl[] = [
  {
    id: 'PC-001',
    name: 'Privacy by Design Framework',
    type: 'organizational',
    description: 'Embed privacy considerations into all system design and development',
    effectiveness: 'high',
    implementation: 'Privacy impact assessments, design reviews, privacy champions',
    applicableTo: ['All data flows']
  },
  {
    id: 'PC-002',
    name: 'Consent Management Platform',
    type: 'technical',
    description: 'Centralized system for managing customer privacy preferences and consent',
    effectiveness: 'high',
    implementation: 'Granular consent options, version tracking, easy withdrawal',
    applicableTo: ['DF-001', 'DF-004', 'DF-005']
  },
  {
    id: 'PC-003',
    name: 'Data Minimization Engine',
    type: 'technical',
    description: 'Automated tools to enforce collection of minimum necessary data',
    effectiveness: 'medium',
    implementation: 'API filters, form validation, retention automation',
    applicableTo: ['All data flows']
  },
  {
    id: 'PC-004',
    name: 'Privacy Rights Portal',
    type: 'technical',
    description: 'Self-service portal for customers to exercise GDPR rights',
    effectiveness: 'high',
    implementation: 'Access, rectification, deletion, portability workflows',
    applicableTo: ['All data flows']
  },
  {
    id: 'PC-005',
    name: 'Third-party Risk Management',
    type: 'organizational',
    description: 'Comprehensive program for managing privacy risks from vendors',
    effectiveness: 'medium',
    implementation: 'Vendor assessments, contracts, ongoing monitoring',
    applicableTo: ['DF-005']
  }
];

export const getThreatsByCategory = (category: string) => 
  linddunThreats.filter(threat => threat.category === category);

export const getThreatsByDataFlow = (dataFlowId: string) => 
  linddunThreats.filter(threat => threat.dataFlow === dataFlowId);

export const getCriticalThreats = () => 
  linddunThreats.filter(threat => threat.privacyImpact === 'critical');

export const getDataFlowById = (id: string) => 
  dataFlows.find(flow => flow.id === id);

export const linddunCategories = [
  { name: 'Linkability', icon: '🔗', description: 'Ability to link data/actions to the same person' },
  { name: 'Identifiability', icon: '👤', description: 'Ability to identify a person from data' },
  { name: 'Non-repudiation', icon: '📝', description: 'Inability to deny actions/data' },
  { name: 'Detectability', icon: '👁️', description: 'Ability to detect existence of data/actions' },
  { name: 'Disclosure', icon: '📢', description: 'Unauthorized access to information' },
  { name: 'Unawareness', icon: '🙈', description: 'Lack of awareness about data processing' },
  { name: 'Non-compliance', icon: '⚖️', description: 'Violation of privacy regulations' }
];