import { useState, useEffect } from 'react';
import { Download } from 'lucide-react';
import { useAnalysisStore } from '../../stores/analysisStore';
import CollapsibleAnalysisSection from './CollapsibleAnalysisSection';
import ExportDialog from './ExportDialog';
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
  const { enabledAnalyses } = useAnalysisStore();
  const [demoMode, setDemoMode] = useState(false);
  const [expandedAnalyses, setExpandedAnalyses] = useState<Set<string>>(new Set());
  const [showExportDialog, setShowExportDialog] = useState(false);
  
  // Check if we're in standalone mode (opened in new window)
  const isStandalone = window.location.pathname === '/analysis/canvas';

  // Listen for demo mode changes
  useEffect(() => {
    const handleDemoModeChange = (event: CustomEvent) => {
      setDemoMode(event.detail.enabled);
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

  // Only show content in demo mode or standalone mode
  if (!demoMode && !isStandalone) {
    return (
      <div className="analysis-canvas empty">
        <div className="empty-state">
          <h3>Welcome to Security Analysis Platform</h3>
          <p>To get started:</p>
          <ol>
            <li>Select input files or links in the Input Selection panel</li>
            <li>Choose analysis plugins to run</li>
            <li>Click "Run Analysis" to begin</li>
          </ol>
          <p className="demo-hint">Or enable Demo Mode to see example analysis results</p>
        </div>
      </div>
    );
  }

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
    </div>
  );
}