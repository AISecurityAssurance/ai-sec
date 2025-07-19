import { useState } from 'react';
import SimpleLayout from '../../components/common/SimpleLayout';
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


  return (
    <SimpleLayout>
      <div className="csat-container">
        <div className="csat-tabs">
          <button 
            className={`csat-tab ${showForm ? 'active' : ''}`}
            onClick={() => setShowForm(true)}
          >
            Submit Feedback
          </button>
          <button 
            className={`csat-tab ${!showForm ? 'active' : ''}`}
            onClick={() => setShowForm(false)}
          >
            View Statistics
          </button>
        </div>
        
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
      </div>
    </SimpleLayout>
  );
}