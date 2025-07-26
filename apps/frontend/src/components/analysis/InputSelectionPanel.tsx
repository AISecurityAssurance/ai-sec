import { useState } from 'react';
import { File, ChevronRight, ChevronDown } from 'lucide-react';
import { useSettingsStore } from '../../stores/settingsStore';
import { useAnalysisStore } from '../../stores/analysisStore';
import AnalysisManagement from './AnalysisManagement';
import './InputSelectionPanel.css';

// For demo purposes - in real app, this would come from analysis store
const mockSelectedTokens = 15234; // Approximate tokens for 4 demo files

// Analysis plugin options
const analysisPlugins = [
  { id: 'stpa-sec-plus', label: 'STPA-Sec+ Orchestrator' },
  { id: 'stpa-sec', label: 'STPA-Sec' },
  { id: 'stride', label: 'STRIDE' },
  { id: 'pasta', label: 'PASTA' },
  { id: 'dread', label: 'DREAD' },
  { id: 'maestro', label: 'MAESTRO' },
  { id: 'linddun', label: 'LINDDUN' },
  { id: 'hazop', label: 'HAZOP' },
  { id: 'octave', label: 'OCTAVE' },
];

interface InputSelectionPanelProps {
  onNewAnalysis?: () => void;
  onAddAnalysis?: () => void;
}

export default function InputSelectionPanel({ onNewAnalysis, onAddAnalysis }: InputSelectionPanelProps = {}) {
  const { tokenEstimation } = useSettingsStore();
  const { enabledAnalyses, setEnabledAnalyses, demoMode, setDemoMode, analysisResults, currentAnalysisId } = useAnalysisStore();
  const [analysisToolsExpanded, setAnalysisToolsExpanded] = useState(false);
  const [inputSelectionExpanded, setInputSelectionExpanded] = useState(false);
  const [analysisPluginsExpanded, setAnalysisPluginsExpanded] = useState(true);
  
  // Use mock tokens for demo - in real app would calculate from actual inputs
  const selectedTokens = currentAnalysisId ? mockSelectedTokens : 0;
  
  // Check which analyses are completed
  const isAnalysisCompleted = (analysisId: string) => {
    return !!analysisResults[analysisId] && 
           analysisResults[analysisId].status.status === 'completed';
  };

  // Toggle demo mode
  const toggleDemoMode = () => {
    const newDemoMode = !demoMode;
    setDemoMode(newDemoMode);
    
    // Dispatch custom event for AnalysisCanvas
    window.dispatchEvent(new CustomEvent('demoModeChanged', { 
      detail: { enabled: newDemoMode } 
    }));
  };

  // Toggle analysis plugin
  const toggleAnalysisPlugin = (pluginId: string) => {
    const newEnabledAnalyses = {
      ...enabledAnalyses,
      [pluginId]: !enabledAnalyses[pluginId]
    };
    setEnabledAnalyses(newEnabledAnalyses);
  };

  const contextPercentage = (selectedTokens / tokenEstimation.maxTokens) * 100;
  const isWarning = contextPercentage > 80;
  const isError = contextPercentage > 100;

  return (
    <div className="input-selection-panel">
      {/* Analysis Tools Section */}
      <div className="panel-section">
        <div 
          className="section-header-link"
          onClick={() => setAnalysisToolsExpanded(!analysisToolsExpanded)}
        >
          {analysisToolsExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
          <span className="section-title-link">Analysis Tools</span>
        </div>
        
        {analysisToolsExpanded && onNewAnalysis && onAddAnalysis && (
          <AnalysisManagement 
            onNewAnalysis={onNewAnalysis}
            onAddAnalysis={onAddAnalysis}
          />
        )}
      </div>
      
      {/* Input Selection Section */}
      <div className="panel-section">
        <div 
          className="section-header-link"
          onClick={() => setInputSelectionExpanded(!inputSelectionExpanded)}
        >
          {inputSelectionExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
          <span className="section-title-link">Inputs</span>
          <span className="section-count">({currentAnalysisId ? '4 files' : '0'})</span>
        </div>
        
        {inputSelectionExpanded && (
          <div className="section-content">
            {currentAnalysisId ? (
              <>
                {/* Token usage for current inputs */}
                <div className="input-token-summary">
                  <div className="token-bar-wrapper">
                    <div className="token-bar">
                      <div 
                        className={`token-fill ${isError ? 'error' : isWarning ? 'warning' : ''}`}
                        style={{ width: `${Math.min(contextPercentage, 100)}%` }}
                      />
                    </div>
                    <div className="token-info">
                      {selectedTokens.toLocaleString()} / {tokenEstimation.maxTokens.toLocaleString()} tokens
                    </div>
                  </div>
                </div>
                
                {/* Selected inputs list */}
                <div className="selected-inputs-list">
                  <div className="input-item">
                    <File size={14} />
                    <span>autonomous-vehicle.txt</span>
                    <span className="input-size">3.9 KB</span>
                  </div>
                  <div className="input-item">
                    <File size={14} />
                    <span>banking-system.yaml</span>
                    <span className="input-size">3.3 KB</span>
                  </div>
                  <div className="input-item">
                    <File size={14} />
                    <span>e-commerce-architecture.md</span>
                    <span className="input-size">2.8 KB</span>
                  </div>
                  <div className="input-item">
                    <File size={14} />
                    <span>healthcare-iot.json</span>
                    <span className="input-size">5.3 KB</span>
                  </div>
                </div>
              </>
            ) : (
              <div className="no-inputs-message">
                No inputs selected. Use "New Analysis" to add inputs.
              </div>
            )}
          </div>
        )}
      </div>

      {/* Analysis Plugins Section */}
      <div className="panel-section">
        <div 
          className="section-header-link"
          onClick={() => setAnalysisPluginsExpanded(!analysisPluginsExpanded)}
        >
          {analysisPluginsExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
          <span className="section-title-link">Analysis Plugins</span>
          <span className="section-count">({Object.values(enabledAnalyses).filter(Boolean).length})</span>
        </div>
        
        {analysisPluginsExpanded && (
          <div className="section-content">
            <div className="analysis-plugins-list">
              {analysisPlugins.map(plugin => {
                const isCompleted = isAnalysisCompleted(plugin.id);
                return (
                  <label key={plugin.id} className={`analysis-plugin-item ${isCompleted ? 'completed' : 'not-run'}`}>
                    <input
                      type="checkbox"
                      checked={enabledAnalyses[plugin.id] || false}
                      onChange={() => toggleAnalysisPlugin(plugin.id)}
                    />
                    <a 
                      href={`/analysis/plugin/${plugin.id}`}
                      className="plugin-label-link"
                      onClick={(e) => e.preventDefault()}
                    >
                      <span className="plugin-label">
                        {plugin.label}
                        {isCompleted && <span className="completed-indicator"> ✓</span>}
                      </span>
                    </a>
                  </label>
                );
              })}
            </div>
          </div>
        )}
      </div>
      
      <div className="demo-mode-section">
        <button 
          className={`demo-mode-btn ${demoMode ? 'active' : ''}`}
          onClick={toggleDemoMode}
        >
          {demoMode ? 'Exit Sample Results' : 'View Sample Results'}
        </button>
        {demoMode && (
          <p className="demo-mode-hint">Viewing pre-populated sample analysis (no AI processing)</p>
        )}
      </div>
    </div>
  );
}