import { useState } from 'react';
import './AdminComponents.css';

export default function ModelConfig() {
  const [temperature, setTemperature] = useState(3);
  const [maxTokens, setMaxTokens] = useState(4000);
  const [chunkSize, setChunkSize] = useState(2000);

  return (
    <div>
      <div className="config-section">
        <h3 className="heading-4 mb-6">Model Configuration</h3>
        
        <div className="control-group">
          <label className="control-label">
            <span>Temperature</span>
            <span className="control-value">{temperature / 10}</span>
          </label>
          <input
            type="range"
            className="slider"
            min="0"
            max="10"
            value={temperature}
            onChange={(e) => setTemperature(Number(e.target.value))}
          />
          <p className="help-text">Lower = more focused, Higher = more creative</p>
        </div>
        
        <div className="control-group">
          <label className="control-label">
            <span>Max Tokens</span>
            <span className="control-value">{maxTokens}</span>
          </label>
          <input
            type="range"
            className="slider"
            min="1000"
            max="8000"
            step="100"
            value={maxTokens}
            onChange={(e) => setMaxTokens(Number(e.target.value))}
          />
          <p className="help-text">Maximum response length</p>
        </div>
        
        <div className="control-group">
          <label className="control-label">
            <span>Chunk Size</span>
            <span className="control-value">{chunkSize}</span>
          </label>
          <input
            type="range"
            className="slider"
            min="500"
            max="4000"
            step="100"
            value={chunkSize}
            onChange={(e) => setChunkSize(Number(e.target.value))}
          />
          <p className="help-text">Document processing chunk size</p>
        </div>
      </div>
      
      <div className="config-section">
        <h3 className="heading-4 mb-6">Active Experiments</h3>
        <div className="experiments-grid">
          <div className="experiment-card">
            <h4>Temperature A/B Test</h4>
            <p className="text-sm text-secondary">Testing 0.1 vs 0.3 vs 0.5</p>
            <div className="progress-bar mt-3">
              <div className="progress-fill" style={{ width: '67%' }} />
            </div>
            <p className="text-xs text-secondary mt-2">2,341 / 3,500 samples</p>
          </div>
          <div className="experiment-card">
            <h4>Prompt Variation Test</h4>
            <p className="text-sm text-secondary">Chain-of-thought vs Direct</p>
            <div className="progress-bar mt-3">
              <div className="progress-fill" style={{ width: '45%' }} />
            </div>
            <p className="text-xs text-secondary mt-2">1,125 / 2,500 samples</p>
          </div>
        </div>
      </div>
    </div>
  );
}