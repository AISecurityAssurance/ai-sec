export interface Stakeholder {
  id: string;
  name: string;
  type: 'primary' | 'secondary' | 'threat-actor';
  interest: string;
  influence: 'low' | 'medium' | 'high' | 'critical';
  expectations?: string[];
  capabilities?: string[];
  motivation?: string;
}

export const primaryStakeholders: Stakeholder[] = [
  {
    id: 'PS1',
    name: 'End Users (Account Holders)',
    type: 'primary',
    interest: 'Secure access to accounts, reliable transactions, data privacy',
    influence: 'high',
    expectations: [
      '24/7 access to banking services',
      'Protection of personal and financial data',
      'Fast and reliable transaction processing',
      'Clear communication about security measures'
    ]
  },
  {
    id: 'PS2',
    name: 'Bank Management',
    type: 'primary',
    interest: 'Profitability, regulatory compliance, reputation management',
    influence: 'critical',
    expectations: [
      'System meets business objectives',
      'Compliance with all regulations',
      'Minimal security incidents',
      'Cost-effective security measures'
    ]
  },
  {
    id: 'PS3',
    name: 'System Administrators',
    type: 'primary',
    interest: 'System stability, manageable complexity, clear procedures',
    influence: 'high',
    expectations: [
      'Clear security policies and procedures',
      'Adequate tools for monitoring and response',
      'Reasonable workload and on-call requirements',
      'Professional development opportunities'
    ]
  },
  {
    id: 'PS4',
    name: 'Security Team',
    type: 'primary',
    interest: 'Threat prevention, incident response capability, security posture',
    influence: 'high',
    expectations: [
      'Comprehensive threat visibility',
      'Effective security controls',
      'Rapid incident response capabilities',
      'Management support for security initiatives'
    ]
  }
];

export const secondaryStakeholders: Stakeholder[] = [
  {
    id: 'SS1',
    name: 'Regulatory Bodies (e.g., FDIC, OCC)',
    type: 'secondary',
    interest: 'Compliance, consumer protection, financial system stability',
    influence: 'critical',
    expectations: [
      'Full compliance with banking regulations',
      'Regular security audits and assessments',
      'Prompt incident reporting',
      'Consumer protection measures'
    ]
  },
  {
    id: 'SS2',
    name: 'Third-party Payment Processors',
    type: 'secondary',
    interest: 'API stability, transaction volume, secure integration',
    influence: 'medium',
    expectations: [
      'Stable and well-documented APIs',
      'Predictable transaction volumes',
      'Secure data exchange protocols',
      'Clear SLAs and support'
    ]
  },
  {
    id: 'SS3',
    name: 'Banking Partners',
    type: 'secondary',
    interest: 'Interoperability, shared security standards, risk management',
    influence: 'high',
    expectations: [
      'Adherence to industry security standards',
      'Secure interconnection protocols',
      'Collaborative incident response',
      'Regular security information sharing'
    ]
  },
  {
    id: 'SS4',
    name: 'Insurance Providers',
    type: 'secondary',
    interest: 'Risk assessment, claim minimization, compliance verification',
    influence: 'medium',
    expectations: [
      'Regular security assessments',
      'Implementation of required controls',
      'Prompt incident notification',
      'Risk mitigation measures'
    ]
  },
  {
    id: 'SS5',
    name: 'Technology Vendors',
    type: 'secondary',
    interest: 'Product deployment, support requirements, reference customers',
    influence: 'low',
    expectations: [
      'Proper product implementation',
      'Regular updates and patches',
      'Feedback for product improvement',
      'Success story opportunities'
    ]
  }
];

export const threatActors: Stakeholder[] = [
  {
    id: 'TA1',
    name: 'Nation-State APT Groups',
    type: 'threat-actor',
    interest: 'Financial gain, economic disruption, intelligence gathering',
    influence: 'critical',
    motivation: 'Strategic advantage, economic warfare, intelligence collection',
    capabilities: [
      'Zero-day exploits',
      'Advanced persistent threats',
      'Supply chain compromises',
      'Long-term undetected presence'
    ]
  },
  {
    id: 'TA2',
    name: 'Organized Cybercrime Syndicates',
    type: 'threat-actor',
    interest: 'Direct financial theft, ransomware, data sale',
    influence: 'high',
    motivation: 'Monetary gain through theft, extortion, or fraud',
    capabilities: [
      'Ransomware deployment',
      'Banking trojans',
      'Money laundering networks',
      'Credential theft operations'
    ]
  },
  {
    id: 'TA3',
    name: 'Malicious Insiders',
    type: 'threat-actor',
    interest: 'Personal gain, revenge, espionage',
    influence: 'high',
    motivation: 'Financial gain, grievance, coercion',
    capabilities: [
      'Privileged access abuse',
      'Knowledge of security controls',
      'Physical access to systems',
      'Social engineering of colleagues'
    ]
  },
  {
    id: 'TA4',
    name: 'Hacktivist Groups',
    type: 'threat-actor',
    interest: 'Public embarrassment, service disruption, data leaks',
    influence: 'medium',
    motivation: 'Ideological or political causes',
    capabilities: [
      'DDoS attacks',
      'Website defacement',
      'Data exfiltration and leaks',
      'Social media campaigns'
    ]
  },
  {
    id: 'TA5',
    name: 'Script Kiddies/Opportunists',
    type: 'threat-actor',
    interest: 'Notoriety, practice, opportunistic gains',
    influence: 'low',
    motivation: 'Recognition, learning, small financial gains',
    capabilities: [
      'Automated scanning tools',
      'Known exploit usage',
      'Basic social engineering',
      'Cryptocurrency mining'
    ]
  }
];

export const allStakeholders = [...primaryStakeholders, ...secondaryStakeholders, ...threatActors];