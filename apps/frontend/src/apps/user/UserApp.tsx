import { useState, useEffect } from 'react';
import SimpleLayout from '../../components/common/SimpleLayout';
import Sidebar from './components/Sidebar';
import AnalysisPanel from './components/AnalysisPanel';
import ChatPanel from './components/ChatPanel';
import { NewAnalysisDialog } from './components/NewAnalysisDialog';
import { useAnalysisStore } from '../../stores/analysisStore';
import { useVersionStore } from '../../stores/versionStore';
import { AnalysisWebSocketProvider } from '../../components/analysis/AnalysisWebSocketProvider';
import { VersionSelector } from '../../components/VersionSelector';
import { generateUUID } from '../../utils/uuid';
import { apiFetch } from '../../config/api';
import './UserApp.css';
import { generateMockAnalysisResults } from '../../mocks/mockAnalysisResults';

export default function UserApp() {
  const [selectedProject, setSelectedProject] = useState(null);
  const [activeAnalysis, setActiveAnalysis] = useState('stpa-sec');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [selectedElement, setSelectedElement] = useState<any>(null);
  const [showNewAnalysisDialog, setShowNewAnalysisDialog] = useState(false);
  
  // Get enabledAnalyses and analysis status from Zustand store
  const { enabledAnalyses, setEnabledAnalyses, setCurrentAnalysisId, analysisStatus, updateAnalysisStatus, isLoadingData, dataLoadError } = useAnalysisStore();
  
  // Update isAnalyzing based on analysisStatus
  useEffect(() => {
    if (analysisStatus.status === 'in_progress') {
      setIsAnalyzing(true);
    } else if (analysisStatus.status === 'completed' || analysisStatus.status === 'failed') {
      setIsAnalyzing(false);
    }
  }, [analysisStatus.status]);
  
  // Load data from API on mount
  useEffect(() => {
    const analysisStore = useAnalysisStore.getState();
    
    // Always load from database API - no fallback to mock data
    analysisStore.loadDataFromApi().catch((error) => {
      console.error('Failed to load data from API:', error);
      // DO NOT fall back to mock data - let the error show
    });
  }, []);

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
      const projectId = generateUUID();
      
      // Reset to demo data first, then create a new version
      const versionStore = useVersionStore.getState();
      const analysisStore = useAnalysisStore.getState();
      
      // If we're on demo, create a new version for this analysis
      if (versionStore.activeVersionId === 'demo-v1') {
        analysisStore.resetToDemoData();
        const newVersionId = versionStore.createVersion(
          `Analysis - ${new Date().toLocaleDateString()}`,
          data.description,
          'demo-v1'
        );
        versionStore.switchVersion(newVersionId);
      }
      
      // Try API call first
      let useSimulation = false;
      try {
        const response = await apiFetch('/api/v1/analysis/', {
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
        
        if (response.ok) {
          const result = await response.json();
          console.log('Analysis created:', result);
          
          // Store the analysis ID in the global store
          if (result.id) {
            setCurrentAnalysisId(result.id);
          }
        } else {
          useSimulation = true;
        }
      } catch (apiError) {
        console.log('API not available, using simulation');
        useSimulation = true;
      }
      
      // If API failed or not available, simulate progress
      if (useSimulation) {
        setCurrentAnalysisId(projectId);
        
        // Simulate analysis progress
        let progress = 0;
        const progressInterval = setInterval(() => {
          progress += Math.random() * 20 + 5; // Random increment between 5-25
          
          if (progress >= 100) {
            progress = 100;
            clearInterval(progressInterval);
            
            updateAnalysisStatus({
              status: 'completed',
              progress: 100,
              message: 'Analysis complete'
            });
            
            // Generate mock results after a short delay
            setTimeout(() => {
              const mockResults = generateMockAnalysisResults(data.frameworks);
              const store = useAnalysisStore.getState();
              
              // Update results for each framework
              Object.entries(mockResults).forEach(([framework, result]) => {
                store.updateAnalysisResult(framework, result);
              });
              
              setIsAnalyzing(false);
            }, 500);
          } else {
            updateAnalysisStatus({
              status: 'in_progress',
              progress: Math.min(progress, 99),
              message: `Analyzing ${data.frameworks.join(', ')}... ${Math.round(progress)}%`
            });
          }
        }, 300);
      }
      
      // Update enabled analyses to only show selected frameworks
      const newEnabledAnalyses: Record<string, boolean> = {};
      ['stpa-sec', 'stride', 'pasta', 'dread', 'maestro', 'linddun', 'hazop', 'octave'].forEach(framework => {
        newEnabledAnalyses[framework] = data.frameworks.includes(framework);
      });
      setEnabledAnalyses(newEnabledAnalyses);
      
      // The WebSocket connection will handle real-time updates
      // and update the analysisStatus which will trigger the useEffect
      
    } catch (error) {
      console.error('Error creating analysis:', error);
      setIsAnalyzing(false);
    }
  };

  // Show loading overlay while fetching data
  if (isLoadingData) {
    return (
      <SimpleLayout>
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
          flexDirection: 'column',
          gap: '20px'
        }}>
          <div style={{ fontSize: '24px', color: 'var(--primary)' }}>⚡</div>
          <div style={{ color: 'var(--text-secondary)' }}>Loading analysis data...</div>
        </div>
      </SimpleLayout>
    );
  }

  // Show error message if data load failed
  if (dataLoadError) {
    return (
      <SimpleLayout>
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
          flexDirection: 'column',
          gap: '20px',
          padding: '40px'
        }}>
          <div style={{ fontSize: '48px', color: 'var(--error)' }}>⚠️</div>
          <h2 style={{ color: 'var(--error)', margin: 0 }}>Database Connection Failed</h2>
          <p style={{ color: 'var(--text-secondary)', textAlign: 'center', maxWidth: '600px' }}>
            {dataLoadError}
          </p>
          <p style={{ color: 'var(--text-secondary)', textAlign: 'center' }}>
            Please ensure the backend is running at http://localhost:8000
          </p>
          <button 
            className="btn-primary" 
            onClick={() => window.location.reload()}
          >
            Retry Connection
          </button>
        </div>
      </SimpleLayout>
    );
  }

  return (
    <SimpleLayout>
      <AnalysisWebSocketProvider>
        <div className="user-layout-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <VersionSelector />
            <button 
              className="btn-primary"
              onClick={() => setShowNewAnalysisDialog(true)}
              disabled={isAnalyzing}
            >
              New Analysis
            </button>
          </div>
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