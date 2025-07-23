import './LoadingOverlay.css';

interface LoadingOverlayProps {
  message?: string;
}

export default function LoadingOverlay({ message = 'Processing...' }: LoadingOverlayProps) {
  return (
    <div className="loading-overlay">
      <div className="loading-content">
        <div className="loading-spinner">
          <div className="spinner"></div>
        </div>
        <p className="loading-message">{message}</p>
      </div>
    </div>
  );
}