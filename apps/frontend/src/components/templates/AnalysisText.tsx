import React, { useState } from 'react';
import { Edit2, X, Save, Download } from 'lucide-react';
import { getSectionUrl } from './utils';
import './AnalysisText.css';

// Simple markdown to HTML converter
function renderMarkdown(text: string): string {
  return text
    // Headers
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
    // Bold
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // Lists
    .replace(/^\* (.+)/gm, '<li>$1</li>')
    .replace(/^\- (.+)/gm, '<li>$1</li>')
    .replace(/^\d+\. (.+)/gm, '<li>$1</li>')
    // Wrap lists
    .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
    // Line breaks
    .replace(/\n\n/g, '</p><p>')
    // Wrap in paragraphs
    .replace(/^([^<].*)$/gm, '<p>$1</p>')
    // Clean up
    .replace(/<p><\/p>/g, '')
    .replace(/<p>(<h[1-6]>)/g, '$1')
    .replace(/(<\/h[1-6]>)<\/p>/g, '$1');
}

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
          <div className={`text-display ${format}`}>
            {format === 'markdown' ? (
              <div dangerouslySetInnerHTML={{ __html: renderMarkdown(textContent) }} />
            ) : format === 'html' ? (
              <div dangerouslySetInnerHTML={{ __html: textContent }} />
            ) : (
              textContent
            )}
          </div>
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