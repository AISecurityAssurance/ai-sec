// Sample analysis data for "View Sample Results" mode
// This shows what a completed analysis would look like without AI processing

export interface SampleAnalysisSection {
  id: string;
  title: string;
  content: any;
  type: 'table' | 'text' | 'list' | 'diagram';
}

export interface SampleAnalysisData {
  [framework: string]: {
    [sectionId: string]: SampleAnalysisSection;
  };
}

export const sampleAnalysisData: SampleAnalysisData = {
  'stpa-sec': {
    'stakeholders': {
      id: 'stakeholders',
      title: 'System Stakeholders',
      type: 'table',
      content: {
        headers: ['Stakeholder', 'Role', 'Security Concerns', 'Access Level'],
        rows: [
          ['Bank Customers', 'End Users', 'Account security, privacy', 'Limited'],
          ['Bank Employees', 'Operations', 'Internal fraud prevention', 'Elevated'],
          ['System Administrators', 'Maintenance', 'System integrity', 'Full'],
          ['Regulatory Bodies', 'Compliance', 'Data protection, AML', 'Audit'],
          ['Third-party Providers', 'Integration', 'API security', 'Restricted']
        ]
      }
    },
    'losses': {
      id: 'losses',
      title: 'Identified Losses',
      type: 'table',
      content: {
        headers: ['Loss ID', 'Description', 'Impact', 'Severity'],
        rows: [
          ['L1', 'Unauthorized access to customer financial data', 'Data breach, regulatory fines', 'Critical'],
          ['L2', 'Financial fraud through compromised accounts', 'Financial loss, reputation damage', 'Critical'],
          ['L3', 'Service unavailability during peak trading hours', 'Revenue loss, customer dissatisfaction', 'High'],
          ['L4', 'Manipulation of investment portfolio data', 'Incorrect financial decisions', 'High'],
          ['L5', 'Payment processing failures', 'Transaction failures, merchant penalties', 'Medium'],
        ]
      }
    },
    'hazards': {
      id: 'hazards',
      title: 'Security Hazards/Vulnerabilities',
      type: 'table',
      content: {
        headers: ['Hazard ID', 'Description', 'Related Loss', 'Likelihood'],
        rows: [
          ['H1', 'Weak authentication mechanisms', 'L1, L2', 'High'],
          ['H2', 'Unencrypted data transmission', 'L1', 'Medium'],
          ['H3', 'SQL injection vulnerabilities', 'L1, L4', 'High'],
          ['H4', 'Insufficient API rate limiting', 'L3', 'Medium'],
          ['H5', 'Lack of input validation', 'L2, L4', 'High'],
        ]
      }
    },
    'system-description': {
      id: 'system-description',
      title: 'System Description',
      type: 'text',
      content: `The financial services platform consists of multiple interconnected components:
      
• **Frontend Layer**: Web and mobile applications with React/React Native
• **API Gateway**: Kong-based gateway handling authentication and rate limiting
• **Core Banking Services**: Microservices handling accounts, transactions, and balances
• **Investment Module**: Real-time portfolio management with market data feeds
• **Payment Gateway**: Multi-currency payment processing with PCI DSS compliance
• **Data Analytics**: Customer behavior analysis and fraud detection
• **External Integrations**: APIs to credit bureaus, payment networks, and market data providers

The system processes over 50,000 transactions daily with 99.9% uptime requirement.`
    },
    'control-structure': {
      id: 'control-structure',
      title: 'Control Structure',
      type: 'diagram',
      content: {
        description: 'Hierarchical control structure showing system components and their interactions',
        elements: [
          'User Interface Layer → API Gateway',
          'API Gateway → Authentication Service',
          'API Gateway → Core Banking Services',
          'Core Banking → Database Cluster',
          'Investment Module → Market Data Feeds',
          'Payment Gateway → Payment Networks'
        ]
      }
    },
    'controllers': {
      id: 'controllers',
      title: 'System Controllers',
      type: 'table',
      content: {
        headers: ['Controller', 'Responsibilities', 'Control Actions', 'Feedback'],
        rows: [
          ['Authentication Service', 'User identity verification', 'Grant/Deny access', 'Login attempts, MFA status'],
          ['Authorization Service', 'Permission management', 'Allow/Block operations', 'Access logs, violations'],
          ['Fraud Detection Engine', 'Transaction monitoring', 'Flag/Block transactions', 'Risk scores, patterns'],
          ['Security Operations Center', 'Threat monitoring', 'Incident response', 'Alerts, metrics']
        ]
      }
    },
    'control-actions': {
      id: 'control-actions',
      title: 'Control Actions',
      type: 'list',
      content: [
        '**Authentication Control**: Verify user credentials, enforce MFA',
        '**Authorization Control**: Check permissions for requested operations',
        '**Transaction Control**: Validate and approve financial transactions',
        '**Data Access Control**: Encrypt and control access to sensitive data',
        '**Session Control**: Manage user sessions and timeouts',
        '**Audit Control**: Log all security-relevant events'
      ]
    },
    'ucas': {
      id: 'ucas',
      title: 'Unsafe/Unsecure Control Actions',
      type: 'table',
      content: {
        headers: ['UCA ID', 'Control Action', 'Context', 'Type', 'Hazard Link'],
        rows: [
          ['UCA-1', 'Grant authentication', 'Invalid credentials', 'Provided unsafely', 'H1'],
          ['UCA-2', 'Not blocking transaction', 'Fraudulent pattern detected', 'Not provided', 'H2'],
          ['UCA-3', 'Session timeout', 'Active user operation', 'Wrong timing', 'H3'],
          ['UCA-4', 'API rate limiting', 'Legitimate high volume', 'Too soon', 'H4']
        ]
      }
    },
    'scenarios': {
      id: 'scenarios',
      title: 'Causal Scenarios',
      type: 'list',
      content: [
        '**Scenario 1**: Attacker exploits weak password policy → Brute force attack → Account compromise',
        '**Scenario 2**: Malicious insider disables logging → Performs unauthorized actions → Goes undetected',
        '**Scenario 3**: API vulnerability → Token replay attack → Unauthorized data access',
        '**Scenario 4**: Phishing campaign → Credential theft → Account takeover → Financial fraud'
      ]
    },
    'wargaming': {
      id: 'wargaming',
      title: 'Wargaming Results',
      type: 'text',
      content: 'Red team exercises identified critical vulnerabilities:\n\n• Social engineering attacks had 65% success rate\n• API endpoints vulnerable to rate limit bypass\n• Insider threat detection needs improvement\n• Recovery procedures need automation\n\nBlue team successfully defended against:\n• Direct infrastructure attacks\n• Known malware variants\n• Standard SQL injection attempts'
    }
  },
  'stride': {
    'overview': {
      id: 'overview',
      title: 'STRIDE Analysis Overview',
      type: 'text',
      content: 'STRIDE threat modeling for the financial services platform identified 47 threats across 6 categories. Critical findings include authentication vulnerabilities and data exposure risks. The analysis covers all system boundaries and data flows.'
    },
    'threats': {
      id: 'threats',
      title: 'Identified Threats',
      type: 'table',
      content: {
        headers: ['Threat', 'Category', 'Component', 'Risk Level', 'Mitigation'],
        rows: [
          ['Spoofing user identity', 'Spoofing', 'Authentication Service', 'High', 'Implement MFA, strong session management'],
          ['API request tampering', 'Tampering', 'API Gateway', 'Medium', 'Use HMAC signatures, TLS encryption'],
          ['Transaction repudiation', 'Repudiation', 'Payment Gateway', 'High', 'Implement audit logs, digital signatures'],
          ['Information disclosure', 'Information Disclosure', 'Database', 'Critical', 'Encrypt data at rest, implement access controls'],
          ['DDoS attacks', 'Denial of Service', 'Web Application', 'Medium', 'Rate limiting, CDN, auto-scaling'],
          ['Privilege escalation', 'Elevation of Privilege', 'User Management', 'High', 'RBAC, principle of least privilege'],
        ]
      }
    },
    'data-flow': {
      id: 'data-flow',
      title: 'Data Flow Analysis',
      type: 'list',
      content: [
        'User Authentication Flow: User → Web App → API Gateway → Auth Service → Database',
        'Payment Processing: User → Payment UI → Payment Gateway → Payment Processor → Bank API',
        'Investment Data: Market API → Data Ingestion → Processing → Portfolio Service → User Dashboard',
        'Analytics Pipeline: Transaction Data → ETL → Data Warehouse → Analytics Engine → Reports'
      ]
    },
    'mitigations': {
      id: 'mitigations',
      title: 'Threat Mitigations',
      type: 'list',
      content: [
        '**Multi-Factor Authentication**: Implement TOTP/SMS/Biometric MFA for all users',
        '**API Security**: Deploy API gateway with rate limiting and signature verification',
        '**Encryption**: TLS 1.3 for transit, AES-256 for data at rest',
        '**Audit Logging**: Comprehensive logging with tamper-proof storage',
        '**Network Segmentation**: Isolate critical services in separate VLANs',
        '**Security Headers**: Implement CSP, HSTS, X-Frame-Options'
      ]
    }
  },
  'pasta': {
    'overview': {
      id: 'overview',
      title: 'PASTA Analysis Overview',
      type: 'text',
      content: 'Process for Attack Simulation and Threat Analysis (PASTA) performed on the financial platform. Seven-stage analysis identified business risks, technical vulnerabilities, and attack scenarios. Focus on risk-centric threat modeling aligned with business objectives.'
    },
    'business-objectives': {
      id: 'business-objectives',
      title: 'Business Objectives',
      type: 'list',
      content: [
        'Maintain 99.9% uptime for critical financial services',
        'Ensure PCI DSS compliance for payment processing',
        'Protect customer financial data from breaches',
        'Prevent financial fraud and unauthorized transactions',
        'Maintain SOC 2 certification for security controls',
        'Enable secure third-party integrations'
      ]
    },
    'technical-scope': {
      id: 'technical-scope',
      title: 'Technical Scope',
      type: 'text',
      content: `**In Scope:**
• Web and mobile applications
• API Gateway and microservices
• Database systems (PostgreSQL, Redis)
• Payment processing infrastructure
• Third-party API integrations

**Out of Scope:**
• Physical security of data centers
• End-user device security
• Third-party service internals`
    },
    'threat-analysis': {
      id: 'threat-analysis',
      title: 'Threat Analysis',
      type: 'table',
      content: {
        headers: ['Attack Vector', 'Threat Actor', 'Impact', 'Probability'],
        rows: [
          ['Credential stuffing', 'External attackers', 'Account takeover', 'High'],
          ['API abuse', 'Malicious users', 'Service degradation', 'Medium'],
          ['Insider threat', 'Malicious employee', 'Data exfiltration', 'Low'],
          ['Supply chain attack', 'APT groups', 'System compromise', 'Medium'],
          ['Social engineering', 'Fraudsters', 'Financial fraud', 'High']
        ]
      }
    },
    'stages': {
      id: 'stages',
      title: 'PASTA Attack Stages',
      type: 'table',
      content: {
        headers: ['Stage', 'Activity', 'Key Findings'],
        rows: [
          ['Stage 1', 'Define Business Objectives', 'Financial integrity, regulatory compliance critical'],
          ['Stage 2', 'Define Technical Scope', 'Web/mobile apps, APIs, databases in scope'],
          ['Stage 3', 'Application Decomposition', '127 components, 45 data flows identified'],
          ['Stage 4', 'Threat Analysis', '89 relevant threats from threat intelligence'],
          ['Stage 5', 'Vulnerability Analysis', '23 high-risk vulnerabilities found'],
          ['Stage 6', 'Attack Modeling', '15 viable attack paths identified'],
          ['Stage 7', 'Risk Analysis', '8 critical risks requiring immediate action']
        ]
      }
    },
    'mitigations': {
      id: 'mitigations',
      title: 'Countermeasures',
      type: 'list',
      content: [
        '**Application Security**: Input validation, output encoding, parameterized queries',
        '**Access Control**: Zero-trust architecture, principle of least privilege',
        '**Monitoring**: Real-time threat detection with ML-based anomaly detection',
        '**Incident Response**: 24/7 SOC with automated response playbooks'
      ]
    }
  },
  'dread': {
    'overview': {
      id: 'overview',
      title: 'DREAD Risk Assessment Overview',
      type: 'text',
      content: 'DREAD risk assessment methodology applied to identified vulnerabilities. Scoring based on Damage potential, Reproducibility, Exploitability, Affected users, and Discoverability. Total of 32 risks assessed with 5 critical, 12 high, 10 medium, and 5 low severity findings.'
    },
    'risk-assessment': {
      id: 'risk-assessment',
      title: 'DREAD Risk Assessment',
      type: 'table',
      content: {
        headers: ['Threat', 'Damage', 'Reproducibility', 'Exploitability', 'Affected Users', 'Discoverability', 'Total Score'],
        rows: [
          ['SQL Injection', '10', '8', '7', '10', '8', '43/50 (Critical)'],
          ['Weak Authentication', '9', '10', '9', '10', '9', '47/50 (Critical)'],
          ['XSS Attacks', '6', '8', '8', '7', '9', '38/50 (High)'],
          ['API Rate Limiting Bypass', '5', '7', '6', '8', '7', '33/50 (Medium)'],
          ['Session Hijacking', '8', '6', '7', '8', '6', '35/50 (High)']
        ]
      }
    },
    'ratings': {
      id: 'ratings',
      title: 'Risk Ratings Summary',
      type: 'text',
      content: '**Critical Risks (5)**: Require immediate remediation\n**High Risks (12)**: Address within 30 days\n**Medium Risks (10)**: Address within 90 days\n**Low Risks (5)**: Address in next release cycle\n\nAverage DREAD score: 36.5/50\nHighest risk area: Authentication and session management'
    },
    'distribution': {
      id: 'distribution',
      title: 'Risk Distribution',
      type: 'list',
      content: [
        'Authentication System: 4 critical, 3 high risks',
        'Payment Processing: 1 critical, 5 high risks',
        'API Gateway: 3 high, 4 medium risks',
        'Data Storage: 2 high, 3 medium risks',
        'Third-party Integrations: 2 high, 3 medium risks'
      ]
    }
  },
  'maestro': {
    'overview': {
      id: 'overview',
      title: 'MAESTRO Analysis Overview',
      type: 'text',
      content: 'MAESTRO framework analysis focusing on AI/ML components in the financial platform. Identified threats specific to machine learning models used for fraud detection, risk scoring, and customer behavior analysis. Special attention to model security and data privacy.'
    },
    'ai-ml-threats': {
      id: 'ai-ml-threats',
      title: 'AI/ML Security Threats',
      type: 'table',
      content: {
        headers: ['Threat', 'Target Component', 'Attack Method', 'Mitigation'],
        rows: [
          ['Model Poisoning', 'Fraud Detection ML', 'Training data manipulation', 'Data validation, anomaly detection'],
          ['Adversarial Inputs', 'Risk Scoring Model', 'Crafted inputs to bypass detection', 'Input sanitization, model hardening'],
          ['Model Extraction', 'Credit Scoring API', 'Repeated queries to steal model', 'Rate limiting, query analysis'],
          ['Privacy Inference', 'Customer Analytics', 'Extract PII from model outputs', 'Differential privacy, output filtering']
        ]
      }
    },
    'analysis': {
      id: 'analysis',
      title: 'AI/ML Threat Analysis',
      type: 'table',
      content: {
        headers: ['Component', 'ML Model Type', 'Threat Vector', 'Risk Level'],
        rows: [
          ['Fraud Detection', 'Neural Network', 'Adversarial examples', 'High'],
          ['Credit Scoring', 'Random Forest', 'Data poisoning', 'Critical'],
          ['Customer Segmentation', 'K-means Clustering', 'Privacy inference', 'Medium'],
          ['Anomaly Detection', 'Autoencoder', 'Model inversion', 'High'],
          ['Transaction Classification', 'SVM', 'Membership inference', 'Medium']
        ]
      }
    }
  },
  'linddun': {
    'overview': {
      id: 'overview',
      title: 'LINDDUN Privacy Analysis Overview',
      type: 'text',
      content: 'LINDDUN privacy threat modeling revealed 28 privacy threats across the financial platform. Analysis focused on personal data flows, user tracking, and compliance with GDPR/CCPA requirements. Critical findings in data linkability and user unawareness categories.'
    },
    'privacy-threats': {
      id: 'privacy-threats',
      title: 'Privacy Threat Analysis',
      type: 'table',
      content: {
        headers: ['Privacy Threat', 'Data Type', 'Impact', 'Mitigation Strategy'],
        rows: [
          ['Linkability', 'Transaction History', 'User profiling', 'Data minimization, pseudonymization'],
          ['Identifiability', 'Account Information', 'Identity theft', 'Encryption, access controls'],
          ['Non-repudiation', 'Financial Transactions', 'Cannot deny actions', 'Privacy-preserving logs'],
          ['Detectability', 'User Behavior', 'Activity monitoring', 'Traffic padding, randomization'],
          ['Disclosure', 'Personal Financial Data', 'Data breach', 'Encryption, secure channels'],
          ['Unawareness', 'Data Collection', 'Unknown tracking', 'Privacy notices, consent'],
          ['Non-compliance', 'GDPR/CCPA', 'Regulatory fines', 'Privacy by design, audits']
        ]
      }
    }
  },
  'hazop': {
    'overview': {
      id: 'overview',
      title: 'HAZOP Study Overview',
      type: 'text',
      content: 'Hazard and Operability Study conducted on critical system processes. Systematic examination using guide words identified 42 deviations with potential security impact. Focus on authentication flows, payment processing, and data synchronization processes.'
    },
    'deviations': {
      id: 'deviations',
      title: 'Process Deviations Analysis',
      type: 'table',
      content: {
        headers: ['Parameter', 'Guide Word', 'Deviation', 'Cause', 'Consequence', 'Safeguard'],
        rows: [
          ['Authentication', 'No', 'No authentication', 'Service bypass', 'Unauthorized access', 'Enforce auth middleware'],
          ['Data Flow', 'More', 'Excessive requests', 'DDoS attack', 'Service unavailable', 'Rate limiting, WAF'],
          ['Encryption', 'Less', 'Weak encryption', 'Legacy protocols', 'Data exposure', 'TLS 1.3 enforcement'],
          ['Authorization', 'Other Than', 'Wrong permissions', 'RBAC misconfiguration', 'Privilege escalation', 'Regular audits'],
          ['Transaction', 'Late', 'Delayed processing', 'System overload', 'Failed payments', 'Queue monitoring, scaling']
        ]
      }
    }
  },
  'octave': {
    'overview': {
      id: 'overview',
      title: 'OCTAVE Assessment Overview',
      type: 'text',
      content: 'Operationally Critical Threat, Asset, and Vulnerability Evaluation completed for the financial platform. Risk-based assessment identified 15 critical assets, 23 relevant threats, and 31 vulnerabilities. Organizational and technical perspectives integrated for comprehensive risk picture.'
    },
    'critical-assets': {
      id: 'critical-assets',
      title: 'Critical Asset Identification',
      type: 'table',
      content: {
        headers: ['Asset', 'Type', 'Value', 'Threats', 'Current Controls'],
        rows: [
          ['Customer PII Database', 'Data', 'Critical', 'Data breach, ransomware', 'Encryption, backups, access control'],
          ['Payment Processing System', 'System', 'Critical', 'Fraud, downtime', 'PCI compliance, monitoring'],
          ['Trading Algorithm IP', 'Information', 'High', 'Theft, reverse engineering', 'Code obfuscation, NDAs'],
          ['API Gateway', 'Service', 'Critical', 'DDoS, exploitation', 'WAF, rate limiting, monitoring'],
          ['Brand Reputation', 'Intangible', 'High', 'Security incidents', 'Incident response, PR plan']
        ]
      }
    },
    'risk-measurement': {
      id: 'risk-measurement',
      title: 'Risk Measurement',
      type: 'list',
      content: [
        '**High Risk**: Customer database breach - $5M potential loss',
        '**High Risk**: Payment system compromise - $2M+ fraud exposure',
        '**Medium Risk**: API abuse - $500K service degradation costs',
        '**Medium Risk**: Insider threat - $1M data value at risk',
        '**Low Risk**: Physical security breach - $100K equipment loss'
      ]
    }
  }
};