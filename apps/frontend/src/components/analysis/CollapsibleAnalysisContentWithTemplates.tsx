import { useState } from 'react';
import { ChevronRight, ChevronDown, FileText, Users, AlertTriangle, ShieldAlert, GitBranch, Zap, Target, Shield } from 'lucide-react';
import { AnalysisSection, AnalysisTable, AnalysisText, AnalysisDiagram, SystemDescriptionTemplate, AnalysisFlow, AnalysisChart, AnalysisDetail } from '../templates';
import { losses, hazards, ucas, causalScenarios, controllers, controlActions } from '../../apps/user/mockData/stpaSecData';
import { dreadThreats, getRiskDistribution } from '../../apps/user/mockData/dreadData';
import { strideThreats } from '../../apps/user/mockData/strideData';
import { businessObjectives, technicalScope, threatActors, attackScenarios, riskAssessments } from '../../apps/user/mockData/pastaData';
import { controlFlowNodes, controlFlowEdges } from '../../apps/user/mockData/controlFlowData';
import { primaryStakeholders, secondaryStakeholders, threatActors as stakeholderThreatActors } from '../../apps/user/mockData/stakeholderData';
import { redTeamScenarios, blueTeamScenarios, purpleTeamScenarios, tabletopScenarios } from '../../apps/user/mockData/wargamingData';
import './CollapsibleAnalysisContent.css';

interface SubSection {
  id: string;
  label: string;
  icon: any;
}

interface CollapsibleAnalysisContentProps {
  analysisId: string;
  enabledAnalyses: Record<string, boolean>;
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
    { id: 'threats', label: 'Threat Analysis', icon: ShieldAlert },
    { id: 'mitigations', label: 'Mitigations', icon: Shield },
  ],
  'pasta': [
    { id: 'overview', label: 'PASTA Overview', icon: FileText },
    { id: 'stages', label: 'Attack Stages', icon: Target },
    { id: 'mitigations', label: 'Countermeasures', icon: Shield },
  ],
  'dread': [
    { id: 'overview', label: 'DREAD Overview', icon: FileText },
    { id: 'ratings', label: 'Risk Ratings', icon: AlertTriangle },
    { id: 'distribution', label: 'Risk Distribution', icon: Target },
  ],
};

export default function CollapsibleAnalysisContent({
  analysisId,
  enabledAnalyses
}: CollapsibleAnalysisContentProps) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());
  const [selectedDetail, setSelectedDetail] = useState<{ title: string; data: any } | null>(null);
  const [selectedExercise, setSelectedExercise] = useState<any | null>(null);
  const subsections = analysisSubsections[analysisId] || [];

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
              fullDescription={`The Digital Banking Platform is a comprehensive online financial services system designed to provide secure, reliable, and user-friendly banking services to millions of customers. The system encompasses web and mobile applications, backend services, and integrations with various financial institutions and payment processors.

The platform processes over 10 million transactions daily, ranging from simple balance inquiries to complex international wire transfers. It serves both retail and business customers, offering features such as account management, bill payments, fund transfers, loan applications, and investment services.

Security is paramount in the system design, with multiple layers of protection including multi-factor authentication, end-to-end encryption, fraud detection algorithms, and continuous monitoring. The system must comply with strict regulatory requirements including PCI DSS, SOX, and regional banking regulations.

The architecture is built on a microservices foundation, deployed across multiple geographic regions for redundancy and performance. Key components include the customer-facing applications, API gateway, authentication service, transaction processing engine, fraud detection system, and core banking integrations.`}
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
          
          return (
            <AnalysisTable
              id={`${analysisId}-${subsectionId}`}
              title="Identified Losses"
              data={losses}
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
          
          return (
            <AnalysisTable
              id={`${analysisId}-${subsectionId}`}
              title="Security Hazards/Vulnerabilities"
              data={hazards}
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
          const ucaColumns = [
            { key: 'id', label: 'ID', sortable: true },
            { key: 'controlAction', label: 'Control Action' },
            { key: 'type', label: 'Type', sortable: true, type: 'dropdown' as const, options: ['not-provided', 'provided', 'wrong-timing', 'wrong-duration'] },
            { key: 'context', label: 'Context' },
            { key: 'relatedHazards', label: 'Related Hazards' }
          ];
          
          // Transform data to include control action name and hazards as string
          const ucasData = ucas.map(u => {
            const ca = controlActions.find(ca => ca.id === u.controlActionId);
            return {
              ...u,
              controlAction: ca?.action || u.controlActionId,
              relatedHazards: u.hazards.join(', ')
            };
          });
          
          return (
            <AnalysisTable
              id={`${analysisId}-${subsectionId}`}
              title="Unsafe/Unsecure Control Actions"
              data={ucasData}
              columns={ucaColumns}
              onSave={handleSave}
              sortable
              filterable
              pageSize={10}
            />
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
          
          // Transform data to include UCA reference and convert arrays to strings
          const scenariosData = causalScenarios.map(s => ({
            id: s.id,
            uca: s.ucaId,
            description: s.description,
            causalFactors: s.causalFactors.join('; '),
            strideCategory: s.strideCategory,
            mitigations: s.mitigations.join('; ')
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
              level={4}
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
              level={4}
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
          const flattenedDreadData = dreadThreats.map(threat => ({
            ...threat,
            damage: threat.scores.damage,
            reproducibility: threat.scores.reproducibility,
            exploitability: threat.scores.exploitability,
            affectedUsers: threat.scores.affectedUsers,
            discoverability: threat.scores.discoverability
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
              level={4}
              onSave={handleSave}
            >
              <div style={{ 
                display: 'grid', 
                gridTemplateColumns: '1fr 1fr', 
                gap: 'var(--space-4)'
              }}>
                <AnalysisChart
                  id={`${analysisId}-risk-distribution`}
                  title="Risk Distribution"
                  type="bar"
                  data={{
                    labels: ['Critical', 'High', 'Medium', 'Low'],
                    datasets: [{
                      label: 'Number of Threats',
                      data: [riskDist.Critical, riskDist.High, riskDist.Medium, riskDist.Low],
                      backgroundColor: ['#dc2626', '#f59e0b', '#3b82f6', '#10b981']
                    }]
                  }}
                  onSave={handleSave}
                />
                
                <AnalysisChart
                  id={`${analysisId}-threat-categories`}
                  title="Threats by Category"
                  type="bar"
                  data={{
                    labels: ['Input Val.', 'Auth', 'Crypto', 'Access', 'Session', 'Audit', 'Config'],
                    datasets: [{
                      label: 'Threats',
                      data: [2, 1, 2, 2, 1, 1, 1],
                      backgroundColor: '#8b5cf6'
                    }]
                  }}
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
            />
          );

        case 'threats':
          const strideColumns = [
            { key: 'id', label: 'ID', sortable: true },
            { key: 'component', label: 'Component' },
            { key: 'threatType', label: 'Type', sortable: true, type: 'dropdown' as const, options: ['Spoofing', 'Tampering', 'Repudiation', 'Information Disclosure', 'Denial of Service', 'Elevation of Privilege'] },
            { key: 'description', label: 'Description' },
            { key: 'likelihood', label: 'Likelihood', sortable: true, type: 'dropdown' as const, options: ['low', 'medium', 'high'] },
            { key: 'impact', label: 'Impact', sortable: true, type: 'dropdown' as const, options: ['low', 'medium', 'high'] },
            { key: 'riskLevel', label: 'Risk', sortable: true, type: 'dropdown' as const, options: ['low', 'medium', 'high', 'critical'] }
          ];

          return (
            <AnalysisTable
              id={`${analysisId}-${subsectionId}`}
              title="STRIDE Threat Analysis"
              data={strideThreats}
              columns={strideColumns}
              onSave={handleSave}
              sortable
              filterable
              pageSize={10}
            />
          );

        case 'mitigations':
          return (
            <AnalysisTable
              id={`${analysisId}-${subsectionId}`}
              title="Threat Mitigations"
              data={strideThreats.map(t => ({
                id: t.id,
                threat: t.description,
                type: t.threatType,
                mitigations: t.mitigations.join('; '),
                status: t.status
              }))}
              columns={[
                { key: 'id', label: 'Threat ID', sortable: true },
                { key: 'threat', label: 'Threat' },
                { key: 'type', label: 'Type', sortable: true },
                { key: 'mitigations', label: 'Mitigations' },
                { key: 'status', label: 'Status', type: 'dropdown' as const, options: ['identified', 'mitigating', 'mitigated', 'accepted'] }
              ]}
              onSave={handleSave}
              sortable
              filterable
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
            />
          );

        case 'stages':
          const attackScenarioColumns = [
            { key: 'id', label: 'ID', sortable: true },
            { key: 'name', label: 'Scenario' },
            { key: 'threatActor', label: 'Threat Actor' },
            { key: 'attackVector', label: 'Attack Vector' },
            { key: 'impact', label: 'Impact' },
            { key: 'likelihood', label: 'Likelihood', type: 'dropdown' as const, options: ['very-low', 'low', 'medium', 'high', 'very-high'] },
            { key: 'risk', label: 'Risk', type: 'dropdown' as const, options: ['low', 'medium', 'high', 'critical'] }
          ];

          return (
            <AnalysisSection
              id={`${analysisId}-${subsectionId}`}
              title="PASTA Attack Stages"
              level={4}
              onSave={handleSave}
            >
              <AnalysisTable
                id={`${analysisId}-business-objectives`}
                title="Stage 1: Business Objectives"
                data={businessObjectives}
                columns={[
                  { key: 'id', label: 'ID' },
                  { key: 'objective', label: 'Objective' },
                  { key: 'priority', label: 'Priority', type: 'dropdown' as const, options: ['low', 'medium', 'high', 'critical'] },
                  { key: 'impactArea', label: 'Impact Area' }
                ]}
                onSave={handleSave}
                sortable
                filterable
              />
              
              <AnalysisTable
                id={`${analysisId}-threat-actors`}
                title="Stage 4: Threat Actors"
                data={threatActors}
                columns={[
                  { key: 'id', label: 'ID' },
                  { key: 'name', label: 'Actor' },
                  { key: 'motivation', label: 'Motivation' },
                  { key: 'capability', label: 'Capability', type: 'dropdown' as const, options: ['opportunist', 'hacktivist', 'insider', 'organized-crime', 'nation-state'] }
                ]}
                onSave={handleSave}
                sortable
                filterable
              />

              <AnalysisTable
                id={`${analysisId}-attack-scenarios`}
                title="Stage 6: Attack Scenarios"
                data={attackScenarios}
                columns={attackScenarioColumns}
                onSave={handleSave}
                sortable
                filterable
                pageSize={10}
              />
            </AnalysisSection>
          );

        case 'mitigations':
          return (
            <AnalysisTable
              id={`${analysisId}-${subsectionId}`}
              title="Risk Treatments & Countermeasures"
              data={riskAssessments.map(r => {
                const scenario = attackScenarios.find(s => s.id === r.scenario);
                return {
                  id: r.id,
                  scenario: scenario?.name || r.scenario,
                  overallRisk: r.overallRisk,
                  treatment: r.treatment,
                  mitigation: r.mitigation || 'N/A'
                };
              })}
              columns={[
                { key: 'id', label: 'ID' },
                { key: 'scenario', label: 'Scenario' },
                { key: 'overallRisk', label: 'Risk Score', sortable: true },
                { key: 'treatment', label: 'Treatment', type: 'dropdown' as const, options: ['mitigate', 'accept', 'transfer', 'avoid'] },
                { key: 'mitigation', label: 'Mitigation Strategy' }
              ]}
              onSave={handleSave}
              sortable
              filterable
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
    </div>
  );
}