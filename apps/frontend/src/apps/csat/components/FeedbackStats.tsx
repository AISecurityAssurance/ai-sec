import './CSATComponents.css';

export default function FeedbackStats() {
  const stats = {
    totalResponses: 342,
    averageRatings: {
      overall: 4.3,
      accuracy: 4.5,
      completeness: 4.1,
      usability: 4.6,
    },
    npsScore: 72,
    topFeatureRequests: [
      { request: 'Export to PDF with diagrams', count: 89 },
      { request: 'Integration with GitHub', count: 67 },
      { request: 'Real-time collaboration', count: 45 },
      { request: 'Custom analysis templates', count: 38 },
    ],
    commonIssues: [
      { issue: 'Analysis timeout on large codebases', severity: 'high', reports: 23 },
      { issue: 'Chat context lost on page refresh', severity: 'medium', reports: 18 },
      { issue: 'Diagram export quality', severity: 'low', reports: 12 },
    ],
  };

  return (
    <div className="feedback-stats">
      <div className="stats-overview">
        <div className="stat-card">
          <div className="stat-value">{stats.totalResponses}</div>
          <div className="stat-label">Total Responses</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.averageRatings.overall}/5</div>
          <div className="stat-label">Average Rating</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.npsScore}</div>
          <div className="stat-label">NPS Score</div>
        </div>
      </div>
      
      <div className="stats-section">
        <h3 className="heading-4">Average Ratings</h3>
        <div className="ratings-grid">
          {Object.entries(stats.averageRatings).map(([category, rating]) => (
            <div key={category} className="rating-item">
              <div className="rating-label">
                {category.charAt(0).toUpperCase() + category.slice(1)}
              </div>
              <div className="rating-bar">
                <div 
                  className="rating-fill"
                  style={{ width: `${(rating / 5) * 100}%` }}
                />
              </div>
              <div className="rating-value">{rating}</div>
            </div>
          ))}
        </div>
      </div>
      
      <div className="stats-section">
        <h3 className="heading-4">Top Feature Requests</h3>
        <div className="feature-requests">
          {stats.topFeatureRequests.map((feature, idx) => (
            <div key={idx} className="feature-item">
              <span className="feature-rank">#{idx + 1}</span>
              <span className="feature-name">{feature.request}</span>
              <span className="feature-count">{feature.count} requests</span>
            </div>
          ))}
        </div>
      </div>
      
      <div className="stats-section">
        <h3 className="heading-4">Common Issues</h3>
        <div className="issues-list">
          {stats.commonIssues.map((issue, idx) => (
            <div key={idx} className="issue-item">
              <span className={`issue-severity ${issue.severity}`}>
                {issue.severity.toUpperCase()}
              </span>
              <span className="issue-description">{issue.issue}</span>
              <span className="issue-count">{issue.reports} reports</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}