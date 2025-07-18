import { useState } from 'react';
import './CSATComponents.css';

interface FeedbackFormProps {
  onSubmit: (feedback: any) => void;
}

const aiConcerns = [
  {
    id: 'not-found',
    text: "404: Concern not found",
    subtext: "I'll still be needed to explain why the AI's security recommendations violate seventeen different compliance frameworks"
  },
  {
    id: 'accepted-fate',
    text: "About as worried as I am about users choosing strong passwords",
    subtext: "So basically, I've accepted my fate"
  },
  {
    id: 'human-dread',
    text: "AI can have my job when it learns to panic at 3 AM about a false positive",
    subtext: "Nothing beats the human touch of existential dread during incident response"
  },
  {
    id: 'executive-pain',
    text: "Bold of you to assume AI wants to deal with explaining security to executives",
    subtext: "Some jobs are punishment enough"
  },
  {
    id: 'coffee-cynicism',
    text: "I'm safe until AI develops the ability to drink coffee and mutter about legacy systems",
    subtext: "The day it masters cynicism is the day I update my resume"
  }
];

export default function FeedbackForm({ onSubmit }: FeedbackFormProps) {
  const [correctnessScore, setCorrectnessScore] = useState<number | null>(null);
  const [coverageScore, setCoverageScore] = useState<number | null>(null);
  const [timeSavingScore, setTimeSavingScore] = useState<number | null>(null);
  const [selectedConcerns, setSelectedConcerns] = useState<string[]>([]);
  const [feedback, setFeedback] = useState('');
  const [featureRequests, setFeatureRequests] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      correctnessScore,
      coverageScore,
      timeSavingScore,
      aiConcerns: selectedConcerns,
      feedback,
      featureRequests: featureRequests.split('\n').filter(f => f.trim()),
    });
  };

  const toggleConcern = (concernId: string) => {
    setSelectedConcerns(prev => 
      prev.includes(concernId) 
        ? prev.filter(id => id !== concernId)
        : [...prev, concernId]
    );
  };

  const renderScoreSelector = (
    label: string,
    description: string,
    value: number | null,
    onChange: (value: number) => void
  ) => {
    return (
      <div className="score-section">
        <h4 className="score-label">{label}</h4>
        <p className="score-description">{description}</p>
        <div className="score-selector">
          <div className="score-track">
            {[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100].map(score => (
              <button
                key={score}
                type="button"
                className={`score-marker ${value === score ? 'selected' : ''}`}
                onClick={() => onChange(score)}
                title={`${score}%`}
              >
                <span className="score-value">{score}</span>
              </button>
            ))}
          </div>
          <div className="score-labels">
            <span>0%</span>
            <span>50%</span>
            <span>100%</span>
          </div>
        </div>
        {value !== null && (
          <div className="selected-score">
            Selected: <strong>{value}%</strong>
          </div>
        )}
      </div>
    );
  };

  return (
    <form className="feedback-form" onSubmit={handleSubmit}>
      <div className="form-section">
        <h3 className="heading-4">How Well Did We Do?</h3>
        <p className="section-intro">As a security analyst, help us understand how our AI analysis compares to your expertise.</p>
        
        {renderScoreSelector(
          "Is the analysis correct?",
          "How accurate are the security findings compared to what you would identify?",
          correctnessScore,
          setCorrectnessScore
        )}
        
        {renderScoreSelector(
          "Does the analysis cover everything?",
          "Did we catch all the security issues you would have found?",
          coverageScore,
          setCoverageScore
        )}
        
        {renderScoreSelector(
          "Does this tool save time?",
          "Compared to manual analysis, how much time does this save you?",
          timeSavingScore,
          setTimeSavingScore
        )}
      </div>
      
      <div className="form-section ai-concerns-section">
        <h3 className="heading-4">🤖 The Million Dollar Question</h3>
        <p className="section-intro">How concerned are you about AI taking over your job? (Select all that apply)</p>
        
        <div className="concern-options">
          {aiConcerns.map(concern => (
            <div
              key={concern.id}
              className={`concern-option ${selectedConcerns.includes(concern.id) ? 'selected' : ''}`}
              onClick={() => toggleConcern(concern.id)}
            >
              <div className="concern-checkbox">
                {selectedConcerns.includes(concern.id) && '✓'}
              </div>
              <div className="concern-content">
                <div className="concern-text">{concern.text}</div>
                <div className="concern-subtext">{concern.subtext}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      <div className="form-section">
        <h3 className="heading-4">Tell Us More</h3>
        
        <div className="form-group">
          <label>Additional Feedback</label>
          <textarea
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="What specific aspects worked well? What missed the mark?"
            rows={4}
            className="input"
          />
        </div>
        
        <div className="form-group">
          <label>Feature Requests</label>
          <textarea
            value={featureRequests}
            onChange={(e) => setFeatureRequests(e.target.value)}
            placeholder="What would make this tool indispensable for your security analysis workflow? (one per line)"
            rows={3}
            className="input"
          />
        </div>
      </div>
      
      <button type="submit" className="btn btn-primary btn-lg">
        Submit Feedback
      </button>
    </form>
  );
}