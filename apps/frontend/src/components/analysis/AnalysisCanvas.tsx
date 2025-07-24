import { useState, useEffect } from 'react';
import { Download, Plus } from 'lucide-react';
import { useAnalysisStore } from '../../stores/analysisStore';
import CollapsibleAnalysisSection from './CollapsibleAnalysisSection';
import ExportDialog from './ExportDialog';
import { AddAnalysisDialog } from './AddAnalysisDialog';
import './AnalysisCanvas.css';

// Analysis plugin order (matches the order in InputSelectionPanel)
const analysisOrder = [
  'stpa-sec',
  'stride', 
  'pasta',
  'dread',
  'maestro',
  'linddun',
  'hazop',
  'octave'
];

export default function AnalysisCanvas() {
  const { enabledAnalyses, demoMode, analysisResults } = useAnalysisStore();
  const [expandedAnalyses, setExpandedAnalyses] = useState<Set<string>>(new Set());
  const [showExportDialog, setShowExportDialog] = useState(false);
  const [showAddAnalysisDialog, setShowAddAnalysisDialog] = useState(false);
  
  // Check if we're in standalone mode (opened in new window)
  const isStandalone = window.location.pathname === '/analysis/canvas';

  // Listen for demo mode changes (for real-time updates across components)
  useEffect(() => {
    const handleDemoModeChange = (event: CustomEvent) => {
      // Demo mode is now handled by the store, but we keep this for backward compatibility
    };
    
    window.addEventListener('demoModeChanged' as any, handleDemoModeChange);
    return () => {
      window.removeEventListener('demoModeChanged' as any, handleDemoModeChange);
    };
  }, []);

  const toggleAnalysis = (analysisId: string) => {
    setExpandedAnalyses(prev => {
      const newSet = new Set(prev);
      if (newSet.has(analysisId)) {
        newSet.delete(analysisId);
      } else {
        newSet.add(analysisId);
      }
      return newSet;
    });
  };

  const handleExport = (format: 'json' | 'pdf' | 'html') => {
    console.log('Exporting in format:', format);
    // TODO: Implement actual export functionality
    alert(`Export to ${format.toUpperCase()} - Coming soon!`);
  };
  
  const handleAddAnalysis = (frameworks: string[]) => {
    console.log('Adding additional analyses:', frameworks);
    // TODO: Trigger new analysis for selected frameworks
    alert(`Running additional analyses: ${frameworks.join(', ')}`);
  };
  
  // Get completed frameworks
  const completedFrameworks = Object.keys(analysisResults)
    .filter(fw => analysisResults[fw]?.status?.status === 'completed');

  // Get list of enabled analyses in order
  const enabledAnalysesList = analysisOrder
    .filter(id => enabledAnalyses[id]);

  const analysisLabels: Record<string, string> = {
    'stpa-sec': 'STPA-Sec',
    'stride': 'STRIDE',
    'pasta': 'PASTA',
    'dread': 'DREAD',
    'maestro': 'MAESTRO',
    'linddun': 'LINDDUN',
    'hazop': 'HAZOP',
    'octave': 'OCTAVE'
  };

  return (
    <div className="analysis-canvas">
      <div className="canvas-header">
        <h2>Security Analysis Results</h2>
        <div className="canvas-actions">
          {completedFrameworks.length < analysisOrder.length && (
            <button 
              className="add-analysis-btn"
              onClick={() => setShowAddAnalysisDialog(true)}
              title="Run additional security analyses"
            >
              <Plus size={16} />
              Add Analysis
            </button>
          )}
          {enabledAnalysesList.length > 0 && (
            <button 
              className="export-btn"
              onClick={() => setShowExportDialog(true)}
            >
              <Download size={16} />
              Export
            </button>
          )}
        </div>
      </div>
      
      <div className="canvas-content">
        {enabledAnalysesList.length === 0 ? (
          <div className="empty-state">
            <h3>No Analysis Selected</h3>
            <p>Select analysis plugins from the Input Selection panel to view results</p>
          </div>
        ) : (
          <div className="analysis-sections">
            {enabledAnalysesList.map(analysisId => (
              <CollapsibleAnalysisSection
                key={analysisId}
                analysisId={analysisId}
                analysisLabel={analysisLabels[analysisId]}
                enabledAnalyses={enabledAnalyses}
                isExpanded={expandedAnalyses.has(analysisId)}
                onToggle={() => toggleAnalysis(analysisId)}
              />
            ))}
          </div>
        )}
      </div>
      
      <ExportDialog
        isOpen={showExportDialog}
        onClose={() => setShowExportDialog(false)}
        onExport={handleExport}
      />
      
      <AddAnalysisDialog
        isOpen={showAddAnalysisDialog}
        onClose={() => setShowAddAnalysisDialog(false)}
        onSubmit={handleAddAnalysis}
        completedFrameworks={completedFrameworks}
      />
    </div>
  );
}