import { useState } from 'react';
import { FileText, FolderOpen, Save, Plus, AlertCircle } from 'lucide-react';
import { useAnalysisStore } from '../../stores/analysisStore';
import SaveAnalysisDialog from './SaveAnalysisDialog';
import LoadAnalysisDialog from './LoadAnalysisDialog';
import './AnalysisManagement.css';

interface AnalysisManagementProps {
  onNewAnalysis: () => void;
  onAddAnalysis: () => void;
}

export default function AnalysisManagement({ onNewAnalysis, onAddAnalysis }: AnalysisManagementProps) {
  const { 
    currentAnalysisId, 
    analysisResults, 
    hasUnsavedChanges = false,
    setHasUnsavedChanges 
  } = useAnalysisStore();
  
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [showLoadDialog, setShowLoadDialog] = useState(false);
  const [showUnsavedWarning, setShowUnsavedWarning] = useState(false);
  
  const completedAnalyses = Object.keys(analysisResults).filter(
    fw => analysisResults[fw]?.status?.status === 'completed'
  );
  
  const handleNewAnalysis = () => {
    if (hasUnsavedChanges) {
      setShowUnsavedWarning(true);
    } else {
      onNewAnalysis();
    }
  };
  
  const handleSave = () => {
    setShowSaveDialog(true);
  };
  
  const handleLoad = () => {
    setShowLoadDialog(true);
  };
  
  const handleUnsavedChoice = (choice: 'save' | 'discard' | 'cancel') => {
    setShowUnsavedWarning(false);
    if (choice === 'save') {
      setShowSaveDialog(true);
    } else if (choice === 'discard') {
      onNewAnalysis();
    }
    // cancel does nothing
  };
  
  return (
    <div className="analysis-management">
      <div className="management-actions-list">
        <button 
          className="management-btn"
          onClick={handleNewAnalysis}
          title="Start a new security analysis"
        >
          <FileText size={16} />
          <span>New Analysis</span>
        </button>
        
        <button 
          className="management-btn"
          onClick={onAddAnalysis}
          disabled={!currentAnalysisId || completedAnalyses.length === 0}
          title="Add more analyses to current project"
        >
          <Plus size={16} />
          <span>Add Analysis</span>
        </button>
        
        <button 
          className="management-btn"
          onClick={handleSave}
          disabled={!currentAnalysisId}
          title="Save current analysis"
        >
          <Save size={16} />
          <span>Save</span>
        </button>
        
        <button 
          className="management-btn"
          onClick={handleLoad}
          title="Load existing analysis"
        >
          <FolderOpen size={16} />
          <span>Load</span>
        </button>
      </div>
      
      {/* Unsaved Changes Warning Dialog */}
      {showUnsavedWarning && (
        <div className="dialog-overlay" onClick={() => setShowUnsavedWarning(false)}>
          <div className="dialog-content warning-dialog" onClick={e => e.stopPropagation()}>
            <div className="dialog-header">
              <AlertCircle size={20} className="warning-icon" />
              <h3>Unsaved Changes</h3>
            </div>
            <div className="dialog-body">
              <p>You have unsaved changes. What would you like to do?</p>
            </div>
            <div className="dialog-actions">
              <button 
                className="btn-secondary"
                onClick={() => handleUnsavedChoice('cancel')}
              >
                Cancel
              </button>
              <button 
                className="btn-secondary"
                onClick={() => handleUnsavedChoice('discard')}
              >
                Discard Changes
              </button>
              <button 
                className="btn-primary"
                onClick={() => handleUnsavedChoice('save')}
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* Save Analysis Dialog */}
      <SaveAnalysisDialog
        isOpen={showSaveDialog}
        onClose={() => setShowSaveDialog(false)}
        onSave={(name, location, description) => {
          console.log('Saving analysis:', { name, location, description });
          // TODO: Implement actual save to backend
          if (location === 'export') {
            // Export as JSON file
            const analysisData = {
              name,
              description,
              date: new Date().toISOString(),
              results: analysisResults
            };
            const blob = new Blob([JSON.stringify(analysisData, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${name.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_analysis.json`;
            a.click();
            URL.revokeObjectURL(url);
            alert('Analysis exported successfully!');
          } else {
            alert(`Analysis "${name}" saved to ${location} storage!`);
          }
          setHasUnsavedChanges?.(false);
          setShowSaveDialog(false);
        }}
      />
      
      {/* Load Analysis Dialog */}
      <LoadAnalysisDialog
        isOpen={showLoadDialog}
        onClose={() => setShowLoadDialog(false)}
        onLoad={(analysisId) => {
          console.log('Loading analysis:', analysisId);
          // TODO: Implement actual load from backend
          alert(`Loading analysis ${analysisId}...`);
          setShowLoadDialog(false);
        }}
      />
    </div>
  );
}