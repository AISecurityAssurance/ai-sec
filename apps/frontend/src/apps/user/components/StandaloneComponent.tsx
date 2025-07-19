import { useParams, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { X, Maximize2, Minimize2 } from 'lucide-react';
import ProcessControlDiagram from './ProcessControlDiagram';
import AnalysisTable from './AnalysisTable';
import EditableTable from './EditableTable';
import WargamingTab from './WargamingTab';
import PastaAnalysis from './PastaAnalysis';
import DreadAnalysis from './DreadAnalysis';
import AnalysisOverview from './AnalysisOverview';
import { STANDALONE_COMPONENTS, type StandaloneComponentType } from '../routes';
import { useBroadcastChannel } from '../hooks/useBroadcastChannel';
import { useAnalysisStore } from '../stores/analysisStore';
import './StandaloneComponent.css';

export default function StandaloneComponent() {
  const { componentType } = useParams<{ componentType: StandaloneComponentType }>();
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);
  
  // Get data from store
  const {
    losses,
    hazards,
    controllers,
    controlActions,
    ucas,
    scenarios,
    enabledAnalyses,
    updateLosses,
    updateHazards,
    updateControllers,
    updateControlActions,
    updateUcas,
    updateScenarios
  } = useAnalysisStore();
  
  // Set up broadcast channel for state sync
  useBroadcastChannel();
  
  // Update window title
  useEffect(() => {
    if (componentType && STANDALONE_COMPONENTS[componentType]) {
      document.title = `${STANDALONE_COMPONENTS[componentType]} - Security Analysis Platform`;
    }
  }, [componentType]);
  
  // Handle fullscreen toggle
  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };
  
  // Close window handler
  const handleClose = () => {
    window.close();
  };
  
  if (!componentType || !STANDALONE_COMPONENTS[componentType]) {
    return <Navigate to="/analysis" replace />;
  }
  
  const renderComponent = () => {
    const TableComponent = isEditMode ? EditableTable : AnalysisTable;
    
    switch (componentType) {
      case 'control-diagram':
        return (
          <ProcessControlDiagram
            controllers={controllers}
            controlActions={controlActions}
            isEditMode={isEditMode}
          />
        );
        
      case 'losses':
        return (
          <TableComponent
            title="Identified Losses"
            columns={[
              { key: 'id', label: 'ID', width: '60px' },
              { key: 'description', label: 'Description' },
              { key: 'severity', label: 'Severity', width: '100px' },
              { key: 'category', label: 'Category', width: '120px' },
              { key: 'stakeholders', label: 'Stakeholders', width: '200px' },
            ]}
            data={losses}
            isEditMode={isEditMode}
            onUpdate={updateLosses}
          />
        );
        
      case 'hazards':
        return (
          <TableComponent
            title="Security Hazards/Vulnerabilities"
            columns={[
              { key: 'id', label: 'ID', width: '60px' },
              { key: 'description', label: 'Description' },
              { key: 'severity', label: 'Severity', width: '100px' },
              { key: 'relatedLosses', label: 'Related Losses', width: '120px' },
              { key: 'worstCase', label: 'Worst Case', width: '300px' },
            ]}
            data={hazards}
            isEditMode={isEditMode}
            onUpdate={updateHazards}
          />
        );
        
      case 'controllers':
        return (
          <TableComponent
            title="System Controllers"
            columns={[
              { key: 'id', label: 'ID', width: '60px' },
              { key: 'name', label: 'Controller Name' },
              { key: 'type', label: 'Type', width: '120px' },
              { key: 'responsibilities', label: 'Responsibilities' },
            ]}
            data={controllers}
            isEditMode={isEditMode}
            onUpdate={updateControllers}
          />
        );
        
      case 'control-actions':
        return (
          <TableComponent
            title="Control Actions"
            columns={[
              { key: 'id', label: 'ID', width: '60px' },
              { key: 'action', label: 'Control Action' },
              { key: 'controllerId', label: 'Controller', width: '100px' },
              { key: 'targetProcess', label: 'Target Process' },
              { key: 'constraints', label: 'Constraints' },
            ]}
            data={controlActions}
            isEditMode={isEditMode}
            onUpdate={updateControlActions}
          />
        );
        
      case 'ucas':
        return (
          <TableComponent
            title="Unsafe/Unsecure Control Actions (UCAs)"
            columns={[
              { key: 'id', label: 'ID', width: '60px' },
              { key: 'controlActionId', label: 'Control Action', width: '120px' },
              { key: 'type', label: 'Type', width: '140px' },
              { key: 'description', label: 'Description' },
              { key: 'context', label: 'Context' },
              { key: 'hazards', label: 'Hazards/Vulnerabilities', width: '120px' },
              { key: 'severity', label: 'Severity', width: '100px' },
            ]}
            data={ucas}
            isEditMode={isEditMode}
            onUpdate={updateUcas}
          />
        );
        
      case 'scenarios':
        return (
          <TableComponent
            title="Causal Scenarios & Mitigations"
            columns={[
              { key: 'id', label: 'ID', width: '60px' },
              { key: 'ucaId', label: 'UCA', width: '80px' },
              { key: 'description', label: 'Scenario Description' },
              { key: 'strideCategory', label: 'STRIDE', width: '120px' },
              { key: 'confidence', label: 'Confidence', width: '100px' },
              { key: 'mitigations', label: 'Mitigations' },
            ]}
            data={scenarios.map(s => ({
              ...s,
              mitigations: s.mitigations.length + ' mitigations'
            }))}
            isEditMode={isEditMode}
            onUpdate={(data) => {
              // Preserve all existing fields and merge with updated data
              const transformedData = data.map(item => {
                const originalScenario = scenarios.find(s => s.id === item.id);
                if (originalScenario) {
                  return {
                    ...originalScenario,
                    ...item,
                    mitigations: originalScenario.mitigations || []
                  };
                }
                // For new scenarios, provide default values
                return {
                  id: item.id,
                  ucaId: item.ucaId || '',
                  description: item.description || '',
                  causalFactors: item.causalFactors || [],
                  strideCategory: item.strideCategory || '',
                  d4Score: item.d4Score || { detectability: 0, difficulty: 0, damage: 0, deniability: 0 },
                  confidence: item.confidence || 0,
                  mitigations: []
                };
              });
              updateScenarios(transformedData);
            }}
          />
        );
        
      case 'wargaming':
        return <WargamingTab scenarios={scenarios} />;
        
      case 'pasta':
        return <PastaAnalysis />;
        
      case 'dread':
        return <DreadAnalysis />;
        
      case 'overview':
        return <AnalysisOverview enabledAnalyses={enabledAnalyses} />;
        
      default:
        return <div>Component not implemented yet</div>;
    }
  };
  
  return (
    <div className="standalone-container">
      <header className="standalone-header">
        <h1>{STANDALONE_COMPONENTS[componentType]}</h1>
        <div className="standalone-controls">
          {['losses', 'hazards', 'controllers', 'control-actions', 'ucas', 'scenarios', 'control-diagram'].includes(componentType) && (
            <button 
              className={`btn-toolbar ${isEditMode ? 'active' : ''}`}
              onClick={() => setIsEditMode(!isEditMode)}
            >
              {isEditMode ? 'Save Changes' : 'Edit Mode'}
            </button>
          )}
          <button 
            className="btn-icon" 
            onClick={toggleFullscreen}
            title={isFullscreen ? 'Exit fullscreen' : 'Enter fullscreen'}
          >
            {isFullscreen ? <Minimize2 size={18} /> : <Maximize2 size={18} />}
          </button>
          <button 
            className="btn-icon btn-close" 
            onClick={handleClose}
            title="Close window"
          >
            <X size={18} />
          </button>
        </div>
      </header>
      
      <main className="standalone-content">
        {renderComponent()}
      </main>
    </div>
  );
}