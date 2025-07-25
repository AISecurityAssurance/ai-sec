import { 
  AnalysisResult, 
  AnalysisSection,
  STPASecAnalysis,
  STRIDEAnalysis,
  Loss,
  Hazard,
  Controller,
  UnsafeControlAction,
  LossScenario,
  Mitigation,
  STRIDEThreat,
  DataFlow,
  TrustBoundary
} from '@security-platform/types';

// Transform backend analysis results to frontend format
export function transformAnalysisResults(
  framework: string,
  backendData: any
): AnalysisResult {
  const baseResult: AnalysisResult = {
    framework,
    sections: [],
    status: { status: 'completed', progress: 100 },
    startedAt: new Date().toISOString(),
    completedAt: new Date().toISOString()
  };

  switch (framework) {
    case 'stpa-sec':
      return transformSTPASecResults(baseResult, backendData);
    case 'stride':
      return transformSTRIDEResults(baseResult, backendData);
    case 'pasta':
      return transformPASTAResults(baseResult, backendData);
    case 'dread':
      return transformDREADResults(baseResult, backendData);
    case 'maestro':
      return transformMAESTROResults(baseResult, backendData);
    case 'linddun':
      return transformLINDDUNResults(baseResult, backendData);
    case 'hazop':
      return transformHAZOPResults(baseResult, backendData);
    case 'octave':
      return transformOCTAVEResults(baseResult, backendData);
    default:
      return baseResult;
  }
}

function transformSTPASecResults(
  baseResult: AnalysisResult,
  data: any
): AnalysisResult {
  const sections: AnalysisSection[] = [
    {
      id: 'system-description',
      title: 'System Description',
      status: 'completed',
      content: {
        description: data?.systemDescription || '',
        components: data?.components || [],
        boundaries: data?.boundaries || []
      }
    },
    {
      id: 'losses',
      title: 'Losses',
      status: 'completed',
      content: {
        losses: data?.losses || []
      }
    },
    {
      id: 'hazards',
      title: 'Hazards/Vulnerabilities',
      status: 'completed',
      content: {
        hazards: data?.hazards || []
      }
    },
    {
      id: 'control-structure',
      title: 'Control Structure',
      status: 'completed',
      content: {
        controllers: data?.controlStructure?.controllers || [],
        controlledProcesses: data?.controlStructure?.controlledProcesses || [],
        connections: data?.controlStructure?.connections || []
      }
    },
    {
      id: 'ucas',
      title: 'Unsafe Control Actions',
      status: 'completed',
      content: {
        ucas: data?.unsafeControlActions || []
      }
    },
    {
      id: 'scenarios',
      title: 'Loss Scenarios',
      status: 'completed',
      content: {
        scenarios: data?.lossScenarios || []
      }
    },
    {
      id: 'mitigations',
      title: 'Mitigations',
      status: 'completed',
      content: {
        mitigations: data?.mitigations || []
      }
    }
  ];

  return {
    ...baseResult,
    sections
  };
}

function transformSTRIDEResults(
  baseResult: AnalysisResult,
  data: any
): AnalysisResult {
  const sections: AnalysisSection[] = [
    {
      id: 'overview',
      title: 'STRIDE Overview',
      status: 'completed',
      content: {
        summary: data?.summary || '',
        threatCount: data?.threats?.length || 0
      }
    },
    {
      id: 'data-flow-diagram',
      title: 'Data Flow Diagram',
      status: 'completed',
      content: {
        dataFlows: data?.dataFlows || [],
        trustBoundaries: data?.trustBoundaries || []
      }
    },
    {
      id: 'threats',
      title: 'Identified Threats',
      status: 'completed',
      content: {
        threats: data?.threats || []
      }
    },
    {
      id: 'mitigations',
      title: 'Mitigation Strategies',
      status: 'completed',
      content: {
        mitigations: data?.mitigations || []
      }
    }
  ];

  return {
    ...baseResult,
    sections
  };
}

function transformPASTAResults(
  baseResult: AnalysisResult,
  data: any
): AnalysisResult {
  const sections: AnalysisSection[] = [
    {
      id: 'stage1-objectives',
      title: 'Business Objectives',
      status: 'completed',
      content: data?.stage1 || {}
    },
    {
      id: 'stage2-technical',
      title: 'Technical Scope',
      status: 'completed',
      content: data?.stage2 || {}
    },
    {
      id: 'stage3-decomposition',
      title: 'Application Decomposition',
      status: 'completed',
      content: data?.stage3 || {}
    },
    {
      id: 'stage4-threats',
      title: 'Threat Analysis',
      status: 'completed',
      content: data?.stage4 || {}
    },
    {
      id: 'stage5-vulnerabilities',
      title: 'Vulnerability Analysis',
      status: 'completed',
      content: data?.stage5 || {}
    },
    {
      id: 'stage6-attacks',
      title: 'Attack Modeling',
      status: 'completed',
      content: data?.stage6 || {}
    },
    {
      id: 'stage7-risk',
      title: 'Risk & Impact Analysis',
      status: 'completed',
      content: data?.stage7 || {}
    }
  ];

  return {
    ...baseResult,
    sections
  };
}

function transformDREADResults(
  baseResult: AnalysisResult,
  data: any
): AnalysisResult {
  const sections: AnalysisSection[] = [
    {
      id: 'overview',
      title: 'DREAD Overview',
      status: 'completed',
      content: {
        summary: data?.summary || '',
        totalThreats: data?.threats?.length || 0
      }
    },
    {
      id: 'ratings',
      title: 'Risk Ratings',
      status: 'completed',
      content: {
        threats: data?.threats || []
      }
    },
    {
      id: 'distribution',
      title: 'Risk Distribution',
      status: 'completed',
      content: {
        distribution: data?.riskDistribution || {}
      }
    }
  ];

  return {
    ...baseResult,
    sections
  };
}

function transformMAESTROResults(
  baseResult: AnalysisResult,
  data: any
): AnalysisResult {
  const sections: AnalysisSection[] = [
    {
      id: 'overview',
      title: 'MAESTRO Overview',
      status: 'completed',
      content: data?.overview || {}
    },
    {
      id: 'ai-components',
      title: 'AI/ML Components',
      status: 'completed',
      content: {
        components: data?.aiComponents || []
      }
    },
    {
      id: 'threat-analysis',
      title: 'AI Threat Analysis',
      status: 'completed',
      content: {
        threats: data?.threats || []
      }
    },
    {
      id: 'controls',
      title: 'Security Controls',
      status: 'completed',
      content: {
        controls: data?.controls || []
      }
    }
  ];

  return {
    ...baseResult,
    sections
  };
}

function transformLINDDUNResults(
  baseResult: AnalysisResult,
  data: any
): AnalysisResult {
  const sections: AnalysisSection[] = [
    {
      id: 'overview',
      title: 'LINDDUN Overview',
      status: 'completed',
      content: data?.overview || {}
    },
    {
      id: 'data-flows',
      title: 'Data Flow Inventory',
      status: 'completed',
      content: {
        dataFlows: data?.dataFlows || []
      }
    },
    {
      id: 'privacy-threats',
      title: 'Privacy Threat Analysis',
      status: 'completed',
      content: {
        threats: data?.threats || []
      }
    },
    {
      id: 'privacy-controls',
      title: 'Privacy Controls',
      status: 'completed',
      content: {
        controls: data?.controls || []
      }
    }
  ];

  return {
    ...baseResult,
    sections
  };
}

function transformHAZOPResults(
  baseResult: AnalysisResult,
  data: any
): AnalysisResult {
  const sections: AnalysisSection[] = [
    {
      id: 'overview',
      title: 'HAZOP Overview',
      status: 'completed',
      content: data?.overview || {}
    },
    {
      id: 'process-nodes',
      title: 'Process Nodes',
      status: 'completed',
      content: {
        nodes: data?.nodes || []
      }
    },
    {
      id: 'deviations',
      title: 'Deviation Analysis',
      status: 'completed',
      content: {
        deviations: data?.deviations || []
      }
    },
    {
      id: 'actions',
      title: 'Action Items',
      status: 'completed',
      content: {
        actions: data?.actions || []
      }
    }
  ];

  return {
    ...baseResult,
    sections
  };
}

function transformOCTAVEResults(
  baseResult: AnalysisResult,
  data: any
): AnalysisResult {
  const sections: AnalysisSection[] = [
    {
      id: 'overview',
      title: 'OCTAVE Overview',
      status: 'completed',
      content: data?.overview || {}
    },
    {
      id: 'critical-assets',
      title: 'Critical Assets',
      status: 'completed',
      content: {
        assets: data?.assets || []
      }
    },
    {
      id: 'threat-profiles',
      title: 'Threat Profiles',
      status: 'completed',
      content: {
        threats: data?.threats || []
      }
    },
    {
      id: 'risk-analysis',
      title: 'Risk Analysis',
      status: 'completed',
      content: {
        risks: data?.risks || []
      }
    },
    {
      id: 'protection-strategy',
      title: 'Protection Strategy',
      status: 'completed',
      content: {
        strategies: data?.protectionStrategies || []
      }
    }
  ];

  return {
    ...baseResult,
    sections
  };
}

// Generate sample analysis data for demo/testing
export function generateSampleAnalysisData(framework: string): any {
  switch (framework) {
    case 'stpa-sec':
      return generateSampleSTPASecData();
    case 'stride':
      return generateSampleSTRIDEData();
    case 'pasta':
      return generateSamplePASTAData();
    case 'dread':
      return generateSampleDREADData();
    default:
      return {};
  }
}

function generateSampleSTPASecData(): Partial<STPASecAnalysis> {
  return {
    losses: [
      {
        id: 'L1',
        description: 'Customer financial data exposed to unauthorized parties',
        severity: 'critical',
        category: 'Data Breach'
      },
      {
        id: 'L2',
        description: 'Financial transactions processed incorrectly',
        severity: 'high',
        category: 'Financial Loss'
      },
      {
        id: 'L3',
        description: 'System unavailable during critical business hours',
        severity: 'high',
        category: 'Service Disruption'
      }
    ],
    hazards: [
      {
        id: 'H1',
        description: 'Authentication system allows unauthorized access',
        relatedLosses: ['L1'],
        severity: 'critical'
      },
      {
        id: 'H2',
        description: 'Payment processing system executes invalid transactions',
        relatedLosses: ['L2'],
        severity: 'high'
      },
      {
        id: 'H3',
        description: 'Core banking services become unresponsive',
        relatedLosses: ['L3'],
        severity: 'high'
      }
    ],
    controlStructure: {
      controllers: [
        {
          id: 'C1',
          name: 'Authentication Service',
          type: 'Security Controller',
          processModel: 'User credentials, session management',
          trustBoundary: 'Internal'
        },
        {
          id: 'C2',
          name: 'Payment Gateway',
          type: 'Transaction Controller',
          processModel: 'Transaction validation, payment processing',
          trustBoundary: 'External'
        }
      ],
      controlledProcesses: [
        {
          id: 'P1',
          name: 'User Session',
          type: 'Security Process',
          state: 'Active/Inactive'
        },
        {
          id: 'P2',
          name: 'Transaction Processing',
          type: 'Financial Process',
          state: 'Pending/Completed/Failed'
        }
      ],
      connections: [
        {
          id: 'CN1',
          from: 'C1',
          to: 'P1',
          type: 'control',
          label: 'Authenticate User'
        },
        {
          id: 'CN2',
          from: 'P1',
          to: 'C1',
          type: 'feedback',
          label: 'Session Status'
        }
      ]
    },
    unsafeControlActions: [
      {
        id: 'UCA1',
        controlAction: 'Authenticate User',
        controllerId: 'C1',
        type: 'provided_incorrectly',
        context: 'When invalid credentials are provided',
        hazards: ['H1'],
        strideCategories: ['spoofing', 'elevation_of_privilege']
      },
      {
        id: 'UCA2',
        controlAction: 'Process Payment',
        controllerId: 'C2',
        type: 'wrong_timing',
        context: 'When account has insufficient funds',
        hazards: ['H2'],
        strideCategories: ['tampering']
      }
    ],
    lossScenarios: [
      {
        id: 'LS1',
        ucaId: 'UCA1',
        description: 'Attacker bypasses authentication using stolen credentials',
        causalFactors: ['Weak password policy', 'No MFA enforcement'],
        attackVector: 'Credential stuffing attack',
        likelihood: 'high',
        impact: 'high'
      }
    ],
    mitigations: [
      {
        id: 'M1',
        scenarioId: 'LS1',
        type: 'preventive',
        description: 'Implement multi-factor authentication',
        implementation: 'Deploy MFA using TOTP or push notifications',
        priority: 'critical'
      }
    ]
  };
}

function generateSampleSTRIDEData(): Partial<STRIDEAnalysis> {
  return {
    threats: [
      {
        id: 'T1',
        category: 'spoofing',
        component: 'Authentication Service',
        description: 'Attacker impersonates legitimate user',
        impact: 'Unauthorized access to customer accounts',
        likelihood: 'high',
        mitigations: ['Implement MFA', 'Use certificate-based authentication']
      },
      {
        id: 'T2',
        category: 'tampering',
        component: 'Payment API',
        description: 'Man-in-the-middle attack on payment requests',
        impact: 'Modified transaction amounts or recipients',
        likelihood: 'medium',
        mitigations: ['End-to-end encryption', 'Request signing']
      },
      {
        id: 'T3',
        category: 'information_disclosure',
        component: 'Database',
        description: 'SQL injection exposes customer data',
        impact: 'PII and financial data breach',
        likelihood: 'medium',
        mitigations: ['Parameterized queries', 'Input validation', 'Database encryption']
      }
    ],
    dataFlows: [
      {
        id: 'DF1',
        from: 'Mobile App',
        to: 'API Gateway',
        data: 'User credentials',
        protocol: 'HTTPS',
        encrypted: true
      },
      {
        id: 'DF2',
        from: 'API Gateway',
        to: 'Authentication Service',
        data: 'Auth tokens',
        protocol: 'gRPC',
        encrypted: true
      }
    ],
    trustBoundaries: [
      {
        id: 'TB1',
        name: 'Internet Boundary',
        components: ['Mobile App', 'Web App', 'API Gateway']
      },
      {
        id: 'TB2',
        name: 'Internal Services',
        components: ['Authentication Service', 'Payment Service', 'Database']
      }
    ]
  };
}

function generateSamplePASTAData(): any {
  return {
    stage1: {
      objectives: [
        'Protect customer financial data',
        'Ensure transaction integrity',
        'Maintain 99.9% uptime',
        'Comply with PCI-DSS requirements'
      ]
    },
    stage2: {
      scope: {
        applications: ['Mobile Banking App', 'Web Portal', 'Payment API'],
        infrastructure: ['AWS Cloud', 'Kubernetes', 'PostgreSQL'],
        users: '2 million active users',
        dataTypes: ['PII', 'Financial Records', 'Transaction History']
      }
    },
    stage3: {
      components: [
        {
          name: 'Authentication Service',
          type: 'Microservice',
          criticality: 'High',
          dependencies: ['User Database', 'Session Cache']
        },
        {
          name: 'Payment Gateway',
          type: 'External Integration',
          criticality: 'Critical',
          dependencies: ['Bank Networks', 'Card Processors']
        }
      ]
    },
    stage4: {
      threatActors: [
        {
          name: 'Cybercriminal Groups',
          motivation: 'Financial gain',
          capabilities: 'High',
          intent: 'Steal funds and data'
        },
        {
          name: 'Insider Threats',
          motivation: 'Various',
          capabilities: 'Medium',
          intent: 'Data theft or sabotage'
        }
      ]
    },
    stage5: {
      vulnerabilities: [
        {
          id: 'V1',
          component: 'Authentication Service',
          description: 'Session fixation vulnerability',
          severity: 'High',
          cvss: 7.5
        }
      ]
    },
    stage6: {
      attackScenarios: [
        {
          name: 'Account Takeover',
          description: 'Attacker gains control of user account',
          steps: ['Phishing', 'Credential theft', 'Session hijacking'],
          likelihood: 'High'
        }
      ]
    },
    stage7: {
      risks: [
        {
          id: 'R1',
          description: 'Customer data breach',
          impact: 'Critical',
          likelihood: 'Medium',
          riskScore: 8.5
        }
      ]
    }
  };
}

function generateSampleDREADData(): any {
  return {
    summary: 'DREAD risk assessment for financial services platform',
    threats: [
      {
        id: 'DT1',
        name: 'SQL Injection in Payment API',
        damage: 9,
        reproducibility: 8,
        exploitability: 7,
        affectedUsers: 10,
        discoverability: 6,
        totalScore: 40,
        riskLevel: 'Critical'
      },
      {
        id: 'DT2',
        name: 'XSS in Customer Portal',
        damage: 6,
        reproducibility: 9,
        exploitability: 8,
        affectedUsers: 7,
        discoverability: 9,
        totalScore: 39,
        riskLevel: 'High'
      },
      {
        id: 'DT3',
        name: 'Weak Password Recovery',
        damage: 7,
        reproducibility: 10,
        exploitability: 9,
        affectedUsers: 8,
        discoverability: 10,
        totalScore: 44,
        riskLevel: 'Critical'
      }
    ],
    riskDistribution: {
      critical: 2,
      high: 1,
      medium: 0,
      low: 0
    }
  };
}