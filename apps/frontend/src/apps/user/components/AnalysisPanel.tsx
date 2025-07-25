import { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { AlertTriangle, ShieldAlert, GitBranch, Zap, Target, FileText, Users, Edit3, Save, Download, Settings, Shield } from 'lucide-react';
import AnalysisTable from './AnalysisTable';
import EditableTable from './EditableTable';
import EditableText from './EditableText';
import EditableList from './EditableList';
import MissionStatementEditor from './MissionStatementEditor';
import InlineTextEditor from './InlineTextEditor';
import PastaAnalysis from './PastaAnalysis';
import DreadAnalysis from './DreadAnalysis';
import StrideAnalysis from './StrideAnalysis';
import MaestroAnalysis from './MaestroAnalysis';
import LinddunAnalysis from './LinddunAnalysis';
import HazopAnalysis from './HazopAnalysis';
import OctaveAnalysis from './OctaveAnalysis';
import AnalysisOverview from './AnalysisOverview';
import WargamingTab from './WargamingTab';
import ProcessControlDiagram from './ProcessControlDiagram';
import { getRelatedData } from '../mockData/stpaSecData';
import type { CausalScenario } from '../mockData/stpaSecData';
import { stakeholders as initialStakeholders, getMissionStatementString } from '../mockData/systemData';
import { useAnalysisStore } from '../../../stores/analysisStore';
import { useBroadcastSync } from '../hooks/useBroadcastChannel';
import { useVersionSync } from '../../../hooks/useVersionSync';
import { useVersionStore } from '../../../stores/versionStore';
import './AnalysisPanel.css';

// Mapping of subtab IDs to component types for standalone windows
const SUBTAB_TO_COMPONENT: Record<string, string> = {
  'losses': 'losses',
  'hazards': 'hazards',
  'control-diagram': 'control-diagram',
  'controllers': 'controllers',
  'control-actions': 'control-actions',
  'ucas': 'ucas',
  'scenarios': 'scenarios',
  'wargaming': 'wargaming'
};

interface AnalysisPanelProps {
  activeAnalysis: string;
  onAnalysisChange: (analysis: string) => void;
  isAnalyzing: boolean;
  onElementSelect?: (element: any, type: string) => void;
  enabledAnalyses?: Record<string, boolean>;
  standaloneMode?: boolean;
  isCollapsible?: boolean;
  onToggleSection?: (sectionId: string) => void;
  onToggleTable?: (tableId: string) => void;
  expandedSections?: Set<string>;
  expandedTables?: Set<string>;
}

export default function AnalysisPanel({ 
  activeAnalysis, 
  onAnalysisChange, 
  isAnalyzing,
  onElementSelect,
  enabledAnalyses = {
    'stpa-sec': true,
    'stride': true
  },
  standaloneMode = false,
  isCollapsible = false,
  onToggleSection,
  onToggleTable,
  expandedSections,
  expandedTables
}: AnalysisPanelProps) {
  const [activeTab, setActiveTab] = useState(activeAnalysis || 'stpa-sec');
  const [stpaSecSubTab, setStpaSecSubTab] = useState('system-description');
  const [selectedElement, setSelectedElement] = useState<any>(null);
  const [isEditMode, setIsEditMode] = useState(false);
  const [stakeholders, setStakeholders] = useState(initialStakeholders);
  const [automationLevel, setAutomationLevel] = useState<'manual' | 'assisted' | 'semi-auto' | 'fully-auto'>('assisted');
  const [hasValidationErrors, setHasValidationErrors] = useState(false);
  
  // Get data from store
  const {
    systemDescription,
    losses,
    hazards,
    controllers,
    controlActions,
    ucas,
    scenarios,
    updateSystemDescription,
    updateLosses,
    updateHazards,
    updateControllers,
    updateControlActions,
    updateUcas,
    updateScenarios
  } = useAnalysisStore();
  
  // Set up broadcast sync and version sync
  useBroadcastSync();
  useVersionSync();
  
  // Get active version from store
  const activeVersionId = useVersionStore((state) => state.activeVersionId);
  
  const originalSystemDescriptionRef = useRef(systemDescription);
  const originalStakeholdersRef = useRef(stakeholders);
  const originalLossesRef = useRef(losses);
  const originalHazardsRef = useRef(hazards);
  const originalControllersRef = useRef(controllers);
  const originalControlActionsRef = useRef(controlActions);
  const originalUcasRef = useRef(ucas);
  const originalScenariosRef = useRef(scenarios);
  
  // Function to open component in new window
  const openInNewWindow = (componentType: string) => {
    const width = 1200;
    const height = 800;
    const left = (window.screen.width - width) / 2;
    const top = (window.screen.height - height) / 2;
    
    window.open(
      `/analysis/component/${componentType}`,
      `${componentType}-window`,
      `width=${width},height=${height},left=${left},top=${top},resizable=yes,scrollbars=yes`
    );
  };
  
  // Function to open analysis view in new window
  const openAnalysisInNewWindow = (analysisType: string) => {
    const width = 1400;
    const height = 900;
    const left = (window.screen.width - width) / 2;
    const top = (window.screen.height - height) / 2;
    
    window.open(
      `/analysis/view/${analysisType}`,
      `${analysisType}-analysis-window`,
      `width=${width},height=${height},left=${left},top=${top},resizable=yes,scrollbars=yes`
    );
  };
  
  // Function to open analysis view in new tab
  const openAnalysisInNewTab = (analysisType: string) => {
    window.open(`/analysis/view/${analysisType}`, '_blank');
  };
  
  // Track original values when entering edit mode
  useEffect(() => {
    if (isEditMode) {
      originalSystemDescriptionRef.current = { ...systemDescription };
      originalStakeholdersRef.current = [...stakeholders];
      originalLossesRef.current = [...losses];
      originalHazardsRef.current = [...hazards];
      originalControllersRef.current = [...controllers];
      originalControlActionsRef.current = [...controlActions];
      originalUcasRef.current = [...ucas];
      originalScenariosRef.current = [...scenarios];
    } else {
      // Clear validation errors when exiting edit mode
      setHasValidationErrors(false);
    }
  }, [isEditMode]);

  // Update activeTab when activeAnalysis changes (for standalone mode)
  useEffect(() => {
    if (activeAnalysis) {
      setActiveTab(activeAnalysis);
    }
  }, [activeAnalysis]);

  // Build tabs based on enabled analyses
  const tabs = [
    ...(enabledAnalyses['stpa-sec'] ? [{ id: 'stpa-sec', label: 'STPA-Sec' }] : []),
    ...(enabledAnalyses['stride'] ? [{ id: 'stride', label: 'STRIDE' }] : []),
    ...(enabledAnalyses['pasta'] ? [{ id: 'pasta', label: 'PASTA' }] : []),
    ...(enabledAnalyses['maestro'] ? [{ id: 'maestro', label: 'MAESTRO' }] : []),
    ...(enabledAnalyses['dread'] ? [{ id: 'dread', label: 'DREAD' }] : []),
    ...(enabledAnalyses['linddun'] ? [{ id: 'linddun', label: 'LINDDUN' }] : []),
    ...(enabledAnalyses['hazop'] ? [{ id: 'hazop', label: 'HAZOP' }] : []),
    ...(enabledAnalyses['octave'] ? [{ id: 'octave', label: 'OCTAVE' }] : []),
    ...(enabledAnalyses['cve'] ? [{ id: 'cve', label: 'CVE Search' }] : []),
    { id: 'overview', label: 'Overview' }, // Always include Overview
  ];
  
  // Ensure activeTab is valid when tabs change
  useEffect(() => {
    const tabIds = tabs.map(t => t.id);
    if (!tabIds.includes(activeTab)) {
      setActiveTab(tabs[0]?.id || 'overview');
    }
  }, [enabledAnalyses]);

  const stpaSecSubTabs = [
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
  ];

  const handleElementSelect = (element: any, type: string) => {
    setSelectedElement({ ...element, type });
    onElementSelect?.(element, type);
  };

  const handleSystemItemClick = (item: string, type: string, index?: number) => {
    const element = {
      id: `${type}-${index || 0}`,
      description: item,
      type: type
    };
    handleElementSelect(element, 'system-item');
  };

  const updateSystemGoals = (goals: string[]) => {
    updateSystemDescription({
      missionStatement: {
        ...systemDescription.missionStatement,
        goals
      }
    });
  };

  const updateSystemConstraints = (constraints: string[]) => {
    updateSystemDescription({
      missionStatement: {
        ...systemDescription.missionStatement,
        constraints
      }
    });
  };

  const updateSystemBoundaries = (type: 'included' | 'excluded', items: string[]) => {
    updateSystemDescription({
      boundaries: {
        ...systemDescription.boundaries,
        [type]: items
      }
    });
  };

  const updateSystemAssumptions = (assumptions: string[]) => {
    updateSystemDescription({
      assumptions
    });
  };

  const handleExport = (format: 'json' | 'pdf' | 'html') => {
    // Export functionality would be implemented here
    const exportData = {
      systemDescription,
      stakeholders,
      losses,
      hazards,
      controllers,
      controlActions,
      ucas,
      scenarios
    };
    console.log(`Exporting as ${format}`, exportData);
  };

  const updateMissionStatement = (field: 'purpose' | 'method', value: string) => {
    updateSystemDescription({
      missionStatement: {
        ...systemDescription.missionStatement,
        [field]: value
      }
    });
  };

  const updateSystemField = (field: 'fullDescription' | 'context', value: string) => {
    updateSystemDescription({
      [field]: value
    });
  };

  const renderSystemDescription = () => (
    <div className="system-description">
      <div className="description-section">
        <h3>Mission Statement</h3>
        <MissionStatementEditor
          purpose={systemDescription.missionStatement.purpose}
          method={systemDescription.missionStatement.method}
          goals={systemDescription.missionStatement.goals}
          onChange={(data) => {
            updateSystemDescription({
              missionStatement: {
                ...systemDescription.missionStatement,
                purpose: data.purpose,
                method: data.method
              }
            });
            // If the why/goals were parsed, update them
            if (data.why !== undefined) {
              const goals = data.why ? data.why.split(',').map(g => g.trim()).filter(g => g) : [];
              updateSystemGoals(goals.length > 0 ? goals : ['']);
            }
          }}
          onReset={() => {
            updateSystemDescription({
              missionStatement: { ...originalSystemDescriptionRef.current.missionStatement }
            });
          }}
          onValidationChange={(isValid) => setHasValidationErrors(!isValid)}
          onClick={() => handleSystemItemClick(getMissionStatementString(systemDescription.missionStatement), 'mission', 0)}
          isEditing={isEditMode}
        />
      </div>

      <div className="description-grid">
        <div className="description-section">
          <h4>System Goals</h4>
          <EditableList
            items={systemDescription.missionStatement.goals}
            onUpdate={updateSystemGoals}
            onItemClick={!isEditMode ? (item, idx) => handleSystemItemClick(item, 'goal', idx) : undefined}
            isEditMode={isEditMode}
            itemIcon="✓"
            itemClassName="goal-list"
            placeholder="Add a new system goal..."
            selectedIndex={selectedElement?.type === 'system-item' && selectedElement?.element?.type === 'goal' ? parseInt(selectedElement.element.id.split('-')[1]) : null}
            componentName="System Goals"
          />
        </div>

        <div className="description-section">
          <h4>System Constraints</h4>
          <EditableList
            items={systemDescription.missionStatement.constraints}
            onUpdate={updateSystemConstraints}
            onItemClick={!isEditMode ? (item, idx) => handleSystemItemClick(item, 'constraint', idx) : undefined}
            isEditMode={isEditMode}
            itemIcon="⚡"
            itemClassName="constraint-list"
            placeholder="Add a new system constraint..."
            selectedIndex={selectedElement?.type === 'system-item' && selectedElement?.element?.type === 'constraint' ? parseInt(selectedElement.element.id.split('-')[1]) : null}
            componentName="System Constraints"
          />
        </div>
      </div>

      <div className="description-section">
        <h4>Full System Description</h4>
        <InlineTextEditor
          text={systemDescription.fullDescription}
          onChange={(value) => updateSystemField('fullDescription', value)}
          onClick={() => handleSystemItemClick(systemDescription.fullDescription, 'description', 0)}
          isEditing={isEditMode}
          minHeight="200px"
          componentName="Full System Description"
        />
      </div>

      <div className="description-grid">
        <div className="description-section">
          <h4>System Boundaries - Included</h4>
          <EditableList
            items={systemDescription.boundaries.included}
            onUpdate={(items) => updateSystemBoundaries('included', items)}
            onItemClick={!isEditMode ? (item, idx) => handleSystemItemClick(item, 'boundary-included', idx) : undefined}
            isEditMode={isEditMode}
            itemIcon="✓"
            itemClassName="boundary-list included-list"
            placeholder="Add an included boundary..."
            selectedIndex={selectedElement?.type === 'system-item' && selectedElement?.element?.type === 'boundary-included' ? parseInt(selectedElement.element.id.split('-')[1]) : null}
            componentName="Included Boundaries"
          />
        </div>

        <div className="description-section">
          <h4>System Boundaries - Excluded</h4>
          <EditableList
            items={systemDescription.boundaries.excluded}
            onUpdate={(items) => updateSystemBoundaries('excluded', items)}
            onItemClick={!isEditMode ? (item, idx) => handleSystemItemClick(item, 'boundary-excluded', idx) : undefined}
            isEditMode={isEditMode}
            itemIcon="✕"
            itemClassName="boundary-list excluded-list"
            placeholder="Add an excluded boundary..."
            selectedIndex={selectedElement?.type === 'system-item' && selectedElement?.element?.type === 'boundary-excluded' ? parseInt(selectedElement.element.id.split('-')[1]) : null}
            componentName="Excluded Boundaries"
          />
        </div>
      </div>

      <div className="description-section">
        <h4>Assumptions</h4>
        <EditableList
          items={systemDescription.assumptions}
          onUpdate={updateSystemAssumptions}
          onItemClick={!isEditMode ? (item, idx) => handleSystemItemClick(item, 'assumption', idx) : undefined}
          isEditMode={isEditMode}
          itemIcon="💡"
          itemClassName="assumption-list"
          placeholder="Add a new assumption..."
          selectedIndex={selectedElement?.type === 'system-item' && selectedElement?.element?.type === 'assumption' ? parseInt(selectedElement.element.id.split('-')[1]) : null}
          componentName="Assumptions"
        />
      </div>

      <div className="description-section">
        <h4>Operating Context</h4>
        <InlineTextEditor
          text={systemDescription.context}
          onChange={(value) => updateSystemField('context', value)}
          onClick={() => handleSystemItemClick(systemDescription.context, 'context', 0)}
          isEditing={isEditMode}
          minHeight="120px"
          componentName="Operating Context"
        />
      </div>
    </div>
  );

  const renderStakeholders = () => {
    const primaryStakeholders = stakeholders.filter(s => s.type === 'primary');
    const secondaryStakeholders = stakeholders.filter(s => s.type === 'secondary');
    const adversaries = stakeholders.filter(s => s.type === 'adversary');
    const TableComponent = isEditMode ? EditableTable : AnalysisTable;

    const influenceOptions = [
      { value: 'high', label: 'High' },
      { value: 'medium', label: 'Medium' },
      { value: 'low', label: 'Low' }
    ];

    const updateStakeholdersByType = (data: any[], type: string) => {
      const otherStakeholders = stakeholders.filter(s => s.type !== type);
      const updatedStakeholders = data.map(s => ({ ...s, type }));
      setStakeholders([...otherStakeholders, ...updatedStakeholders]);
    };

    return (
      <div className="stakeholders-view">
        <div className="stakeholder-section">
          <h3>Primary Stakeholders</h3>
          <TableComponent
            columns={[
              { key: 'id', label: 'ID', width: '80px', editable: false },
              { key: 'name', label: 'Name', width: '200px' },
              { key: 'role', label: 'Role' },
              { key: 'interests', label: 'Key Interests' },
              { key: 'influenceLevel', label: 'Influence', width: '100px', editType: 'select', options: influenceOptions },
              { key: 'accessLevel', label: 'Access Level' },
            ]}
            data={primaryStakeholders.map(s => ({
              ...s,
              interests: s.interests.join(', ')
            }))}
            onRowSelect={(row) => handleElementSelect(row, 'stakeholder')}
            selectedRowId={selectedElement?.type === 'stakeholder' ? selectedElement.id : null}
            onUpdate={isEditMode ? (data) => updateStakeholdersByType(data, 'primary') : undefined}
            isEditMode={isEditMode}
          />
        </div>

        <div className="stakeholder-section">
          <h3>Secondary Stakeholders</h3>
          <TableComponent
            columns={[
              { key: 'id', label: 'ID', width: '80px', editable: false },
              { key: 'name', label: 'Name', width: '200px' },
              { key: 'role', label: 'Role' },
              { key: 'interests', label: 'Key Interests' },
              { key: 'influenceLevel', label: 'Influence', width: '100px', editType: 'select', options: influenceOptions },
            ]}
            data={secondaryStakeholders.map(s => ({
              ...s,
              interests: s.interests.join(', ')
            }))}
            onRowSelect={(row) => handleElementSelect(row, 'stakeholder')}
            selectedRowId={selectedElement?.type === 'stakeholder' ? selectedElement.id : null}
            onUpdate={isEditMode ? (data) => updateStakeholdersByType(data, 'secondary') : undefined}
            isEditMode={isEditMode}
          />
        </div>

        <div className="stakeholder-section adversaries">
          <h3>Adversaries / Threat Actors</h3>
          <TableComponent
            columns={[
              { key: 'id', label: 'ID', width: '80px', editable: false },
              { key: 'name', label: 'Threat Actor', width: '200px' },
              { key: 'role', label: 'Description' },
              { key: 'interests', label: 'Objectives' },
              { key: 'influenceLevel', label: 'Threat Level', width: '100px', editType: 'select', options: influenceOptions },
            ]}
            data={adversaries.map(s => ({
              ...s,
              interests: s.interests.join(', ')
            }))}
            onRowSelect={(row) => handleElementSelect(row, 'adversary')}
            selectedRowId={selectedElement?.type === 'adversary' ? selectedElement.id : null}
            onUpdate={isEditMode ? (data) => updateStakeholdersByType(data, 'adversary') : undefined}
            isEditMode={isEditMode}
          />
        </div>
      </div>
    );
  };

  const renderLosses = () => {
    const TableComponent = isEditMode ? EditableTable : AnalysisTable;
    
    const severityOptions = [
      { value: 'critical', label: 'Critical' },
      { value: 'high', label: 'High' },
      { value: 'medium', label: 'Medium' },
      { value: 'low', label: 'Low' }
    ];
    
    return (
      <div className="single-table-view">
        <TableComponent
          title="Identified Losses"
          columns={[
            { key: 'id', label: 'ID', width: '60px', editable: false },
            { key: 'description', label: 'Description', width: '35%' },
            { key: 'severity', label: 'Severity', width: '100px', editType: 'select', options: severityOptions },
            { key: 'category', label: 'Category', width: '120px' },
            { key: 'stakeholders', label: 'Stakeholders', width: '200px' },
          ]}
          data={losses}
          onRowSelect={(row) => handleElementSelect(row, 'loss')}
          selectedRowId={selectedElement?.type === 'loss' ? selectedElement.id : null}
          onUpdate={isEditMode ? updateLosses : undefined}
          isEditMode={isEditMode}
          // itemType="loss"
          // linkable={!isEditMode}
        />
      </div>
    );
  };
  
  const renderHazards = () => {
    const TableComponent = isEditMode ? EditableTable : AnalysisTable;
    
    const severityOptions = [
      { value: 'critical', label: 'Critical' },
      { value: 'high', label: 'High' },
      { value: 'medium', label: 'Medium' },
      { value: 'low', label: 'Low' }
    ];
    
    return (
      <div className="single-table-view">
        <TableComponent
          title="Security Hazards/Vulnerabilities"
          columns={[
            { key: 'id', label: 'ID', width: '60px', editable: false },
            { key: 'description', label: 'Description', width: '30%' },
            { key: 'severity', label: 'Severity', width: '100px', editType: 'select', options: severityOptions },
            { key: 'relatedLosses', label: 'Related Losses', width: '120px' },
            { key: 'worstCase', label: 'Worst Case', width: '25%' },
          ]}
          data={hazards}
          onRowSelect={(row) => handleElementSelect(row, 'hazard')}
          selectedRowId={selectedElement?.type === 'hazard' ? selectedElement.id : null}
          onUpdate={isEditMode ? updateHazards : undefined}
          isEditMode={isEditMode}
          // itemType="hazard"
          // linkable={!isEditMode}
        />
      </div>
    );
  };

  const renderControllers = () => {
    const TableComponent = isEditMode ? EditableTable : AnalysisTable;
    
    return (
      <div className="single-table-view">
        <TableComponent
          title="System Controllers"
          columns={[
            { key: 'id', label: 'ID', width: '60px' },
            { key: 'name', label: 'Controller Name', width: '25%' },
            { key: 'type', label: 'Type', width: '120px' },
            { key: 'responsibilities', label: 'Responsibilities', width: '45%' },
          ]}
          data={controllers}
          onRowSelect={(row) => handleElementSelect(row, 'controller')}
          selectedRowId={selectedElement?.type === 'controller' ? selectedElement.id : null}
          onUpdate={isEditMode ? updateControllers : undefined}
          isEditMode={isEditMode}
          // itemType="controller"
          // linkable={!isEditMode}
        />
      </div>
    );
  };
  
  const renderControlActions = () => {
    const TableComponent = isEditMode ? EditableTable : AnalysisTable;
    
    return (
      <div className="single-table-view">
        <TableComponent
          title="Control Actions"
          columns={[
            { key: 'id', label: 'ID', width: '60px' },
            { key: 'action', label: 'Control Action', width: '25%' },
            { key: 'controllerId', label: 'Controller', width: '100px' },
            { key: 'targetProcess', label: 'Target Process', width: '20%' },
            { key: 'constraints', label: 'Constraints', width: '30%' },
          ]}
          data={controlActions}
          onRowSelect={(row) => handleElementSelect(row, 'controlAction')}
          selectedRowId={selectedElement?.type === 'controlAction' ? selectedElement.id : null}
          onUpdate={isEditMode ? updateControlActions : undefined}
          isEditMode={isEditMode}
          // itemType="control-action"
          // linkable={!isEditMode}
        />
      </div>
    );
  };
  
  const renderControlDiagram = () => {
    return (
      <ProcessControlDiagram 
        controllers={controllers}
        controlActions={controlActions}
        isEditMode={isEditMode}
      />
    );
  };

  const renderUCAs = () => {
    const TableComponent = isEditMode ? EditableTable : AnalysisTable;
    
    const ucaTypeOptions = [
      { value: 'not-provided', label: 'Not Provided' },
      { value: 'provided-causes-hazard', label: 'Provided Causes Hazard/Vulnerability' },
      { value: 'wrong-timing', label: 'Wrong Timing/Order' },
      { value: 'stopped-too-soon', label: 'Stopped Too Soon/Applied Too Long' }
    ];
    
    const severityOptions = [
      { value: 'critical', label: 'Critical' },
      { value: 'high', label: 'High' },
      { value: 'medium', label: 'Medium' },
      { value: 'low', label: 'Low' }
    ];
    
    return (
      <TableComponent
        title="Unsafe/Unsecure Control Actions (UCAs)"
        columns={[
          { key: 'id', label: 'ID', width: '60px', editable: false },
          { key: 'controlActionId', label: 'Control Action', width: '120px' },
          { key: 'type', label: 'Type', width: '140px', editType: 'select', options: ucaTypeOptions },
          { key: 'description', label: 'Description', width: '25%' },
          { key: 'context', label: 'Context', width: '20%' },
          { key: 'hazards', label: 'Hazards/Vulnerabilities', width: '120px' },
          { key: 'severity', label: 'Severity', width: '100px', editType: 'select', options: severityOptions },
        ]}
        data={ucas}
        onRowSelect={(row) => handleElementSelect(row, 'uca')}
        selectedRowId={selectedElement?.type === 'uca' ? selectedElement.id : null}
        onUpdate={isEditMode ? updateUcas : undefined}
        isEditMode={isEditMode}
        // itemType="uca"
        // linkable={!isEditMode}
      />
    );
  };

  const renderScenarios = () => {
    const TableComponent = isEditMode ? EditableTable : AnalysisTable;
    
    return (
      <TableComponent
        title="Causal Scenarios & Mitigations"
        columns={[
          { key: 'id', label: 'ID', width: '60px' },
          { key: 'ucaId', label: 'UCA', width: '80px' },
          { key: 'description', label: 'Scenario Description', width: '30%' },
          { key: 'strideCategory', label: 'STRIDE', width: '120px' },
          { key: 'confidence', label: 'Confidence', width: '100px' },
          { key: 'mitigations', label: 'Mitigations', width: '25%' },
        ]}
        data={scenarios.map(s => ({
          ...s,
          mitigations: s.mitigations.join('; ')
        }))}
        onRowSelect={(row) => handleElementSelect(row, 'scenario')}
        selectedRowId={selectedElement?.type === 'scenario' ? selectedElement.id : null}
        onUpdate={isEditMode ? (data) => {
          // Preserve all existing fields and merge with updated data
          const updatedScenarios = data.map(d => {
            const existing = scenarios.find(s => s.id === d.id);
            if (existing) {
              return {
                ...existing,
                ...d,
                mitigations: existing.mitigations || []
              };
            }
            // For new scenarios, provide default values
            return {
              id: d.id,
              ucaId: d.ucaId || '',
              description: d.description || '',
              causalFactors: d.causalFactors || [],
              strideCategory: d.strideCategory || '',
              d4Score: d.d4Score || { detectability: 0, difficulty: 0, damage: 0, deniability: 0 },
              confidence: d.confidence || 0,
              mitigations: []
            } as CausalScenario;
          });
          updateScenarios(updatedScenarios);
        } : undefined}
        isEditMode={isEditMode}
        // itemType="scenario"
        // linkable={!isEditMode}
      />
    );
  };

  const renderWargaming = () => <WargamingTab scenarios={scenarios} />;

  const renderTraceability = () => {
    if (!selectedElement) return null;
    
    const related = getRelatedData(selectedElement.id, selectedElement.type);
    
    return (
      <div className="traceability-panel">
        <h4>Traceability for {selectedElement.type.toUpperCase()} {selectedElement.id}</h4>
        
        {related.losses.length > 0 && (
          <div className="trace-section">
            <h5>Related Losses ({related.losses.length})</h5>
            {related.losses.map(l => (
              <div key={l.id} className="trace-item">
                <span className="trace-id">{l.id}</span>
                <span className="trace-desc">{l.description}</span>
              </div>
            ))}
          </div>
        )}
        
        {related.hazards.length > 0 && (
          <div className="trace-section">
            <h5>Related Hazards ({related.hazards.length})</h5>
            {related.hazards.map(h => (
              <div key={h.id} className="trace-item">
                <span className="trace-id">{h.id}</span>
                <span className="trace-desc">{h.description}</span>
              </div>
            ))}
          </div>
        )}
        
        {related.ucas.length > 0 && (
          <div className="trace-section">
            <h5>Related UCAs ({related.ucas.length})</h5>
            {related.ucas.map(u => (
              <div key={u.id} className="trace-item">
                <span className="trace-id">{u.id}</span>
                <span className="trace-desc">{u.description}</span>
              </div>
            ))}
          </div>
        )}
        
        {related.scenarios.length > 0 && (
          <div className="trace-section">
            <h5>Related Scenarios ({related.scenarios.length})</h5>
            {related.scenarios.map(s => (
              <div key={s.id} className="trace-item">
                <span className="trace-id">{s.id}</span>
                <span className="trace-desc">{s.description}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <main className="analysis-panel">
      {showDemoWarning && (
        <div style={{
          background: 'var(--color-warning-light)',
          border: '1px solid var(--color-warning)',
          borderRadius: 'var(--radius-md)',
          padding: '12px',
          margin: '0 0 16px 0',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <span style={{ color: 'var(--color-warning-dark)' }}>
            You're editing demo data. Create a new version to save your changes.
          </span>
          <button
            onClick={() => {
              const newVersionId = createVersion(
                `Analysis ${new Date().toLocaleDateString()}`,
                'Created from demo data modifications',
                'demo-v1'
              );
              switchVersion(newVersionId);
              setShowDemoWarning(false);
            }}
            style={{
              padding: '6px 12px',
              background: 'var(--color-primary)',
              color: 'white',
              border: 'none',
              borderRadius: 'var(--radius-sm)',
              cursor: 'pointer',
              fontSize: 'var(--font-size-sm)'
            }}
          >
            Create New Version
          </button>
        </div>
      )}
      <div className="analysis-toolbar">
        <div className="toolbar-left">
          {!isEditMode ? (
            <button
              className="btn-toolbar"
              onClick={() => {
                setIsEditMode(true);
              }}
              title="Enter edit mode"
            >
              <Edit3 size={16} />
              <span>Edit Mode</span>
            </button>
          ) : (
            <>
              <button
                className={`btn-toolbar primary ${hasValidationErrors ? 'disabled' : ''}`}
                onClick={() => {
                  if (!hasValidationErrors) {
                    setIsEditMode(false);
                  }
                }}
                title={hasValidationErrors ? 'Fix validation errors before saving' : 'Save changes and exit edit mode'}
                disabled={hasValidationErrors}
              >
                <Save size={16} />
                <span>Save Changes</span>
              </button>
              <button
                className="btn-toolbar secondary"
                onClick={() => {
                  // Restore all original values
                  updateSystemDescription(originalSystemDescriptionRef.current);
                  setStakeholders(originalStakeholdersRef.current);
                  updateLosses(originalLossesRef.current);
                  updateHazards(originalHazardsRef.current);
                  updateControllers(originalControllersRef.current);
                  updateControlActions(originalControlActionsRef.current);
                  updateUcas(originalUcasRef.current);
                  updateScenarios(originalScenariosRef.current);
                  setIsEditMode(false);
                }}
                title="Cancel changes and exit edit mode"
              >
                <span>Cancel</span>
              </button>
            </>
          )}
          
          <div className="automation-selector">
            <Settings size={16} />
            <select 
              value={automationLevel} 
              onChange={(e) => setAutomationLevel(e.target.value as any)}
              className="select-automation"
            >
              <option value="manual">Fully Manual</option>
              <option value="assisted">AI Assisted</option>
              <option value="semi-auto">Semi-Automated</option>
              <option value="fully-auto">Fully Automated</option>
            </select>
          </div>
        </div>
        
        <div className="toolbar-right">
          <div className="export-menu">
            <button className="btn-toolbar">
              <Download size={16} />
              <span>Export</span>
            </button>
            <div className="export-dropdown">
              <button onClick={() => handleExport('json')}>Export as JSON</button>
              <button onClick={() => handleExport('pdf')}>Export as PDF</button>
              <button onClick={() => handleExport('html')}>Export as HTML</button>
            </div>
          </div>
        </div>
      </div>
      
      {!standaloneMode && (
        <div className="tabs">
          {tabs.map(tab => (
            <Link
              key={tab.id}
              to={`/analysis/view/${tab.id}`}
              className={`tab ${activeTab === tab.id ? 'active' : ''}`}
              onClick={(e) => {
                e.preventDefault();
                setActiveTab(tab.id);
                onAnalysisChange(tab.id);
              }}
            >
              {tab.label}
            </Link>
          ))}
        </div>
      )}
      
      {activeTab === 'stpa-sec' && !standaloneMode && (
        <div className="subtabs">
          {stpaSecSubTabs.map(subTab => {
            const Icon = subTab.icon;
            const canOpenStandalone = SUBTAB_TO_COMPONENT[subTab.id];
            
            const href = canOpenStandalone 
              ? `/analysis/component/${canOpenStandalone}`
              : '#';
            
            return (
              <Link
                key={subTab.id}
                to={href}
                className={`subtab ${stpaSecSubTab === subTab.id ? 'active' : ''}`}
                onClick={(e) => {
                  e.preventDefault();
                  setStpaSecSubTab(subTab.id);
                }}
              >
                <Icon size={16} />
                <span>{subTab.label}</span>
              </Link>
            );
          })}
        </div>
      )}
      
      <div className="analysis-content">
        {isAnalyzing ? (
          <div className="analyzing-state">
            <div className="analyzing-spinner" />
            <p>Analyzing your system...</p>
            <div className="progress-bar mt-4">
              <div className="progress-fill" style={{ width: '40%' }} />
            </div>
          </div>
        ) : (
          <>
            {activeTab === 'stpa-sec' && (
              <div className="stpa-sec-content">
                {stpaSecSubTab === 'system-description' && renderSystemDescription()}
                {stpaSecSubTab === 'stakeholders' && renderStakeholders()}
                {stpaSecSubTab === 'losses' && renderLosses()}
                {stpaSecSubTab === 'hazards' && renderHazards()}
                {stpaSecSubTab === 'control-diagram' && renderControlDiagram()}
                {stpaSecSubTab === 'controllers' && renderControllers()}
                {stpaSecSubTab === 'control-actions' && renderControlActions()}
                {stpaSecSubTab === 'ucas' && renderUCAs()}
                {stpaSecSubTab === 'scenarios' && renderScenarios()}
                {stpaSecSubTab === 'wargaming' && renderWargaming()}
                
                {selectedElement && (stpaSecSubTab !== 'system-description') && (stpaSecSubTab !== 'wargaming') && (stpaSecSubTab !== 'control-diagram') && (
                  <div className="selection-details">
                    {renderTraceability()}
                  </div>
                )}
              </div>
            )}
            
            {activeTab === 'stride' && <StrideAnalysis onElementSelect={handleElementSelect} />}
            
            {activeTab === 'pasta' && <PastaAnalysis onElementSelect={handleElementSelect} />}
            
            {activeTab === 'maestro' && <MaestroAnalysis onElementSelect={handleElementSelect} />}
            
            {activeTab === 'dread' && <DreadAnalysis onElementSelect={handleElementSelect} />}
            
            {activeTab === 'linddun' && <LinddunAnalysis onElementSelect={handleElementSelect} />}
            
            {activeTab === 'hazop' && <HazopAnalysis onElementSelect={handleElementSelect} />}
            
            {activeTab === 'octave' && <OctaveAnalysis onElementSelect={handleElementSelect} />}
            
            {activeTab === 'cve' && (
              <div className="analysis-section">
                <h3>CVE Search Results</h3>
                <p className="text-secondary">Common Vulnerabilities and Exposures database search results will appear here...</p>
              </div>
            )}
            
            {activeTab === 'overview' && <AnalysisOverview enabledAnalyses={enabledAnalyses} />}
          </>
        )}
      </div>
    </main>
  );
}