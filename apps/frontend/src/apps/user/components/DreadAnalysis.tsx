import { useState } from 'react';
import { AlertTriangle, BarChart, Shield } from 'lucide-react';
import AnalysisTable from './AnalysisTable';
import { 
  dreadThreats, 
  threatCategories,
  getHighestRiskThreats,
  getRiskDistribution,
  getAverageRiskScore 
} from '../mockData/dreadData';
import './AnalysisPanel.css';

export default function DreadAnalysis() {
  const [selectedThreat, setSelectedThreat] = useState<any>(null);
  const [viewMode, setViewMode] = useState<'all' | 'category'>('all');
  
  const riskDistribution = getRiskDistribution();
  const avgScore = getAverageRiskScore();

  const renderScoreBar = (score: number, max: number = 3) => {
    const percentage = (score / max) * 100;
    const color = score === 3 ? 'var(--color-error)' : score === 2 ? 'var(--color-warning)' : 'var(--color-success)';
    
    return (
      <div className="score-bar">
        <div 
          className="score-fill" 
          style={{ 
            width: `${percentage}%`,
            backgroundColor: color
          }}
        />
        <span className="score-text">{score}/{max}</span>
      </div>
    );
  };

  const renderSummary = () => (
    <div className="dread-summary">
      <div className="summary-cards">
        <div className="summary-card">
          <h4>Total Threats</h4>
          <div className="summary-value">{dreadThreats.length}</div>
        </div>
        <div className="summary-card">
          <h4>Average Risk Score</h4>
          <div className="summary-value">{avgScore}</div>
        </div>
        <div className="summary-card critical">
          <h4>Critical Risks</h4>
          <div className="summary-value">{riskDistribution.Critical}</div>
        </div>
        <div className="summary-card high">
          <h4>High Risks</h4>
          <div className="summary-value">{riskDistribution.High}</div>
        </div>
      </div>
      
      <div className="risk-distribution">
        <h4>Risk Distribution</h4>
        <div className="distribution-bars">
          {Object.entries(riskDistribution).map(([level, count]) => (
            <div key={level} className="distribution-item">
              <span className="level-label">{level}</span>
              <div className="level-bar">
                <div 
                  className={`level-fill ${level.toLowerCase()}`}
                  style={{ height: `${(count / dreadThreats.length) * 100}%` }}
                />
              </div>
              <span className="level-count">{count}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderAllThreats = () => (
    <AnalysisTable
      title="All DREAD Threats"
      columns={[
        { key: 'id', label: 'ID', width: '80px' },
        { key: 'threat', label: 'Threat' },
        { key: 'category', label: 'Category', width: '120px' },
        { key: 'totalScore', label: 'Score', width: '80px' },
        { key: 'riskLevel', label: 'Risk', width: '80px' },
        { key: 'status', label: 'Status', width: '100px' },
      ]}
      data={dreadThreats}
      onRowSelect={setSelectedThreat}
      selectedRowId={selectedThreat?.id}
      getRowClassName={(row) => `risk-${row.riskLevel.toLowerCase()}`}
    />
  );

  const renderCategoryView = () => (
    <div className="category-view">
      {threatCategories.map(category => (
        <div key={category.name} className="threat-category">
          <h3>{category.name}</h3>
          <p className="category-description">{category.description}</p>
          <AnalysisTable
            columns={[
              { key: 'id', label: 'ID', width: '80px' },
              { key: 'threat', label: 'Threat' },
              { key: 'totalScore', label: 'Score', width: '80px' },
              { key: 'riskLevel', label: 'Risk', width: '80px' },
            ]}
            data={category.threats}
            onRowSelect={setSelectedThreat}
            selectedRowId={selectedThreat?.id}
            getRowClassName={(row) => `risk-${row.riskLevel.toLowerCase()}`}
          />
        </div>
      ))}
    </div>
  );

  const renderThreatDetails = () => {
    if (!selectedThreat) return null;
    
    const scores = selectedThreat.scores;
    
    return (
      <div className="threat-details">
        <h3>{selectedThreat.threat}</h3>
        <div className="detail-section">
          <h4>Description</h4>
          <p>{selectedThreat.description}</p>
        </div>
        
        <div className="detail-section">
          <h4>DREAD Scores</h4>
          <div className="dread-scores">
            <div className="score-item">
              <span className="score-label">Damage:</span>
              {renderScoreBar(scores.damage)}
            </div>
            <div className="score-item">
              <span className="score-label">Reproducibility:</span>
              {renderScoreBar(scores.reproducibility)}
            </div>
            <div className="score-item">
              <span className="score-label">Exploitability:</span>
              {renderScoreBar(scores.exploitability)}
            </div>
            <div className="score-item">
              <span className="score-label">Affected Users:</span>
              {renderScoreBar(scores.affectedUsers)}
            </div>
            <div className="score-item">
              <span className="score-label">Discoverability:</span>
              {renderScoreBar(scores.discoverability)}
            </div>
            <div className="score-item total">
              <span className="score-label">Total Score:</span>
              <span className={`total-score ${selectedThreat.riskLevel.toLowerCase()}`}>
                {selectedThreat.totalScore}/15
              </span>
            </div>
          </div>
        </div>
        
        <div className="detail-section">
          <h4>Mitigation</h4>
          <p>{selectedThreat.mitigation}</p>
        </div>
        
        <div className="detail-section">
          <h4>Status</h4>
          <span className={`status-badge ${selectedThreat.status}`}>
            {selectedThreat.status}
          </span>
        </div>
      </div>
    );
  };

  return (
    <div className="dread-analysis">
      <div className="analysis-header">
        <h2>DREAD Risk Assessment</h2>
        <p>Systematic threat rating using Damage, Reproducibility, Exploitability, Affected Users, and Discoverability</p>
      </div>
      
      {renderSummary()}
      
      <div className="view-controls">
        <button 
          className={`view-button ${viewMode === 'all' ? 'active' : ''}`}
          onClick={() => setViewMode('all')}
        >
          <BarChart size={16} />
          All Threats
        </button>
        <button 
          className={`view-button ${viewMode === 'category' ? 'active' : ''}`}
          onClick={() => setViewMode('category')}
        >
          <Shield size={16} />
          By Category
        </button>
      </div>
      
      <div className="dread-content">
        <div className="threats-section">
          {viewMode === 'all' ? renderAllThreats() : renderCategoryView()}
        </div>
        
        {selectedThreat && (
          <div className="details-section">
            {renderThreatDetails()}
          </div>
        )}
      </div>
    </div>
  );
}