import React, { useState } from 'react';
import { Edit2, X, Save, Download } from 'lucide-react';
import { getSectionUrl } from './utils';
import './AnalysisText.css';

interface AnalysisTextProps {
  id: string;
  title?: string;
  content: string;
  format?: 'plain' | 'markdown' | 'html';
  maxLength?: number;
  editable?: boolean;
  onSave?: (id: string, data: any) => void;
}

export function AnalysisText({
  id,
  title,
  content,
  format = 'plain',
  maxLength,
  editable = true,
  onSave
}: AnalysisTextProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [textContent, setTextContent] = useState(content);

  const handleEdit = () => setIsEditing(true);
  const handleCancel = () => {
    setIsEditing(false);
    setTextContent(content);
  };
  const handleSave = () => {
    if (onSave) onSave(id, { content: textContent });
    setIsEditing(false);
  };
  const handleExport = () => console.log('Export text:', id);

  return (
    <div className={`analysis-text-template ${isEditing ? 'editing' : ''}`}>
      <div className="text-header">
        {title && (
          <a 
            href={getSectionUrl(id)}
            className="text-title-link"
            onClick={(e) => e.preventDefault()}
          >
            <h4 className="text-title">{title}</h4>
          </a>
        )}
        {editable && (
          <div className="text-toolbar">
            {isEditing ? (
              <>
                <button 
                  className="toolbar-btn cancel" 
                  onClick={handleCancel}
                  title="Cancel changes"
                  aria-label="Cancel changes"
                >
                  <X size={16} />
                </button>
                <button 
                  className="toolbar-btn save" 
                  onClick={handleSave}
                  title="Save changes"
                  aria-label="Save changes"
                >
                  <Save size={16} />
                </button>
              </>
            ) : (
              <>
                <button 
                  className="toolbar-btn edit" 
                  onClick={handleEdit}
                  title="Edit text"
                  aria-label="Edit text"
                >
                  <Edit2 size={16} />
                </button>
                <button 
                  className="toolbar-btn export" 
                  onClick={handleExport}
                  title="Export text"
                  aria-label="Export text"
                >
                  <Download size={16} />
                </button>
              </>
            )}
          </div>
        )}
      </div>

      <div className="text-content">
        {isEditing ? (
          <textarea
            value={textContent}
            onChange={(e) => setTextContent(e.target.value)}
            maxLength={maxLength}
            className="text-editor"
            placeholder="Enter content..."
          />
        ) : (
          <div className={`text-display ${format}`}>{textContent}</div>
        )}
      </div>

      {isEditing && maxLength && (
        <div className="text-footer">
          <span className="char-count">
            {textContent.length} / {maxLength}
          </span>
        </div>
      )}
    </div>
  );
}