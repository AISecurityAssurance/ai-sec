import { useState } from 'react';
import AppLayout from '../../components/common/AppLayout';
import FeedbackForm from './components/FeedbackForm';
import FeedbackStats from './components/FeedbackStats';
import './CSATApp.css';

export default function CSATApp() {
  const [showForm, setShowForm] = useState(true);
  const [submittedFeedback, setSubmittedFeedback] = useState(false);

  const handleSubmitFeedback = (feedback: any) => {
    console.log('Feedback submitted:', feedback);
    setSubmittedFeedback(true);
    setTimeout(() => {
      setSubmittedFeedback(false);
    }, 3000);
  };

  const header = (
    <header className="csat-header">
      <h1 className="heading-3">💬 Security Analysis Platform - Feedback</h1>
      <div className="header-tabs">
        <button 
          className={`tab-btn ${showForm ? 'active' : ''}`}
          onClick={() => setShowForm(true)}
        >
          Submit Feedback
        </button>
        <button 
          className={`tab-btn ${!showForm ? 'active' : ''}`}
          onClick={() => setShowForm(false)}
        >
          View Statistics
        </button>
      </div>
    </header>
  );

  return (
    <AppLayout header={header}>
      <div className="csat-content">
        {submittedFeedback && (
          <div className="success-banner">
            ✅ Thank you for your feedback! Your response has been recorded.
          </div>
        )}
        
        {showForm ? (
          <FeedbackForm onSubmit={handleSubmitFeedback} />
        ) : (
          <FeedbackStats />
        )}
      </div>
    </AppLayout>
  );
}