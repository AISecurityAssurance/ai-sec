import { useState, useEffect } from 'react';
import SimpleLayout from '../../components/common/SimpleLayout';
import ThreePanelLayout from '../../components/common/ThreePanelLayout';
import InputSelectionPanel from '../../components/analysis/InputSelectionPanel';
import AnalysisCanvas from '../../components/analysis/AnalysisCanvas';
import ChatPanel from '../user/components/ChatPanel';
import WelcomeScreen from '../../components/analysis/WelcomeScreen';
import LoadingOverlay from '../../components/common/LoadingOverlay';
import AnalysisProgress from '../../components/analysis/AnalysisProgress';
import type { AnalysisStep } from '../../components/analysis/AnalysisProgress';
import { NewAnalysisDialog } from '../user/components/NewAnalysisDialog';
import { AnalysisWebSocketProvider } from '../../components/analysis/AnalysisWebSocketProvider';
import { useAnalysisStore } from '../../stores/analysisStore';
import { isFirstVisit } from '../../utils/resetStores';
import { generateUUID } from '../../utils/uuid';
import { apiFetch } from '../../config/api';
import wsClient from '../../utils/websocket';
import './AnalysisApp.css';

export default function AnalysisApp() {
  const [activeAnalysis, setActiveAnalysis] = useState('stpa-sec');
  const [showNewAnalysisDialog, setShowNewAnalysisDialog] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showWelcome, setShowWelcome] = useState(true);
  const [analysisSteps, setAnalysisSteps] = useState<AnalysisStep[]>([]);
  const [currentFramework, setCurrentFramework] = useState<string>('');
  const [analysisFrameworks, setAnalysisFrameworks] = useState<string[]>([]);
  const [analysisError, setAnalysisError] = useState<string>('');
  
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
  
  // Helper function to get framework-specific analysis steps
  const getFrameworkSteps = (framework: string): AnalysisStep[] => {
    const baseSteps: Record<string, AnalysisStep[]> = {
      'stpa-sec': [
        { id: `${framework}-system-modeling`, name: 'System Modeling', status: 'pending' as const },
        { id: `${framework}-hazard-analysis`, name: 'Hazard Analysis', status: 'pending' as const },
        { id: `${framework}-control-structure`, name: 'Control Structure', status: 'pending' as const },
        { id: `${framework}-unsafe-actions`, name: 'Unsafe Control Actions', status: 'pending' as const },
        { id: `${framework}-loss-scenarios`, name: 'Loss Scenarios', status: 'pending' as const },
      ],
      'stride': [
        { id: `${framework}-data-flow`, name: 'Data Flow Analysis', status: 'pending' as const },
        { id: `${framework}-threat-modeling`, name: 'Threat Modeling', status: 'pending' as const },
        { id: `${framework}-threat-categorization`, name: 'Threat Categorization', status: 'pending' as const },
        { id: `${framework}-mitigation`, name: 'Mitigation Strategies', status: 'pending' as const },
      ],
      'pasta': [
        { id: `${framework}-business-objectives`, name: 'Business Objectives', status: 'pending' as const },
        { id: `${framework}-tech-scope`, name: 'Technical Scope', status: 'pending' as const },
        { id: `${framework}-app-decomposition`, name: 'Application Decomposition', status: 'pending' as const },
        { id: `${framework}-threat-analysis`, name: 'Threat Analysis', status: 'pending' as const },
        { id: `${framework}-vulnerability-analysis`, name: 'Vulnerability Analysis', status: 'pending' as const },
        { id: `${framework}-attack-modeling`, name: 'Attack Modeling', status: 'pending' as const },
        { id: `${framework}-risk-analysis`, name: 'Risk Analysis', status: 'pending' as const },
      ],
      'dread': [
        { id: `${framework}-damage-potential`, name: 'Damage Potential', status: 'pending' as const },
        { id: `${framework}-reproducibility`, name: 'Reproducibility', status: 'pending' as const },
        { id: `${framework}-exploitability`, name: 'Exploitability', status: 'pending' as const },
        { id: `${framework}-affected-users`, name: 'Affected Users', status: 'pending' as const },
        { id: `${framework}-discoverability`, name: 'Discoverability', status: 'pending' as const },
      ],
      'maestro': [
        { id: `${framework}-mission-critical`, name: 'Mission Critical Analysis', status: 'pending' as const },
        { id: `${framework}-attack-vectors`, name: 'Attack Vectors', status: 'pending' as const },
        { id: `${framework}-exploit-scenarios`, name: 'Exploit Scenarios', status: 'pending' as const },
        { id: `${framework}-security-testing`, name: 'Security Testing', status: 'pending' as const },
        { id: `${framework}-risk-optimization`, name: 'Risk Optimization', status: 'pending' as const },
      ],
      'linddun': [
        { id: `${framework}-data-flow-diagram`, name: 'Data Flow Diagram', status: 'pending' as const },
        { id: `${framework}-privacy-threats`, name: 'Privacy Threats', status: 'pending' as const },
        { id: `${framework}-threat-mapping`, name: 'Threat Mapping', status: 'pending' as const },
        { id: `${framework}-elicitation`, name: 'Threat Elicitation', status: 'pending' as const },
        { id: `${framework}-privacy-controls`, name: 'Privacy Controls', status: 'pending' as const },
      ],
      'hazop': [
        { id: `${framework}-parameter-identification`, name: 'Parameter Identification', status: 'pending' as const },
        { id: `${framework}-guide-words`, name: 'Guide Word Application', status: 'pending' as const },
        { id: `${framework}-deviation-analysis`, name: 'Deviation Analysis', status: 'pending' as const },
        { id: `${framework}-consequence-assessment`, name: 'Consequence Assessment', status: 'pending' as const },
        { id: `${framework}-safeguards`, name: 'Safeguards', status: 'pending' as const },
      ],
      'octave': [
        { id: `${framework}-asset-identification`, name: 'Asset Identification', status: 'pending' as const },
        { id: `${framework}-threat-profiling`, name: 'Threat Profiling', status: 'pending' as const },
        { id: `${framework}-vulnerability-identification`, name: 'Vulnerability Identification', status: 'pending' as const },
        { id: `${framework}-risk-measurement`, name: 'Risk Measurement', status: 'pending' as const },
        { id: `${framework}-protection-strategy`, name: 'Protection Strategy', status: 'pending' as const },
      ],
    };
    
    return baseSteps[framework] || [
      { id: `${framework}-analysis`, name: 'Analysis', status: 'pending' as const }
    ];
  };
  
  // Listen for WebSocket updates to update progress
  useEffect(() => {
    if (!currentAnalysisId || !isAnalyzing) return;
    
    const handleAnalysisUpdate = (event: CustomEvent) => {
      const { status, progress, message, framework } = event.detail;
      
      if (framework) {
        setCurrentFramework(framework);
      }
      
      // Update step status based on progress message
      if (message && analysisSteps.length > 0) {
        setAnalysisSteps(prevSteps => 
          prevSteps.map(step => {
            // Check if this step is mentioned in the message
            if (message.toLowerCase().includes(step.name.toLowerCase())) {
              return { ...step, status: 'in_progress' as const, message };
            }
            // Mark previous steps as completed if we're past them
            if (step.status === 'in_progress') {
              return { ...step, status: 'completed' as const };
            }
            return step;
          })
        );
      }
      
      // Handle completion
      if (status === 'completed') {
        setAnalysisSteps(prevSteps =>
          prevSteps.map(step => ({ ...step, status: 'completed' as const }))
        );
        setIsAnalyzing(false);
      } else if (status === 'failed') {
        setAnalysisError(message || 'Analysis failed');
        setIsAnalyzing(false);
      }
    };
    
    const handleSectionUpdate = (event: CustomEvent) => {
      const { framework, section_id, status } = event.detail;
      
      setAnalysisSteps(prevSteps =>
        prevSteps.map(step => {
          if (step.id === `${framework}-${section_id}`) {
            return { 
              ...step, 
              status: status === 'completed' ? 'completed' : 
                      status === 'failed' ? 'failed' : 
                      status === 'in_progress' ? 'in_progress' : 
                      'pending' as const
            };
          }
          return step;
        })
      );
    };
    
    // Listen for WebSocket events
    window.addEventListener('analysis-update', handleAnalysisUpdate as EventListener);
    window.addEventListener('section-update', handleSectionUpdate as EventListener);
    
    return () => {
      window.removeEventListener('analysis-update', handleAnalysisUpdate as EventListener);
      window.removeEventListener('section-update', handleSectionUpdate as EventListener);
    };
  }, [currentAnalysisId, isAnalyzing, analysisSteps]);
  
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
    setAnalysisFrameworks(data.frameworks);
    setAnalysisError('');
    
    // Initialize analysis steps based on selected frameworks
    const initialSteps: AnalysisStep[] = [];
    data.frameworks.forEach(framework => {
      // Add framework-specific steps
      const frameworkSteps = getFrameworkSteps(framework);
      initialSteps.push(...frameworkSteps);
    });
    console.log('Setting initial steps:', initialSteps);
    setAnalysisSteps(initialSteps);
    
    try {
      const projectId = generateUUID();
      
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
      
      if (!response.ok) {
        throw new Error('Failed to create analysis');
      }
      
      const result = await response.json();
      console.log('Analysis created:', result);
      
      // Store the analysis ID in the global store
      if (result.id) {
        setCurrentAnalysisId(result.id);
        // Delay hiding welcome to ensure state is preserved
        setTimeout(() => {
          setShowWelcome(false);
        }, 100);
      }
      
      // Keep analyzing state true until WebSocket updates indicate completion
      // The AnalysisWebSocketProvider will handle setting it to false
      
      // Mock progress simulation for demo/testing
      // This simulates what the WebSocket would normally do
      const USE_MOCK_PROGRESS = false; // Set to false when backend is ready
      
      if (USE_MOCK_PROGRESS && (!result.id || process.env.NODE_ENV === 'development')) {
        console.log('Starting mock progress simulation');
        let stepIndex = 0;
        const totalSteps = initialSteps.length;
        
        const progressInterval = setInterval(() => {
          if (stepIndex < totalSteps) {
            const currentStep = initialSteps[stepIndex];
            const frameworkName = currentStep.id.split('-')[0];
            
            // Mark current step as in progress
            setAnalysisSteps(prevSteps => 
              prevSteps.map(step => 
                step.id === currentStep.id 
                  ? { ...step, status: 'in_progress' as const }
                  : step.status === 'in_progress' 
                    ? { ...step, status: 'completed' as const }
                    : step
              )
            );
            
            // Update current framework
            setCurrentFramework(frameworkName);
            
            // After 1.5 seconds, mark as completed and move to next
            setTimeout(() => {
              setAnalysisSteps(prevSteps =>
                prevSteps.map(step =>
                  step.id === currentStep.id
                    ? { ...step, status: 'completed' as const }
                    : step
                )
              );
              stepIndex++;
              
              // If all steps completed, finish analysis
              if (stepIndex >= totalSteps) {
                clearInterval(progressInterval);
                setTimeout(() => {
                  setIsAnalyzing(false);
                  console.log('Mock analysis completed');
                }, 1000);
              }
            }, 1500);
          }
        }, 2000);
        
        // Store interval ID for cleanup if needed
        (window as any).__analysisProgressInterval = progressInterval;
      }
      
    } catch (error) {
      console.error('Error creating analysis:', error);
      setIsAnalyzing(false);
      setAnalysisError('Failed to create analysis. Please check your connection and try again.');
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
        {isAnalyzing && (
          <LoadingOverlay>
            <AnalysisProgress 
              frameworks={analysisFrameworks}
              steps={analysisSteps}
              currentFramework={currentFramework}
              error={analysisError}
            />
          </LoadingOverlay>
        )}
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
        {isAnalyzing && (
          <LoadingOverlay>
            <AnalysisProgress 
              frameworks={analysisFrameworks}
              steps={analysisSteps}
              currentFramework={currentFramework}
              error={analysisError}
            />
          </LoadingOverlay>
        )}
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