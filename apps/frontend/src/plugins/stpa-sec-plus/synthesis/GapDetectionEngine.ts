/**
 * Gap Detection Engine
 * 
 * Identifies gaps in security analysis coverage across frameworks
 */

import { StandardizedAnalysis, AnalysisGap } from '../types';

export class GapDetectionEngine {
  // Main gap detection function
  async detectGaps(analyses: StandardizedAnalysis[]): Promise<AnalysisGap[]> {
    const gaps: AnalysisGap[] = [];
    
    // Framework coverage gaps
    gaps.push(...this.detectFrameworkGaps(analyses));
    
    // Entity coverage gaps
    gaps.push(...this.detectEntityCoverageGaps(analyses));
    
    // Control coverage gaps
    gaps.push(...this.detectControlCoverageGaps(analyses));
    
    // Compliance gaps
    gaps.push(...this.detectComplianceGaps(analyses));
    
    // Data classification gaps
    gaps.push(...this.detectDataClassificationGaps(analyses));
    
    // Threat modeling gaps
    gaps.push(...this.detectThreatModelingGaps(analyses));
    
    // Sort by severity and deduplicate
    return this.prioritizeAndDeduplicate(gaps);
  }
  
  // Detect missing framework analyses
  private detectFrameworkGaps(analyses: StandardizedAnalysis[]): AnalysisGap[] {
    const gaps: AnalysisGap[] = [];
    const frameworks = new Set(analyses.map(a => a.framework));
    
    // Check for missing privacy analysis
    if (this.hasPersonalData(analyses) && !frameworks.has('LINDDUN')) {
      gaps.push({
        id: 'gap-privacy-framework',
        type: 'missing_privacy_analysis',
        severity: 'high',
        description: 'Personal data processing detected without privacy threat modeling (LINDDUN)',
        affectedEntities: this.getPersonalDataEntities(analyses),
        recommendation: 'Conduct LINDDUN privacy threat modeling for all personal data flows',
        estimatedEffort: '3-5 days',
        businessImpact: 'GDPR/CCPA compliance risk, potential fines up to 4% of annual revenue',
        complianceImpact: ['GDPR', 'CCPA', 'PIPEDA'],
        suggestedFramework: 'LINDDUN'
      });
    }
    
    // Check for missing AI/ML security
    if (this.hasAIComponents(analyses) && !frameworks.has('MAESTRO')) {
      gaps.push({
        id: 'gap-ai-framework',
        type: 'missing_ai_security',
        severity: 'critical',
        description: 'AI/ML components identified without specialized security analysis',
        affectedEntities: this.getAIEntities(analyses),
        recommendation: 'Apply MAESTRO framework for AI/ML security assessment',
        estimatedEffort: '5-7 days',
        businessImpact: 'Model poisoning, adversarial attacks, IP theft risks',
        suggestedFramework: 'MAESTRO'
      });
    }
    
    // Check for missing quantitative risk assessment
    if (!this.hasQuantitativeRiskScoring(analyses)) {
      gaps.push({
        id: 'gap-quantitative-risk',
        type: 'missing_quantitative_assessment',
        severity: 'medium',
        description: 'No standardized quantitative risk scoring methodology applied',
        recommendation: 'Implement DREAD or FAIR quantitative risk scoring',
        estimatedEffort: '2-3 days',
        businessImpact: 'Inconsistent risk prioritization affecting resource allocation',
        suggestedFramework: 'DREAD'
      });
    }
    
    // Check for missing business context
    if (!frameworks.has('PASTA') && !frameworks.has('OCTAVE')) {
      gaps.push({
        id: 'gap-business-context',
        type: 'missing_business_context',
        severity: 'medium',
        description: 'Technical security analysis lacks business risk context',
        recommendation: 'Add PASTA or OCTAVE for business-driven threat modeling',
        estimatedEffort: '3-4 days',
        businessImpact: 'Security investments may not align with business priorities',
        suggestedFramework: 'PASTA'
      });
    }
    
    return gaps;
  }
  
  // Detect entity coverage gaps
  private detectEntityCoverageGaps(analyses: StandardizedAnalysis[]): AnalysisGap[] {
    const gaps: AnalysisGap[] = [];
    const allEntities = this.getAllUniqueEntities(analyses);
    
    // Check each entity for analysis coverage
    allEntities.forEach(entity => {
      const coverage = this.calculateEntityCoverage(entity, analyses);
      
      if (coverage.threatCoverage < 0.5) {
        gaps.push({
          id: `gap-entity-threat-${entity.id}`,
          type: 'insufficient_threat_coverage',
          severity: entity.criticality === 'high' ? 'high' : 'medium',
          description: `Entity '${entity.name}' has insufficient threat analysis coverage (${Math.round(coverage.threatCoverage * 100)}%)`,
          affectedEntities: [entity.name],
          recommendation: 'Perform comprehensive threat modeling for this entity',
          estimatedEffort: '1-2 days',
          businessImpact: 'Unidentified threats could lead to security breaches'
        });
      }
      
      if (coverage.controlCoverage < 0.3) {
        gaps.push({
          id: `gap-entity-control-${entity.id}`,
          type: 'insufficient_control_coverage',
          severity: entity.criticality === 'high' ? 'critical' : 'high',
          description: `Entity '${entity.name}' lacks adequate security controls (${Math.round(coverage.controlCoverage * 100)}% coverage)`,
          affectedEntities: [entity.name],
          recommendation: 'Implement additional security controls',
          estimatedEffort: '3-5 days',
          businessImpact: 'Entity vulnerable to identified threats'
        });
      }
    });
    
    return gaps;
  }
  
  // Detect control coverage gaps
  private detectControlCoverageGaps(analyses: StandardizedAnalysis[]): AnalysisGap[] {
    const gaps: AnalysisGap[] = [];
    const threats = this.getAllThreats(analyses);
    const controls = this.getAllControls(analyses);
    
    // Check for unmitigated threats
    threats.forEach(threat => {
      const mitigatingControls = this.findMitigatingControls(threat, controls);
      
      if (mitigatingControls.length === 0) {
        gaps.push({
          id: `gap-unmitigated-${threat.originalId}`,
          type: 'unmitigated_threat',
          severity: threat.severity as any,
          description: `Threat '${threat.name}' has no mitigating controls`,
          affectedEntities: threat.affectedEntity ? [threat.affectedEntity] : [],
          recommendation: 'Implement controls to mitigate this threat',
          estimatedEffort: '2-3 days',
          businessImpact: this.calculateThreatImpact(threat)
        });
      } else if (mitigatingControls.length === 1) {
        gaps.push({
          id: `gap-single-control-${threat.originalId}`,
          type: 'single_point_of_failure',
          severity: 'medium',
          description: `Threat '${threat.name}' relies on single control`,
          affectedEntities: threat.affectedEntity ? [threat.affectedEntity] : [],
          recommendation: 'Implement defense in depth with multiple controls',
          estimatedEffort: '1-2 days',
          businessImpact: 'Control failure would leave threat unmitigated'
        });
      }
    });
    
    // Check for control effectiveness
    const ineffectiveControls = controls.filter(c => 
      c.properties?.effectiveness === 'low' || 
      c.properties?.effectiveness === 'untested'
    );
    
    if (ineffectiveControls.length > 0) {
      gaps.push({
        id: 'gap-ineffective-controls',
        type: 'ineffective_controls',
        severity: 'high',
        description: `${ineffectiveControls.length} controls have low or untested effectiveness`,
        recommendation: 'Test and improve control effectiveness',
        estimatedEffort: '5-7 days',
        businessImpact: 'Controls may not prevent or detect attacks as expected'
      });
    }
    
    return gaps;
  }
  
  // Detect compliance gaps
  private detectComplianceGaps(analyses: StandardizedAnalysis[]): AnalysisGap[] {
    const gaps: AnalysisGap[] = [];
    const dataTypes = this.getDataTypes(analyses);
    
    // GDPR compliance gaps
    if (dataTypes.includes('personal') || dataTypes.includes('pii')) {
      const gdprControls = this.checkGDPRCompliance(analyses);
      if (!gdprControls.encryptionAtRest) {
        gaps.push({
          id: 'gap-gdpr-encryption',
          type: 'compliance_gap',
          severity: 'high',
          description: 'Personal data not encrypted at rest (GDPR Article 32)',
          recommendation: 'Implement encryption for all personal data storage',
          estimatedEffort: '3-5 days',
          businessImpact: 'GDPR non-compliance, potential fines',
          complianceImpact: ['GDPR']
        });
      }
      
      if (!gdprControls.accessControls) {
        gaps.push({
          id: 'gap-gdpr-access',
          type: 'compliance_gap',
          severity: 'high',
          description: 'Insufficient access controls for personal data (GDPR Article 32)',
          recommendation: 'Implement role-based access control for personal data',
          estimatedEffort: '5-7 days',
          businessImpact: 'Unauthorized access to personal data',
          complianceImpact: ['GDPR']
        });
      }
    }
    
    // PCI-DSS compliance gaps
    if (dataTypes.includes('payment') || dataTypes.includes('credit_card')) {
      const pciControls = this.checkPCICompliance(analyses);
      if (!pciControls.networkSegmentation) {
        gaps.push({
          id: 'gap-pci-segmentation',
          type: 'compliance_gap',
          severity: 'critical',
          description: 'Payment card data not properly segmented (PCI-DSS Requirement 1)',
          recommendation: 'Implement network segmentation for cardholder data environment',
          estimatedEffort: '10-15 days',
          businessImpact: 'PCI-DSS non-compliance, loss of payment processing',
          complianceImpact: ['PCI-DSS']
        });
      }
    }
    
    // HIPAA compliance gaps
    if (dataTypes.includes('health') || dataTypes.includes('phi')) {
      const hipaaControls = this.checkHIPAACompliance(analyses);
      if (!hipaaControls.auditLogging) {
        gaps.push({
          id: 'gap-hipaa-audit',
          type: 'compliance_gap',
          severity: 'high',
          description: 'Insufficient audit logging for PHI access (HIPAA §164.312)',
          recommendation: 'Implement comprehensive audit logging for all PHI access',
          estimatedEffort: '5-7 days',
          businessImpact: 'HIPAA violation, potential fines up to $50,000 per violation',
          complianceImpact: ['HIPAA']
        });
      }
    }
    
    return gaps;
  }
  
  // Detect data classification gaps
  private detectDataClassificationGaps(analyses: StandardizedAnalysis[]): AnalysisGap[] {
    const gaps: AnalysisGap[] = [];
    const unclassifiedData = this.findUnclassifiedData(analyses);
    
    if (unclassifiedData.length > 0) {
      gaps.push({
        id: 'gap-data-classification',
        type: 'missing_data_classification',
        severity: 'medium',
        description: `${unclassifiedData.length} data assets lack proper classification`,
        affectedEntities: unclassifiedData.map(d => d.name),
        recommendation: 'Classify all data assets according to sensitivity',
        estimatedEffort: '2-3 days',
        businessImpact: 'Cannot apply appropriate security controls without classification'
      });
    }
    
    // Check for high-value data without extra protection
    const highValueData = this.findHighValueData(analyses);
    const unprotectedHighValue = highValueData.filter(d => 
      !this.hasAdequateProtection(d, analyses)
    );
    
    if (unprotectedHighValue.length > 0) {
      gaps.push({
        id: 'gap-high-value-protection',
        type: 'insufficient_data_protection',
        severity: 'critical',
        description: `${unprotectedHighValue.length} high-value data assets lack adequate protection`,
        affectedEntities: unprotectedHighValue.map(d => d.name),
        recommendation: 'Implement enhanced security controls for high-value data',
        estimatedEffort: '5-10 days',
        businessImpact: 'Critical data at risk of theft or compromise'
      });
    }
    
    return gaps;
  }
  
  // Detect threat modeling gaps
  private detectThreatModelingGaps(analyses: StandardizedAnalysis[]): AnalysisGap[] {
    const gaps: AnalysisGap[] = [];
    
    // Check for missing threat categories
    const threatCategories = this.getThreatCategories(analyses);
    const expectedCategories = [
      'spoofing', 'tampering', 'repudiation', 
      'information_disclosure', 'denial_of_service', 
      'elevation_of_privilege'
    ];
    
    const missingCategories = expectedCategories.filter(cat => 
      !threatCategories.includes(cat)
    );
    
    if (missingCategories.length > 0) {
      gaps.push({
        id: 'gap-threat-categories',
        type: 'incomplete_threat_modeling',
        severity: 'medium',
        description: `Missing threat analysis for categories: ${missingCategories.join(', ')}`,
        recommendation: 'Complete STRIDE threat modeling for all categories',
        estimatedEffort: '3-4 days',
        businessImpact: 'Blind spots in threat landscape'
      });
    }
    
    // Check for external threat analysis
    if (!this.hasExternalThreatAnalysis(analyses)) {
      gaps.push({
        id: 'gap-external-threats',
        type: 'missing_external_threat_analysis',
        severity: 'high',
        description: 'No analysis of external threat actors and their capabilities',
        recommendation: 'Conduct threat intelligence analysis for relevant threat actors',
        estimatedEffort: '2-3 days',
        businessImpact: 'Unprepared for targeted attacks'
      });
    }
    
    // Check for supply chain threats
    if (this.hasThirdPartyComponents(analyses) && !this.hasSupplyChainAnalysis(analyses)) {
      gaps.push({
        id: 'gap-supply-chain',
        type: 'missing_supply_chain_analysis',
        severity: 'high',
        description: 'Third-party components identified without supply chain risk analysis',
        recommendation: 'Assess supply chain and third-party risks',
        estimatedEffort: '3-5 days',
        businessImpact: 'Vulnerable to supply chain attacks like SolarWinds'
      });
    }
    
    return gaps;
  }
  
  // Helper methods
  private hasPersonalData(analyses: StandardizedAnalysis[]): boolean {
    return analyses.some(a => 
      a.entities.some(e => 
        e.properties?.dataClassification?.toLowerCase().includes('personal') ||
        e.properties?.dataClassification?.toLowerCase().includes('pii') ||
        e.name.toLowerCase().includes('user') ||
        e.name.toLowerCase().includes('customer')
      ) ||
      a.relationships.some(r => 
        r.properties?.dataTypes?.some((t: string) => 
          t.toLowerCase().includes('personal') ||
          t.toLowerCase().includes('pii')
        )
      )
    );
  }
  
  private hasAIComponents(analyses: StandardizedAnalysis[]): boolean {
    return analyses.some(a =>
      a.entities.some(e =>
        e.type === 'ai' ||
        e.type === 'ml_model' ||
        e.properties?.technology?.toLowerCase().includes('ai') ||
        e.properties?.technology?.toLowerCase().includes('machine learning') ||
        e.properties?.technology?.toLowerCase().includes('neural') ||
        e.name.toLowerCase().includes('model') ||
        e.name.toLowerCase().includes('ai')
      )
    );
  }
  
  private hasQuantitativeRiskScoring(analyses: StandardizedAnalysis[]): boolean {
    return analyses.some(a => {
      // Check if risks have numeric scores
      const hasNumericScores = a.risks.some(r => 
        typeof r.score === 'number' && r.score > 0
      );
      
      // Check if using a known quantitative framework
      const hasQuantitativeFramework = ['DREAD', 'FAIR', 'OCTAVE'].includes(a.framework);
      
      return hasNumericScores || hasQuantitativeFramework;
    });
  }
  
  private getPersonalDataEntities(analyses: StandardizedAnalysis[]): string[] {
    const entities = new Set<string>();
    
    analyses.forEach(a => {
      a.entities
        .filter(e => 
          e.properties?.dataClassification?.toLowerCase().includes('personal') ||
          e.properties?.dataClassification?.toLowerCase().includes('pii')
        )
        .forEach(e => entities.add(e.name));
    });
    
    return Array.from(entities);
  }
  
  private getAIEntities(analyses: StandardizedAnalysis[]): string[] {
    const entities = new Set<string>();
    
    analyses.forEach(a => {
      a.entities
        .filter(e =>
          e.type === 'ai' ||
          e.type === 'ml_model' ||
          e.properties?.technology?.toLowerCase().includes('ai') ||
          e.properties?.technology?.toLowerCase().includes('machine learning')
        )
        .forEach(e => entities.add(e.name));
    });
    
    return Array.from(entities);
  }
  
  private getAllUniqueEntities(analyses: StandardizedAnalysis[]): any[] {
    const entityMap = new Map<string, any>();
    
    analyses.forEach(a => {
      a.entities.forEach(e => {
        const key = e.name.toLowerCase();
        if (!entityMap.has(key)) {
          entityMap.set(key, {
            id: e.originalId,
            name: e.name,
            type: e.type,
            criticality: e.properties?.criticality || 'medium'
          });
        }
      });
    });
    
    return Array.from(entityMap.values());
  }
  
  private calculateEntityCoverage(entity: any, analyses: StandardizedAnalysis[]): any {
    let threatCount = 0;
    let controlCount = 0;
    let totalPossibleThreats = 6; // STRIDE categories
    let totalPossibleControls = 10; // Reasonable control expectation
    
    analyses.forEach(a => {
      // Count threats for this entity
      threatCount += a.threats.filter(t => 
        t.affectedEntity === entity.id ||
        t.affectedEntity?.includes(entity.name)
      ).length;
      
      // Count controls for this entity
      controlCount += a.controls.filter(c => 
        c.properties?.protectedEntity === entity.id ||
        c.properties?.protectedEntity?.includes(entity.name)
      ).length;
    });
    
    return {
      threatCoverage: Math.min(threatCount / totalPossibleThreats, 1),
      controlCoverage: Math.min(controlCount / totalPossibleControls, 1)
    };
  }
  
  private getAllThreats(analyses: StandardizedAnalysis[]): any[] {
    const threats: any[] = [];
    analyses.forEach(a => threats.push(...a.threats));
    return threats;
  }
  
  private getAllControls(analyses: StandardizedAnalysis[]): any[] {
    const controls: any[] = [];
    analyses.forEach(a => controls.push(...a.controls));
    return controls;
  }
  
  private findMitigatingControls(threat: any, controls: any[]): any[] {
    return controls.filter(c => 
      c.threatId === threat.originalId ||
      c.properties?.mitigates?.includes(threat.originalId) ||
      c.properties?.mitigates?.includes(threat.name)
    );
  }
  
  private calculateThreatImpact(threat: any): string {
    const severityImpact: Record<string, string> = {
      'critical': 'Catastrophic business impact, potential company failure',
      'high': 'Major financial loss, reputation damage',
      'medium': 'Significant operational disruption',
      'low': 'Minor inconvenience or limited impact'
    };
    
    return severityImpact[threat.severity] || 'Unknown impact';
  }
  
  private getDataTypes(analyses: StandardizedAnalysis[]): string[] {
    const dataTypes = new Set<string>();
    
    analyses.forEach(a => {
      a.entities.forEach(e => {
        if (e.properties?.dataClassification) {
          dataTypes.add(e.properties.dataClassification.toLowerCase());
        }
      });
      
      a.relationships.forEach(r => {
        if (r.properties?.dataTypes) {
          r.properties.dataTypes.forEach((dt: string) => 
            dataTypes.add(dt.toLowerCase())
          );
        }
      });
    });
    
    return Array.from(dataTypes);
  }
  
  private checkGDPRCompliance(analyses: StandardizedAnalysis[]): any {
    const compliance = {
      encryptionAtRest: false,
      encryptionInTransit: false,
      accessControls: false,
      dataMinimization: false,
      rightToBeForgotten: false
    };
    
    analyses.forEach(a => {
      a.controls.forEach(c => {
        const controlName = c.name.toLowerCase();
        if (controlName.includes('encryption') && controlName.includes('rest')) {
          compliance.encryptionAtRest = true;
        }
        if (controlName.includes('encryption') && controlName.includes('transit')) {
          compliance.encryptionInTransit = true;
        }
        if (controlName.includes('access control') || controlName.includes('rbac')) {
          compliance.accessControls = true;
        }
      });
    });
    
    return compliance;
  }
  
  private checkPCICompliance(analyses: StandardizedAnalysis[]): any {
    const compliance = {
      networkSegmentation: false,
      strongCryptography: false,
      accessLogging: false,
      vulnerabilityScanning: false
    };
    
    analyses.forEach(a => {
      a.controls.forEach(c => {
        const controlName = c.name.toLowerCase();
        if (controlName.includes('segmentation') || controlName.includes('isolation')) {
          compliance.networkSegmentation = true;
        }
        if (controlName.includes('encryption') && 
            (controlName.includes('aes') || controlName.includes('strong'))) {
          compliance.strongCryptography = true;
        }
      });
    });
    
    return compliance;
  }
  
  private checkHIPAACompliance(analyses: StandardizedAnalysis[]): any {
    const compliance = {
      accessControls: false,
      auditLogging: false,
      encryption: false,
      integrityControls: false
    };
    
    analyses.forEach(a => {
      a.controls.forEach(c => {
        const controlName = c.name.toLowerCase();
        if (controlName.includes('audit') || controlName.includes('logging')) {
          compliance.auditLogging = true;
        }
        if (controlName.includes('access control')) {
          compliance.accessControls = true;
        }
        if (controlName.includes('encryption')) {
          compliance.encryption = true;
        }
        if (controlName.includes('integrity') || controlName.includes('hash')) {
          compliance.integrityControls = true;
        }
      });
    });
    
    return compliance;
  }
  
  private findUnclassifiedData(analyses: StandardizedAnalysis[]): any[] {
    const unclassified: any[] = [];
    
    analyses.forEach(a => {
      a.entities
        .filter(e => 
          e.type === 'datastore' && 
          !e.properties?.dataClassification
        )
        .forEach(e => unclassified.push(e));
    });
    
    return unclassified;
  }
  
  private findHighValueData(analyses: StandardizedAnalysis[]): any[] {
    const highValue: any[] = [];
    
    analyses.forEach(a => {
      a.entities
        .filter(e => 
          e.properties?.dataClassification?.includes('confidential') ||
          e.properties?.dataClassification?.includes('secret') ||
          e.properties?.criticality === 'high' ||
          e.properties?.businessValue === 'high'
        )
        .forEach(e => highValue.push(e));
    });
    
    return highValue;
  }
  
  private hasAdequateProtection(data: any, analyses: StandardizedAnalysis[]): boolean {
    // Check if high-value data has multiple layers of protection
    let protectionLayers = 0;
    
    analyses.forEach(a => {
      a.controls.forEach(c => {
        if (c.properties?.protectedEntity === data.originalId ||
            c.properties?.protectedAssets?.includes(data.name)) {
          protectionLayers++;
        }
      });
    });
    
    return protectionLayers >= 3; // Expect at least 3 layers for high-value data
  }
  
  private getThreatCategories(analyses: StandardizedAnalysis[]): string[] {
    const categories = new Set<string>();
    
    analyses.forEach(a => {
      a.threats.forEach(t => {
        if (t.category) {
          categories.add(t.category.toLowerCase());
        }
      });
    });
    
    return Array.from(categories);
  }
  
  private hasExternalThreatAnalysis(analyses: StandardizedAnalysis[]): boolean {
    return analyses.some(a => 
      a.entities.some(e => e.type === 'adversary') ||
      a.threats.some(t => 
        t.properties?.threatActor || 
        t.properties?.externalThreat === true
      )
    );
  }
  
  private hasThirdPartyComponents(analyses: StandardizedAnalysis[]): boolean {
    return analyses.some(a => 
      a.entities.some(e => 
        e.type === 'external_service' ||
        e.properties?.isThirdParty === true ||
        e.properties?.vendor ||
        e.name.toLowerCase().includes('third-party') ||
        e.name.toLowerCase().includes('external')
      )
    );
  }
  
  private hasSupplyChainAnalysis(analyses: StandardizedAnalysis[]): boolean {
    return analyses.some(a => 
      a.threats.some(t => 
        t.category === 'supply_chain' ||
        t.name.toLowerCase().includes('supply chain') ||
        t.description.toLowerCase().includes('third-party')
      )
    );
  }
  
  // Prioritize and deduplicate gaps
  private prioritizeAndDeduplicate(gaps: AnalysisGap[]): AnalysisGap[] {
    // Remove duplicates based on type and affected entities
    const uniqueGaps = new Map<string, AnalysisGap>();
    
    gaps.forEach(gap => {
      const key = `${gap.type}-${(gap.affectedEntities || []).join(',')}`;
      const existing = uniqueGaps.get(key);
      
      // Keep the more severe gap if duplicate
      if (!existing || this.severityScore(gap.severity) > this.severityScore(existing.severity)) {
        uniqueGaps.set(key, gap);
      }
    });
    
    // Sort by severity
    return Array.from(uniqueGaps.values()).sort((a, b) => 
      this.severityScore(b.severity) - this.severityScore(a.severity)
    );
  }
  
  private severityScore(severity: string): number {
    const scores: Record<string, number> = {
      'critical': 4,
      'high': 3,
      'medium': 2,
      'low': 1
    };
    
    return scores[severity] || 0;
  }
}