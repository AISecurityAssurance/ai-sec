import { useState, useEffect } from 'react';
import SimpleLayout from '../../components/common/SimpleLayout';
import ThreePanelLayout from '../../components/common/ThreePanelLayout';
import InputSelectionPanel from '../../components/analysis/InputSelectionPanel';
import AnalysisCanvas from '../../components/analysis/AnalysisCanvas';
import ChatPanel from '../user/components/ChatPanel';
import WelcomeScreen from '../../components/analysis/WelcomeScreen';
import { NewAnalysisDialog } from '../user/components/NewAnalysisDialog';
import { AnalysisWebSocketProvider } from '../../components/analysis/AnalysisWebSocketProvider';
import { useAnalysisStore } from '../../stores/analysisStore';
import { isFirstVisit } from '../../utils/resetStores';
import './AnalysisApp.css';

export default function AnalysisApp() {
  const [activeAnalysis, setActiveAnalysis] = useState('stpa-sec');
  const [showNewAnalysisDialog, setShowNewAnalysisDialog] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showWelcome, setShowWelcome] = useState(true);
  
  const { currentAnalysisId, setCurrentAnalysisId, demoMode, setDemoMode, clearAnalysisResults } = useAnalysisStore();
  
  // Check if we should show welcome screen
  useEffect(() => {
    // Always show welcome on first visit
    if (isFirstVisit()) {
      setShowWelcome(true);
      // Ensure demo mode is off on first visit
      setDemoMode(false);
    } else if (currentAnalysisId || demoMode) {
      setShowWelcome(false);
    }
  }, [currentAnalysisId, demoMode, setDemoMode]);
  
  const handleOpenInNewWindow = (panel: 'left' | 'center' | 'right') => {
    const urls = {
      left: '/analysis/input-selection',
      center: '/analysis/canvas',
      right: '/analysis/agent'
    };
    
    const sizes = {
      left: { width: 400, height: 600 },
      center: { width: 800, height: 600 },
      right: { width: 400, height: 600 }
    };
    
    const size = sizes[panel];
    const features = `width=${size.width},height=${size.height},menubar=no,toolbar=no,location=no,status=no`;
    window.open(urls[panel], `analysis-${panel}`, features);
  };

  const handleCreateAnalysis = async (data: { description: string; frameworks: string[] }) => {
    console.log('Creating analysis with:', data);
    setIsAnalyzing(true);
    
    try {
      const projectId = crypto.randomUUID();
      
      const response = await fetch('/api/v1/analysis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          project_id: projectId,
          system_description: data.description,
          frameworks: data.frameworks,
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to create analysis');
      }
      
      const result = await response.json();
      console.log('Analysis created:', result);
      
      // Store the analysis ID in the global store
      if (result.id) {
        setCurrentAnalysisId(result.id);
        setShowWelcome(false);
      }
      
    } catch (error) {
      console.error('Error creating analysis:', error);
      setIsAnalyzing(false);
    }
  };
  
  const handleLoadDemo = () => {
    // Clear any existing analysis and enable demo mode
    clearAnalysisResults();
    setDemoMode(true);
    setShowWelcome(false);
  };
  
  // Show welcome screen if no analysis is active
  if (showWelcome) {
    return (
      <SimpleLayout>
        <WelcomeScreen 
          onNewAnalysis={() => setShowNewAnalysisDialog(true)}
          onLoadDemo={handleLoadDemo}
        />
        <NewAnalysisDialog
          isOpen={showNewAnalysisDialog}
          onClose={() => setShowNewAnalysisDialog(false)}
          onSubmit={handleCreateAnalysis}
        />
      </SimpleLayout>
    );
  }

  return (
    <SimpleLayout>
      <AnalysisWebSocketProvider>
        <div className="analysis-header" style={{ padding: '10px 20px', display: 'flex', alignItems: 'center', borderBottom: '1px solid var(--border-color)' }}>
          <button 
            className="btn-primary"
            onClick={() => setShowNewAnalysisDialog(true)}
            disabled={isAnalyzing}
          >
            New Analysis
          </button>
          {isAnalyzing && (
            <span style={{ marginLeft: '20px', color: 'var(--text-secondary)' }}>
              Analysis in progress...
              <span className="progress-indicator" style={{ marginLeft: '10px' }}>⚡</span>
            </span>
          )}
        </div>
        <ThreePanelLayout
          leftPanel={<InputSelectionPanel />}
          centerPanel={<AnalysisCanvas />}
          rightPanel={<ChatPanel activeAnalysis={activeAnalysis} />}
          onOpenInNewWindow={handleOpenInNewWindow}
        />
        
        <NewAnalysisDialog
          isOpen={showNewAnalysisDialog}
          onClose={() => setShowNewAnalysisDialog(false)}
          onSubmit={handleCreateAnalysis}
        />
      </AnalysisWebSocketProvider>
    </SimpleLayout>
  );
}