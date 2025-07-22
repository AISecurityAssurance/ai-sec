import { useParams, Navigate } from 'react-router-dom';
import { useState } from 'react';
import { X, Menu } from 'lucide-react';
import AnalysisPanel from './AnalysisPanel';
import ChatPanel from './ChatPanel';
import { useAnalysisStore } from '../../../stores/analysisStore';
import { useBroadcastSync } from '../hooks/useBroadcastChannel';
import './StandaloneAnalysisView.css';

const ANALYSIS_TYPES = {
  'stpa-sec': 'STPA-Sec',
  'stride': 'STRIDE',
  'pasta': 'PASTA',
  'dread': 'DREAD',
  'maestro': 'MAESTRO',
  'linddun': 'LINDDUN',
  'hazop': 'HAZOP',
  'octave': 'OCTAVE',
  'cve': 'CVE Search',
  'overview': 'Overview'
} as const;

export type AnalysisType = keyof typeof ANALYSIS_TYPES;

export default function StandaloneAnalysisView() {
  const { analysisType } = useParams<{ analysisType: string }>();
  const [showChat, setShowChat] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  
  // Get enabled analyses from store
  const { enabledAnalyses } = useAnalysisStore();
  
  // Set up broadcast sync
  useBroadcastSync();
  
  if (!analysisType || !ANALYSIS_TYPES[analysisType as AnalysisType]) {
    return <Navigate to="/analysis" replace />;
  }
  
  const handleRunAnalysis = async () => {
    setIsAnalyzing(true);
    // Simulate analysis
    setTimeout(() => {
      setIsAnalyzing(false);
    }, 3000);
  };
  
  const handleClose = () => {
    window.close();
  };
  
  return (
    <div className="standalone-analysis-view">
      <header className="standalone-analysis-header">
        <div className="header-left">
          <h1>🛡️ {ANALYSIS_TYPES[analysisType as AnalysisType]} Analysis</h1>
        </div>
        <div className="header-controls">
          <button 
            className="btn btn-primary"
            onClick={handleRunAnalysis}
            disabled={isAnalyzing}
          >
            {isAnalyzing ? (
              <>
                <div className="spinner" />
                Analyzing...
              </>
            ) : (
              <>
                <span>▶</span>
                Run Analysis
              </>
            )}
          </button>
          <button
            className="btn-icon"
            onClick={() => setShowChat(!showChat)}
            title={showChat ? 'Hide SA Agent' : 'Show SA Agent'}
          >
            <Menu size={18} />
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
      
      <div className="standalone-analysis-content">
        <div className="analysis-main">
          <AnalysisPanel
            activeAnalysis={analysisType}
            onAnalysisChange={() => {}} // No-op since we're in standalone mode
            isAnalyzing={isAnalyzing}
            enabledAnalyses={{
              [analysisType]: true  // Only enable the current analysis type
            }}
            standaloneMode={true}
          />
        </div>
        
        {showChat && (
          <ChatPanel
            projectId={null}
            activeAnalysis={analysisType}
            selectedElement={null}
          />
        )}
      </div>
    </div>
  );
}