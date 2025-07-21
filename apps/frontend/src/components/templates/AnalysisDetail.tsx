import { useState } from 'react';
import { X, Edit2, Download } from 'lucide-react';
import './AnalysisDetail.css';

interface AnalysisDetailProps {
  title: string;
  data: Record<string, any>;
  onClose: () => void;
  onEdit?: (data: Record<string, any>) => void;
}

export function AnalysisDetail({ title, data, onClose, onEdit }: AnalysisDetailProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState(data);

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleSave = () => {
    setIsEditing(false);
    if (onEdit) {
      onEdit(editData);
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
    setEditData(data);
  };

  const handleExport = () => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${title.replace(/\s+/g, '-').toLowerCase()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const renderValue = (key: string, value: any) => {
    if (Array.isArray(value)) {
      return (
        <ul className="detail-list">
          {value.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>
      );
    }
    
    if (typeof value === 'object' && value !== null) {
      return (
        <div className="detail-object">
          {Object.entries(value).map(([k, v]) => (
            <div key={k} className="detail-nested">
              <span className="detail-key">{k}:</span>
              <span className="detail-value">{String(v)}</span>
            </div>
          ))}
        </div>
      );
    }
    
    return <span className="detail-value">{String(value)}</span>;
  };

  return (
    <div className="analysis-detail-overlay" onClick={onClose}>
      <div className="analysis-detail" onClick={(e) => e.stopPropagation()}>
        <div className="analysis-detail-header">
          <h2>{title}</h2>
          <div className="analysis-detail-actions">
            {onEdit && (
              <button onClick={handleEdit} className="icon-button" title="Edit">
                <Edit2 size={18} />
              </button>
            )}
            <button onClick={handleExport} className="icon-button" title="Export">
              <Download size={18} />
            </button>
            <button onClick={onClose} className="icon-button" title="Close">
              <X size={18} />
            </button>
          </div>
        </div>
        
        <div className="analysis-detail-content">
          {Object.entries(data).map(([key, value]) => (
            <div key={key} className="detail-row">
              <div className="detail-label">{key}:</div>
              <div className="detail-value-wrapper">
                {renderValue(key, value)}
              </div>
            </div>
          ))}
        </div>
        
        {isEditing && (
          <div className="analysis-detail-footer">
            <button onClick={handleSave} className="button button-primary">Save</button>
            <button onClick={handleCancel} className="button">Cancel</button>
          </div>
        )}
      </div>
    </div>
  );
}