import { useState, useRef, useEffect } from 'react';
import { Check, X, Edit2 } from 'lucide-react';
import './EditableText.css';

interface EditableTextProps {
  text: string;
  onSave: (newText: string) => void;
  isEditing?: boolean;
  multiline?: boolean;
  placeholder?: string;
  className?: string;
  editIcon?: boolean;
}

export default function EditableText({
  text,
  onSave,
  isEditing: externalIsEditing = false,
  multiline = false,
  placeholder = 'Click to edit...',
  className = '',
  editIcon = true
}: EditableTextProps) {
  const [isEditing, setIsEditing] = useState(externalIsEditing);
  const [editValue, setEditValue] = useState(text);
  const [isHovered, setIsHovered] = useState(false);
  const inputRef = useRef<HTMLInputElement | HTMLTextAreaElement>(null);

  useEffect(() => {
    setIsEditing(externalIsEditing);
  }, [externalIsEditing]);

  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isEditing]);

  const handleSave = () => {
    if (editValue.trim() !== text) {
      onSave(editValue.trim());
    }
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditValue(text);
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !multiline) {
      e.preventDefault();
      handleSave();
    } else if (e.key === 'Escape') {
      handleCancel();
    }
  };

  if (isEditing) {
    return (
      <div className={`editable-text editing ${className}`}>
        {multiline ? (
          <textarea
            ref={inputRef as React.RefObject<HTMLTextAreaElement>}
            value={editValue}
            onChange={(e) => setEditValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            className="edit-input"
            rows={3}
          />
        ) : (
          <input
            ref={inputRef as React.RefObject<HTMLInputElement>}
            type="text"
            value={editValue}
            onChange={(e) => setEditValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            className="edit-input"
          />
        )}
        <div className="edit-actions">
          <button
            onClick={handleSave}
            className="btn-save"
            title="Save (Enter)"
          >
            <Check size={16} />
          </button>
          <button
            onClick={handleCancel}
            className="btn-cancel"
            title="Cancel (Esc)"
          >
            <X size={16} />
          </button>
        </div>
      </div>
    );
  }

  return (
    <div
      className={`editable-text ${className}`}
      onClick={() => setIsEditing(true)}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <span className="text-content">{text || placeholder}</span>
      {editIcon && isHovered && (
        <Edit2 size={14} className="edit-icon" />
      )}
    </div>
  );
}