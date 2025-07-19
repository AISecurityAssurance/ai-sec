import { useState } from 'react';
import { Save, Download, Upload, RotateCcw, ChevronRight } from 'lucide-react';
import AppLayout from '../../components/common/AppLayout';
import { useSettingsStore } from '../../stores/settingsStore';
import { usePromptStore } from '../../stores/promptStore';
import './SettingsApp.css';

type SettingsTab = 'general' | 'tokens' | 'prompts' | 'panels' | 'analysis';

export default function SettingsApp() {
  const [activeTab, setActiveTab] = useState<SettingsTab>('general');
  const {
    tokenEstimation,
    panels,
    analysis,
    general,
    updateTokenEstimation,
    updatePanelSettings,
    updateAnalysisSettings,
    updateGeneralSettings,
    resetToDefaults,
    exportSettings,
    importSettings
  } = useSettingsStore();

  const handleExportSettings = () => {
    const settings = exportSettings();
    const blob = new Blob([settings], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `security-platform-settings-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleImportSettings = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        const success = importSettings(content);
        if (success) {
          alert('Settings imported successfully!');
        } else {
          alert('Failed to import settings. Please check the file format.');
        }
      };
      reader.readAsText(file);
    }
  };

  const renderGeneralSettings = () => (
    <div className="settings-section">
      <h2>General Settings</h2>
      
      <div className="setting-group">
        <label className="setting-label">
          <span>Demo Mode</span>
          <p className="setting-description">
            Enable demo mode to use mock data instead of real analysis
          </p>
        </label>
        <label className="toggle-switch">
          <input
            type="checkbox"
            checked={general.demoMode}
            onChange={(e) => updateGeneralSettings({ demoMode: e.target.checked })}
          />
          <span className="toggle-slider"></span>
        </label>
      </div>

      <div className="setting-group">
        <label className="setting-label">
          <span>Theme</span>
          <p className="setting-description">Choose your preferred color theme</p>
        </label>
        <select
          value={general.theme}
          onChange={(e) => updateGeneralSettings({ theme: e.target.value as 'light' | 'dark' | 'system' })}
          className="setting-select"
        >
          <option value="light">Light</option>
          <option value="dark">Dark</option>
          <option value="system">System</option>
        </select>
      </div>

      <div className="setting-group">
        <label className="setting-label">
          <span>Auto-save Interval</span>
          <p className="setting-description">
            How often to auto-save your work (in seconds)
          </p>
        </label>
        <input
          type="number"
          value={general.autoSaveInterval}
          onChange={(e) => updateGeneralSettings({ autoSaveInterval: parseInt(e.target.value) || 30 })}
          min="10"
          max="300"
          step="10"
          className="setting-input"
        />
      </div>
    </div>
  );

  const renderTokenSettings = () => (
    <div className="settings-section">
      <h2>Token Estimation Settings</h2>
      
      <div className="setting-group">
        <label className="setting-label">
          <span>Calculation Method</span>
          <p className="setting-description">
            How to estimate token count from content
          </p>
        </label>
        <select
          value={tokenEstimation.calculationMethod}
          onChange={(e) => updateTokenEstimation({ calculationMethod: e.target.value as any })}
          className="setting-select"
        >
          <option value="chars">Characters per Token</option>
          <option value="bytes">Bytes per Token</option>
          <option value="custom">Custom Tokenizer</option>
        </select>
      </div>

      {tokenEstimation.calculationMethod === 'chars' && (
        <div className="setting-group">
          <label className="setting-label">
            <span>Characters per Token</span>
            <p className="setting-description">
              Average number of characters per token (default: 4)
            </p>
          </label>
          <input
            type="number"
            value={tokenEstimation.charsPerToken}
            onChange={(e) => updateTokenEstimation({ charsPerToken: parseFloat(e.target.value) || 4 })}
            min="1"
            max="10"
            step="0.1"
            className="setting-input"
          />
        </div>
      )}

      {tokenEstimation.calculationMethod === 'bytes' && (
        <div className="setting-group">
          <label className="setting-label">
            <span>Bytes per Token</span>
            <p className="setting-description">
              Average number of bytes per token (default: 4)
            </p>
          </label>
          <input
            type="number"
            value={tokenEstimation.bytesPerToken}
            onChange={(e) => updateTokenEstimation({ bytesPerToken: parseFloat(e.target.value) || 4 })}
            min="1"
            max="10"
            step="0.1"
            className="setting-input"
          />
        </div>
      )}

      <div className="setting-group">
        <label className="setting-label">
          <span>Maximum Tokens</span>
          <p className="setting-description">
            Maximum allowed tokens for context window (default: 250,000)
          </p>
        </label>
        <input
          type="number"
          value={tokenEstimation.maxTokens}
          onChange={(e) => updateTokenEstimation({ maxTokens: parseInt(e.target.value) || 250000 })}
          min="1000"
          max="1000000"
          step="1000"
          className="setting-input"
        />
      </div>

      <div className="setting-group">
        <label className="setting-label">
          <span>Overflow Behavior</span>
          <p className="setting-description">
            What to do when context window is exceeded
          </p>
        </label>
        <select
          value={tokenEstimation.overflowBehavior}
          onChange={(e) => updateTokenEstimation({ overflowBehavior: e.target.value as any })}
          className="setting-select"
        >
          <option value="warn">Warn (show warning but allow)</option>
          <option value="block">Block (prevent selection)</option>
        </select>
      </div>
    </div>
  );

  const renderPanelSettings = () => (
    <div className="settings-section">
      <h2>Panel Layout Settings</h2>
      
      <div className="setting-group">
        <label className="setting-label">
          <span>Left Panel Width</span>
          <p className="setting-description">
            Default width percentage for Input/Plugin panel
          </p>
        </label>
        <input
          type="number"
          value={panels.leftPanelWidth}
          onChange={(e) => updatePanelSettings({ leftPanelWidth: parseInt(e.target.value) || 20 })}
          min="10"
          max="40"
          step="5"
          className="setting-input"
        />
        <span className="setting-suffix">%</span>
      </div>

      <div className="setting-group">
        <label className="setting-label">
          <span>Middle Panel Width</span>
          <p className="setting-description">
            Default width percentage for Analysis Canvas
          </p>
        </label>
        <input
          type="number"
          value={panels.middlePanelWidth}
          onChange={(e) => updatePanelSettings({ middlePanelWidth: parseInt(e.target.value) || 50 })}
          min="30"
          max="70"
          step="5"
          className="setting-input"
        />
        <span className="setting-suffix">%</span>
      </div>

      <div className="setting-group">
        <label className="setting-label">
          <span>Right Panel Width</span>
          <p className="setting-description">
            Default width percentage for SA Agent
          </p>
        </label>
        <input
          type="number"
          value={panels.rightPanelWidth}
          onChange={(e) => updatePanelSettings({ rightPanelWidth: parseInt(e.target.value) || 30 })}
          min="10"
          max="40"
          step="5"
          className="setting-input"
        />
        <span className="setting-suffix">%</span>
      </div>

      <div className="setting-note">
        Note: Total must equal 100%. Current total: {panels.leftPanelWidth + panels.middlePanelWidth + panels.rightPanelWidth}%
      </div>
    </div>
  );

  const renderAnalysisSettings = () => (
    <div className="settings-section">
      <h2>Analysis Settings</h2>
      
      <div className="setting-group">
        <label className="setting-label">
          <span>Auto-run Analysis</span>
          <p className="setting-description">
            Automatically run analysis when inputs are selected
          </p>
        </label>
        <label className="toggle-switch">
          <input
            type="checkbox"
            checked={analysis.autoRunAnalysis}
            onChange={(e) => updateAnalysisSettings({ autoRunAnalysis: e.target.checked })}
          />
          <span className="toggle-slider"></span>
        </label>
      </div>

      <div className="setting-group">
        <label className="setting-label">
          <span>Preserve Locked Sections</span>
          <p className="setting-description">
            Keep locked sections unchanged during re-analysis
          </p>
        </label>
        <label className="toggle-switch">
          <input
            type="checkbox"
            checked={analysis.preserveLockedSections}
            onChange={(e) => updateAnalysisSettings({ preserveLockedSections: e.target.checked })}
          />
          <span className="toggle-slider"></span>
        </label>
      </div>

      <div className="setting-group">
        <label className="setting-label">
          <span>Default Analysis Order</span>
          <p className="setting-description">
            Drag to reorder how analyses appear by default
          </p>
        </label>
        <div className="analysis-order-list">
          {analysis.defaultAnalysisOrder.map((analysisType, index) => (
            <div key={analysisType} className="analysis-order-item">
              <span className="order-number">{index + 1}</span>
              <span className="analysis-name">{analysisType.toUpperCase()}</span>
              <ChevronRight size={16} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderPromptsSettings = () => {
    const { templates, settings } = usePromptStore();
    
    return (
      <div className="settings-section">
        <h2>Prompt Settings</h2>
        
        <div className="setting-group">
          <label className="setting-label">
            <span>Temperature</span>
            <p className="setting-description">
              Controls randomness in responses (0 = deterministic, 1 = creative)
            </p>
          </label>
          <input
            type="number"
            value={settings.temperature}
            onChange={(e) => usePromptStore.getState().updateSettings({ temperature: parseFloat(e.target.value) || 0.7 })}
            min="0"
            max="1"
            step="0.1"
            className="setting-input"
          />
        </div>

        <div className="setting-group">
          <label className="setting-label">
            <span>Use Generated Artifacts</span>
            <p className="setting-description">
              Use outputs from one analysis as inputs for others
            </p>
          </label>
          <label className="toggle-switch">
            <input
              type="checkbox"
              checked={settings.useGeneratedArtifacts}
              onChange={(e) => usePromptStore.getState().updateSettings({ useGeneratedArtifacts: e.target.checked })}
            />
            <span className="toggle-slider"></span>
          </label>
        </div>

        <div className="setting-group">
          <label className="setting-label">
            <span>Prompt Templates</span>
            <p className="setting-description">
              Manage prompt templates for different analyses
            </p>
          </label>
          <div className="template-count">
            {templates.length} templates configured
          </div>
        </div>
      </div>
    );
  };

  const header = (
    <div className="settings-header">
      <h1>Settings</h1>
      <div className="header-actions">
        <button onClick={handleExportSettings} className="header-button">
          <Download size={20} />
          Export
        </button>
        <label className="header-button">
          <Upload size={20} />
          Import
          <input
            type="file"
            accept=".json"
            onChange={handleImportSettings}
            style={{ display: 'none' }}
          />
        </label>
        <button onClick={resetToDefaults} className="header-button">
          <RotateCcw size={20} />
          Reset
        </button>
      </div>
    </div>
  );

  return (
    <AppLayout header={header}>
      <div className="settings-container">
        <div className="settings-sidebar">
          <div className="settings-tabs">
            <button
              className={`settings-tab ${activeTab === 'general' ? 'active' : ''}`}
              onClick={() => setActiveTab('general')}
            >
              General
            </button>
            <button
              className={`settings-tab ${activeTab === 'tokens' ? 'active' : ''}`}
              onClick={() => setActiveTab('tokens')}
            >
              Token Estimation
            </button>
            <button
              className={`settings-tab ${activeTab === 'prompts' ? 'active' : ''}`}
              onClick={() => setActiveTab('prompts')}
            >
              Prompts
            </button>
            <button
              className={`settings-tab ${activeTab === 'panels' ? 'active' : ''}`}
              onClick={() => setActiveTab('panels')}
            >
              Panel Layout
            </button>
            <button
              className={`settings-tab ${activeTab === 'analysis' ? 'active' : ''}`}
              onClick={() => setActiveTab('analysis')}
            >
              Analysis
            </button>
          </div>
        </div>
        
        <div className="settings-content">
          {activeTab === 'general' && renderGeneralSettings()}
          {activeTab === 'tokens' && renderTokenSettings()}
          {activeTab === 'prompts' && renderPromptsSettings()}
          {activeTab === 'panels' && renderPanelSettings()}
          {activeTab === 'analysis' && renderAnalysisSettings()}
        </div>
      </div>
    </AppLayout>
  );
}