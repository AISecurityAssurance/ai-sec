import { useState } from 'react';
import { ChevronRight, ChevronDown, FileText, Users, AlertTriangle, ShieldAlert, GitBranch, Zap, Target, Shield } from 'lucide-react';
import { AnalysisSection, AnalysisTable, AnalysisText, AnalysisDiagram, SystemDescriptionTemplate, AnalysisFlow, AnalysisChart, AnalysisDetail, AnalysisBarChart, AnalysisHeatMap, ThreatListDetail, ThreatListInline } from '../templates';
import { RiskMatrixWithDetails } from './RiskMatrixWithDetails';
import { losses, hazards, ucas, causalScenarios, controllers, controlActions } from '../../apps/user/mockData/stpaSecData';
import { dreadThreats, getRiskDistribution } from '../../apps/user/mockData/dreadData';
import { strideThreats, strideComponents, strideThreatTypes, getStrideByType, componentThreats, threatCategorySummary, riskMatrix } from '../../apps/user/mockData/strideData';
import { businessObjectives, technicalScope, threatActors, attackScenarios, riskAssessments, getCriticalRisks } from '../../apps/user/mockData/pastaData';
import { applicationComponents, vulnerabilities, threatIntelligence, riskHeatMap } from '../../apps/user/mockData/pastaAdditionalData';
import { controlFlowNodes, controlFlowEdges } from '../../apps/user/mockData/controlFlowData';
import { primaryStakeholders, secondaryStakeholders, threatActors as stakeholderThreatActors } from '../../apps/user/mockData/stakeholderData';
import { redTeamScenarios, blueTeamScenarios, purpleTeamScenarios, tabletopScenarios } from '../../apps/user/mockData/wargamingData';
import { maestroAgents, maestroThreats, maestroControls, maestroCategories, getThreatsByAgent, getCriticalThreats as getMaestroCriticalThreats } from '../../apps/user/mockData/maestroData';
import { linddunThreats, dataFlows, privacyControls, linddunCategories, getThreatsByCategory as getLinddunThreatsByCategory, getCriticalThreats as getLinddunCriticalThreats } from '../../apps/user/mockData/linddunData';
import { hazopNodes, hazopDeviations, hazopActions, hazopGuideWords, getDeviationsByNode, getCriticalDeviations, getOpenActions } from '../../apps/user/mockData/hazopData';
import { octaveAssets, octaveThreats, octaveVulnerabilities, octaveRisks, octaveProtectionStrategies, getCriticalRisks as getOctaveCriticalRisks, getHighValueAssets, getThreatsByAsset } from '../../apps/user/mockData/octaveData';
import { useAnalysisStore } from '../../stores/analysisStore';
import { useUCAData } from '../../hooks/useUCAData';
import './CollapsibleAnalysisContent.css';

interface SubSection {
  id: string;
  label: string;
  icon: any;
}

interface CollapsibleAnalysisContentProps {
  analysisId: string;
  enabledAnalyses: Record<string, boolean>;
  focusedSection?: string;
}

// Define subsections for each analysis type
const analysisSubsections: Record<string, SubSection[]> = {
  'stpa-sec': [
    { id: 'system-description', label: 'System Description', icon: FileText },
    { id: 'stakeholders', label: 'Stakeholders', icon: Users },
    { id: 'losses', label: 'Losses', icon: AlertTriangle },
    { id: 'hazards', label: 'Hazards/Vulnerabilities', icon: ShieldAlert },
    { id: 'control-diagram', label: 'Control Diagram', icon: GitBranch },
    { id: 'controllers', label: 'Controllers', icon: Users },
    { id: 'control-actions', label: 'Control Actions', icon: Zap },
    { id: 'ucas', label: 'Unsafe/Unsecure Control Actions', icon: Zap },
    { id: 'scenarios', label: 'Causal Scenarios', icon: Target },
    { id: 'wargaming', label: 'Wargaming', icon: Shield },
  ],
  'stride': [
    { id: 'overview', label: 'STRIDE Overview', icon: FileText },
    { id: 'data-flow-diagram', label: 'Data Flow Diagram', icon: GitBranch },
    { id: 'threats-by-component', label: 'Threats by Component', icon: Shield },
    { id: 'threats-by-category', label: 'Threats by Category', icon: ShieldAlert },
    { id: 'threat-details', label: 'Threat Details', icon: AlertTriangle },
    { id: 'mitigations', label: 'Mitigation Strategies', icon: Shield },
    { id: 'risk-matrix', label: 'Risk Matrix', icon: Target },
  ],
  'pasta': [
    { id: 'overview', label: 'PASTA Overview', icon: FileText },
    { id: 'stage1-objectives', label: 'Stage 1: Business Objectives', icon: Target },
    { id: 'stage2-technical', label: 'Stage 2: Technical Scope', icon: GitBranch },
    { id: 'stage3-decomposition', label: 'Stage 3: Application Decomposition', icon: Shield },
    { id: 'stage4-threats', label: 'Stage 4: Threat Analysis', icon: AlertTriangle },
    { id: 'stage5-vulnerabilities', label: 'Stage 5: Vulnerability Analysis', icon: ShieldAlert },
    { id: 'stage6-attacks', label: 'Stage 6: Attack Modeling', icon: Zap },
    { id: 'stage7-risk', label: 'Stage 7: Risk & Impact Analysis', icon: Target },
  ],
  'dread': [
    { id: 'overview', label: 'DREAD Overview', icon: FileText },
    { id: 'ratings', label: 'Risk Ratings', icon: AlertTriangle },
    { id: 'distribution', label: 'Risk Distribution', icon: Target },
  ],
  'maestro': [
    { id: 'overview', label: 'MAESTRO Overview', icon: FileText },
    { id: 'ai-components', label: 'AI/ML Components', icon: Shield },
    { id: 'threat-analysis', label: 'AI Threat Analysis', icon: AlertTriangle },
    { id: 'data-flows', label: 'Data Flow Mapping', icon: GitBranch },
    { id: 'model-risks', label: 'Model Risk Assessment', icon: ShieldAlert },
    { id: 'compliance', label: 'AI Compliance', icon: Target },
    { id: 'controls', label: 'Security Controls', icon: Shield },
  ],
  'linddun': [
    { id: 'overview', label: 'LINDDUN Overview', icon: FileText },
    { id: 'data-flows', label: 'Data Flow Inventory', icon: GitBranch },
    { id: 'privacy-threats', label: 'Privacy Threat Analysis', icon: ShieldAlert },
    { id: 'threat-categories', label: 'Threat Categories', icon: AlertTriangle },
    { id: 'privacy-controls', label: 'Privacy Controls', icon: Shield },
    { id: 'compliance-mapping', label: 'GDPR Compliance', icon: Target },
  ],
  'hazop': [
    { id: 'overview', label: 'HAZOP Overview', icon: FileText },
    { id: 'process-nodes', label: 'Process Nodes', icon: GitBranch },
    { id: 'deviations', label: 'Deviation Analysis', icon: AlertTriangle },
    { id: 'risk-matrix', label: 'Risk Assessment', icon: Target },
    { id: 'actions', label: 'Action Items', icon: Zap },
    { id: 'guide-words', label: 'Guide Word Reference', icon: Shield },
  ],
  'octave': [
    { id: 'overview', label: 'OCTAVE Overview', icon: FileText },
    { id: 'critical-assets', label: 'Critical Assets', icon: Shield },
    { id: 'threat-profiles', label: 'Threat Profiles', icon: AlertTriangle },
    { id: 'vulnerabilities', label: 'Vulnerability Assessment', icon: ShieldAlert },
    { id: 'risk-analysis', label: 'Risk Analysis', icon: Target },
    { id: 'protection-strategy', label: 'Protection Strategy', icon: Shield },
  ],
};

export default function CollapsibleAnalysisContent({
  analysisId,
  enabledAnalyses,
  focusedSection
}: CollapsibleAnalysisContentProps) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());
  const [selectedDetail, setSelectedDetail] = useState<{ title: string; data: any } | null>(null);
  const [selectedThreats, setSelectedThreats] = useState<{ title: string; threats: any[] } | null>(null);
  const [selectedExercise, setSelectedExercise] = useState<any | null>(null);
  const [selectedHeatMapCell, setSelectedHeatMapCell] = useState<{ title: string; items: any[] } | null>(null);
  const subsections = analysisSubsections[analysisId] || [];
  
  // Get analysis results from store
  const { analysisResults, demoMode } = useAnalysisStore();
  const frameworkResults = analysisResults[analysisId];
  
  // Use the UCA data hook for reactive updates
  const { ucaData, heatMapData, updateUCAData } = useUCAData(analysisId);

  const toggleSection = (sectionId: string) => {
    setExpandedSections(prev => {
      const newSet = new Set(prev);
      if (newSet.has(sectionId)) {
        newSet.delete(sectionId);
      } else {
        newSet.add(sectionId);
      }
      return newSet;
    });
  };

  const handleSave = (id: string, data: any) => {
    console.log(`Saving ${id}:`, data);
    // In real app, would save to backend
  };

  const renderExerciseDetails = (exercise: any) => {
    if (!exercise) return null;

    return (
      <AnalysisSection
        id={`exercise-details-${exercise.id}`}
        title={`Exercise Details: ${exercise.name}`}
        level={4}
        onSave={handleSave}
        defaultExpanded={true}
      >
        <div style={{ padding: 'var(--space-3)' }}>
          <div style={{ marginBottom: 'var(--space-4)' }}>
            <h5>Description</h5>
            <p>{exercise.description}</p>
          </div>

          {exercise.objectives && (
            <div style={{ marginBottom: 'var(--space-4)' }}>
              <h5>Objectives</h5>
              <ul>
                {exercise.objectives.map((obj: string, idx: number) => (
                  <li key={idx}>{obj}</li>
                ))}
              </ul>
            </div>
          )}

          {exercise.scope && (
            <div style={{ marginBottom: 'var(--space-4)' }}>
              <h5>Scope</h5>
              <ul>
                {exercise.scope.map((item: string, idx: number) => (
                  <li key={idx}>{item}</li>
                ))}
              </ul>
            </div>
          )}

          {exercise.tactics && (
            <div style={{ marginBottom: 'var(--space-4)' }}>
              <h5>Tactics</h5>
              <ul>
                {exercise.tactics.map((tactic: string, idx: number) => (
                  <li key={idx}>{tactic}</li>
                ))}
              </ul>
            </div>
          )}

          {exercise.findings && (
            <div style={{ marginBottom: 'var(--space-4)' }}>
              <h5>Findings</h5>
              <ul>
                {exercise.findings.map((finding: string, idx: number) => (
                  <li key={idx}>{finding}</li>
                ))}
              </ul>
            </div>
          )}

          {exercise.improvements && (
            <div style={{ marginBottom: 'var(--space-4)' }}>
              <h5>Improvements</h5>
              <ul>
                {exercise.improvements.map((imp: string, idx: number) => (
                  <li key={idx}>{imp}</li>
                ))}
              </ul>
            </div>
          )}

          <div style={{ marginTop: 'var(--space-4)' }}>
            <button 
              onClick={() => setSelectedExercise(null)}
              style={{
                padding: 'var(--space-2) var(--space-4)',
                background: 'var(--primary)',
                color: 'white',
                border: 'none',
                borderRadius: 'var(--radius-sm)',
                cursor: 'pointer'
              }}
            >
              Close Details
            </button>
          </div>
        </div>
      </AnalysisSection>
    );
  };

  // Render subsection content based on analysis type and subsection
  const renderSubsectionContent = (analysisId: string, subsectionId: string) => {
    if (analysisId === 'stpa-sec') {
      switch (subsectionId) {
        case 'system-description':
          return (
            <SystemDescriptionTemplate
              id={`${analysisId}-${subsectionId}`}
              missionStatement={{
                purpose: "protect sensitive financial data and maintain transaction integrity",
                method: "implementing multi-layered security controls and continuous monitoring",
                goals: [
                  "Process financial transactions securely",
                  "Protect user accounts from unauthorized access",
                  "Maintain data confidentiality and integrity",
                  "Ensure regulatory compliance"
                ],
                constraints: [
                  "Must comply with PCI DSS standards",
                  "Cannot store unencrypted card data",
                  "Must maintain 99.9% uptime",
                  "Response time must be under 2 seconds"
                ]
              }}
              fullDescription={`## System Overview
The Digital Banking Platform is a comprehensive online financial services system designed to provide secure, reliable, and user-friendly banking services to millions of customers.

## Key Components
• **Customer Applications**: Web and mobile applications for account access
• **Backend Services**: Microservices architecture for transaction processing  
• **API Gateway**: Centralized service orchestration and routing
• **Authentication Service**: Multi-factor authentication and session management
• **Transaction Engine**: Core processing system for financial operations
• **Fraud Detection**: Real-time monitoring and anomaly detection
• **Banking Integrations**: Connections to core banking and payment systems

## Operations and Scale
The platform processes over **10 million transactions daily**, serving both retail and business customers with:
• Account management and balance inquiries
• Bill payments and scheduled transfers
• Domestic and international fund transfers
• Loan applications and management
• Investment services and portfolio tracking

## Security Architecture
### Multi-Layered Protection
• **Authentication**: Multi-factor authentication (MFA) for all users
• **Encryption**: End-to-end encryption for data in transit and at rest
• **Monitoring**: 24/7 security operations center (SOC)
• **Detection**: Machine learning-based fraud detection
• **Testing**: Regular penetration testing and vulnerability assessments

### Compliance
• PCI DSS Level 1 certified
• SOX compliant
• GDPR compliant
• Regional banking regulations adherence

## Technical Architecture
Built on a **microservices foundation** with:
• Multi-region deployment for high availability
• Kubernetes orchestration for container management
• Auto-scaling to handle peak loads
• Disaster recovery sites with RPO < 1 hour
• Global load balancing for optimal performance`}
              systemGoals={[
                "Prevent unauthorized access to user accounts",
                "Detect and prevent fraudulent transactions",
                "Maintain audit trail for all financial operations",
                "Ensure data encryption in transit and at rest"
              ]}
              systemConstraints={[
                "Must support 10,000 concurrent users",
                "Cannot exceed $500k annual infrastructure cost",
                "Must integrate with existing banking APIs",
                "Development team limited to 15 engineers"
              ]}
              assumptions={[
                "Users have secure devices for authentication",
                "Third-party payment processors are trustworthy",
                "Network infrastructure is reliable",
                "Regulatory requirements remain stable"
              ]}
              boundariesIncluded={[
                "Web application frontend",
                "Mobile applications (iOS/Android)",
                "API gateway and microservices",
                "User authentication system",
                "Transaction processing engine"
              ]}
              boundariesExcluded={[
                "Third-party payment processors",
                "User devices and browsers",
                "Banking partner systems",
                "Internet service providers"
              ]}
              onSave={handleSave}
            />
          );

        case 'losses':
          const lossColumns = [
            { key: 'id', label: 'ID', sortable: true },
            { key: 'description', label: 'Description' },
            { key: 'stakeholders', label: 'Affected Stakeholders' },
            { key: 'severity', label: 'Severity', sortable: true, type: 'dropdown' as const, options: ['critical', 'high', 'medium', 'low'] }
          ];
          
          // Use data from analysis results if available, otherwise use mock data
          const lossesData = frameworkResults?.sections.find(s => s.id === 'losses')?.content?.losses || losses;
          
          return (
            <AnalysisTable
              id={`${analysisId}-${subsectionId}`}
              title="Identified Losses"
              data={lossesData}
              columns={lossColumns}
              onSave={handleSave}
              sortable
              filterable
              clickableRows
              onRowClick={(row) => {
                setSelectedDetail({
                  title: `Loss ${row.id}: ${row.description}`,
                  data: row
                });
              }}
            />
          );

        case 'hazards':
          const hazardColumns = [
            { key: 'id', label: 'ID', sortable: true },
            { key: 'description', label: 'Description' },
            { key: 'relatedLosses', label: 'Related Losses' },
            { key: 'severity', label: 'Severity', sortable: true, type: 'dropdown' as const, options: ['critical', 'high', 'medium', 'low'] }
          ];
          
          // Use data from analysis results if available, otherwise use mock data
          const hazardsData = frameworkResults?.sections.find(s => s.id === 'hazards')?.content?.hazards || hazards;
          
          return (
            <AnalysisTable
              id={`${analysisId}-${subsectionId}`}
              title="Security Hazards/Vulnerabilities"
              data={hazardsData}
              columns={hazardColumns}
              onSave={handleSave}
              sortable
              filterable
            />
          );

        case 'control-diagram':
          return (
            <AnalysisFlow
              id={`${analysisId}-${subsectionId}`}
              title="System Control Flow Diagram"
              initialNodes={controlFlowNodes}
              initialEdges={controlFlowEdges}
              onSave={handleSave}
            />
          );

        case 'ucas':
          return (
            <AnalysisSection
              id={`${analysisId}-${subsectionId}`}
              title="Unsafe Control Actions Analysis"
              level={3}
              onSave={handleSave}
            >
              <AnalysisHeatMap
                id={`${analysisId}-uca-heatmap`}
                title="UCA Risk Heat Map"
                config={{
                  rows: controlActions.map(ca => ca.action),
                  cols: ['Not Provided', 'Provided Unsafely', 'Wrong Timing', 'Wrong Duration'],
                  cells: heatMapData, // Use data from hook - automatically updates when ucaData changes
                  colorScale: {
                    min: { value: 1, color: '#27ae60', label: 'Very Low' },
                    low: { value: 2, color: '#2ecc71', label: 'Low' },
                    medium: { value: 3, color: '#f1c40f', label: 'Medium' },
                    high: { value: 4, color: '#f39c12', label: 'High' },
                    max: { value: 5, color: '#e74c3c', label: 'Critical' }
                  },
                  xAxisLabel: 'UCA Types',
                  yAxisLabel: 'Control Actions'
                }}
                onSave={handleSave}
                onCellClick={(cell) => {
                  if (cell.data && cell.data.length > 0) {
                    setSelectedHeatMapCell({
                      title: `${cell.row} - ${cell.col}`,
                      items: cell.data
                    });
                  }
                }}
              />
              
              {selectedHeatMapCell && selectedHeatMapCell.items.length > 0 && (
                <div style={{ marginTop: 'var(--space-4)' }}>
                  <ThreatListInline
                    title={selectedHeatMapCell.title}
                    threats={selectedHeatMapCell.items.map(uca => ({
                      id: uca.id,
                      component: controlActions.find(ca => ca.id === uca.controlActionId)?.action || uca.controlActionId,
                      threatType: uca.type,
                      description: uca.description,
                      impact: uca.severity,
                      likelihood: 'medium',
                      riskLevel: uca.severity,
                      mitigations: [`Context: ${uca.context}`, `Hazards: ${uca.hazards.join(', ')}`]
                    }))}
                    onClose={() => setSelectedHeatMapCell(null)}
                  />
                </div>
              )}
              
              <AnalysisTable
                id={`${analysisId}-uca-details`}
                title="Detailed Unsafe Control Actions"
                data={(() => {
                  // Use ucaData from hook instead of separate source
                  return ucaData.map(u => {
                    const ca = controlActions.find(ca => ca.id === u.controlActionId);
                    return {
                      ...u,
                      controlAction: ca?.action || u.controlActionId,
                      relatedHazards: Array.isArray(u.hazards) ? u.hazards.join(', ') : (u.relatedHazards || '')
                    };
                  });
                })()}
                columns={[
                  { key: 'id', label: 'ID', sortable: true },
                  { key: 'controlAction', label: 'Control Action', type: 'dropdown' as const,
                    options: controlActions.map(ca => ca.action)
                  },
                  { key: 'type', label: 'Type', sortable: true, type: 'dropdown' as const, 
                    options: ['not-provided', 'provided', 'wrong-timing', 'wrong-duration']
                  },
                  { key: 'description', label: 'Description' },
                  { key: 'context', label: 'Context' },
                  { key: 'relatedHazards', label: 'Related Hazards' },
                  { key: 'severity', label: 'Severity', sortable: true, type: 'dropdown' as const, 
                    options: ['critical', 'high', 'medium', 'low']
                  }
                ]}
                onSave={(id, updatedData) => {
                  // Transform the data back to the correct format
                  const transformedData = updatedData.map((row: any) => {
                    // Find control action ID from the action name
                    const ca = controlActions.find(c => c.action === row.controlAction);
                    return {
                      ...row,
                      controlActionId: ca?.id || row.controlActionId || controlActions[0]?.id,
                      hazards: typeof row.relatedHazards === 'string' 
                        ? row.relatedHazards.split(',').map((h: string) => h.trim()).filter((h: string) => h)
                        : (row.hazards || [])
                    };
                  });
                  
                  // Update through the hook - this will update store and trigger heat map re-render
                  updateUCAData(transformedData);
                  handleSave(id, transformedData);
                }}
                sortable
                filterable
                pageSize={10}
                editable={true}
              />
              
              <AnalysisText
                id={`${analysisId}-uca-guidance`}
                title="UCA Analysis Guidance"
                content={`## Unsafe Control Action Types

**Not Provided**: Control action is not provided when it should be to prevent a hazard
- Example: Authentication not granted to legitimate user

**Provided Unsafely**: Control action is provided when it creates a hazard
- Example: Authentication granted with invalid credentials

**Wrong Timing**: Control action has correct intent but wrong timing (too early/late)
- Example: IP blocked after attack already succeeded

**Wrong Duration**: Control action applied for wrong duration (too long/short)
- Example: Rate limit applied indefinitely to legitimate traffic

## Comprehensive Analysis
Each control action should be analyzed for all four UCA types to ensure complete coverage. Consider both security (STRIDE) and safety perspectives when identifying UCAs.`}
                onSave={handleSave}
                format="markdown"
              />
            </AnalysisSection>
          );

        case 'scenarios':
          const scenarioColumns = [
            { key: 'id', label: 'ID', sortable: true },
            { key: 'uca', label: 'Related UCA' },
            { key: 'description', label: 'Scenario' },
            { key: 'causalFactors', label: 'Causal Factors' },
            { key: 'strideCategory', label: 'STRIDE Category' },
            { key: 'mitigations', label: 'Mitigations' }
          ];
          
          // Use data from analysis results if available, otherwise use mock data
          const scenariosRaw = frameworkResults?.sections.find(s => s.id === 'scenarios')?.content?.scenarios || causalScenarios;
          
          // Transform data to include UCA reference and convert arrays to strings
          const scenariosData = scenariosRaw.map(s => ({
            id: s.id,
            uca: s.ucaId || s.uca,
            description: s.description,
            causalFactors: Array.isArray(s.causalFactors) ? s.causalFactors.join('; ') : (s.causalFactors || ''),
            strideCategory: s.strideCategory || '',
            mitigations: Array.isArray(s.mitigations) ? s.mitigations.join('; ') : (s.mitigations || '')
          }));
          
          return (
            <AnalysisTable
              id={`${analysisId}-${subsectionId}`}
              title="Causal Scenarios"
              data={scenariosData}
              columns={scenarioColumns}
              onSave={handleSave}
              sortable
              filterable
              pageSize={15}
              clickableRows
              onRowClick={(row) => {
                const scenario = causalScenarios.find(s => s.id === row.id);
                if (scenario) {
                  setSelectedDetail({
                    title: `Scenario ${scenario.id}: ${scenario.description}`,
                    data: scenario
                  });
                }
              }}
            />
          );

        case 'stakeholders':
          return (
            <AnalysisSection
              id={`${analysisId}-${subsectionId}`}
              title="Stakeholder Analysis"
              level={3}
              onSave={handleSave}
            >
              <AnalysisTable
                id={`${analysisId}-primary-stakeholders`}
                title="Primary Stakeholders"
                data={primaryStakeholders}
                columns={[
                  { key: 'id', label: 'ID', sortable: true },
                  { key: 'name', label: 'Stakeholder' },
                  { key: 'interest', label: 'Primary Interests' },
                  { key: 'influence', label: 'Influence', sortable: true, type: 'dropdown', options: ['low', 'medium', 'high', 'critical'] }
                ]}
                onSave={handleSave}
                sortable
                filterable
              />
              
              <AnalysisTable
                id={`${analysisId}-secondary-stakeholders`}
                title="Secondary Stakeholders"
                data={secondaryStakeholders}
                columns={[
                  { key: 'id', label: 'ID', sortable: true },
                  { key: 'name', label: 'Stakeholder' },
                  { key: 'interest', label: 'Primary Interests' },
                  { key: 'influence', label: 'Influence', sortable: true, type: 'dropdown', options: ['low', 'medium', 'high', 'critical'] }
                ]}
                onSave={handleSave}
                sortable
                filterable
              />
              
              <AnalysisTable
                id={`${analysisId}-threat-actors`}
                title="Threat Actors"
                data={stakeholderThreatActors}
                columns={[
                  { key: 'id', label: 'ID', sortable: true },
                  { key: 'name', label: 'Threat Actor' },
                  { key: 'interest', label: 'Objectives' },
                  { key: 'motivation', label: 'Motivation' },
                  { key: 'influence', label: 'Threat Level', sortable: true, type: 'dropdown', options: ['low', 'medium', 'high', 'critical'] }
                ]}
                onSave={handleSave}
                sortable
                filterable
              />
            </AnalysisSection>
          );

        case 'controllers':
          const controllerColumns = [
            { key: 'id', label: 'ID', sortable: true },
            { key: 'name', label: 'Controller' },
            { key: 'type', label: 'Type', sortable: true, type: 'dropdown' as const, options: ['human', 'software', 'organizational'] },
            { key: 'responsibilities', label: 'Responsibilities' },
            { key: 'processModel', label: 'Process Model' }
          ];
          
          // Transform array fields to strings for display
          const controllersData = controllers.map(c => ({
            ...c,
            responsibilities: c.responsibilities.join('; '),
            processModel: c.processModel.join('; ')
          }));
          
          return (
            <AnalysisTable
              id={`${analysisId}-${subsectionId}`}
              title="System Controllers"
              data={controllersData}
              columns={controllerColumns}
              onSave={handleSave}
              sortable
              filterable
            />
          );

        case 'control-actions':
          const controlActionColumns = [
            { key: 'id', label: 'ID', sortable: true },
            { key: 'controllerId', label: 'Controller', sortable: true },
            { key: 'action', label: 'Control Action' },
            { key: 'targetProcess', label: 'Target Process' },
            { key: 'constraints', label: 'Constraints' }
          ];
          
          // Transform array fields to strings for display
          const controlActionsData = controlActions.map(ca => ({
            ...ca,
            constraints: ca.constraints.join('; ')
          }));
          
          return (
            <AnalysisTable
              id={`${analysisId}-${subsectionId}`}
              title="Control Actions"
              data={controlActionsData}
              columns={controlActionColumns}
              onSave={handleSave}
              sortable
              filterable
            />
          );

        case 'wargaming':
          return (
            <AnalysisSection
              id={`${analysisId}-${subsectionId}`}
              title="Wargaming & Security Exercises"
              level={3}
              onSave={handleSave}
            >
              <AnalysisTable
                id={`${analysisId}-red-team`}
                title="Red Team Exercises"
                data={redTeamScenarios.map(s => ({
                  id: s.id,
                  name: s.name,
                  description: s.description,
                  objectives: s.objectives.join('; '),
                  duration: s.duration,
                  findings: s.findings ? s.findings.length : 0
                }))}
                columns={[
                  { key: 'id', label: 'ID' },
                  { key: 'name', label: 'Exercise Name' },
                  { key: 'description', label: 'Description' },
                  { key: 'objectives', label: 'Objectives' },
                  { key: 'duration', label: 'Duration' },
                  { key: 'findings', label: 'Findings Count', sortable: true }
                ]}
                onSave={handleSave}
                sortable
                filterable
                clickableRows
                onRowClick={(row) => {
                  const scenario = redTeamScenarios.find(s => s.id === row.id);
                  if (scenario) {
                    setSelectedExercise(scenario);
                  }
                }}
              />
              
              <AnalysisTable
                id={`${analysisId}-blue-team`}
                title="Blue Team Exercises"
                data={blueTeamScenarios.map(s => ({
                  id: s.id,
                  name: s.name,
                  description: s.description,
                  objectives: s.objectives.join('; '),
                  duration: s.duration,
                  improvements: s.improvements ? s.improvements.length : 0
                }))}
                columns={[
                  { key: 'id', label: 'ID' },
                  { key: 'name', label: 'Exercise Name' },
                  { key: 'description', label: 'Description' },
                  { key: 'objectives', label: 'Objectives' },
                  { key: 'duration', label: 'Duration' },
                  { key: 'improvements', label: 'Improvements', sortable: true }
                ]}
                onSave={handleSave}
                sortable
                filterable
                clickableRows
                onRowClick={(row) => {
                  const scenario = blueTeamScenarios.find(s => s.id === row.id);
                  if (scenario) {
                    setSelectedExercise(scenario);
                  }
                }}
              />
              
              <AnalysisTable
                id={`${analysisId}-purple-team`}
                title="Purple Team Exercises"
                data={purpleTeamScenarios.map(s => ({
                  id: s.id,
                  name: s.name,
                  description: s.description,
                  objectives: s.objectives.join('; '),
                  duration: s.duration,
                  improvements: s.improvements ? s.improvements.length : 0
                }))}
                columns={[
                  { key: 'id', label: 'ID' },
                  { key: 'name', label: 'Exercise Name' },
                  { key: 'description', label: 'Description' },
                  { key: 'objectives', label: 'Objectives' },
                  { key: 'duration', label: 'Duration' },
                  { key: 'improvements', label: 'Improvements', sortable: true }
                ]}
                onSave={handleSave}
                sortable
                filterable
                clickableRows
                onRowClick={(row) => {
                  const scenario = purpleTeamScenarios.find(s => s.id === row.id);
                  if (scenario) {
                    setSelectedExercise(scenario);
                  }
                }}
              />
              
              <AnalysisTable
                id={`${analysisId}-tabletop`}
                title="Tabletop Exercises"
                data={tabletopScenarios.map(s => ({
                  id: s.id,
                  name: s.name,
                  description: s.description,
                  objectives: s.objectives.join('; '),
                  participants: s.participants.join(', '),
                  duration: s.duration
                }))}
                columns={[
                  { key: 'id', label: 'ID' },
                  { key: 'name', label: 'Exercise Name' },
                  { key: 'description', label: 'Description' },
                  { key: 'objectives', label: 'Objectives' },
                  { key: 'participants', label: 'Participants' },
                  { key: 'duration', label: 'Duration' }
                ]}
                onSave={handleSave}
                sortable
                filterable
                clickableRows
                onRowClick={(row) => {
                  const scenario = tabletopScenarios.find(s => s.id === row.id);
                  if (scenario) {
                    setSelectedExercise(scenario);
                  }
                }}
              />
              
              {selectedExercise && renderExerciseDetails(selectedExercise)}
            </AnalysisSection>
          );

        default:
          return (
            <AnalysisText
              id={`${analysisId}-${subsectionId}`}
              title={subsectionId}
              content={`Content for ${subsectionId} would go here...`}
              onSave={handleSave}
            />
          );
      }
    }

    if (analysisId === 'dread') {
      switch (subsectionId) {
        case 'ratings':
          // Use data from analysis results if available
          const dreadThreatsRaw = frameworkResults?.sections.find(s => s.id === 'ratings')?.content?.threats || dreadThreats;
          
          const dreadColumns = [
            { key: 'id', label: 'ID', sortable: true },
            { key: 'threat', label: 'Threat' },
            { key: 'category', label: 'Category', sortable: true, type: 'dropdown' as const, options: ['Input Validation', 'Authentication', 'Authorization', 'Data Exposure', 'Business Logic'] },
            { key: 'damage', label: 'D', sortable: true, type: 'dropdown' as const, options: ['1', '2', '3'] },
            { key: 'reproducibility', label: 'R', sortable: true, type: 'dropdown' as const, options: ['1', '2', '3'] },
            { key: 'exploitability', label: 'E', sortable: true, type: 'dropdown' as const, options: ['1', '2', '3'] },
            { key: 'affectedUsers', label: 'A', sortable: true, type: 'dropdown' as const, options: ['1', '2', '3'] },
            { key: 'discoverability', label: 'D', sortable: true, type: 'dropdown' as const, options: ['1', '2', '3'] },
            { key: 'totalScore', label: 'Score', sortable: true },
            { key: 'riskLevel', label: 'Level', sortable: true, type: 'dropdown' as const, options: ['Low', 'Medium', 'High', 'Critical'] }
          ];
          
          // Flatten the dreadThreats data to make scores accessible
          const flattenedDreadData = dreadThreatsRaw.map(threat => ({
            ...threat,
            damage: threat.damage || threat.scores?.damage || 0,
            reproducibility: threat.reproducibility || threat.scores?.reproducibility || 0,
            exploitability: threat.exploitability || threat.scores?.exploitability || 0,
            affectedUsers: threat.affectedUsers || threat.scores?.affectedUsers || 0,
            discoverability: threat.discoverability || threat.scores?.discoverability || 0,
            totalScore: threat.totalScore || threat.scores?.total || 0,
            threat: threat.threat || threat.name || '',
            riskLevel: threat.riskLevel || 'Medium'
          }));
          
          return (
            <AnalysisTable
              id={`${analysisId}-${subsectionId}`}
              title="DREAD Risk Ratings"
              data={flattenedDreadData}
              columns={dreadColumns}
              onSave={handleSave}
              sortable
              filterable
            />
          );

        case 'distribution':
          const riskDist = getRiskDistribution();
          return (
            <AnalysisSection
              id={`${analysisId}-${subsectionId}`}
              title="Risk Analysis Charts"
              level={3}
              onSave={handleSave}
            >
              <div style={{ 
                display: 'grid', 
                gridTemplateColumns: '1fr 1fr', 
                gap: 'var(--space-4)'
              }}>
                <AnalysisBarChart
                  id={`${analysisId}-risk-distribution`}
                  title="Risk Distribution"
                  data={[
                    { label: 'Critical', value: riskDist.Critical, color: '#dc2626' },
                    { label: 'High', value: riskDist.High, color: '#f59e0b' },
                    { label: 'Medium', value: riskDist.Medium, color: '#3b82f6' },
                    { label: 'Low', value: riskDist.Low, color: '#10b981' }
                  ]}
                  xAxisLabel="Number of Threats"
                  useColors={true}
                  onSave={handleSave}
                />
                
                <AnalysisBarChart
                  id={`${analysisId}-threat-categories`}
                  title="Threats by Category"
                  data={[
                    { label: 'Input Val.', value: 2 },
                    { label: 'Auth', value: 1 },
                    { label: 'Crypto', value: 2 },
                    { label: 'Access', value: 2 },
                    { label: 'Session', value: 1 },
                    { label: 'Audit', value: 1 },
                    { label: 'Config', value: 1 }
                  ]}
                  xAxisLabel="Number of Threats"
                  defaultColor="#8b5cf6"
                  onSave={handleSave}
                />
              </div>
            </AnalysisSection>
          );

        case 'overview':
          return (
            <AnalysisText
              id={`${analysisId}-${subsectionId}`}
              title="DREAD Overview"
              content={`DREAD is a risk assessment model developed by Microsoft for evaluating security threats. It helps quantify and prioritize risks based on five key factors:

**D**amage: How bad would an attack be?
**R**eproducibility: How easy is it to reproduce the attack?
**E**xploitability: How much work is it to launch the attack?
**A**ffected Users: How many people will be impacted?
**D**iscoverability: How easy is it to discover the threat?

Each factor is scored from 1-3:
- 1 = Low risk/impact
- 2 = Medium risk/impact  
- 3 = High risk/impact

Total scores range from 5-15:
- 5-6: Low Risk
- 7-9: Medium Risk
- 10-12: High Risk
- 13-15: Critical Risk

This systematic approach helps security teams prioritize threats based on their potential impact and likelihood.`}
              onSave={handleSave}
              format="markdown"
            />
          );

        default:
          return (
            <AnalysisText
              id={`${analysisId}-${subsectionId}`}
              title="DREAD Overview"
              content="DREAD is a risk assessment model..."
              onSave={handleSave}
            />
          );
      }
    }

    if (analysisId === 'stride') {
      switch (subsectionId) {
        case 'overview':
          return (
            <AnalysisText
              id={`${analysisId}-${subsectionId}`}
              title="STRIDE Overview"
              content={`STRIDE is a threat modeling framework developed by Microsoft that categorizes security threats into six types:

**S**poofing: Pretending to be something or someone else
**T**ampering: Modifying data or code
**R**epudiation: Claiming to not have performed an action
**I**nformation Disclosure: Exposing information to unauthorized users
**D**enial of Service: Deny or degrade service availability
**E**levation of Privilege: Gain unauthorized capabilities

STRIDE helps identify and categorize threats systematically during the design phase, enabling teams to build appropriate security controls for each threat type.`}
              onSave={handleSave}
              format="markdown"
            />
          );

        case 'data-flow-diagram':
          // Create STRIDE-specific data flow nodes
          const strideDataFlowNodes = [
            { id: '1', data: { label: 'User Browser' }, position: { x: 100, y: 100 }, style: { background: '#e3f2fd' } },
            { id: '2', data: { label: 'Web Portal' }, position: { x: 300, y: 100 }, style: { background: '#fff3e0' } },
            { id: '3', data: { label: 'API Gateway' }, position: { x: 500, y: 100 }, style: { background: '#f3e5f5' } },
            { id: '4', data: { label: 'Auth Service' }, position: { x: 300, y: 250 }, style: { background: '#e8f5e9' } },
            { id: '5', data: { label: 'Transaction Engine' }, position: { x: 500, y: 250 }, style: { background: '#fce4ec' } },
            { id: '6', data: { label: 'Customer DB' }, position: { x: 700, y: 250 }, style: { background: '#fff9c4' } },
            { id: '7', data: { label: 'Fraud Detection' }, position: { x: 500, y: 400 }, style: { background: '#ffebee' } },
            { id: '8', data: { label: 'Core Banking' }, position: { x: 700, y: 400 }, style: { background: '#e0f2f1' } }
          ];
          
          const strideDataFlowEdges = [
            { id: 'e1-2', source: '1', target: '2', label: 'HTTPS', animated: true },
            { id: 'e2-3', source: '2', target: '3', label: 'API Calls' },
            { id: 'e3-4', source: '3', target: '4', label: 'Auth Request' },
            { id: 'e3-5', source: '3', target: '5', label: 'Transaction' },
            { id: 'e4-6', source: '4', target: '6', label: 'User Lookup' },
            { id: 'e5-7', source: '5', target: '7', label: 'Risk Check' },
            { id: 'e5-8', source: '5', target: '8', label: 'Process' },
            { id: 'e6-4', source: '6', target: '4', label: 'User Data', style: { stroke: '#888' } },
            { id: 'e7-5', source: '7', target: '5', label: 'Risk Score', style: { stroke: '#f44336' } }
          ];
          
          return (
            <AnalysisFlow
              id={`${analysisId}-${subsectionId}`}
              title="System Data Flow Diagram"
              initialNodes={strideDataFlowNodes}
              initialEdges={strideDataFlowEdges}
              onSave={handleSave}
            />
          );

        case 'threats-by-component':
          // Use data from analysis results if available
          const strideThreatsData = frameworkResults?.sections.find(s => s.id === 'threats')?.content?.threats || strideThreats;
          
          const componentColumns = [
            { key: 'component', label: 'Component' },
            { key: 'spoofing', label: 'S', sortable: true },
            { key: 'tampering', label: 'T', sortable: true },
            { key: 'repudiation', label: 'R', sortable: true },
            { key: 'informationDisclosure', label: 'I', sortable: true },
            { key: 'denialOfService', label: 'D', sortable: true },
            { key: 'elevationOfPrivilege', label: 'E', sortable: true },
            { key: 'total', label: 'Total', sortable: true }
          ];

          return (
            <AnalysisTable
              id={`${analysisId}-${subsectionId}`}
              title="Threats by Component"
              data={componentThreats}
              columns={componentColumns}
              onSave={handleSave}
              sortable
              clickableRows
              onRowClick={(row) => {
                const threats = strideThreats.filter(t => t.component === row.component);
                setSelectedThreats({
                  title: `${row.component} Threats`,
                  threats: threats
                });
              }}
            />
          );

        case 'threats-by-category':
          return (
            <AnalysisSection
              id={`${analysisId}-${subsectionId}`}
              title="Threats by Category"
              level={3}
              onSave={handleSave}
            >
              {strideThreatTypes.map(category => {
                const categoryThreats = getStrideByType(category.type as any);
                return (
                  <AnalysisSection
                    key={category.type}
                    id={`${analysisId}-${category.type.toLowerCase().replace(/\s+/g, '-')}`}
                    title={`${category.type} ${category.icon}`}
                    level={3}
                    onSave={handleSave}
                    collapsible
                    defaultExpanded={false}
                  >
                    <AnalysisText
                      id={`${analysisId}-${category.type}-description`}
                      content={category.description}
                      onSave={handleSave}
                    />
                    <AnalysisTable
                      id={`${analysisId}-${category.type}-threats`}
                      title=""
                      data={categoryThreats}
                      columns={[
                        { key: 'id', label: 'ID' },
                        { key: 'component', label: 'Component' },
                        { key: 'description', label: 'Threat' },
                        { key: 'impact', label: 'Impact' },
                        { key: 'status', label: 'Status' }
                      ]}
                      onSave={handleSave}
                      pageSize={5}
                    />
                  </AnalysisSection>
                );
              })}
            </AnalysisSection>
          );

        case 'threat-details':
          const strideColumns = [
            { key: 'id', label: 'ID', sortable: true },
            { key: 'component', label: 'Component', sortable: true },
            { key: 'threatType', label: 'Type', sortable: true, type: 'dropdown' as const, options: ['Spoofing', 'Tampering', 'Repudiation', 'Information Disclosure', 'Denial of Service', 'Elevation of Privilege'] },
            { key: 'description', label: 'Description' },
            { key: 'likelihood', label: 'Likelihood', sortable: true, type: 'dropdown' as const, options: ['low', 'medium', 'high'] },
            { key: 'impact', label: 'Impact', sortable: true, type: 'dropdown' as const, options: ['low', 'medium', 'high'] },
            { key: 'riskLevel', label: 'Risk', sortable: true, type: 'dropdown' as const, options: ['low', 'medium', 'high', 'critical'] },
            { key: 'status', label: 'Status', type: 'dropdown' as const, options: ['identified', 'mitigating', 'mitigated', 'accepted'] }
          ];

          return (
            <AnalysisTable
              id={`${analysisId}-${subsectionId}`}
              title="All STRIDE Threats"
              data={strideThreats}
              columns={strideColumns}
              onSave={handleSave}
              sortable
              filterable
              pageSize={10}
              clickableRows
              onRowClick={(row) => {
                setSelectedDetail({
                  title: `Threat Details: ${row.id}`,
                  data: row
                });
              }}
            />
          );

        case 'mitigations':
          return (
            <AnalysisTable
              id={`${analysisId}-${subsectionId}`}
              title="Mitigation Strategies"
              data={strideThreats.map(t => ({
                id: t.id,
                threat: t.description,
                type: t.threatType,
                component: t.component,
                mitigations: t.mitigations.join('; '),
                status: t.status
              }))}
              columns={[
                { key: 'id', label: 'Threat ID', sortable: true },
                { key: 'component', label: 'Component', sortable: true },
                { key: 'type', label: 'Type', sortable: true },
                { key: 'threat', label: 'Threat' },
                { key: 'mitigations', label: 'Mitigation Strategies' },
                { key: 'status', label: 'Status', type: 'dropdown' as const, options: ['identified', 'mitigating', 'mitigated', 'accepted'] }
              ]}
              onSave={handleSave}
              sortable
              filterable
            />
          );

        case 'risk-matrix':
          return (
            <AnalysisSection
              id={`${analysisId}-${subsectionId}`}
              title="Risk Matrix Visualization"
              level={3}
              onSave={handleSave}
            >
              <RiskMatrixWithDetails 
                threats={strideThreats}
                onSave={handleSave}
              />
              
              {/* STRIDE category colors */}
              {(() => {
                const strideColors: Record<string, string> = {
                  'spoofing': '#e74c3c',
                  'tampering': '#e67e22',
                  'repudiation': '#f39c12',
                  'informationDisclosure': '#9b59b6',
                  'denialOfService': '#3498db',
                  'elevationOfPrivilege': '#2ecc71'
                };
                
                return (
                  <AnalysisBarChart
                    id={`${analysisId}-threat-distribution`}
                    title="Threat Category Distribution"
                    data={Object.entries(threatCategorySummary).map(([key, value]) => ({
                      label: key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase()),
                      value: value as number,
                      color: strideColors[key] || '#95a5a6'
                    }))}
                    xAxisLabel="Threat Category"
                    yAxisLabel="Number of Threats"
                    horizontal={true}
                    useColors={true}
                    onSave={handleSave}
                  />
                );
              })()}
            </AnalysisSection>
          );

        default:
          return (
            <AnalysisText
              id={`${analysisId}-${subsectionId}`}
              title={subsectionId}
              content={`Content for ${subsectionId} would go here...`}
              onSave={handleSave}
            />
          );
      }
    }

    if (analysisId === 'pasta') {
      switch (subsectionId) {
        case 'overview':
          return (
            <AnalysisText
              id={`${analysisId}-${subsectionId}`}
              title="PASTA Overview"
              content={`PASTA (Process for Attack Simulation and Threat Analysis) is a seven-stage risk-centric threat modeling methodology:

1. **Define Business Objectives** - Identify what needs protection
2. **Define Technical Scope** - Map the technical environment
3. **Application Decomposition** - Break down the application architecture
4. **Threat Analysis** - Identify threat actors and methods
5. **Vulnerability Analysis** - Find weaknesses that could be exploited
6. **Attack Modeling** - Simulate attack scenarios
7. **Risk & Impact Analysis** - Quantify and prioritize risks

PASTA aligns technical threats with business impact, helping organizations make risk-based security decisions.`}
              onSave={handleSave}
              format="markdown"
            />
          );

        case 'stage1-objectives':
          return (
            <AnalysisTable
              id={`${analysisId}-${subsectionId}`}
              title="Stage 1: Business Objectives"
              data={businessObjectives}
              columns={[
                { key: 'id', label: 'ID', sortable: true },
                { key: 'objective', label: 'Business Objective' },
                { key: 'priority', label: 'Priority', type: 'dropdown' as const, options: ['low', 'medium', 'high', 'critical'] },
                { key: 'impactArea', label: 'Impact Area' },
                { key: 'relatedAssets', label: 'Related Assets' }
              ]}
              onSave={handleSave}
              sortable
              filterable
            />
          );

        case 'stage2-technical':
          return (
            <AnalysisTable
              id={`${analysisId}-${subsectionId}`}
              title="Stage 2: Technical Scope"
              data={technicalScope}
              columns={[
                { key: 'id', label: 'ID' },
                { key: 'component', label: 'Component' },
                { key: 'technology', label: 'Technology Stack' },
                { key: 'interfaces', label: 'Interfaces' },
                { key: 'dependencies', label: 'Dependencies' }
              ]}
              onSave={handleSave}
              sortable
              filterable
            />
          );

        case 'stage3-decomposition':
          return (
            <AnalysisSection
              id={`${analysisId}-${subsectionId}`}
              title="Stage 3: Application Decomposition"
              level={3}
              onSave={handleSave}
            >
              <AnalysisFlow
                id={`${analysisId}-data-flow`}
                title="Data Flow Diagram"
                initialNodes={[
                  { id: 'AC-001', data: { label: 'Customer Web Portal' }, position: { x: 100, y: 100 }, style: { background: '#e3f2fd' } },
                  { id: 'AC-002', data: { label: 'API Gateway' }, position: { x: 400, y: 100 }, style: { background: '#f3e5f5' } },
                  { id: 'AC-003', data: { label: 'Transaction Processing' }, position: { x: 400, y: 300 }, style: { background: '#fce4ec' } },
                  { id: 'AC-004', data: { label: 'Customer Database' }, position: { x: 700, y: 200 }, style: { background: '#fff9c4' } },
                  { id: 'CDN', data: { label: 'CDN' }, position: { x: 100, y: 0 }, style: { background: '#e0f2f1' } },
                  { id: 'Auth', data: { label: 'Auth Service' }, position: { x: 400, y: 200 }, style: { background: '#e8f5e9' } },
                  { id: 'CoreBanking', data: { label: 'Core Banking' }, position: { x: 700, y: 300 }, style: { background: '#f5f5f5' } },
                  { id: 'FraudDetection', data: { label: 'Fraud Detection' }, position: { x: 400, y: 400 }, style: { background: '#ffebee' } }
                ]}
                initialEdges={[
                  { id: 'e1', source: 'AC-001', target: 'CDN', label: 'Static Assets', animated: true, style: { stroke: '#2ecc71' } },
                  { id: 'e2', source: 'AC-001', target: 'AC-002', label: 'User Requests', animated: true, style: { stroke: '#2ecc71' } },
                  { id: 'e3', source: 'AC-002', target: 'Auth', label: 'Auth Requests', animated: true, style: { stroke: '#2ecc71' } },
                  { id: 'e4', source: 'AC-002', target: 'AC-003', label: 'Transactions', animated: true, style: { stroke: '#2ecc71' } },
                  { id: 'e5', source: 'AC-003', target: 'CoreBanking', label: 'Transaction Requests', animated: true, style: { stroke: '#2ecc71' } },
                  { id: 'e6', source: 'FraudDetection', target: 'AC-003', label: 'Risk Scores', animated: true, style: { stroke: '#2ecc71' } },
                  { id: 'e7', source: 'Auth', target: 'AC-004', label: 'User Queries', animated: true, style: { stroke: '#2ecc71' } },
                  { id: 'e8', source: 'AC-004', target: 'Auth', label: 'User Data', style: { stroke: '#888' } }
                ]}
                onSave={handleSave}
              />

              <AnalysisTable
                id={`${analysisId}-components`}
                title="Application Components"
                data={applicationComponents}
                columns={[
                  { key: 'id', label: 'ID' },
                  { key: 'name', label: 'Component Name' },
                  { key: 'type', label: 'Type', type: 'dropdown' as const, options: ['frontend', 'backend', 'database', 'infrastructure', 'external'] },
                  { key: 'trustBoundaries', label: 'Trust Boundaries' },
                  { key: 'assets', label: 'Protected Assets' }
                ]}
                onSave={handleSave}
                sortable
                filterable
              />
            </AnalysisSection>
          );

        case 'stage4-threats':
          return (
            <AnalysisSection
              id={`${analysisId}-${subsectionId}`}
              title="Stage 4: Threat Analysis"
              level={3}
              onSave={handleSave}
            >
              <AnalysisTable
                id={`${analysisId}-threat-actors`}
                title="Threat Actors"
                data={threatActors}
                columns={[
                  { key: 'id', label: 'ID' },
                  { key: 'name', label: 'Threat Actor' },
                  { key: 'motivation', label: 'Motivation' },
                  { key: 'capability', label: 'Capability', type: 'dropdown' as const, options: ['opportunist', 'hacktivist', 'insider', 'organized-crime', 'nation-state'] },
                  { key: 'targetedAssets', label: 'Targeted Assets' },
                  { key: 'ttps', label: 'TTPs' }
                ]}
                onSave={handleSave}
                sortable
                filterable
              />

              <AnalysisTable
                id={`${analysisId}-threat-intelligence`}
                title="Threat Intelligence Feed"
                data={threatIntelligence}
                columns={[
                  { key: 'id', label: 'ID' },
                  { key: 'source', label: 'Source' },
                  { key: 'date', label: 'Date' },
                  { key: 'ioc', label: 'IoC' },
                  { key: 'threatActor', label: 'Actor' },
                  { key: 'relevance', label: 'Relevance', type: 'dropdown' as const, options: ['low', 'medium', 'high'] },
                  { key: 'description', label: 'Description' }
                ]}
                onSave={handleSave}
                sortable
                filterable
              />
            </AnalysisSection>
          );

        case 'stage5-vulnerabilities':
          return (
            <AnalysisTable
              id={`${analysisId}-${subsectionId}`}
              title="Stage 5: Vulnerability Analysis"
              data={vulnerabilities}
              columns={[
                { key: 'id', label: 'ID' },
                { key: 'component', label: 'Component' },
                { key: 'category', label: 'Category', type: 'dropdown' as const, options: ['design', 'implementation', 'configuration', 'operational'] },
                { key: 'description', label: 'Description' },
                { key: 'cwe', label: 'CWE' },
                { key: 'cvss', label: 'CVSS Score', sortable: true },
                { key: 'exploitability', label: 'Exploitability', type: 'dropdown' as const, options: ['low', 'medium', 'high'] },
                { key: 'status', label: 'Status', type: 'dropdown' as const, options: ['open', 'in-progress', 'remediated', 'accepted'] }
              ]}
              onSave={handleSave}
              sortable
              filterable
              pageSize={10}
            />
          );

        case 'stage6-attacks':
          return (
            <AnalysisSection
              id={`${analysisId}-${subsectionId}`}
              title="Stage 6: Attack Modeling"
              level={3}
              onSave={handleSave}
            >
              <AnalysisTable
                id={`${analysisId}-attack-scenarios`}
                title="Attack Scenarios"
                data={attackScenarios}
                columns={[
                  { key: 'id', label: 'ID', sortable: true },
                  { key: 'name', label: 'Attack Scenario' },
                  { key: 'threatActor', label: 'Threat Actor' },
                  { key: 'attackVector', label: 'Attack Vector' },
                  { key: 'vulnerability', label: 'Exploited Vulnerability' },
                  { key: 'impact', label: 'Impact' },
                  { key: 'likelihood', label: 'Likelihood', type: 'dropdown' as const, options: ['very-low', 'low', 'medium', 'high', 'very-high'] },
                  { key: 'risk', label: 'Risk Level', type: 'dropdown' as const, options: ['low', 'medium', 'high', 'critical'] }
                ]}
                onSave={handleSave}
                sortable
                filterable
                pageSize={10}
              />

              <AnalysisDiagram
                id={`${analysisId}-attack-tree-1`}
                title="Attack Tree 1: Steal Customer Financial Data"
              >
                <svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
                    {/* Root Goal */}
                    <rect x="300" y="20" width="200" height="40" fill="#e74c3c" stroke="#333" strokeWidth="2"/>
                    <text x="400" y="45" textAnchor="middle" fill="white" fontWeight="bold">Steal Customer Data</text>
                    
                    {/* OR Gate */}
                    <circle cx="400" cy="100" r="20" fill="#f39c12" stroke="#333" strokeWidth="2"/>
                    <text x="400" y="107" textAnchor="middle" fill="white" fontWeight="bold">OR</text>
                    
                    {/* Branch 1: SQL Injection */}
                    <rect x="100" y="160" width="180" height="40" fill="#3498db" stroke="#333" strokeWidth="2"/>
                    <text x="190" y="185" textAnchor="middle" fill="white">SQL Injection Attack</text>
                    
                    {/* Branch 2: Compromise Admin */}
                    <rect x="520" y="160" width="180" height="40" fill="#3498db" stroke="#333" strokeWidth="2"/>
                    <text x="610" y="185" textAnchor="middle" fill="white">Compromise Admin</text>
                    
                    {/* AND Gate for SQL Injection */}
                    <circle cx="190" cy="240" r="20" fill="#9b59b6" stroke="#333" strokeWidth="2"/>
                    <text x="190" y="247" textAnchor="middle" fill="white" fontWeight="bold">AND</text>
                    
                    {/* AND Gate for Admin */}
                    <circle cx="610" cy="240" r="20" fill="#9b59b6" stroke="#333" strokeWidth="2"/>
                    <text x="610" y="247" textAnchor="middle" fill="white" fontWeight="bold">AND</text>
                    
                    {/* SQL Injection Sub-nodes */}
                    <rect x="50" y="300" width="120" height="35" fill="#2ecc71" stroke="#333" strokeWidth="2"/>
                    <text x="110" y="322" textAnchor="middle" fill="white" fontSize="12">Find Vulnerable</text>
                    
                    <rect x="210" y="300" width="120" height="35" fill="#2ecc71" stroke="#333" strokeWidth="2"/>
                    <text x="270" y="322" textAnchor="middle" fill="white" fontSize="12">Bypass WAF</text>
                    
                    {/* Admin Compromise Sub-nodes */}
                    <rect x="470" y="300" width="120" height="35" fill="#2ecc71" stroke="#333" strokeWidth="2"/>
                    <text x="530" y="322" textAnchor="middle" fill="white" fontSize="12">Phish Credentials</text>
                    
                    <rect x="630" y="300" width="120" height="35" fill="#2ecc71" stroke="#333" strokeWidth="2"/>
                    <text x="690" y="322" textAnchor="middle" fill="white" fontSize="12">Bypass MFA</text>
                    
                    {/* Connections */}
                    <line x1="400" y1="60" x2="400" y2="80" stroke="#333" strokeWidth="2"/>
                    <line x1="400" y1="120" x2="190" y2="160" stroke="#333" strokeWidth="2"/>
                    <line x1="400" y1="120" x2="610" y2="160" stroke="#333" strokeWidth="2"/>
                    <line x1="190" y1="200" x2="190" y2="220" stroke="#333" strokeWidth="2"/>
                    <line x1="610" y1="200" x2="610" y2="220" stroke="#333" strokeWidth="2"/>
                    <line x1="190" y1="260" x2="110" y2="300" stroke="#333" strokeWidth="2"/>
                    <line x1="190" y1="260" x2="270" y2="300" stroke="#333" strokeWidth="2"/>
                    <line x1="610" y1="260" x2="530" y2="300" stroke="#333" strokeWidth="2"/>
                    <line x1="610" y1="260" x2="690" y2="300" stroke="#333" strokeWidth="2"/>
                    
                    {/* Probability Labels */}
                    <text x="110" y="350" textAnchor="middle" fill="#666" fontSize="11">P=0.7</text>
                    <text x="270" y="350" textAnchor="middle" fill="#666" fontSize="11">P=0.4</text>
                    <text x="530" y="350" textAnchor="middle" fill="#666" fontSize="11">P=0.3</text>
                    <text x="690" y="350" textAnchor="middle" fill="#666" fontSize="11">P=0.2</text>
                    
                    {/* Legend */}
                    <text x="50" y="450" fontWeight="bold" fontSize="14">Legend:</text>
                    <rect x="50" y="460" width="30" height="20" fill="#e74c3c"/>
                    <text x="90" y="475" fontSize="12">Goal</text>
                    <rect x="150" y="460" width="30" height="20" fill="#3498db"/>
                    <text x="190" y="475" fontSize="12">Sub-goal</text>
                    <rect x="270" y="460" width="30" height="20" fill="#2ecc71"/>
                    <text x="310" y="475" fontSize="12">Attack Step</text>
                    <circle cx="415" cy="470" r="10" fill="#f39c12"/>
                    <text x="435" y="475" fontSize="12">OR Gate</text>
                    <circle cx="520" cy="470" r="10" fill="#9b59b6"/>
                    <text x="540" y="475" fontSize="12">AND Gate</text>
                  </svg>
              </AnalysisDiagram>
              
              <AnalysisDiagram
                id={`${analysisId}-attack-tree-2`}
                title="Attack Tree 2: Denial of Service Attack"
              >
                <svg viewBox="0 0 800 500" xmlns="http://www.w3.org/2000/svg">
                    {/* Root Goal */}
                    <rect x="300" y="20" width="200" height="40" fill="#e74c3c" stroke="#333" strokeWidth="2"/>
                    <text x="400" y="45" textAnchor="middle" fill="white" fontWeight="bold">Disrupt Service</text>
                    
                    {/* OR Gate */}
                    <circle cx="400" cy="100" r="20" fill="#f39c12" stroke="#333" strokeWidth="2"/>
                    <text x="400" y="107" textAnchor="middle" fill="white" fontWeight="bold">OR</text>
                    
                    {/* Branch 1: DDoS Attack */}
                    <rect x="50" y="160" width="150" height="40" fill="#3498db" stroke="#333" strokeWidth="2"/>
                    <text x="125" y="185" textAnchor="middle" fill="white">DDoS Attack</text>
                    
                    {/* Branch 2: Resource Exhaustion */}
                    <rect x="225" y="160" width="150" height="40" fill="#3498db" stroke="#333" strokeWidth="2"/>
                    <text x="300" y="185" textAnchor="middle" fill="white">Resource Exhaustion</text>
                    
                    {/* Branch 3: Infrastructure Attack */}
                    <rect x="400" y="160" width="150" height="40" fill="#3498db" stroke="#333" strokeWidth="2"/>
                    <text x="475" y="185" textAnchor="middle" fill="white">Infrastructure Attack</text>
                    
                    {/* Branch 4: Logic Bomb */}
                    <rect x="575" y="160" width="150" height="40" fill="#3498db" stroke="#333" strokeWidth="2"/>
                    <text x="650" y="185" textAnchor="middle" fill="white">Logic Bomb</text>
                    
                    {/* DDoS Sub-branches */}
                    <rect x="20" y="240" width="90" height="30" fill="#2ecc71" stroke="#333" strokeWidth="2"/>
                    <text x="65" y="260" textAnchor="middle" fill="white" fontSize="12">Volume Attack</text>
                    
                    <rect x="120" y="240" width="90" height="30" fill="#2ecc71" stroke="#333" strokeWidth="2"/>
                    <text x="165" y="260" textAnchor="middle" fill="white" fontSize="12">Protocol Attack</text>
                    
                    {/* Resource Exhaustion Sub-branches */}
                    <rect x="195" y="240" width="90" height="30" fill="#2ecc71" stroke="#333" strokeWidth="2"/>
                    <text x="240" y="260" textAnchor="middle" fill="white" fontSize="12">API Abuse</text>
                    
                    <rect x="295" y="240" width="90" height="30" fill="#2ecc71" stroke="#333" strokeWidth="2"/>
                    <text x="340" y="260" textAnchor="middle" fill="white" fontSize="12">Memory Leak</text>
                    
                    {/* Infrastructure Sub-branches */}
                    <rect x="370" y="240" width="90" height="30" fill="#2ecc71" stroke="#333" strokeWidth="2"/>
                    <text x="415" y="260" textAnchor="middle" fill="white" fontSize="12">DNS Attack</text>
                    
                    <rect x="470" y="240" width="90" height="30" fill="#2ecc71" stroke="#333" strokeWidth="2"/>
                    <text x="515" y="260" textAnchor="middle" fill="white" fontSize="12">CDN Attack</text>
                    
                    {/* Logic Bomb Sub-branches */}
                    <rect x="545" y="240" width="90" height="30" fill="#2ecc71" stroke="#333" strokeWidth="2"/>
                    <text x="590" y="260" textAnchor="middle" fill="white" fontSize="12">Time Trigger</text>
                    
                    <rect x="645" y="240" width="90" height="30" fill="#2ecc71" stroke="#333" strokeWidth="2"/>
                    <text x="690" y="260" textAnchor="middle" fill="white" fontSize="12">Event Trigger</text>
                    
                    {/* Connections */}
                    <line x1="400" y1="60" x2="400" y2="80" stroke="#333" strokeWidth="2"/>
                    <line x1="400" y1="120" x2="125" y2="160" stroke="#333" strokeWidth="2"/>
                    <line x1="400" y1="120" x2="300" y2="160" stroke="#333" strokeWidth="2"/>
                    <line x1="400" y1="120" x2="475" y2="160" stroke="#333" strokeWidth="2"/>
                    <line x1="400" y1="120" x2="650" y2="160" stroke="#333" strokeWidth="2"/>
                    
                    {/* DDoS connections */}
                    <line x1="125" y1="200" x2="65" y2="240" stroke="#333" strokeWidth="2"/>
                    <line x1="125" y1="200" x2="165" y2="240" stroke="#333" strokeWidth="2"/>
                    
                    {/* Resource connections */}
                    <line x1="300" y1="200" x2="240" y2="240" stroke="#333" strokeWidth="2"/>
                    <line x1="300" y1="200" x2="340" y2="240" stroke="#333" strokeWidth="2"/>
                    
                    {/* Infrastructure connections */}
                    <line x1="475" y1="200" x2="415" y2="240" stroke="#333" strokeWidth="2"/>
                    <line x1="475" y1="200" x2="515" y2="240" stroke="#333" strokeWidth="2"/>
                    
                    {/* Logic Bomb connections */}
                    <line x1="650" y1="200" x2="590" y2="240" stroke="#333" strokeWidth="2"/>
                    <line x1="650" y1="200" x2="690" y2="240" stroke="#333" strokeWidth="2"/>
                </svg>
              </AnalysisDiagram>
              
              <AnalysisDiagram
                id={`${analysisId}-attack-tree-3`}
                title="Attack Tree 3: Account Takeover"
              >
                <svg viewBox="0 0 800 500" xmlns="http://www.w3.org/2000/svg">
                    {/* Root Goal */}
                    <rect x="300" y="20" width="200" height="40" fill="#e74c3c" stroke="#333" strokeWidth="2"/>
                    <text x="400" y="45" textAnchor="middle" fill="white" fontWeight="bold">Account Takeover</text>
                    
                    {/* OR Gate */}
                    <circle cx="400" cy="100" r="20" fill="#f39c12" stroke="#333" strokeWidth="2"/>
                    <text x="400" y="107" textAnchor="middle" fill="white" fontWeight="bold">OR</text>
                    
                    {/* Branch 1: Credential Theft */}
                    <rect x="100" y="160" width="150" height="40" fill="#3498db" stroke="#333" strokeWidth="2"/>
                    <text x="175" y="185" textAnchor="middle" fill="white">Credential Theft</text>
                    
                    {/* Branch 2: Session Hijacking */}
                    <rect x="325" y="160" width="150" height="40" fill="#3498db" stroke="#333" strokeWidth="2"/>
                    <text x="400" y="185" textAnchor="middle" fill="white">Session Hijacking</text>
                    
                    {/* Branch 3: Social Engineering */}
                    <rect x="550" y="160" width="150" height="40" fill="#3498db" stroke="#333" strokeWidth="2"/>
                    <text x="625" y="185" textAnchor="middle" fill="white">Social Engineering</text>
                    
                    {/* AND Gate for Credential Theft */}
                    <circle cx="175" cy="240" r="20" fill="#9b59b6" stroke="#333" strokeWidth="2"/>
                    <text x="175" y="247" textAnchor="middle" fill="white" fontWeight="bold">AND</text>
                    
                    {/* Credential Theft Sub-branches */}
                    <rect x="50" y="290" width="100" height="30" fill="#2ecc71" stroke="#333" strokeWidth="2"/>
                    <text x="100" y="310" textAnchor="middle" fill="white" fontSize="12">Phishing</text>
                    
                    <rect x="200" y="290" width="100" height="30" fill="#2ecc71" stroke="#333" strokeWidth="2"/>
                    <text x="250" y="310" textAnchor="middle" fill="white" fontSize="12">Keylogger</text>
                    
                    {/* Session Hijacking Sub-branches */}
                    <rect x="275" y="240" width="100" height="30" fill="#2ecc71" stroke="#333" strokeWidth="2"/>
                    <text x="325" y="260" textAnchor="middle" fill="white" fontSize="12">XSS Attack</text>
                    
                    <rect x="425" y="240" width="100" height="30" fill="#2ecc71" stroke="#333" strokeWidth="2"/>
                    <text x="475" y="260" textAnchor="middle" fill="white" fontSize="12">MITM Attack</text>
                    
                    {/* Social Engineering Sub-branches */}
                    <rect x="500" y="240" width="100" height="30" fill="#2ecc71" stroke="#333" strokeWidth="2"/>
                    <text x="550" y="260" textAnchor="middle" fill="white" fontSize="12">Pretexting</text>
                    
                    <rect x="650" y="240" width="100" height="30" fill="#2ecc71" stroke="#333" strokeWidth="2"/>
                    <text x="700" y="260" textAnchor="middle" fill="white" fontSize="12">Vishing</text>
                    
                    {/* Connections */}
                    <line x1="400" y1="60" x2="400" y2="80" stroke="#333" strokeWidth="2"/>
                    <line x1="400" y1="120" x2="175" y2="160" stroke="#333" strokeWidth="2"/>
                    <line x1="400" y1="120" x2="400" y2="160" stroke="#333" strokeWidth="2"/>
                    <line x1="400" y1="120" x2="625" y2="160" stroke="#333" strokeWidth="2"/>
                    
                    {/* Credential Theft connections */}
                    <line x1="175" y1="200" x2="175" y2="220" stroke="#333" strokeWidth="2"/>
                    <line x1="175" y1="260" x2="100" y2="290" stroke="#333" strokeWidth="2"/>
                    <line x1="175" y1="260" x2="250" y2="290" stroke="#333" strokeWidth="2"/>
                    
                    {/* Session Hijacking connections */}
                    <line x1="400" y1="200" x2="325" y2="240" stroke="#333" strokeWidth="2"/>
                    <line x1="400" y1="200" x2="475" y2="240" stroke="#333" strokeWidth="2"/>
                    
                    {/* Social Engineering connections */}
                    <line x1="625" y1="200" x2="550" y2="240" stroke="#333" strokeWidth="2"/>
                    <line x1="625" y1="200" x2="700" y2="240" stroke="#333" strokeWidth="2"/>
                </svg>
              </AnalysisDiagram>
            </AnalysisSection>
          );

        case 'stage7-risk':
          return (
            <AnalysisSection
              id={`${analysisId}-${subsectionId}`}
              title="Stage 7: Risk & Impact Analysis"
              level={3}
              onSave={handleSave}
            >
              <AnalysisTable
                id={`${analysisId}-risk-assessment`}
                title="Risk Assessment"
                data={riskAssessments}
                columns={[
                  { key: 'id', label: 'ID' },
                  { key: 'scenario', label: 'Attack Scenario' },
                  { key: 'businessImpact', label: 'Business Impact (1-5)', sortable: true },
                  { key: 'technicalImpact', label: 'Technical Impact (1-5)', sortable: true },
                  { key: 'likelihood', label: 'Likelihood (1-5)', sortable: true },
                  { key: 'overallRisk', label: 'Risk Score', sortable: true },
                  { key: 'treatment', label: 'Treatment', type: 'dropdown' as const, options: ['mitigate', 'accept', 'transfer', 'avoid'] },
                  { key: 'mitigation', label: 'Mitigation Strategy' }
                ]}
                onSave={handleSave}
                sortable
                filterable
              />

              {/* Risk Heat Map - showing each risk category separately */}
              <AnalysisBarChart
                id={`${analysisId}-risk-heatmap-confidentiality`}
                title="Confidentiality Risk by Component"
                data={riskHeatMap.map(r => ({
                  label: r.component,
                  value: r.risks.confidentiality,
                  color: '#e74c3c'
                }))}
                xAxisLabel="Risk Score"
                yAxisLabel="Component"
                horizontal={true}
                useColors={true}
                onSave={handleSave}
              />
              
              <AnalysisBarChart
                id={`${analysisId}-risk-heatmap-integrity`}
                title="Integrity Risk by Component"
                data={riskHeatMap.map(r => ({
                  label: r.component,
                  value: r.risks.integrity,
                  color: '#f39c12'
                }))}
                xAxisLabel="Risk Score"
                yAxisLabel="Component"
                horizontal={true}
                useColors={true}
                onSave={handleSave}
              />
              
              <AnalysisBarChart
                id={`${analysisId}-risk-heatmap-availability`}
                title="Availability Risk by Component"
                data={riskHeatMap.map(r => ({
                  label: r.component,
                  value: r.risks.availability,
                  color: '#3498db'
                }))}
                xAxisLabel="Risk Score"
                yAxisLabel="Component"
                horizontal={true}
                useColors={true}
                onSave={handleSave}
              />

              <AnalysisText
                id={`${analysisId}-executive-summary`}
                title="Executive Summary"
                content={`## Risk Analysis Summary

Based on our PASTA analysis of the Digital Banking Platform, we have identified:

- **${getCriticalRisks().length} Critical Risks** requiring immediate attention
- **${attackScenarios.filter(s => s.risk === 'high').length} High Risks** to be addressed in the next quarter
- **${threatActors.filter(t => t.capability === 'nation-state' || t.capability === 'organized-crime').length} Advanced Threat Actors** with significant capabilities
- **${vulnerabilities.filter(v => v.status === 'open').length} Open Vulnerabilities** pending remediation

### Top Recommendations:
1. Implement advanced bot protection and rate limiting for API endpoints
2. Migrate from SMS-based MFA to app-based or hardware token solutions
3. Deploy comprehensive vendor security assessment program
4. Enhance database activity monitoring and privileged access management
5. Conduct regular security awareness training focused on phishing prevention

### Resource Allocation:
- 40% - Technical controls implementation
- 30% - Process improvements and governance
- 20% - Security awareness and training
- 10% - Continuous monitoring and assessment`}
                onSave={handleSave}
                format="markdown"
              />
            </AnalysisSection>
          );

        default:
          return (
            <AnalysisText
              id={`${analysisId}-${subsectionId}`}
              title={subsectionId}
              content={`Content for ${subsectionId} would go here...`}
              onSave={handleSave}
            />
          );
      }
    }

    if (analysisId === 'maestro') {
      switch (subsectionId) {
        case 'overview':
          return (
            <AnalysisText
              id={`${analysisId}-${subsectionId}`}
              title="MAESTRO Overview"
              content={`MAESTRO (Multi-Agent Evaluated Securely Through Rigorous Oversight) is a comprehensive threat modeling framework specifically designed for AI/ML systems and agents.

## Key Focus Areas:
- **AI/ML Component Security** - Identifying and securing all AI models, agents, and pipelines
- **Adversarial Threat Analysis** - Understanding AI-specific attack vectors
- **Data Flow Protection** - Securing training and inference data pipelines
- **Model Risk Assessment** - Evaluating bias, hallucination, and reliability risks
- **AI Compliance** - Meeting regulatory requirements for AI systems
- **Security Controls** - Implementing AI-specific security measures

MAESTRO helps organizations secure their AI/ML infrastructure against emerging threats while ensuring responsible AI deployment.`}
              onSave={handleSave}
              format="markdown"
            />
          );

        case 'ai-components':
          return (
            <AnalysisTable
              id={`${analysisId}-${subsectionId}`}
              title="AI/ML Components Inventory"
              data={maestroAgents}
              columns={[
                { key: 'id', label: 'ID' },
                { key: 'name', label: 'Component Name' },
                { key: 'type', label: 'Type', type: 'dropdown' as const, options: ['AI Assistant', 'ML Model', 'Decision Engine', 'Automation Agent'] },
                { key: 'purpose', label: 'Purpose' },
                { key: 'dataAccess', label: 'Data Access' },
                { key: 'trustLevel', label: 'Trust Level', type: 'dropdown' as const, options: ['untrusted', 'partially-trusted', 'trusted', 'critical'] }
              ]}
              onSave={handleSave}
              sortable
              filterable
            />
          );

        case 'threat-analysis':
          return (
            <AnalysisSection
              id={`${analysisId}-${subsectionId}`}
              title="AI Threat Analysis"
              level={3}
              onSave={handleSave}
            >
              <AnalysisTable
                id={`${analysisId}-threats`}
                title="AI/ML Specific Threats"
                data={maestroThreats.map(threat => ({
                  ...threat,
                  agent: maestroAgents.find(a => a.id === threat.agentId)?.name || threat.agentId
                }))}
                columns={[
                  { key: 'id', label: 'ID' },
                  { key: 'agent', label: 'AI Component' },
                  { key: 'category', label: 'Category', type: 'dropdown' as const, options: ['Adversarial', 'Data Poisoning', 'Model Theft', 'Privacy Breach', 'Bias', 'Hallucination'] },
                  { key: 'threat', label: 'Threat' },
                  { key: 'likelihood', label: 'Likelihood', type: 'dropdown' as const, options: ['low', 'medium', 'high'] },
                  { key: 'impact', label: 'Impact', type: 'dropdown' as const, options: ['low', 'medium', 'high', 'critical'] },
                  { key: 'detectionDifficulty', label: 'Detection Difficulty', type: 'dropdown' as const, options: ['easy', 'moderate', 'hard', 'very hard'] }
                ]}
                onSave={handleSave}
                sortable
                filterable
                pageSize={10}
              />

              <AnalysisBarChart
                id={`${analysisId}-threat-categories`}
                title="Threat Category Distribution"
                data={maestroCategories.map(c => ({
                  label: c.name,
                  value: maestroThreats.filter(t => t.category === c.name).length
                }))}
                xAxisLabel="Number of Threats"
                useColors={false}
                onSave={handleSave}
              />
            </AnalysisSection>
          );

        case 'data-flows':
          return (
            <AnalysisFlow
              id={`${analysisId}-${subsectionId}`}
              title="AI Data Flow Mapping"
              initialNodes={[
                // AI/ML Components
                { id: 'MA-001', data: { label: 'Customer Service Chatbot' }, position: { x: 400, y: 100 }, style: { background: '#e3f2fd', width: 180, textAlign: 'center' } },
                { id: 'MA-002', data: { label: 'Fraud Detection Model' }, position: { x: 400, y: 250 }, style: { background: '#ffebee', width: 180, textAlign: 'center' } },
                { id: 'MA-003', data: { label: 'Credit Risk Assessor' }, position: { x: 700, y: 175 }, style: { background: '#fff3e0', width: 180, textAlign: 'center' } },
                { id: 'MA-004', data: { label: 'Investment Advisor Bot' }, position: { x: 700, y: 325 }, style: { background: '#e8f5e9', width: 180, textAlign: 'center' } },
                { id: 'MA-005', data: { label: 'AML Transaction Monitor' }, position: { x: 400, y: 400 }, style: { background: '#fce4ec', width: 180, textAlign: 'center' } },
                // Data Sources
                { id: 'data-sources', data: { label: 'External Data Sources' }, position: { x: 50, y: 100 }, style: { background: '#f5f5f5', width: 150, textAlign: 'center' } },
                { id: 'user-input', data: { label: 'User Inputs' }, position: { x: 50, y: 250 }, style: { background: '#f5f5f5', width: 150, textAlign: 'center' } },
                { id: 'training-data', data: { label: 'Training Data' }, position: { x: 50, y: 400 }, style: { background: '#f5f5f5', width: 150, textAlign: 'center' } },
                // Output/Storage
                { id: 'decision-log', data: { label: 'Decision Log' }, position: { x: 1000, y: 250 }, style: { background: '#e1f5fe', width: 150, textAlign: 'center' } }
              ]}
              initialEdges={[
                // Input flows
                { id: 'e1', source: 'user-input', target: 'MA-001', label: 'Queries', animated: true },
                { id: 'e2', source: 'data-sources', target: 'MA-002', label: 'Transaction Feed', animated: true },
                { id: 'e3', source: 'training-data', target: 'MA-002', label: 'Model Training' },
                { id: 'e4', source: 'data-sources', target: 'MA-003', label: 'Credit History' },
                { id: 'e5', source: 'data-sources', target: 'MA-005', label: 'Sanctions Lists' },
                { id: 'e6', source: 'user-input', target: 'MA-004', label: 'Investment Goals' },
                // Inter-component flows
                { id: 'e7', source: 'MA-002', target: 'MA-005', label: 'Risk Scores' },
                { id: 'e8', source: 'MA-001', target: 'MA-003', label: 'Loan Applications' },
                { id: 'e9', source: 'MA-003', target: 'MA-004', label: 'Credit Data' },
                { id: 'e10', source: 'MA-005', target: 'MA-002', label: 'Feedback Loop', style: { stroke: '#888' } },
                // Output flows
                { id: 'e11', source: 'MA-001', target: 'decision-log', label: 'Chat Logs' },
                { id: 'e12', source: 'MA-002', target: 'decision-log', label: 'Fraud Alerts' },
                { id: 'e13', source: 'MA-003', target: 'decision-log', label: 'Credit Decisions' },
                { id: 'e14', source: 'MA-004', target: 'decision-log', label: 'Recommendations' },
                { id: 'e15', source: 'MA-005', target: 'decision-log', label: 'AML Flags' }
              ]}
              onSave={handleSave}
            />
          );

        case 'model-risks':
          return (
            <AnalysisSection
              id={`${analysisId}-${subsectionId}`}
              title="Model Risk Assessment"
              level={3}
              onSave={handleSave}
            >
              <AnalysisHeatMap
                id={`${analysisId}-risk-heatmap`}
                title="AI Risk Heat Map"
                config={{
                  rows: ['Adversarial Risk', 'Bias Risk', 'Privacy Risk', 'Reliability Risk'],
                  cols: ['Fraud Detection', 'Chatbot', 'Credit Scoring', 'Investment Advisor', 'AML Monitor'],
                  cells: (() => {
                    // Map agent IDs to model names
                    const agentToModel: Record<string, string> = {
                      'MA-001': 'chatbot',
                      'MA-002': 'fraud-detection',
                      'MA-003': 'credit-scoring',
                      'MA-004': 'investment-advisor',
                      'MA-005': 'aml-monitor'
                    };
                    
                    // Map risk categories to threat categories
                    const riskToThreatCategory: Record<string, string[]> = {
                      'Adversarial Risk': ['Adversarial'],
                      'Bias Risk': ['Bias'],
                      'Privacy Risk': ['Privacy Breach', 'Data Poisoning'],
                      'Reliability Risk': ['Hallucination', 'Model Theft']
                    };
                    
                    // Create cells with threat data for each risk/model combination
                    const riskData: any[] = [];
                    
                    // Generate cells for each risk/model combination
                    ['Adversarial Risk', 'Bias Risk', 'Privacy Risk', 'Reliability Risk'].forEach(risk => {
                      ['Fraud Detection', 'Chatbot', 'Credit Scoring', 'Investment Advisor', 'AML Monitor'].forEach(model => {
                        // Map model display name to internal name
                        const modelMap: Record<string, string> = {
                          'Fraud Detection': 'fraud-detection',
                          'Chatbot': 'chatbot',
                          'Credit Scoring': 'credit-scoring',
                          'Investment Advisor': 'investment-advisor',
                          'AML Monitor': 'aml-monitor'
                        };
                        
                        const modelKey = modelMap[model];
                        const categories = riskToThreatCategory[risk] || [];
                        
                        // Find all threats matching this risk/model combination
                        const threats = maestroThreats.filter(t => 
                          categories.includes(t.category) && 
                          agentToModel[t.agentId] === modelKey
                        );
                        
                        // Use actual threat count as the value
                        const threatCount = threats.length;
                        
                        // Calculate risk value based on threat count and severity
                        // If there are threats, minimum value is 1, max is 5
                        let value = 0;
                        if (threatCount > 0) {
                          // Calculate average severity based on impact/likelihood
                          const avgSeverity = threats.reduce((sum, t) => {
                            const impactScore = t.impact === 'critical' ? 4 : t.impact === 'high' ? 3 : t.impact === 'medium' ? 2 : 1;
                            const likelihoodScore = t.likelihood === 'high' ? 3 : t.likelihood === 'medium' ? 2 : 1;
                            return sum + (impactScore + likelihoodScore) / 2;
                          }, 0) / threatCount;
                          
                          value = Math.min(5, Math.max(1, Math.round(avgSeverity)));
                        }
                        
                        riskData.push({
                          row: risk,
                          col: model,
                          value,
                          label: threatCount.toString(), // Show actual count
                          threats,
                          data: threats
                        });
                      });
                    });
                    
                    return riskData.map(cell => ({
                      ...cell,
                      data: cell.threats,
                      tooltip: cell.threats.length > 0 
                        ? `${cell.threats.length} threat${cell.threats.length !== 1 ? 's' : ''} identified`
                        : 'No threats identified'
                    }));
                  })(),
                  colorScale: {
                    min: { value: 1, color: '#27ae60', label: 'Very Low' },
                    low: { value: 2, color: '#2ecc71', label: 'Low' },
                    medium: { value: 3, color: '#f1c40f', label: 'Medium' },
                    high: { value: 4, color: '#f39c12', label: 'High' },
                    max: { value: 5, color: '#e74c3c', label: 'Critical' }
                  },
                  xAxisLabel: 'AI Models',
                  yAxisLabel: 'Risk Categories'
                }}
                onSave={handleSave}
                onCellClick={(cell) => {
                  if (cell.data && cell.data.length > 0) {
                    setSelectedHeatMapCell({
                      title: `${cell.row} - ${cell.col}`,
                      items: cell.data
                    });
                  }
                }}
              />
              
              {selectedHeatMapCell && selectedHeatMapCell.items.length > 0 && (
                <div style={{ marginTop: 'var(--space-4)' }}>
                  <ThreatListInline
                    title={selectedHeatMapCell.title}
                    threats={selectedHeatMapCell.items.map(threat => ({
                      id: threat.id,
                      component: maestroAgents.find(a => a.id === threat.agentId)?.name || threat.agentId,
                      threatType: threat.category,
                      description: threat.threat,
                      impact: threat.impact,
                      likelihood: threat.likelihood,
                      riskLevel: `${threat.impact === 'critical' ? 'critical' : threat.impact === 'high' && threat.likelihood === 'high' ? 'high' : 'medium'}`,
                      mitigations: threat.mitigations
                    }))}
                    onClose={() => setSelectedHeatMapCell(null)}
                  />
                </div>
              )}

              <AnalysisText
                id={`${analysisId}-risk-summary`}
                title="Risk Summary"
                content={`## Critical Risk Areas

### High-Risk Components:
1. **Credit Risk Scoring Engine** - High bias risk affecting loan decisions
2. **Fraud Detection Model** - Vulnerable to adversarial attacks
3. **Customer Chatbot** - Prone to prompt injection and hallucination

### Key Mitigation Priorities:
- Implement comprehensive bias testing for all decision-making models
- Deploy adversarial defenses for critical ML systems
- Enhance input validation and output filtering for LLM-based agents
- Establish continuous monitoring for model drift and performance degradation`}
                onSave={handleSave}
                format="markdown"
              />
            </AnalysisSection>
          );

        case 'compliance':
          return (
            <AnalysisTable
              id={`${analysisId}-${subsectionId}`}
              title="AI Compliance Requirements"
              data={[
                { id: 'COMP-001', framework: 'EU AI Act', requirement: 'High-risk system conformity assessment', status: 'In Progress', gap: 'Documentation incomplete' },
                { id: 'COMP-002', framework: 'GDPR', requirement: 'Right to explanation', status: 'Compliant', gap: 'None' },
                { id: 'COMP-003', framework: 'NIST AI RMF', requirement: 'Risk management framework', status: 'Partial', gap: 'Testing procedures needed' },
                { id: 'COMP-004', framework: 'ISO 23053', requirement: 'AI trustworthiness', status: 'Planning', gap: 'Full assessment required' }
              ]}
              columns={[
                { key: 'id', label: 'ID' },
                { key: 'framework', label: 'Framework' },
                { key: 'requirement', label: 'Requirement' },
                { key: 'status', label: 'Status', type: 'dropdown' as const, options: ['Not Started', 'Planning', 'In Progress', 'Partial', 'Compliant'] },
                { key: 'gap', label: 'Gap Analysis' }
              ]}
              onSave={handleSave}
              sortable
              filterable
            />
          );

        case 'controls':
          return (
            <AnalysisSection
              id={`${analysisId}-${subsectionId}`}
              title="AI Security Controls"
              level={3}
              onSave={handleSave}
            >
              <AnalysisTable
                id={`${analysisId}-control-matrix`}
                title="Control Implementation Matrix"
                data={maestroControls}
                columns={[
                  { key: 'id', label: 'ID' },
                  { key: 'name', label: 'Control Name' },
                  { key: 'type', label: 'Type', type: 'dropdown' as const, options: ['preventive', 'detective', 'corrective'] },
                  { key: 'description', label: 'Description' },
                  { key: 'effectiveness', label: 'Effectiveness', type: 'dropdown' as const, options: ['low', 'medium', 'high'] },
                  { key: 'coverage', label: 'Components Covered' }
                ]}
                onSave={handleSave}
                sortable
                filterable
              />

              <AnalysisText
                id={`${analysisId}-control-recommendations`}
                title="Control Recommendations"
                content={`## Priority Control Implementations

### Immediate Actions:
1. **Adversarial Testing Suite** - Implement comprehensive testing for all production models
2. **Model Monitoring Dashboard** - Real-time visibility into model behavior and drift
3. **Data Validation Pipeline** - Prevent training data poisoning attacks

### Medium-term Initiatives:
1. **Federated Learning** - Enhance privacy while maintaining model performance
2. **Homomorphic Encryption** - Secure inference without exposing data
3. **AI Security Operations Center** - Dedicated team for AI threat monitoring

### Long-term Strategy:
- Establish AI governance framework
- Build security into ML development lifecycle
- Create incident response procedures for AI-specific threats`}
                onSave={handleSave}
                format="markdown"
              />
            </AnalysisSection>
          );

        default:
          return (
            <AnalysisText
              id={`${analysisId}-${subsectionId}`}
              title={subsectionId}
              content={`Content for ${subsectionId} would go here...`}
              onSave={handleSave}
            />
          );
      }
    }

    if (analysisId === 'linddun') {
      switch (subsectionId) {
        case 'overview':
          return (
            <AnalysisText
              id={`${analysisId}-${subsectionId}`}
              title="LINDDUN Overview"
              content={`LINDDUN is a privacy threat modeling methodology that systematically identifies and mitigates privacy risks in systems.

## LINDDUN Categories:
- **Linkability** - Ability to link data or actions to the same person
- **Identifiability** - Ability to identify a person from available data
- **Non-repudiation** - Inability to deny actions or data
- **Detectability** - Ability to detect the existence of data or actions
- **Disclosure of Information** - Unauthorized access to personal data
- **Unawareness** - Lack of user awareness about data processing
- **Non-compliance** - Violation of privacy regulations

LINDDUN helps organizations build privacy-preserving systems while ensuring regulatory compliance.`}
              onSave={handleSave}
              format="markdown"
            />
          );

        case 'data-flows':
          return (
            <AnalysisTable
              id={`${analysisId}-${subsectionId}`}
              title="Personal Data Flow Inventory"
              data={dataFlows}
              columns={[
                { key: 'id', label: 'ID' },
                { key: 'name', label: 'Data Flow' },
                { key: 'source', label: 'Source' },
                { key: 'destination', label: 'Destination' },
                { key: 'dataTypes', label: 'Data Types' },
                { key: 'purpose', label: 'Purpose' },
                { key: 'retention', label: 'Retention Period' },
                { key: 'encryption', label: 'Encryption', type: 'dropdown' as const, options: ['none', 'transit', 'rest', 'both'] }
              ]}
              onSave={handleSave}
              sortable
              filterable
            />
          );

        case 'privacy-threats':
          return (
            <AnalysisSection
              id={`${analysisId}-${subsectionId}`}
              title="Privacy Threat Analysis"
              level={3}
              onSave={handleSave}
            >
              <AnalysisTable
                id={`${analysisId}-threat-details`}
                title="Identified Privacy Threats"
                data={linddunThreats.map(threat => ({
                  ...threat,
                  dataFlowName: dataFlows.find(df => df.id === threat.dataFlow)?.name || threat.dataFlow
                }))}
                columns={[
                  { key: 'id', label: 'ID' },
                  { key: 'category', label: 'Category', type: 'dropdown' as const, options: ['Linkability', 'Identifiability', 'Non-repudiation', 'Detectability', 'Disclosure', 'Unawareness', 'Non-compliance'] },
                  { key: 'dataFlowName', label: 'Data Flow' },
                  { key: 'threat', label: 'Threat' },
                  { key: 'privacyImpact', label: 'Privacy Impact', type: 'dropdown' as const, options: ['low', 'medium', 'high', 'critical'] },
                  { key: 'likelihood', label: 'Likelihood', type: 'dropdown' as const, options: ['low', 'medium', 'high'] },
                  { key: 'status', label: 'Status', type: 'dropdown' as const, options: ['identified', 'mitigating', 'mitigated', 'accepted'] }
                ]}
                onSave={handleSave}
                sortable
                filterable
                pageSize={10}
              />

              <AnalysisHeatMap
                id={`${analysisId}-impact-matrix`}
                title="Privacy Impact Heat Map"
                config={{
                  rows: ['Critical Impact', 'High Impact', 'Medium Impact', 'Low Impact'],
                  cols: ['Low Likelihood', 'Medium Likelihood', 'High Likelihood'],
                  cells: (() => {
                    const cells: any[] = [];
                    const impacts = ['Critical', 'High', 'Medium', 'Low'];
                    const likelihoods = ['low', 'medium', 'high'];
                    const likelihoodLabels = ['Low Likelihood', 'Medium Likelihood', 'High Likelihood'];
                    
                    impacts.forEach((impact, impactIdx) => {
                      likelihoods.forEach((likelihood, likelihoodIdx) => {
                        const cellThreats = linddunThreats.filter(t => 
                          t.likelihood === likelihood && 
                          (impact === 'Critical' ? t.privacyImpact === 'critical' : 
                           impact === 'High' ? t.privacyImpact === 'high' :
                           impact === 'Medium' ? t.privacyImpact === 'medium' :
                           t.privacyImpact === 'low')
                        );
                        
                        const riskLevel = 
                          (likelihood === 'high' && (impact === 'Critical' || impact === 'High')) ? 5 :
                          (likelihood === 'high' && impact === 'Medium') || (likelihood === 'medium' && (impact === 'Critical' || impact === 'High')) ? 4 :
                          (likelihood === 'medium' && impact === 'Medium') || (likelihood === 'low' && (impact === 'Critical' || impact === 'High')) ? 3 :
                          2;
                        
                        cells.push({
                          row: `${impact} Impact`,
                          col: likelihoodLabels[likelihoodIdx],
                          value: riskLevel,
                          label: cellThreats.length > 0 ? `${cellThreats.length} threats` : '',
                          tooltip: cellThreats.map(t => t.threat).join(', ')
                        });
                      });
                    });
                    
                    return cells;
                  })(),
                  colorScale: {
                    min: { value: 1, color: '#27ae60', label: 'Very Low' },
                    low: { value: 2, color: '#2ecc71', label: 'Low' },
                    medium: { value: 3, color: '#f1c40f', label: 'Medium' },
                    high: { value: 4, color: '#f39c12', label: 'High' },
                    max: { value: 5, color: '#e74c3c', label: 'Critical' }
                  },
                  xAxisLabel: 'Likelihood',
                  yAxisLabel: 'Privacy Impact'
                }}
                onSave={handleSave}
              />
            </AnalysisSection>
          );

        case 'threat-categories':
          return (
            <AnalysisSection
              id={`${analysisId}-${subsectionId}`}
              title="LINDDUN Threat Categories"
              level={3}
              onSave={handleSave}
            >
              <AnalysisBarChart
                id={`${analysisId}-category-distribution`}
                title="Threat Distribution by Category"
                data={linddunCategories.map(c => ({
                  label: c.name,
                  value: linddunThreats.filter(t => t.category === c.name).length
                }))}
                xAxisLabel="Number of Threats"
                useColors={false}
                onSave={handleSave}
              />

              {linddunCategories.map(category => {
                const categoryThreats = linddunThreats.filter(t => t.category === category.name);
                if (categoryThreats.length === 0) return null;
                
                return (
                  <AnalysisText
                    key={category.name}
                    id={`${analysisId}-category-${category.name.toLowerCase()}`}
                    title={`${category.icon} ${category.name}`}
                    content={`**${category.description}**

**Number of Threats:** ${categoryThreats.length}

**Critical Threats:** ${categoryThreats.filter(t => t.privacyImpact === 'critical').length}

**Example Scenarios:**
${categoryThreats.slice(0, 2).map(t => `- ${t.scenario}`).join('\n')}`}
                    onSave={handleSave}
                    format="markdown"
                  />
                );
              })}
            </AnalysisSection>
          );

        case 'privacy-controls':
          return (
            <AnalysisTable
              id={`${analysisId}-${subsectionId}`}
              title="Privacy Control Implementation"
              data={privacyControls}
              columns={[
                { key: 'id', label: 'ID' },
                { key: 'name', label: 'Control Name' },
                { key: 'type', label: 'Type', type: 'dropdown' as const, options: ['technical', 'organizational', 'legal'] },
                { key: 'description', label: 'Description' },
                { key: 'effectiveness', label: 'Effectiveness', type: 'dropdown' as const, options: ['low', 'medium', 'high'] },
                { key: 'implementation', label: 'Implementation Details' }
              ]}
              onSave={handleSave}
              sortable
              filterable
            />
          );

        case 'compliance-mapping':
          return (
            <AnalysisSection
              id={`${analysisId}-${subsectionId}`}
              title="GDPR Compliance Mapping"
              level={3}
              onSave={handleSave}
            >
              <AnalysisTable
                id={`${analysisId}-gdpr-articles`}
                title="GDPR Article Coverage"
                data={[
                  { article: 'Art. 5', title: 'Principles', threats: linddunThreats.filter(t => t.gdprArticles?.some(a => a.includes('Art. 5'))).length, status: 'Partial' },
                  { article: 'Art. 6', title: 'Lawfulness', threats: linddunThreats.filter(t => t.gdprArticles?.some(a => a.includes('Art. 6'))).length, status: 'Compliant' },
                  { article: 'Art. 7', title: 'Consent', threats: linddunThreats.filter(t => t.gdprArticles?.some(a => a.includes('Art. 7'))).length, status: 'In Progress' },
                  { article: 'Art. 8', title: 'Child\'s consent', threats: linddunThreats.filter(t => t.gdprArticles?.some(a => a.includes('Art. 8'))).length, status: 'Compliant' },
                  { article: 'Art. 12-22', title: 'Data Subject Rights', threats: linddunThreats.filter(t => t.gdprArticles?.some(a => a.includes('Art. 1') && a.includes('2'))).length, status: 'Partial' },
                  { article: 'Art. 25', title: 'Privacy by Design', threats: linddunThreats.filter(t => t.gdprArticles?.some(a => a.includes('Art. 25'))).length, status: 'In Progress' },
                  { article: 'Art. 32', title: 'Security', threats: linddunThreats.filter(t => t.gdprArticles?.some(a => a.includes('Art. 32'))).length, status: 'Compliant' },
                  { article: 'Chapter V', title: 'International Transfers', threats: linddunThreats.filter(t => t.gdprArticles?.some(a => a.includes('Chapter V'))).length, status: 'In Progress' }
                ]}
                columns={[
                  { key: 'article', label: 'GDPR Article' },
                  { key: 'title', label: 'Title' },
                  { key: 'threats', label: 'Related Threats' },
                  { key: 'status', label: 'Compliance Status', type: 'dropdown' as const, options: ['Not Started', 'In Progress', 'Partial', 'Compliant'] }
                ]}
                onSave={handleSave}
                sortable
              />

              <AnalysisText
                id={`${analysisId}-compliance-summary`}
                title="Privacy Compliance Summary"
                content={`## GDPR Compliance Status

### Critical Gaps:
- **International Data Transfers** - Need to implement SCCs for all third-country transfers
- **Consent Management** - Granular consent mechanisms need enhancement
- **Data Subject Rights** - Automated fulfillment of access and portability requests

### Recent Improvements:
- Implemented Privacy by Design framework
- Deployed consent management platform
- Enhanced data minimization practices

### Next Steps:
1. Complete Transfer Impact Assessments (TIAs) for all international data flows
2. Implement automated data portability API
3. Enhance minor protection mechanisms
4. Deploy privacy-preserving analytics

**Overall Compliance Score: 78%**`}
                onSave={handleSave}
                format="markdown"
              />
            </AnalysisSection>
          );

        default:
          return (
            <AnalysisText
              id={`${analysisId}-${subsectionId}`}
              title={subsectionId}
              content={`Content for ${subsectionId} would go here...`}
              onSave={handleSave}
            />
          );
      }
    }

    if (analysisId === 'hazop') {
      switch (subsectionId) {
        case 'overview':
          return (
            <AnalysisText
              id={`${analysisId}-${subsectionId}`}
              title="HAZOP Overview"
              content={`HAZOP (Hazard and Operability Study) is a systematic technique for identifying potential hazards and operability problems in complex systems.

## Key Concepts:
- **Process Nodes** - Specific points in the system to analyze
- **Guide Words** - Systematic prompts to identify deviations (No, More, Less, etc.)
- **Parameters** - Aspects of each node that can deviate
- **Deviations** - Departures from design intent
- **Risk Assessment** - Evaluation of likelihood and consequences

HAZOP helps identify what can go wrong before it happens, enabling proactive risk mitigation in banking systems.`}
              onSave={handleSave}
              format="markdown"
            />
          );

        case 'process-nodes':
          return (
            <AnalysisTable
              id={`${analysisId}-${subsectionId}`}
              title="System Process Nodes"
              data={hazopNodes}
              columns={[
                { key: 'id', label: 'Node ID' },
                { key: 'name', label: 'Node Name' },
                { key: 'type', label: 'Type', type: 'dropdown' as const, options: ['process', 'data-flow', 'interface', 'storage', 'service'] },
                { key: 'description', label: 'Description' },
                { key: 'parameters', label: 'Parameters' },
                { key: 'normalOperation', label: 'Normal Operation' }
              ]}
              onSave={handleSave}
              sortable
              filterable
            />
          );

        case 'deviations':
          return (
            <AnalysisSection
              id={`${analysisId}-${subsectionId}`}
              title="Deviation Analysis"
              level={3}
              onSave={handleSave}
            >
              <AnalysisTable
                id={`${analysisId}-deviation-table`}
                title="Identified Deviations"
                data={hazopDeviations.map(dev => ({
                  ...dev,
                  nodeName: hazopNodes.find(n => n.id === dev.nodeId)?.name || dev.nodeId
                }))}
                columns={[
                  { key: 'id', label: 'ID' },
                  { key: 'nodeName', label: 'Process Node' },
                  { key: 'parameter', label: 'Parameter' },
                  { key: 'guideWord', label: 'Guide Word', type: 'dropdown' as const, options: ['No', 'More', 'Less', 'As well as', 'Part of', 'Reverse', 'Other than', 'Early', 'Late', 'Before', 'After'] },
                  { key: 'deviation', label: 'Deviation' },
                  { key: 'severity', label: 'Severity', type: 'dropdown' as const, options: ['low', 'medium', 'high', 'critical'] },
                  { key: 'likelihood', label: 'Likelihood', type: 'dropdown' as const, options: ['rare', 'unlikely', 'possible', 'likely', 'almost certain'] },
                  { key: 'riskRating', label: 'Risk Rating', type: 'dropdown' as const, options: ['low', 'medium', 'high', 'critical'] },
                  { key: 'status', label: 'Status', type: 'dropdown' as const, options: ['open', 'in-review', 'mitigated', 'accepted'] }
                ]}
                onSave={handleSave}
                sortable
                filterable
                pageSize={10}
              />

              <AnalysisBarChart
                id={`${analysisId}-deviation-by-node`}
                title="Deviations by Process Node"
                data={hazopNodes.map(n => {
                  const criticalCount = getDeviationsByNode(n.id).filter(d => d.riskRating === 'critical').length;
                  return {
                    label: n.name,
                    value: getDeviationsByNode(n.id).length,
                    color: criticalCount > 0 ? '#e74c3c' : '#3498db'
                  };
                })}
                xAxisLabel="Number of Deviations"
                useColors={true}
                onSave={handleSave}
              />
            </AnalysisSection>
          );

        case 'risk-matrix':
          return (
            <AnalysisSection
              id={`${analysisId}-${subsectionId}`}
              title="Risk Assessment Matrix"
              level={3}
              onSave={handleSave}
            >
              <AnalysisHeatMap
                id={`${analysisId}-risk-heatmap`}
                title="Risk Heat Map"
                config={{
                  rows: ['Critical', 'High', 'Medium', 'Low'],
                  cols: ['Rare', 'Unlikely', 'Possible', 'Likely', 'Almost Certain'],
                  cells: (() => {
                    // Count deviations for each cell and store the actual deviations
                    const cellData: Record<string, { count: number; deviations: typeof hazopDeviations }> = {};
                    hazopDeviations.forEach(dev => {
                      const row = dev.severity.charAt(0).toUpperCase() + dev.severity.slice(1);
                      const col = dev.likelihood.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
                      const key = `${row}-${col}`;
                      if (!cellData[key]) {
                        cellData[key] = { count: 0, deviations: [] };
                      }
                      cellData[key].count++;
                      cellData[key].deviations.push(dev);
                    });
                    
                    // Create cells with counts and data
                    return Object.entries(cellData).map(([key, data]) => {
                      const [row, col] = key.split('-');
                      const severity = row.toLowerCase();
                      const likelihood = col.toLowerCase();
                      
                      // Determine risk level based on severity and likelihood
                      let value = 2; // default medium
                      if (severity === 'critical' && (likelihood === 'likely' || likelihood === 'almost certain')) value = 5;
                      else if (severity === 'critical' || (severity === 'high' && likelihood !== 'rare')) value = 4;
                      else if (severity === 'high' || (severity === 'medium' && likelihood !== 'rare')) value = 3;
                      else if (severity === 'low') value = 1;
                      
                      return {
                        row,
                        col,
                        value,
                        label: data.count.toString(),
                        tooltip: `${data.count} deviation${data.count > 1 ? 's' : ''} at ${row} severity, ${col} likelihood`,
                        data: data.deviations
                      };
                    });
                  })(),
                  xAxisLabel: 'Likelihood →',
                  yAxisLabel: 'Severity →'
                }}
                onSave={handleSave}
                onCellClick={(cell) => {
                  if (cell.data && cell.data.length > 0) {
                    setSelectedHeatMapCell({
                      title: `${cell.row} Severity / ${cell.col} Likelihood Deviations`,
                      items: cell.data
                    });
                  }
                }}
              />
              
              {selectedHeatMapCell && selectedHeatMapCell.items.length > 0 && (
                <div style={{ marginTop: 'var(--space-4)' }}>
                  <ThreatListInline
                    title={selectedHeatMapCell.title}
                    threats={selectedHeatMapCell.items.map(dev => ({
                      id: dev.id,
                      component: dev.node,
                      threatType: dev.guideWord,
                      description: dev.deviation,
                      impact: dev.consequence,
                      likelihood: dev.likelihood,
                      riskLevel: dev.riskRating,
                      mitigations: dev.safeguards
                    }))}
                    onClose={() => setSelectedHeatMapCell(null)}
                  />
                </div>
              )}

              <AnalysisText
                id={`${analysisId}-risk-summary`}
                title="Risk Summary"
                content={`## Risk Distribution

- **Critical Risks:** ${getCriticalDeviations().length} deviations
- **High Risks:** ${hazopDeviations.filter(d => d.riskRating === 'high').length} deviations
- **Medium Risks:** ${hazopDeviations.filter(d => d.riskRating === 'medium').length} deviations
- **Low Risks:** ${hazopDeviations.filter(d => d.riskRating === 'low').length} deviations

### Top Risk Areas:
1. **Authentication System** - Multiple critical deviations affecting access control
2. **Payment Processing** - High-risk deviations in transaction handling
3. **Data Encryption** - Critical risks in data protection mechanisms

### Risk Mitigation Focus:
- Prioritize critical risks in authentication and payment systems
- Implement recommended safeguards for high-likelihood deviations
- Regular review of risk ratings as controls are implemented`}
                onSave={handleSave}
                format="markdown"
              />
            </AnalysisSection>
          );

        case 'actions':
          return (
            <AnalysisSection
              id={`${analysisId}-${subsectionId}`}
              title="Action Items"
              level={3}
              onSave={handleSave}
            >
              <AnalysisTable
                id={`${analysisId}-action-items`}
                title="HAZOP Action Tracker"
                data={hazopActions.map(action => ({
                  ...action,
                  deviation: hazopDeviations.find(d => d.id === action.deviationId)?.deviation || action.deviationId
                }))}
                columns={[
                  { key: 'id', label: 'Action ID' },
                  { key: 'deviation', label: 'Related Deviation' },
                  { key: 'action', label: 'Action Required' },
                  { key: 'responsible', label: 'Responsible Party' },
                  { key: 'dueDate', label: 'Due Date' },
                  { key: 'priority', label: 'Priority', type: 'dropdown' as const, options: ['low', 'medium', 'high', 'urgent'] },
                  { key: 'status', label: 'Status', type: 'dropdown' as const, options: ['pending', 'in-progress', 'completed', 'overdue'] }
                ]}
                onSave={handleSave}
                sortable
                filterable
              />

              <AnalysisBarChart
                id={`${analysisId}-action-status`}
                title="Action Status Overview"
                data={[
                  { label: 'Pending', value: hazopActions.filter(a => a.status === 'pending').length, color: '#f39c12' },
                  { label: 'In Progress', value: hazopActions.filter(a => a.status === 'in-progress').length, color: '#3498db' },
                  { label: 'Completed', value: hazopActions.filter(a => a.status === 'completed').length, color: '#2ecc71' },
                  { label: 'Overdue', value: hazopActions.filter(a => a.status === 'overdue').length, color: '#e74c3c' }
                ]}
                xAxisLabel="Number of Actions"
                useColors={true}
                onSave={handleSave}
              />
            </AnalysisSection>
          );

        case 'guide-words':
          return (
            <AnalysisTable
              id={`${analysisId}-${subsectionId}`}
              title="HAZOP Guide Word Reference"
              data={hazopGuideWords}
              columns={[
                { key: 'word', label: 'Guide Word' },
                { key: 'description', label: 'Description' }
              ]}
              onSave={handleSave}
            />
          );

        default:
          return (
            <AnalysisText
              id={`${analysisId}-${subsectionId}`}
              title={subsectionId}
              content={`Content for ${subsectionId} would go here...`}
              onSave={handleSave}
            />
          );
      }
    }

    if (analysisId === 'octave') {
      switch (subsectionId) {
        case 'overview':
          return (
            <AnalysisText
              id={`${analysisId}-${subsectionId}`}
              title="OCTAVE Overview"
              content={`OCTAVE (Operationally Critical Threat, Asset, and Vulnerability Evaluation) is a risk-based strategic assessment and planning technique for security.

## Key Components:
- **Critical Assets** - Identify what's most important to the organization
- **Security Requirements** - Define CIA requirements for each asset
- **Threat Profiles** - Analyze threats from multiple sources
- **Vulnerability Assessment** - Identify weaknesses in protection
- **Risk Analysis** - Evaluate and prioritize risks
- **Protection Strategy** - Develop mitigation plans

OCTAVE focuses on organizational risk and strategic, practice-related issues, distinguishing it from technology-focused assessments.`}
              onSave={handleSave}
              format="markdown"
            />
          );

        case 'critical-assets':
          return (
            <AnalysisSection
              id={`${analysisId}-${subsectionId}`}
              title="Critical Asset Identification"
              level={3}
              onSave={handleSave}
            >
              <AnalysisTable
                id={`${analysisId}-asset-inventory`}
                title="Organizational Critical Assets"
                data={octaveAssets}
                columns={[
                  { key: 'id', label: 'Asset ID' },
                  { key: 'name', label: 'Asset Name' },
                  { key: 'type', label: 'Type', type: 'dropdown' as const, options: ['information', 'system', 'service', 'people', 'facility'] },
                  { key: 'criticality', label: 'Criticality', type: 'dropdown' as const, options: ['low', 'medium', 'high', 'critical'] },
                  { key: 'owner', label: 'Owner' },
                  { key: 'description', label: 'Description' }
                ]}
                onSave={handleSave}
                sortable
                filterable
              />

              <AnalysisChart
                id={`${analysisId}-asset-criticality`}
                title="Asset Criticality Distribution"
                type="bar"
                data={{
                  labels: ['Critical', 'High', 'Medium', 'Low'],
                  datasets: [{
                    label: 'Number of Assets',
                    data: [
                      octaveAssets.filter(a => a.criticality === 'critical').length,
                      octaveAssets.filter(a => a.criticality === 'high').length,
                      octaveAssets.filter(a => a.criticality === 'medium').length,
                      octaveAssets.filter(a => a.criticality === 'low').length
                    ],
                    backgroundColor: ['#e74c3c', '#f39c12', '#f1c40f', '#2ecc71']
                  }]
                }}
                onSave={handleSave}
              />

              <AnalysisText
                id={`${analysisId}-cia-requirements`}
                title="Security Requirements Summary"
                content={`## CIA Requirements for Critical Assets

${getHighValueAssets().map(asset => `### ${asset.name}
- **Confidentiality:** ${asset.securityRequirements.confidentiality}
- **Integrity:** ${asset.securityRequirements.integrity}
- **Availability:** ${asset.securityRequirements.availability}
- **Rationale:** ${asset.rationale}
`).join('\n')}`}
                onSave={handleSave}
                format="markdown"
              />
            </AnalysisSection>
          );

        case 'threat-profiles':
          return (
            <AnalysisSection
              id={`${analysisId}-${subsectionId}`}
              title="Threat Profile Analysis"
              level={3}
              onSave={handleSave}
            >
              <AnalysisTable
                id={`${analysisId}-threat-sources`}
                title="Identified Threat Sources"
                data={octaveThreats.map(threat => ({
                  ...threat,
                  assetName: octaveAssets.find(a => a.id === threat.assetId)?.name || threat.assetId,
                  overallImpact: Math.max(
                    threat.impact.confidentiality,
                    threat.impact.integrity,
                    threat.impact.availability,
                    threat.impact.financial,
                    threat.impact.reputation,
                    threat.impact.compliance
                  )
                }))}
                columns={[
                  { key: 'id', label: 'Threat ID' },
                  { key: 'assetName', label: 'Target Asset' },
                  { key: 'source', label: 'Source', type: 'dropdown' as const, options: ['internal-accidental', 'internal-deliberate', 'external-accidental', 'external-deliberate', 'system-problems', 'natural-disasters'] },
                  { key: 'actor', label: 'Threat Actor' },
                  { key: 'means', label: 'Attack Vector' },
                  { key: 'probability', label: 'Probability', type: 'dropdown' as const, options: ['very-low', 'low', 'medium', 'high', 'very-high'] },
                  { key: 'overallImpact', label: 'Max Impact' }
                ]}
                onSave={handleSave}
                sortable
                filterable
                pageSize={10}
              />

              <AnalysisBarChart
                id={`${analysisId}-threat-sources-chart`}
                title="Threats by Source Category"
                data={[
                  { label: 'Internal Accidental', value: octaveThreats.filter(t => t.source === 'internal-accidental').length, color: '#3498db' },
                  { label: 'Internal Deliberate', value: octaveThreats.filter(t => t.source === 'internal-deliberate').length, color: '#e74c3c' },
                  { label: 'External Accidental', value: octaveThreats.filter(t => t.source === 'external-accidental').length, color: '#f39c12' },
                  { label: 'External Deliberate', value: octaveThreats.filter(t => t.source === 'external-deliberate').length, color: '#c0392b' },
                  { label: 'System Problems', value: octaveThreats.filter(t => t.source === 'system-problems').length, color: '#95a5a6' },
                  { label: 'Natural Disasters', value: octaveThreats.filter(t => t.source === 'natural-disasters').length, color: '#27ae60' }
                ]}
                xAxisLabel="Number of Threats"
                useColors={true}
                onSave={handleSave}
              />
            </AnalysisSection>
          );

        case 'vulnerabilities':
          return (
            <AnalysisTable
              id={`${analysisId}-${subsectionId}`}
              title="Vulnerability Assessment"
              data={octaveVulnerabilities.map(vuln => ({
                ...vuln,
                assetName: octaveAssets.find(a => a.id === vuln.assetId)?.name || vuln.assetId
              }))}
              columns={[
                { key: 'id', label: 'Vuln ID' },
                { key: 'assetName', label: 'Asset' },
                { key: 'type', label: 'Type', type: 'dropdown' as const, options: ['technical', 'physical', 'organizational'] },
                { key: 'category', label: 'Category' },
                { key: 'description', label: 'Description' },
                { key: 'severity', label: 'Severity', type: 'dropdown' as const, options: ['low', 'medium', 'high', 'critical'] },
                { key: 'exploitability', label: 'Exploitability', type: 'dropdown' as const, options: ['low', 'medium', 'high'] },
                { key: 'status', label: 'Status', type: 'dropdown' as const, options: ['identified', 'analyzing', 'mitigating', 'mitigated'] }
              ]}
              onSave={handleSave}
              sortable
              filterable
              pageSize={10}
            />
          );

        case 'risk-analysis':
          return (
            <AnalysisSection
              id={`${analysisId}-${subsectionId}`}
              title="Organizational Risk Analysis"
              level={3}
              onSave={handleSave}
            >
              <AnalysisTable
                id={`${analysisId}-risk-register`}
                title="Risk Register"
                data={octaveRisks.map(risk => ({
                  ...risk,
                  assetName: octaveAssets.find(a => a.id === risk.assetId)?.name || risk.assetId,
                  threatDesc: octaveThreats.find(t => t.id === risk.threatId)?.outcome || risk.threatId
                }))}
                columns={[
                  { key: 'id', label: 'Risk ID' },
                  { key: 'assetName', label: 'Asset' },
                  { key: 'description', label: 'Risk Description' },
                  { key: 'likelihood', label: 'Likelihood', type: 'dropdown' as const, options: ['very-low', 'low', 'medium', 'high', 'very-high'] },
                  { key: 'impact', label: 'Impact', type: 'dropdown' as const, options: ['negligible', 'minor', 'moderate', 'major', 'severe'] },
                  { key: 'riskLevel', label: 'Risk Level', type: 'dropdown' as const, options: ['low', 'medium', 'high', 'critical'] },
                  { key: 'strategy', label: 'Strategy', type: 'dropdown' as const, options: ['accept', 'mitigate', 'transfer', 'avoid'] }
                ]}
                onSave={handleSave}
                sortable
                filterable
              />

              <AnalysisHeatMap
                id={`${analysisId}-risk-matrix`}
                title="Risk Heat Map"
                config={{
                  rows: ['Severe', 'Major', 'Moderate', 'Minor', 'Negligible'],
                  cols: ['Very Low', 'Low', 'Medium', 'High', 'Very High'],
                  cells: (() => {
                    // Count risks for each cell
                    const cellCounts: Record<string, { count: number; risks: typeof octaveRisks }> = {};
                    octaveRisks.forEach(risk => {
                      const row = risk.impact.charAt(0).toUpperCase() + risk.impact.slice(1);
                      const col = risk.likelihood.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
                      const key = `${row}-${col}`;
                      if (!cellCounts[key]) {
                        cellCounts[key] = { count: 0, risks: [] };
                      }
                      cellCounts[key].count++;
                      cellCounts[key].risks.push(risk);
                    });
                    
                    // Create cells with counts
                    return Object.entries(cellCounts).map(([key, data]) => {
                      const [row, col] = key.split('-');
                      const avgRiskLevel = data.risks.reduce((sum, r) => 
                        sum + (r.riskLevel === 'critical' ? 5 : r.riskLevel === 'high' ? 4 : r.riskLevel === 'medium' ? 3 : 2), 0
                      ) / data.count;
                      
                      return {
                        row,
                        col,
                        value: Math.round(avgRiskLevel),
                        label: data.count.toString(),
                        tooltip: `${data.count} risk${data.count > 1 ? 's' : ''} at ${row} impact, ${col} likelihood`
                      };
                    });
                  })(),
                  xAxisLabel: 'Likelihood →',
                  yAxisLabel: 'Impact →'
                }}
                onSave={handleSave}
              />

              <AnalysisText
                id={`${analysisId}-risk-summary`}
                title="Risk Analysis Summary"
                content={`## Risk Profile

- **Critical Risks:** ${getOctaveCriticalRisks().length}
- **High Risks:** ${octaveRisks.filter(r => r.riskLevel === 'high').length}
- **Medium Risks:** ${octaveRisks.filter(r => r.riskLevel === 'medium').length}
- **Low Risks:** ${octaveRisks.filter(r => r.riskLevel === 'low').length}

### Risk Treatment Summary:
- **Mitigate:** ${octaveRisks.filter(r => r.strategy === 'mitigate').length} risks
- **Transfer:** ${octaveRisks.filter(r => r.strategy === 'transfer').length} risks
- **Accept:** ${octaveRisks.filter(r => r.strategy === 'accept').length} risks
- **Avoid:** ${octaveRisks.filter(r => r.strategy === 'avoid').length} risks

### Top Risk Drivers:
1. External deliberate threats targeting critical data assets
2. Internal process vulnerabilities in change management
3. Supply chain dependencies creating single points of failure`}
                onSave={handleSave}
                format="markdown"
              />
            </AnalysisSection>
          );

        case 'protection-strategy':
          return (
            <AnalysisSection
              id={`${analysisId}-${subsectionId}`}
              title="Protection Strategy Development"
              level={3}
              onSave={handleSave}
            >
              <AnalysisTable
                id={`${analysisId}-protection-strategies`}
                title="Security Protection Strategies"
                data={octaveProtectionStrategies}
                columns={[
                  { key: 'id', label: 'Strategy ID' },
                  { key: 'name', label: 'Strategy Name' },
                  { key: 'type', label: 'Type', type: 'dropdown' as const, options: ['preventive', 'detective', 'corrective', 'deterrent'] },
                  { key: 'description', label: 'Description' },
                  { key: 'effectiveness', label: 'Effectiveness', type: 'dropdown' as const, options: ['low', 'medium', 'high'] },
                  { key: 'cost', label: 'Cost', type: 'dropdown' as const, options: ['low', 'medium', 'high'] },
                  { key: 'timeframe', label: 'Timeframe' },
                  { key: 'status', label: 'Status', type: 'dropdown' as const, options: ['proposed', 'approved', 'implementing', 'operational'] }
                ]}
                onSave={handleSave}
                sortable
                filterable
              />

              <AnalysisBarChart
                id={`${analysisId}-strategy-effectiveness`}
                title="Strategy Effectiveness vs Cost"
                data={octaveProtectionStrategies.map(s => ({
                  label: s.name,
                  value: s.effectiveness === 'high' ? 3 : s.effectiveness === 'medium' ? 2 : 1
                }))}
                xAxisLabel="Effectiveness Level"
                useColors={false}
                onSave={handleSave}
              />

              <AnalysisText
                id={`${analysisId}-implementation-roadmap`}
                title="Implementation Roadmap"
                content={`## Protection Strategy Roadmap

### Phase 1: Immediate (0-3 months)
- **Zero Trust Architecture** - Begin implementation for critical assets
- **Privileged Access Management** - Deploy for high-risk accounts

### Phase 2: Short-term (3-6 months)
- **Advanced Threat Detection** - Deploy XDR platform
- **Security Champions Program** - Establish in dev teams

### Phase 3: Medium-term (6-12 months)
- **Automated Incident Response** - SOAR implementation
- **Supply Chain Security** - Enhanced vendor risk management

### Success Metrics:
- Reduce critical vulnerabilities by 60%
- Decrease mean time to detect (MTTD) to <1 hour
- Achieve 95% coverage of critical assets with protection strategies`}
                onSave={handleSave}
                format="markdown"
              />
            </AnalysisSection>
          );

        default:
          return (
            <AnalysisText
              id={`${analysisId}-${subsectionId}`}
              title={subsectionId}
              content={`Content for ${subsectionId} would go here...`}
              onSave={handleSave}
            />
          );
      }
    }
    
    // Default placeholder for other analysis types
    return (
      <AnalysisText
        id={`${analysisId}-${subsectionId}`}
        title={subsectionId}
        content={`Content for ${analysisId} - ${subsectionId} would go here...`}
        onSave={handleSave}
      />
    );
  };

  // If focusedSection is provided, only render that section
  if (focusedSection) {
    const subsection = subsections.find(s => s.id === focusedSection);
    if (!subsection) {
      return <div>Section not found</div>;
    }
    
    return (
      <div className="collapsible-analysis-content focused-section">
        {renderSubsectionContent(analysisId, subsection.id)}
        
        {selectedDetail && (
          <AnalysisDetail
            title={selectedDetail.title}
            data={selectedDetail.data}
            onClose={() => setSelectedDetail(null)}
          />
        )}
      </div>
    );
  }

  // Otherwise render all sections
  return (
    <div className="collapsible-analysis-content">
      {subsections.map(subsection => {
        const Icon = subsection.icon;
        const sectionKey = `${analysisId}-${subsection.id}`;
        const isExpanded = expandedSections.has(sectionKey);

        return (
          <AnalysisSection
            key={subsection.id}
            id={sectionKey}
            title={subsection.label}
            icon={<Icon size={16} />}
            level={3}
            collapsible
            defaultExpanded={false}
            onSave={handleSave}
          >
            {renderSubsectionContent(analysisId, subsection.id)}
          </AnalysisSection>
        );
      })}
      
      {selectedDetail && (
        <AnalysisDetail
          title={selectedDetail.title}
          data={selectedDetail.data}
          onClose={() => setSelectedDetail(null)}
        />
      )}
      
      {selectedThreats && (
        <ThreatListDetail
          title={selectedThreats.title}
          threats={selectedThreats.threats}
          onClose={() => setSelectedThreats(null)}
        />
      )}
    </div>
  );
}