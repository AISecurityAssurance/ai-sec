import React, { useState } from 'react';
import { Edit2, X, Save, Download } from 'lucide-react';
import './AnalysisDiagram.css';

interface AnalysisDiagramProps {
  id: string;
  title?: string;
  type?: 'flowchart' | 'chart' | 'diagram';
  children: React.ReactNode;
  editable?: boolean;
  onSave?: (id: string, data: any) => void;
}

export function AnalysisDiagram({
  id,
  title,
  type = 'diagram',
  children,
  editable = true,
  onSave
}: AnalysisDiagramProps) {
  const [isEditing, setIsEditing] = useState(false);

  const handleEdit = () => setIsEditing(true);
  const handleCancel = () => setIsEditing(false);
  const handleSave = () => {
    if (onSave) onSave(id, {});
    setIsEditing(false);
  };
  const handleExport = () => console.log('Export diagram:', id);

  return (
    <div className={`analysis-diagram-template ${isEditing ? 'editing' : ''}`}>
      <div className="diagram-header">
        {title && (
          <a 
            href={`/analysis/diagram/${id}`}
            className="diagram-title-link"
            onClick={(e) => e.preventDefault()}
          >
            <h4 className="diagram-title">{title}</h4>
          </a>
        )}
        {editable && (
          <div className="diagram-toolbar">
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
                  title="Edit diagram"
                  aria-label="Edit diagram"
                >
                  <Edit2 size={16} />
                </button>
                <button 
                  className="toolbar-btn export" 
                  onClick={handleExport}
                  title="Export diagram"
                  aria-label="Export diagram"
                >
                  <Download size={16} />
                </button>
              </>
            )}
          </div>
        )}
      </div>

      <div className="diagram-content">
        {children}
      </div>
    </div>
  );
}