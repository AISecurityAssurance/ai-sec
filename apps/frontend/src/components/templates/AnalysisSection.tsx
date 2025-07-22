import React, { useState } from 'react';
import { ChevronDown, ChevronRight, Edit2, X, Save, Download } from 'lucide-react';
import { getSectionUrl } from './utils';
import './AnalysisSection.css';

interface AnalysisSectionProps {
  id: string;
  title: string;
  icon?: React.ReactNode;
  level?: 1 | 2 | 3 | 4;
  collapsible?: boolean;
  defaultExpanded?: boolean;
  editable?: boolean;
  children: React.ReactNode;
  onSave?: (id: string, data: any) => void;
}

export function AnalysisSection({
  id,
  title,
  icon,
  level = 3,
  collapsible = true,
  defaultExpanded = false,
  editable = true,
  children,
  onSave
}: AnalysisSectionProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);
  const [isEditing, setIsEditing] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  const handleEdit = () => {
    setIsEditing(true);
    setHasChanges(false);
  };

  const handleCancel = () => {
    setIsEditing(false);
    setHasChanges(false);
  };

  const handleSave = () => {
    if (onSave) {
      onSave(id, {}); // In real implementation, would pass actual data
    }
    setIsEditing(false);
    setHasChanges(false);
  };

  const handleExport = () => {
    console.log('Export section:', id);
  };


  const HeadingTag = `h${level}` as keyof JSX.IntrinsicElements;

  return (
    <div className={`analysis-section-template ${isEditing ? 'editing' : ''}`}>
      <div className="section-header">
        {collapsible && (
          <button
            className="section-toggle"
            onClick={() => setIsExpanded(!isExpanded)}
            aria-label={isExpanded ? 'Collapse section' : 'Expand section'}
          >
            {isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
          </button>
        )}
        {icon && <span className="section-icon">{icon}</span>}
        <a 
          href={getSectionUrl(id)}
          className="section-title-link"
          onClick={(e) => e.preventDefault()}
        >
          <HeadingTag className="section-title">{title}</HeadingTag>
        </a>
        
        {editable && (
          <div className="section-toolbar">
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
                  disabled={!hasChanges}
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
                  title="Edit section"
                  aria-label="Edit section"
                >
                  <Edit2 size={16} />
                </button>
                <button 
                  className="toolbar-btn export" 
                  onClick={handleExport}
                  title="Export section"
                  aria-label="Export section"
                >
                  <Download size={16} />
                </button>
              </>
            )}
          </div>
        )}
      </div>
      
      {(!collapsible || isExpanded) && (
        <div className="section-content">
          {typeof children === 'function' ? children({ isEditing }) : children}
        </div>
      )}
    </div>
  );
}