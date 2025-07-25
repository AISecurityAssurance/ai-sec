// STPA-Sec Data Service
// Manages data flow: Database → Table → Heat Map → Details

import type { 
  UCA, 
  ControlAction, 
  UCAHeatMapData,
  StpaSecAnalysis 
} from '../types/stpaSecTypes';

export class StpaSecDataService {
  // Generate heat map data from UCAs
  static generateHeatMapData(
    ucas: UCA[], 
    controlActions: ControlAction[]
  ): UCAHeatMapData[] {
    const heatMapData: UCAHeatMapData[] = [];
    
    // For each control action and UCA type combination
    controlActions.forEach(ca => {
      ['not-provided', 'provided', 'wrong-timing', 'wrong-duration'].forEach(type => {
        const relevantUCAs = ucas.filter(u => 
          u.controlActionId === ca.id && u.type === type
        );
        
        // Calculate average severity
        let averageSeverity = 0;
        if (relevantUCAs.length > 0) {
          const severityScores = relevantUCAs.map(u => 
            u.severity === 'critical' ? 5 :
            u.severity === 'high' ? 4 :
            u.severity === 'medium' ? 3 : 2
          );
          averageSeverity = severityScores.reduce((a, b) => a + b, 0) / severityScores.length;
        }
        
        heatMapData.push({
          controlAction: ca.action,
          ucaType: type,
          count: relevantUCAs.length,
          averageSeverity,
          ucas: relevantUCAs
        });
      });
    });
    
    return heatMapData;
  }
  
  // Transform heat map cell data for display
  static getHeatMapCells(heatMapData: UCAHeatMapData[]) {
    const typeMap: Record<string, string> = {
      'not-provided': 'Not Provided',
      'provided': 'Provided Unsafely',
      'wrong-timing': 'Wrong Timing',
      'wrong-duration': 'Wrong Duration'
    };
    
    return heatMapData.map(data => ({
      row: data.controlAction,
      col: typeMap[data.ucaType],
      value: Math.round(data.averageSeverity),
      label: data.count.toString(),
      tooltip: `${data.count} UCA${data.count !== 1 ? 's' : ''} identified`,
      data: data.ucas
    }));
  }
  
  // Filter UCAs based on selection
  static filterUCAs(
    ucas: UCA[], 
    controlActionId?: string, 
    type?: string,
    severity?: string
  ): UCA[] {
    return ucas.filter(uca => {
      if (controlActionId && uca.controlActionId !== controlActionId) return false;
      if (type && uca.type !== type) return false;
      if (severity && uca.severity !== severity) return false;
      return true;
    });
  }
  
  // Validate UCA before save
  static validateUCA(uca: Partial<UCA>): string[] {
    const errors: string[] = [];
    
    if (!uca.controlActionId) errors.push('Control Action is required');
    if (!uca.type) errors.push('UCA Type is required');
    if (!uca.description) errors.push('Description is required');
    if (!uca.hazards || uca.hazards.length === 0) errors.push('At least one hazard must be selected');
    if (!uca.context) errors.push('Context is required');
    if (!uca.severity) errors.push('Severity is required');
    
    return errors;
  }
  
  // Generate UCA ID
  static generateUCAId(controlActionId: string, type: string, index: number): string {
    const caNumber = controlActionId.replace('CA', '');
    const typePrefix = type.split('-').map(w => w[0].toUpperCase()).join('');
    return `UCA${caNumber}-${typePrefix}${index}`;
  }
  
  // Calculate risk metrics
  static calculateRiskMetrics(ucas: UCA[]) {
    const total = ucas.length;
    const bySeverity = {
      critical: ucas.filter(u => u.severity === 'critical').length,
      high: ucas.filter(u => u.severity === 'high').length,
      medium: ucas.filter(u => u.severity === 'medium').length,
      low: ucas.filter(u => u.severity === 'low').length
    };
    
    const byType = {
      'not-provided': ucas.filter(u => u.type === 'not-provided').length,
      'provided': ucas.filter(u => u.type === 'provided').length,
      'wrong-timing': ucas.filter(u => u.type === 'wrong-timing').length,
      'wrong-duration': ucas.filter(u => u.type === 'wrong-duration').length
    };
    
    return {
      total,
      bySeverity,
      byType,
      criticalPercentage: total > 0 ? (bySeverity.critical / total) * 100 : 0,
      highRiskCount: bySeverity.critical + bySeverity.high
    };
  }
  
  // Export to CSV
  static exportUCAsToCSV(ucas: UCA[], controlActions: ControlAction[]): string {
    const headers = [
      'ID',
      'Control Action',
      'Type',
      'Description',
      'Hazards',
      'Context',
      'Severity',
      'STRIDE Categories'
    ];
    
    const rows = ucas.map(uca => {
      const ca = controlActions.find(c => c.id === uca.controlActionId);
      return [
        uca.id,
        ca?.action || uca.controlActionId,
        uca.type,
        `"${uca.description}"`,
        uca.hazards.join('; '),
        `"${uca.context}"`,
        uca.severity,
        uca.strideCategories?.join('; ') || ''
      ];
    });
    
    return [headers, ...rows].map(row => row.join(',')).join('\n');
  }
  
  // Import from CSV
  static importUCAsFromCSV(
    csvContent: string, 
    controlActions: ControlAction[]
  ): { ucas: UCA[], errors: string[] } {
    const lines = csvContent.split('\n');
    const errors: string[] = [];
    const ucas: UCA[] = [];
    
    // Skip header
    for (let i = 1; i < lines.length; i++) {
      const line = lines[i].trim();
      if (!line) continue;
      
      // Simple CSV parsing (would need proper parser for production)
      const parts = line.split(',');
      if (parts.length < 7) {
        errors.push(`Line ${i + 1}: Invalid format`);
        continue;
      }
      
      const [id, controlActionName, type, description, hazards, context, severity] = parts;
      
      // Find control action ID
      const ca = controlActions.find(c => c.action === controlActionName);
      if (!ca) {
        errors.push(`Line ${i + 1}: Unknown control action "${controlActionName}"`);
        continue;
      }
      
      ucas.push({
        id: id.trim(),
        controlActionId: ca.id,
        type: type.trim() as UCA['type'],
        description: description.replace(/"/g, '').trim(),
        hazards: hazards.split(';').map(h => h.trim()),
        context: context.replace(/"/g, '').trim(),
        severity: severity.trim() as UCA['severity']
      });
    }
    
    return { ucas, errors };
  }
}

// Storage service for persistence
export class StpaSecStorageService {
  private static readonly STORAGE_KEY = 'stpasec_analysis';
  
  // Save to localStorage (temporary until database)
  static saveAnalysis(analysis: StpaSecAnalysis): void {
    localStorage.setItem(
      `${this.STORAGE_KEY}_${analysis.id}`,
      JSON.stringify(analysis)
    );
  }
  
  // Load from localStorage
  static loadAnalysis(id: string): StpaSecAnalysis | null {
    const data = localStorage.getItem(`${this.STORAGE_KEY}_${id}`);
    return data ? JSON.parse(data) : null;
  }
  
  // List all analyses
  static listAnalyses(): StpaSecAnalysis[] {
    const analyses: StpaSecAnalysis[] = [];
    
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key?.startsWith(this.STORAGE_KEY)) {
        const data = localStorage.getItem(key);
        if (data) {
          analyses.push(JSON.parse(data));
        }
      }
    }
    
    return analyses;
  }
  
  // Delete analysis
  static deleteAnalysis(id: string): void {
    localStorage.removeItem(`${this.STORAGE_KEY}_${id}`);
  }
}