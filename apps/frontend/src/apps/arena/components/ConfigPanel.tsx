import './ArenaComponents.css';

interface ConfigPanelProps {
  selectedScenario: string;
  onScenarioChange: (scenario: string) => void;
}

const scenarios = [
  { id: 'banking', name: 'Banking API Analysis', description: 'Complex financial system with 50+ endpoints' },
  { id: 'iot', name: 'IoT Device Network', description: 'Distributed sensor system with edge computing' },
];

const metrics = [
  { id: 'completeness', label: 'Completeness', enabled: true },
  { id: 'accuracy', label: 'Accuracy', enabled: true },
  { id: 'time', label: 'Response Time', enabled: true },
  { id: 'cost', label: 'Cost per Analysis', enabled: false },
];

export default function ConfigPanel({ selectedScenario, onScenarioChange }: ConfigPanelProps) {
  return (
    <aside className="test-config-panel">
      <h3 className="heading-4 mb-5">Test Configuration</h3>
      
      <div className="control-group">
        <label className="control-label">Test Scenario</label>
        {scenarios.map(scenario => (
          <div
            key={scenario.id}
            className={`test-scenario ${selectedScenario === scenario.id ? 'active' : ''}`}
            onClick={() => onScenarioChange(scenario.id)}
          >
            <div className="scenario-title">{scenario.name}</div>
            <div className="scenario-desc">{scenario.description}</div>
          </div>
        ))}
      </div>
      
      <div className="control-group">
        <label className="control-label">Variants to Compare</label>
        <label className="checkbox-label">
          <input type="checkbox" defaultChecked />
          Variant A (Current Production)
        </label>
        <label className="checkbox-label">
          <input type="checkbox" defaultChecked />
          Variant B (Experimental)
        </label>
        <label className="checkbox-label">
          <input type="checkbox" />
          Variant C (High Temperature)
        </label>
      </div>
      
      <div className="control-group">
        <label className="control-label">Success Metrics</label>
        {metrics.map(metric => (
          <label key={metric.id} className="checkbox-label">
            <input type="checkbox" defaultChecked={metric.enabled} />
            {metric.label}
          </label>
        ))}
      </div>
    </aside>
  );
}