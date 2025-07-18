import { useState, useEffect } from 'react';
import { Edit2, Save, X, Plus, Trash2 } from 'lucide-react';
import EditableList from './EditableList';
import './SystemDescriptionEditor.css';

interface SystemDescriptionEditorProps {
  fullDescription: string;
  onChange: (description: string) => void;
  onClick?: () => void;
  isEditing?: boolean;
}

interface ParsedDescription {
  overview: string;
  components: string[];
}

export default function SystemDescriptionEditor({
  fullDescription,
  onChange,
  onClick,
  isEditing = false
}: SystemDescriptionEditorProps) {
  const [isLocalEdit, setIsLocalEdit] = useState(false);
  const [editedOverview, setEditedOverview] = useState('');
  const [editedComponents, setEditedComponents] = useState<string[]>([]);

  // Parse the description to extract overview and components
  const parseDescription = (text: string): ParsedDescription => {
    const consistsOfIndex = text.toLowerCase().indexOf('consists of:');
    
    if (consistsOfIndex !== -1) {
      const overview = text.substring(0, consistsOfIndex).trim();
      const componentsText = text.substring(consistsOfIndex + 12).trim();
      
      // Parse components - split by newlines and bullets
      const components = componentsText
        .split(/\n|(?=-)/)
        .map(c => c.replace(/^[-•]\s*/, '').trim())
        .filter(c => c.length > 0);
      
      return { overview, components };
    }
    
    // If no "consists of:" found, treat entire text as overview
    return { overview: text, components: [] };
  };

  // Initialize parsed data
  useEffect(() => {
    const parsed = parseDescription(fullDescription);
    setEditedOverview(parsed.overview);
    setEditedComponents(parsed.components);
  }, [fullDescription]);

  const handleSave = () => {
    // Reconstruct the full description
    let newDescription = editedOverview;
    
    if (editedComponents.length > 0) {
      if (!newDescription.toLowerCase().includes('consists of:')) {
        newDescription += '\n\nThe system consists of:';
      }
      newDescription += '\n' + editedComponents.map(c => `- ${c}`).join('\n');
    }
    
    onChange(newDescription);
    setIsLocalEdit(false);
  };

  const handleCancel = () => {
    const parsed = parseDescription(fullDescription);
    setEditedOverview(parsed.overview);
    setEditedComponents(parsed.components);
    setIsLocalEdit(false);
  };

  if (!isEditing && !isLocalEdit) {
    return (
      <div 
        className="system-description-display"
        onClick={onClick}
      >
        <div className="description-content">
          {fullDescription}
        </div>
      </div>
    );
  }

  return (
    <div className="system-description-editor">
      <div className="editor-section">
        <label>System Overview</label>
        <textarea
          value={editedOverview}
          onChange={(e) => setEditedOverview(e.target.value)}
          className="overview-textarea"
          rows={4}
          placeholder="Describe the overall system purpose and functionality..."
        />
      </div>

      <div className="editor-section">
        <label>System Components</label>
        <EditableList
          items={editedComponents}
          onUpdate={setEditedComponents}
          isEditMode={true}
          itemIcon="•"
          placeholder="Add a system component..."
        />
      </div>

      <div className="editor-actions">
        <button onClick={handleSave} className="btn-save">
          <Save size={16} />
          <span>Save Changes</span>
        </button>
        <button onClick={handleCancel} className="btn-cancel">
          <X size={16} />
          <span>Cancel</span>
        </button>
      </div>
    </div>
  );
}