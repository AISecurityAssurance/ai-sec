// Enhanced STPA-Sec data with comprehensive UCA analysis and STRIDE integration

import { ucas as existingUCAs } from './stpaSecData';
import type { UCA } from './stpaSecData';

// Comprehensive UCA types for each control action
export const ucaTypes = [
  { id: 'not-provided', label: 'Not Provided', description: 'Control action not provided when required' },
  { id: 'provided', label: 'Provided Unsafely', description: 'Control action provided when it should not be' },
  { id: 'wrong-timing', label: 'Wrong Timing', description: 'Control action provided too early or too late' },
  { id: 'wrong-duration', label: 'Wrong Duration', description: 'Control action applied for too long or too short' }
];

// STRIDE categories for security analysis
export const strideCategories = [
  { id: 'spoofing', label: 'Spoofing', icon: '🎭' },
  { id: 'tampering', label: 'Tampering', icon: '🔨' },
  { id: 'repudiation', label: 'Repudiation', icon: '🚫' },
  { id: 'info-disclosure', label: 'Information Disclosure', icon: '📖' },
  { id: 'dos', label: 'Denial of Service', icon: '⛔' },
  { id: 'elevation', label: 'Elevation of Privilege', icon: '⬆️' }
];

// Comprehensive UCAs with all 4 types for each control action
export const comprehensiveUCAs: UCA[] = [
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

// Extended UCA interface with STRIDE mapping
export interface UCAWithSTRIDE extends UCA {
  strideThreats: string[]; // Which STRIDE categories apply
  d4Score?: {
    detectability: number; // 1-5
    difficulty: number; // 1-5
    damage: number; // 1-5
    deniability: number; // 1-5
  };
}

// Map UCAs to STRIDE threats
export const ucaStrideMapping: Record<string, string[]> = {
  'UCA1-1': ['dos'], // DoS when legitimate users can't authenticate
  'UCA1-2': ['spoofing', 'elevation'], // Spoofing identity, privilege escalation
  'UCA1-3': ['spoofing', 'repudiation'], // Session hijacking
  'UCA1-4': ['spoofing', 'info-disclosure'], // Extended exposure window
  
  'UCA2-1': ['dos'], // Service denial for legitimate transactions
  'UCA2-2': ['tampering', 'repudiation'], // Financial tampering
  'UCA2-3': ['tampering', 'repudiation'], // Unauthorized transactions
  'UCA2-4': ['dos'], // Service degradation
  
  'UCA3-1': ['spoofing', 'info-disclosure'], // Continued attack access
  'UCA3-2': ['dos'], // Blocking legitimate users
  'UCA3-3': ['info-disclosure', 'tampering'], // Data already compromised
  'UCA3-4': ['spoofing'], // Re-attack possibility
  
  'UCA4-1': ['dos'], // Service overwhelmed
  'UCA4-2': ['dos'], // Legitimate service blocked
  'UCA4-3': ['dos'], // Service already impacted
  'UCA4-4': ['dos'] // Extended service disruption
};

// Controller to Control Flow Node mapping
export const controllerNodeMapping = {
  'C1': 'auth-service', // Authentication Service
  'C2': 'transaction-processor', // Transaction Processor
  'C3': 'siem', // Security Operations Team (SIEM)
  'C4': 'api-gateway' // API Gateway
};

// Generate heat map data for UCA risk levels
export interface UCAHeatMapCell {
  controller: string;
  ucaType: string;
  riskLevel: number; // 1-5
  count: number;
  ucas: UCA[];
}

export function generateUCAHeatMap(): UCAHeatMapCell[] {
  const cells: UCAHeatMapCell[] = [];
  const controllers = ['C1', 'C2', 'C3', 'C4'];
  const types = ['not-provided', 'provided', 'wrong-timing', 'wrong-duration'];
  
  controllers.forEach(controller => {
    types.forEach(type => {
      const ucasForCell = comprehensiveUCAs.filter(uca => {
        const ca = uca.controlActionId;
        const controllerMatch = ca === 'CA1' && controller === 'C1' ||
                               ca === 'CA2' && controller === 'C2' ||
                               ca === 'CA3' && controller === 'C3' ||
                               ca === 'CA4' && controller === 'C4';
        return controllerMatch && uca.type === type;
      });
      
      // Calculate average risk level
      let riskLevel = 0;
      if (ucasForCell.length > 0) {
        const severityScores = ucasForCell.map(u => 
          u.severity === 'critical' ? 5 :
          u.severity === 'high' ? 4 :
          u.severity === 'medium' ? 3 : 2
        );
        riskLevel = Math.round(severityScores.reduce((a, b) => a + b, 0) / severityScores.length);
      }
      
      cells.push({
        controller,
        ucaType: type,
        riskLevel,
        count: ucasForCell.length,
        ucas: ucasForCell
      });
    });
  });
  
  return cells;
}

// Comprehensive causal scenario template
export interface ComprehensiveCausalScenario {
  id: string;
  ucaId: string;
  description: string;
  causalFactors: {
    technical: string[];
    human: string[];
    organizational: string[];
  };
  strideCategories: string[];
  attackVectors: string[];
  prerequisites: string[];
  indicators: string[];
  mitigations: {
    preventive: string[];
    detective: string[];
    corrective: string[];
  };
  residualRisk: 'low' | 'medium' | 'high' | 'critical';
}