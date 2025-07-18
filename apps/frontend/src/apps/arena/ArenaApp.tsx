import { useState } from 'react';
import { Menu } from 'lucide-react';
import AppLayout from '../../components/common/AppLayout';
import ConfigPanel from './components/ConfigPanel';
import TestColumn from './components/TestColumn';
import ChatPanel from '../user/components/ChatPanel';
import './ArenaApp.css';

export default function ArenaApp() {
  const [isRunning, setIsRunning] = useState(false);
  const [selectedScenario, setSelectedScenario] = useState('banking');
  const [configPanelVisible, setConfigPanelVisible] = useState(true);

  const handleRunComparison = () => {
    setIsRunning(true);
    setTimeout(() => {
      setIsRunning(false);
    }, 3000);
  };

  const header = (
    <header className="arena-header">
      <div className="header-left">
        <button 
          className="config-toggle"
          onClick={() => setConfigPanelVisible(!configPanelVisible)}
          title={configPanelVisible ? 'Hide configuration' : 'Show configuration'}
        >
          <Menu size={20} />
        </button>
        <h1 className="heading-3">🧪 Security Analysis Testing Arena</h1>
      </div>
      <div className="header-controls">
        <button className="btn btn-secondary">Load Scenario</button>
        <button 
          className="btn btn-primary"
          onClick={handleRunComparison}
          disabled={isRunning}
        >
          {isRunning ? 'Running...' : 'Run Comparison'}
        </button>
      </div>
    </header>
  );

  return (
    <AppLayout header={header}>
      <div className="arena-layout">
        {configPanelVisible && (
          <ConfigPanel 
            selectedScenario={selectedScenario}
            onScenarioChange={setSelectedScenario}
          />
        )}
        
        <div className="test-main">
          <TestColumn 
            variant="A"
            label="Production"
            isRunning={isRunning}
          />
          <TestColumn 
            variant="B"
            label="Experimental"
            isRunning={isRunning}
            isExperimental
          />
        </div>
        
        <ChatPanel 
          projectId={selectedScenario}
          activeAnalysis="comparison"
        />
      </div>
    </AppLayout>
  );
}