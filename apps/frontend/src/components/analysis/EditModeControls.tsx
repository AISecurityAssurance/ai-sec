import { Edit, Save, X, Download } from 'lucide-react';
import './EditModeControls.css';

interface EditModeControlsProps {
  editMode: boolean;
  onToggleEditMode: () => void;
  onSave: () => void;
  onCancel: () => void;
  onExport: (format: 'json' | 'pdf' | 'html') => void;
}

export default function EditModeControls({
  editMode,
  onToggleEditMode,
  onSave,
  onCancel,
  onExport
}: EditModeControlsProps) {
  return (
    <div className="edit-mode-controls">
      {editMode ? (
        <>
          <button className="control-btn save" onClick={onSave}>
            <Save size={18} />
            <span>Save Changes</span>
          </button>
          <button className="control-btn cancel" onClick={onCancel}>
            <X size={18} />
            <span>Cancel</span>
          </button>
        </>
      ) : (
        <>
          <button className="control-btn edit" onClick={onToggleEditMode}>
            <Edit size={18} />
            <span>Edit Mode</span>
          </button>
          <div className="export-dropdown">
            <button className="control-btn export">
              <Download size={18} />
              <span>Export</span>
            </button>
            <div className="export-menu">
              <button onClick={() => onExport('json')}>Export as JSON</button>
              <button onClick={() => onExport('pdf')}>Export as PDF</button>
              <button onClick={() => onExport('html')}>Export as HTML</button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}