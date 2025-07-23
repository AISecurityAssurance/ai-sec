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
    // TODO: Call backend API to create analysis
    // For now, just simulate
    setTimeout(() => {
      setIsAnalyzing(false);
    }, 2000);
  };

  return (
    <SimpleLayout>
      <AnalysisWebSocketProvider>
        <div className="user-layout-header">
          <button 
            className="btn-primary"
            onClick={() => setShowNewAnalysisDialog(true)}
          >
            New Analysis
          </button>
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