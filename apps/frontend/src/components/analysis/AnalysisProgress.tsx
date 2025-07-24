import { Check, Circle, Loader2 } from 'lucide-react';
import './AnalysisProgress.css';

export interface AnalysisStep {
  id: string;
  name: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  message?: string;
}

interface AnalysisProgressProps {
  frameworks: string[];
  steps: AnalysisStep[];
  currentFramework?: string;
  error?: string;
}

const frameworkNames: Record<string, string> = {
  'stpa-sec': 'STPA-Sec',
  'stride': 'STRIDE',
  'pasta': 'PASTA',
  'dread': 'DREAD',
  'maestro': 'MAESTRO',
  'linddun': 'LINDDUN',
  'hazop': 'HAZOP',
  'octave': 'OCTAVE'
};

export default function AnalysisProgress({ 
  frameworks, 
  steps, 
  currentFramework,
  error 
}: AnalysisProgressProps) {
  const getStepIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <Check className="step-icon completed" size={16} />;
      case 'in_progress':
        return <Loader2 className="step-icon in-progress spinning" size={16} />;
      case 'failed':
        return <Circle className="step-icon failed" size={16} />;
      default:
        return <Circle className="step-icon pending" size={16} />;
    }
  };

  // Group steps by framework
  const stepsByFramework = steps.reduce((acc, step) => {
    const framework = step.id.split('-')[0];
    if (!acc[framework]) acc[framework] = [];
    acc[framework].push(step);
    return acc;
  }, {} as Record<string, AnalysisStep[]>);
  
  // Ensure all selected frameworks are represented
  frameworks.forEach(framework => {
    if (!stepsByFramework[framework]) {
      stepsByFramework[framework] = [];
    }
  });

  // Show loading state if no frameworks or steps yet
  if (frameworks.length === 0 || steps.length === 0) {
    return (
      <div className="analysis-progress">
        <div className="progress-header">
          <h2>Starting Security Analysis</h2>
        </div>
        <div className="frameworks-progress">
          <div className="framework-section">
            <div className="steps-list">
              <div className="step-item in_progress">
                <Loader2 className="step-icon in-progress spinning" size={16} />
                <span className="step-name">Initializing analysis...</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="analysis-progress">
      <div className="progress-header">
        <h2>Security Analysis in Progress</h2>
        {currentFramework && (
          <p className="current-framework">
            Currently analyzing: <strong>{frameworkNames[currentFramework] || currentFramework}</strong>
          </p>
        )}
      </div>

      {error && (
        <div className="progress-error">
          <strong>Error:</strong> {error}
        </div>
      )}

      <div className="frameworks-progress">
        {frameworks.map(framework => (
          <div key={framework} className="framework-section">
            <h3 className="framework-title">
              {frameworkNames[framework] || framework}
              {stepsByFramework[framework]?.length > 0 && 
               stepsByFramework[framework].every(s => s.status === 'completed') && (
                <Check className="framework-complete" size={18} />
              )}
            </h3>
            
            <div className="steps-list">
              {stepsByFramework[framework]?.length > 0 ? (
                stepsByFramework[framework].map(step => (
                  <div key={step.id} className={`step-item ${step.status}`}>
                    {getStepIcon(step.status)}
                    <span className="step-name">{step.name}</span>
                    {step.message && (
                      <span className="step-message">{step.message}</span>
                    )}
                  </div>
                ))
              ) : (
                <div className="step-item pending">
                  <Circle className="step-icon pending" size={16} />
                  <span className="step-name">Waiting to start...</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="progress-footer">
        <p>This may take a few minutes. Please wait while the analysis completes.</p>
      </div>
    </div>
  );
}