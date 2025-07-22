import { useState } from 'react';
import { Save, Download, Upload, RotateCcw, ChevronRight, Key, Globe, Cpu, AlertCircle, Check } from 'lucide-react';
import SimpleLayout from '../../components/common/SimpleLayout';
import { useSettingsStore } from '../../stores/settingsStore';
import './SettingsApp.css';

type SettingsTab = 'general' | 'models' | 'tokens' | 'panels' | 'analysis';

export default function SettingsApp() {
  const [activeTab, setActiveTab] = useState<SettingsTab>('general');
  const {
    tokenEstimation,
    panels,
    analysis,
    general,
    models,
    updateTokenEstimation,
    updatePanelSettings,
    updateAnalysisSettings,
    updateGeneralSettings,
    updateModelSettings,
    updateProviderConfig,
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

  const renderModelSettings = () => {
    const providerInfo = {
      anthropic: { name: 'Anthropic (Claude)', icon: '🤖', supportsOAuth: true },
      openai: { name: 'OpenAI (GPT)', icon: '🧠', supportsOAuth: false },
      groq: { name: 'Groq', icon: '⚡', supportsOAuth: false },
      gemini: { name: 'Google Gemini', icon: '✨', supportsOAuth: true },
      ollama: { name: 'Ollama (Local)', icon: '🦙', supportsOAuth: false },
      custom: { name: 'Custom Provider', icon: '🔧', supportsOAuth: false }
    };

    return (
      <div className="settings-section">
        <h2>Model Settings</h2>
        
        <div className="setting-group">
          <label className="setting-label">
            <span>Active Provider</span>
            <p className="setting-description">
              Select the primary model provider for analysis
            </p>
          </label>
          <select
            value={models.activeProvider}
            onChange={(e) => updateModelSettings({ activeProvider: e.target.value as any })}
            className="setting-select"
          >
            {Object.entries(providerInfo).map(([key, info]) => (
              <option key={key} value={key} disabled={!models.providers[key as any].isEnabled}>
                {info.icon} {info.name} {!models.providers[key as any].isEnabled && '(Not configured)'}
              </option>
            ))}
          </select>
        </div>

        <div className="setting-group">
          <label className="setting-label">
            <span>Enable Fallback</span>
            <p className="setting-description">
              Automatically switch to backup providers if primary fails
            </p>
          </label>
          <label className="toggle-switch">
            <input
              type="checkbox"
              checked={models.enableFallback}
              onChange={(e) => updateModelSettings({ enableFallback: e.target.checked })}
            />
            <span className="toggle-slider"></span>
          </label>
        </div>

        <div className="setting-group">
          <label className="setting-label">
            <span>Stream Responses</span>
            <p className="setting-description">
              Show analysis results as they're generated
            </p>
          </label>
          <label className="toggle-switch">
            <input
              type="checkbox"
              checked={models.streamResponses}
              onChange={(e) => updateModelSettings({ streamResponses: e.target.checked })}
            />
            <span className="toggle-slider"></span>
          </label>
        </div>

        <div className="model-providers">
          <h3>Provider Configuration</h3>
          {Object.entries(providerInfo).map(([providerId, info]) => {
            const provider = models.providers[providerId as any];
            return (
              <div key={providerId} className="provider-config">
                <div className="provider-header">
                  <span className="provider-name">
                    {info.icon} {info.name}
                  </span>
                  {provider.isEnabled && <Check size={16} className="enabled-icon" />}
                </div>
                
                {provider.authMethod === 'api-key' && (
                  <div className="provider-field">
                    <label>API Key</label>
                    <input
                      type="password"
                      value={provider.apiKey || ''}
                      onChange={(e) => updateProviderConfig(providerId as any, { 
                        apiKey: e.target.value,
                        isEnabled: e.target.value.length > 0
                      })}
                      placeholder="Enter API key"
                      className="setting-input"
                    />
                  </div>
                )}
                
                {(providerId === 'ollama' || providerId === 'custom') && (
                  <div className="provider-field">
                    <label>API Endpoint</label>
                    <input
                      type="text"
                      value={provider.apiEndpoint || ''}
                      onChange={(e) => updateProviderConfig(providerId as any, { apiEndpoint: e.target.value })}
                      placeholder={providerId === 'ollama' ? 'http://localhost:11434' : 'https://api.example.com'}
                      className="setting-input"
                    />
                  </div>
                )}
                
                <div className="provider-field">
                  <label>Model</label>
                  <input
                    type="text"
                    value={provider.model || ''}
                    onChange={(e) => updateProviderConfig(providerId as any, { model: e.target.value })}
                    placeholder={provider.model || 'Default model'}
                    className="setting-input"
                  />
                </div>
                
                <div className="provider-field-row">
                  <div className="provider-field">
                    <label>Temperature</label>
                    <input
                      type="number"
                      value={provider.temperature || models.defaultTemperature}
                      onChange={(e) => updateProviderConfig(providerId as any, { temperature: parseFloat(e.target.value) })}
                      min="0"
                      max="1"
                      step="0.1"
                      className="setting-input small"
                    />
                  </div>
                  
                  <div className="provider-field">
                    <label>Max Tokens</label>
                    <input
                      type="number"
                      value={provider.maxTokens || models.defaultMaxTokens}
                      onChange={(e) => updateProviderConfig(providerId as any, { maxTokens: parseInt(e.target.value) })}
                      min="1"
                      max="32768"
                      step="1024"
                      className="setting-input small"
                    />
                  </div>
                </div>
                
                {info.supportsOAuth && (
                  <div className="provider-note">
                    <AlertCircle size={14} />
                    OAuth login support coming soon
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    );
  };


  return (
    <SimpleLayout>
      <div className="settings-page">
        <div className="settings-page-header">
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
              className={`settings-tab ${activeTab === 'models' ? 'active' : ''}`}
              onClick={() => setActiveTab('models')}
            >
              Models
            </button>
            <button
              className={`settings-tab ${activeTab === 'tokens' ? 'active' : ''}`}
              onClick={() => setActiveTab('tokens')}
            >
              Token Estimation
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
          {activeTab === 'models' && renderModelSettings()}
          {activeTab === 'tokens' && renderTokenSettings()}
          {activeTab === 'panels' && renderPanelSettings()}
          {activeTab === 'analysis' && renderAnalysisSettings()}
        </div>
      </div>
      </div>
    </SimpleLayout>
  );
}