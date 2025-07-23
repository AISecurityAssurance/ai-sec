import { Shield, Zap, FileText, Users, ChevronRight } from 'lucide-react';
import './WelcomeScreen.css';

interface WelcomeScreenProps {
  onNewAnalysis: () => void;
  onLoadDemo: () => void;
}

export default function WelcomeScreen({ onNewAnalysis, onLoadDemo }: WelcomeScreenProps) {
  return (
    <div className="welcome-screen">
      <div className="welcome-content">
        <div className="welcome-header">
          <Shield className="welcome-icon" size={48} />
          <h1>Welcome to Security Analysis Platform</h1>
          <p className="welcome-subtitle">
            Comprehensive threat modeling and security analysis for your systems
          </p>
        </div>

        <div className="welcome-actions">
          <button className="welcome-action-primary" onClick={onNewAnalysis}>
            <Zap size={20} />
            Start New Analysis
          </button>
          <button className="welcome-action-secondary" onClick={onLoadDemo}>
            <FileText size={20} />
            View Demo Analysis
          </button>
        </div>

        <div className="welcome-features">
          <h2>What you can do:</h2>
          <div className="feature-grid">
            <div className="feature-card">
              <h3>🔍 Multiple Frameworks</h3>
              <p>Analyze your system using STPA-SEC, STRIDE, PASTA, DREAD, and more security frameworks</p>
            </div>
            <div className="feature-card">
              <h3>🤖 AI-Powered Assistant</h3>
              <p>Get intelligent insights and recommendations from our SA Agent throughout your analysis</p>
            </div>
            <div className="feature-card">
              <h3>📊 Visual Analysis</h3>
              <p>Interactive canvas for exploring relationships between threats, vulnerabilities, and controls</p>
            </div>
            <div className="feature-card">
              <h3>📁 Context-Aware</h3>
              <p>Upload system documentation and architecture files for deeper, more accurate analysis</p>
            </div>
          </div>
        </div>

        <div className="welcome-quick-start">
          <h2>Quick Start Guide:</h2>
          <ol className="quick-start-steps">
            <li>
              <span className="step-number">1</span>
              <div className="step-content">
                <strong>Describe Your System</strong>
                <p>Provide a clear description of your system, its components, and boundaries</p>
              </div>
            </li>
            <li>
              <span className="step-number">2</span>
              <div className="step-content">
                <strong>Select Analysis Frameworks</strong>
                <p>Choose one or more security frameworks based on your analysis needs</p>
              </div>
            </li>
            <li>
              <span className="step-number">3</span>
              <div className="step-content">
                <strong>Review Results</strong>
                <p>Explore findings through the analysis canvas and get insights from SA Agent</p>
              </div>
            </li>
            <li>
              <span className="step-number">4</span>
              <div className="step-content">
                <strong>Export & Share</strong>
                <p>Generate reports and share findings with your team</p>
              </div>
            </li>
          </ol>
        </div>

        <div className="welcome-footer">
          <p>
            <Users size={16} style={{ verticalAlign: 'middle', marginRight: '4px' }} />
            Need help? Ask the SA Agent or check our documentation
          </p>
        </div>
      </div>
    </div>
  );
}