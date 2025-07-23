import { ReactNode } from 'react';
import './LoadingOverlay.css';

interface LoadingOverlayProps {
  message?: string;
  children?: ReactNode;
}

export default function LoadingOverlay({ message = 'Processing...', children }: LoadingOverlayProps) {
  return (
    <div className="loading-overlay">
      {children ? (
        children
      ) : (
        <div className="loading-content">
          <div className="loading-spinner">
            <div className="spinner"></div>
          </div>
          <p className="loading-message">{message}</p>
        </div>
      )}
    </div>
  );
}