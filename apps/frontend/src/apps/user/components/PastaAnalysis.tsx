import { useState } from 'react';
import { Activity, Target, Shield, AlertTriangle, TrendingUp, Users } from 'lucide-react';
import AnalysisTable from './AnalysisTable';
import { 
  businessObjectives, 
  technicalScope, 
  threatActors, 
  attackScenarios,
  riskAssessments,
  getCriticalRisks,
  getHighPriorityObjectives 
} from '../mockData/pastaData';
import './AnalysisPanel.css';

export default function PastaAnalysis() {
  const [activeStage, setActiveStage] = useState('objectives');
  const [selectedItem, setSelectedItem] = useState<any>(null);

  const stages = [
    { id: 'objectives', label: 'Business Objectives', icon: Target },
    { id: 'scope', label: 'Technical Scope', icon: Activity },
    { id: 'threats', label: 'Threat Actors', icon: Users },
    { id: 'scenarios', label: 'Attack Scenarios', icon: AlertTriangle },
    { id: 'risk', label: 'Risk Assessment', icon: TrendingUp },
  ];

  const renderObjectives = () => (
    <div className="pasta-stage">
      <h3>Stage 1: Business Objectives</h3>
      <p className="stage-description">
        Define and prioritize business objectives that could be impacted by security threats
      </p>
      <AnalysisTable
        columns={[
          { key: 'id', label: 'ID', width: '80px' },
          { key: 'objective', label: 'Business Objective' },
          { key: 'priority', label: 'Priority', width: '100px' },
          { key: 'impactArea', label: 'Impact Area', width: '150px' },
          { key: 'relatedAssets', label: 'Related Assets' },
        ]}
        data={businessObjectives.map(obj => ({
          ...obj,
          relatedAssets: obj.relatedAssets.join(', ')
        }))}
        onRowSelect={setSelectedItem}
        selectedRowId={selectedItem?.id}
      />
    </div>
  );

  const renderScope = () => (
    <div className="pasta-stage">
      <h3>Stage 2: Technical Scope Definition</h3>
      <p className="stage-description">
        Map technical components, technologies, and interfaces in the system
      </p>
      <AnalysisTable
        columns={[
          { key: 'id', label: 'ID', width: '80px' },
          { key: 'component', label: 'Component' },
          { key: 'technology', label: 'Technology', width: '150px' },
          { key: 'interfaces', label: 'Interfaces' },
          { key: 'dependencies', label: 'Dependencies' },
        ]}
        data={technicalScope.map(scope => ({
          ...scope,
          interfaces: scope.interfaces.join(', '),
          dependencies: scope.dependencies.join(', ')
        }))}
        onRowSelect={setSelectedItem}
        selectedRowId={selectedItem?.id}
      />
    </div>
  );

  const renderThreats = () => (
    <div className="pasta-stage">
      <h3>Stage 4: Threat Analysis</h3>
      <p className="stage-description">
        Identify threat actors, their capabilities, and targeted assets
      </p>
      <AnalysisTable
        columns={[
          { key: 'id', label: 'ID', width: '80px' },
          { key: 'name', label: 'Threat Actor' },
          { key: 'capability', label: 'Capability', width: '120px' },
          { key: 'motivation', label: 'Motivation' },
          { key: 'targetedAssets', label: 'Targeted Assets' },
        ]}
        data={threatActors.map(actor => ({
          ...actor,
          targetedAssets: actor.targetedAssets.join(', ')
        }))}
        onRowSelect={setSelectedItem}
        selectedRowId={selectedItem?.id}
      />
    </div>
  );

  const renderScenarios = () => (
    <div className="pasta-stage">
      <h3>Stage 6: Attack Scenarios</h3>
      <p className="stage-description">
        Model specific attack scenarios based on threat actors and vulnerabilities
      </p>
      <AnalysisTable
        columns={[
          { key: 'id', label: 'ID', width: '80px' },
          { key: 'name', label: 'Scenario' },
          { key: 'threatActor', label: 'Actor', width: '80px' },
          { key: 'attackVector', label: 'Attack Vector' },
          { key: 'likelihood', label: 'Likelihood', width: '100px' },
          { key: 'risk', label: 'Risk', width: '80px' },
        ]}
        data={attackScenarios}
        onRowSelect={setSelectedItem}
        selectedRowId={selectedItem?.id}
        getRowClassName={(row) => `risk-${row.risk}`}
      />
    </div>
  );

  const renderRisk = () => (
    <div className="pasta-stage">
      <h3>Stage 7: Risk & Impact Analysis</h3>
      <p className="stage-description">
        Assess business and technical impact with risk treatment decisions
      </p>
      <AnalysisTable
        columns={[
          { key: 'id', label: 'ID', width: '80px' },
          { key: 'scenario', label: 'Scenario', width: '100px' },
          { key: 'businessImpact', label: 'Business Impact', width: '120px' },
          { key: 'technicalImpact', label: 'Technical Impact', width: '120px' },
          { key: 'overallRisk', label: 'Risk Score', width: '100px' },
          { key: 'treatment', label: 'Treatment', width: '100px' },
          { key: 'mitigation', label: 'Mitigation' },
        ]}
        data={riskAssessments.map(risk => ({
          ...risk,
          businessImpact: `${risk.businessImpact}/5`,
          technicalImpact: `${risk.technicalImpact}/5`,
          overallRisk: risk.overallRisk.toFixed(1)
        }))}
        onRowSelect={setSelectedItem}
        selectedRowId={selectedItem?.id}
      />
    </div>
  );

  return (
    <div className="analysis-content">
      <div className="pasta-header">
        <h2>PASTA - Process for Attack Simulation and Threat Analysis</h2>
        <p>A seven-stage risk-centric methodology aligning business objectives with technical threats</p>
      </div>
      
      <div className="pasta-stages">
        {stages.map(stage => {
          const Icon = stage.icon;
          return (
            <button
              key={stage.id}
              className={`stage-button ${activeStage === stage.id ? 'active' : ''}`}
              onClick={() => setActiveStage(stage.id)}
            >
              <Icon size={16} />
              <span>{stage.label}</span>
            </button>
          );
        })}
      </div>

      <div className="pasta-content">
        {activeStage === 'objectives' && renderObjectives()}
        {activeStage === 'scope' && renderScope()}
        {activeStage === 'threats' && renderThreats()}
        {activeStage === 'scenarios' && renderScenarios()}
        {activeStage === 'risk' && renderRisk()}
      </div>

      {selectedItem && (
        <div className="pasta-details">
          <h4>Selected: {selectedItem.id}</h4>
          <pre>{JSON.stringify(selectedItem, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}