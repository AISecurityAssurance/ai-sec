/**
 * STPA-Sec+ Orchestrator Panel
 * 
 * Main UI component for the STPA-Sec+ analysis orchestrator
 */

import React, { useState, useEffect } from 'react';
import { 
  StandardizedAnalysis, 
  AnalysisGap, 
  CrossFrameworkInsight,
  SynthesisResult 
} from '../types';
import { STPASecPlusPlugin } from '../index';
import './STPASecPlusPanel.css';

interface STPASecPlusPanelProps {
  projectId: string;
  onAnalysisComplete?: (result: any) => void;
}

export function STPASecPlusPanel({ projectId, onAnalysisComplete }: STPASecPlusPanelProps) {
  const [mode, setMode] = useState<'import' | 'native' | 'synthesis' | 'hybrid'>('import');
  const [importedAnalyses, setImportedAnalyses] = useState<StandardizedAnalysis[]>([]);
  const [synthesisResult, setSynthesisResult] = useState<SynthesisResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'gaps' | 'insights' | 'recommendations'>('overview');
  
  const plugin = new STPASecPlusPlugin();
  
  // Initialize plugin
  useEffect(() => {
    plugin.initialize({ analysisStore: {} });
  }, []);
  
  const handleFileImport = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    
    setIsAnalyzing(true);
    
    try {
      const content = await file.text();
      const data = JSON.parse(content);
      
      // Detect format and import
      const result = await plugin.analyze({
        mode: 'import',
        data,
        config: {
          format: detectFormat(file.name),
          file: file.name
        }
      });
      
      if (result.success && result.data) {
        setImportedAnalyses(prev => [...prev, result.data.imported]);
        
        // Auto-run synthesis after import
        await runSynthesis();
      }
    } catch (error) {
      console.error('Import failed:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };
  
  const runSynthesis = async () => {
    setIsAnalyzing(true);
    
    try {
      const result = await plugin.analyze({
        mode: 'synthesis',
        config: {}
      });
      
      if (result.success && result.data) {
        setSynthesisResult(result.data.synthesis);
        onAnalysisComplete?.(result.data);
      }
    } catch (error) {
      console.error('Synthesis failed:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };
  
  const detectFormat = (filename: string): string => {
    if (filename.endsWith('.tm7')) return 'microsoft-tmt';
    if (filename.endsWith('.csv')) return 'stride-csv';
    if (filename.endsWith('.json')) return 'custom-json';
    return 'unknown';
  };
  
  return (
    <div className="stpa-sec-plus-panel">
      {/* Header */}
      <div className="panel-header">
        <h2>STPA-Sec+ Analysis Orchestrator</h2>
        <p className="subtitle">Intelligent synthesis across security frameworks</p>
      </div>
      
      {/* Mode Selector */}
      <div className="mode-selector">
        <button 
          className={`mode-btn ${mode === 'import' ? 'active' : ''}`}
          onClick={() => setMode('import')}
        >
          Import & Synthesize
        </button>
        <button 
          className={`mode-btn ${mode === 'native' ? 'active' : ''}`}
          onClick={() => setMode('native')}
        >
          Native Analysis
        </button>
        <button 
          className={`mode-btn ${mode === 'hybrid' ? 'active' : ''}`}
          onClick={() => setMode('hybrid')}
        >
          Hybrid Approach
        </button>
      </div>
      
      {/* Import Section */}
      {mode === 'import' && (
        <div className="import-section">
          <h3>Import Existing Analyses</h3>
          <div className="import-options">
            <label className="file-upload">
              <input 
                type="file" 
                accept=".tm7,.csv,.json,.xml"
                onChange={handleFileImport}
                disabled={isAnalyzing}
              />
              <span className="upload-btn">
                <i className="icon-upload" /> Choose File
              </span>
            </label>
            
            <div className="supported-formats">
              <p>Supported formats:</p>
              <ul>
                <li>Microsoft Threat Modeling Tool (.tm7)</li>
                <li>STRIDE CSV (.csv)</li>
                <li>PASTA JSON (.json)</li>
                <li>NIST CSF Excel (.xlsx)</li>
              </ul>
            </div>
          </div>
          
          {/* Imported Analyses List */}
          {importedAnalyses.length > 0 && (
            <div className="imported-list">
              <h4>Imported Analyses ({importedAnalyses.length})</h4>
              {importedAnalyses.map((analysis, index) => (
                <div key={index} className="imported-item">
                  <span className="framework-badge">{analysis.framework}</span>
                  <span className="source">{analysis.metadata.source}</span>
                  <span className="confidence">
                    {Math.round(analysis.metadata.confidence * 100)}% confidence
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
      
      {/* Synthesis Results */}
      {synthesisResult && (
        <div className="synthesis-results">
          <div className="tabs">
            <button 
              className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
              onClick={() => setActiveTab('overview')}
            >
              Overview
            </button>
            <button 
              className={`tab ${activeTab === 'gaps' ? 'active' : ''}`}
              onClick={() => setActiveTab('gaps')}
            >
              Gaps ({synthesisResult.gaps.length})
            </button>
            <button 
              className={`tab ${activeTab === 'insights' ? 'active' : ''}`}
              onClick={() => setActiveTab('insights')}
            >
              Insights ({synthesisResult.insights.length})
            </button>
            <button 
              className={`tab ${activeTab === 'recommendations' ? 'active' : ''}`}
              onClick={() => setActiveTab('recommendations')}
            >
              Recommendations
            </button>
          </div>
          
          {/* Tab Content */}
          <div className="tab-content">
            {activeTab === 'overview' && (
              <OverviewTab synthesisResult={synthesisResult} />
            )}
            
            {activeTab === 'gaps' && (
              <GapsTab gaps={synthesisResult.gaps} />
            )}
            
            {activeTab === 'insights' && (
              <InsightsTab insights={synthesisResult.insights} />
            )}
            
            {activeTab === 'recommendations' && (
              <RecommendationsTab recommendations={synthesisResult.recommendations} />
            )}
          </div>
        </div>
      )}
      
      {/* Loading State */}
      {isAnalyzing && (
        <div className="loading-overlay">
          <div className="loading-spinner" />
          <p>Analyzing...</p>
        </div>
      )}
    </div>
  );
}

// Overview Tab Component
function OverviewTab({ synthesisResult }: { synthesisResult: SynthesisResult }) {
  const { metrics } = synthesisResult;
  
  return (
    <div className="overview-tab">
      <div className="metrics-grid">
        <div className="metric-card">
          <h4>Unified Risk Score</h4>
          <div className="metric-value">{Math.round(metrics.unifiedRiskScore)}</div>
          <div className="metric-label">out of 100</div>
        </div>
        
        <div className="metric-card">
          <h4>Analysis Completeness</h4>
          <div className="metric-value">{Math.round(metrics.completenessScore * 100)}%</div>
          <div className="metric-progress">
            <div 
              className="progress-fill" 
              style={{ width: `${metrics.completenessScore * 100}%` }}
            />
          </div>
        </div>
        
        <div className="metric-card">
          <h4>Confidence Level</h4>
          <div className="metric-value">{Math.round(metrics.confidenceLevel * 100)}%</div>
          <div className={`confidence-indicator ${getConfidenceClass(metrics.confidenceLevel)}`}>
            {getConfidenceLabel(metrics.confidenceLevel)}
          </div>
        </div>
      </div>
      
      <div className="coverage-map">
        <h4>Coverage Analysis</h4>
        <div className="coverage-grid">
          {Object.entries(metrics.coverageMap).map(([domain, coverage]) => (
            <div key={domain} className="coverage-item">
              <span className="domain">{domain}</span>
              <div className="coverage-bar">
                <div 
                  className="coverage-fill"
                  style={{ width: `${coverage * 100}%` }}
                />
              </div>
              <span className="coverage-percent">{Math.round(coverage * 100)}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Gaps Tab Component
function GapsTab({ gaps }: { gaps: AnalysisGap[] }) {
  const sortedGaps = [...gaps].sort((a, b) => {
    const severityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
    return severityOrder[a.severity] - severityOrder[b.severity];
  });
  
  return (
    <div className="gaps-tab">
      {sortedGaps.map(gap => (
        <div key={gap.id} className={`gap-card severity-${gap.severity}`}>
          <div className="gap-header">
            <span className="severity-badge">{gap.severity}</span>
            <span className="gap-type">{gap.type.replace(/_/g, ' ')}</span>
          </div>
          
          <p className="gap-description">{gap.description}</p>
          
          <div className="gap-details">
            <div className="detail-item">
              <strong>Business Impact:</strong> {gap.businessImpact}
            </div>
            
            <div className="detail-item">
              <strong>Recommendation:</strong> {gap.recommendation}
            </div>
            
            <div className="detail-item">
              <strong>Effort:</strong> {gap.estimatedEffort}
            </div>
            
            {gap.affectedEntities && gap.affectedEntities.length > 0 && (
              <div className="affected-entities">
                <strong>Affected:</strong>
                {gap.affectedEntities.map(entity => (
                  <span key={entity} className="entity-tag">{entity}</span>
                ))}
              </div>
            )}
          </div>
          
          <button className="action-btn">
            Fill Gap with {gap.suggestedFramework || 'Analysis'}
          </button>
        </div>
      ))}
    </div>
  );
}

// Insights Tab Component
function InsightsTab({ insights }: { insights: CrossFrameworkInsight[] }) {
  return (
    <div className="insights-tab">
      {insights.map(insight => (
        <div key={insight.id} className="insight-card">
          <div className="insight-header">
            <span className={`severity-badge severity-${insight.severity}`}>
              {insight.severity}
            </span>
            <div className="frameworks">
              {insight.frameworks.map(fw => (
                <span key={fw} className="framework-tag">{fw}</span>
              ))}
            </div>
          </div>
          
          <p className="insight-description">{insight.description}</p>
          
          <div className="insight-details">
            <div className="detail-row">
              <span className="label">Business Value:</span>
              <span className="value">{insight.businessValue}</span>
            </div>
            
            <div className="detail-row">
              <span className="label">Effort:</span>
              <span className={`effort-badge effort-${insight.effort}`}>
                {insight.effort}
              </span>
            </div>
            
            <div className="detail-row">
              <span className="label">Actionability:</span>
              <span className={`action-badge action-${insight.actionability}`}>
                {insight.actionability}
              </span>
            </div>
          </div>
          
          <div className="recommendation">
            <strong>Recommendation:</strong> {insight.recommendation}
          </div>
        </div>
      ))}
    </div>
  );
}

// Recommendations Tab Component
function RecommendationsTab({ recommendations }: { recommendations: any[] }) {
  return (
    <div className="recommendations-tab">
      {recommendations.map((rec, index) => (
        <div key={index} className={`recommendation-card priority-${rec.priority}`}>
          <div className="rec-header">
            <span className="priority">Priority {rec.priority}</span>
            <span className="type">{rec.type.replace(/_/g, ' ')}</span>
          </div>
          
          <h4>{rec.action}</h4>
          
          <p className="rationale">{rec.rationale}</p>
          
          <div className="rec-details">
            <div className="impact">
              <strong>Impact:</strong> {rec.impact}
            </div>
            
            <div className="effort">
              <strong>Effort:</strong> {rec.effort}
            </div>
            
            {rec.framework && (
              <div className="framework">
                <strong>Framework:</strong> {rec.framework}
              </div>
            )}
          </div>
          
          <button className="implement-btn">Implement</button>
        </div>
      ))}
    </div>
  );
}

// Helper functions
function getConfidenceClass(confidence: number): string {
  if (confidence >= 0.8) return 'high';
  if (confidence >= 0.6) return 'medium';
  return 'low';
}

function getConfidenceLabel(confidence: number): string {
  if (confidence >= 0.8) return 'High Confidence';
  if (confidence >= 0.6) return 'Medium Confidence';
  return 'Low Confidence';
}