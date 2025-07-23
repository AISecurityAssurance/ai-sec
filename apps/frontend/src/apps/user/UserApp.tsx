import { useState } from 'react';
import SimpleLayout from '../../components/common/SimpleLayout';
import Sidebar from './components/Sidebar';
import AnalysisPanel from './components/AnalysisPanel';
import ChatPanel from './components/ChatPanel';
import { NewAnalysisDialog } from './components/NewAnalysisDialog';
import { useAnalysisStore } from '../../stores/analysisStore';
import { AnalysisWebSocketProvider } from '../../components/analysis/AnalysisWebSocketProvider';
import './UserApp.css';

export default function UserApp() {
  const [selectedProject, setSelectedProject] = useState(null);
  const [activeAnalysis, setActiveAnalysis] = useState('stpa-sec');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [selectedElement, setSelectedElement] = useState<any>(null);
  const [showNewAnalysisDialog, setShowNewAnalysisDialog] = useState(false);
  
  // Get enabledAnalyses from Zustand store
  const { enabledAnalyses, setEnabledAnalyses } = useAnalysisStore();

  const handleRunAnalysis = async () => {
    setIsAnalyzing(true);
    // Simulate analysis
    setTimeout(() => {
      setIsAnalyzing(false);
    }, 3000);
  };

  const handleCreateAnalysis = async (data: { description: string; frameworks: string[] }) => {
    console.log('Creating analysis with:', data);
    setIsAnalyzing(true);
    
    try {
      // Create a temporary project ID for now
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
      
      // Update UI to show analysis in progress
      // The WebSocket connection should handle real-time updates
      
    } catch (error) {
      console.error('Error creating analysis:', error);
      setIsAnalyzing(false);
    }
  };

  return (
    <SimpleLayout>
      <AnalysisWebSocketProvider>
        <div className="user-layout-header">
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
        <div className="user-layout">
          <Sidebar 
            selectedProject={selectedProject}
            onProjectSelect={setSelectedProject}
            onAnalysisTypesChange={setEnabledAnalyses}
          />
          
          <div className="user-main">
            <AnalysisPanel 
              activeAnalysis={activeAnalysis}
              onAnalysisChange={setActiveAnalysis}
              isAnalyzing={isAnalyzing}
              onElementSelect={(element, type) => setSelectedElement({ element, type })}
              enabledAnalyses={enabledAnalyses}
            />
          </div>
          
          <ChatPanel 
            projectId={selectedProject?.id}
            activeAnalysis={activeAnalysis}
            selectedElement={selectedElement}
          />
        </div>
        
        <NewAnalysisDialog
          isOpen={showNewAnalysisDialog}
          onClose={() => setShowNewAnalysisDialog(false)}
          onSubmit={handleCreateAnalysis}
        />
      </AnalysisWebSocketProvider>
    </SimpleLayout>
  );
}