import { useEffect } from 'react';
import { Check, AlertCircle, X } from 'lucide-react';
import './NotificationToast.css';

interface NotificationToastProps {
  message: string;
  type: 'success' | 'error' | 'info';
  onClose: () => void;
  duration?: number;
}

export default function NotificationToast({ 
  message, 
  type, 
  onClose, 
  duration = 3000 
}: NotificationToastProps) {
  useEffect(() => {
    const timer = setTimeout(onClose, duration);
    return () => clearTimeout(timer);
  }, [duration, onClose]);

  const icon = type === 'success' ? <Check size={16} /> : 
               type === 'error' ? <X size={16} /> : 
               <AlertCircle size={16} />;

  return (
    <div className={`notification-toast ${type}`}>
      <div className="toast-icon">{icon}</div>
      <div className="toast-message">{message}</div>
      <button className="toast-close" onClick={onClose}>
        <X size={14} />
      </button>
    </div>
  );
}