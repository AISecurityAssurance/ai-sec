import { useState, useRef, useEffect } from 'react';
import { X } from 'lucide-react';
import './InlineTextEditor.css';

interface InlineTextEditorProps {
  text: string;
  onChange: (text: string) => void;
  onClick?: () => void;
  isEditing?: boolean;
  className?: string;
  minHeight?: string;
  componentName?: string;
}

export default function InlineTextEditor({
  text,
  onChange,
  onClick,
  isEditing = false,
  className = '',
  minHeight = '150px',
  componentName = 'Text'
}: InlineTextEditorProps) {
  const [isLocalEdit, setIsLocalEdit] = useState(false);
  const [editValue, setEditValue] = useState(text);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const originalValueRef = useRef<string>(text);

  useEffect(() => {
    setEditValue(text);
  }, [text]);

  // Track original value when entering edit mode
  useEffect(() => {
    if (isEditing) {
      originalValueRef.current = text;
    }
  }, [isEditing]);

  useEffect(() => {
    if ((isEditing || isLocalEdit) && textareaRef.current) {
      // Auto-resize textarea to fit content
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
      // Don't auto-focus when globally entering edit mode, only when this specific component is clicked
      if (isLocalEdit) {
        textareaRef.current.focus();
      }
    }
  }, [isEditing, isLocalEdit, editValue]);

  const handleCancel = () => {
    // Restore original value
    setEditValue(originalValueRef.current);
    onChange(originalValueRef.current);
    setIsLocalEdit(false);
  };

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setEditValue(e.target.value);
    onChange(e.target.value);  // Auto-save changes
    // Auto-resize
    e.target.style.height = 'auto';
    e.target.style.height = e.target.scrollHeight + 'px';
  };

  if (!isEditing && !isLocalEdit) {
    return (
      <div 
        className={`inline-text-display ${className}`}
        onClick={onClick}
        style={{ minHeight }}
      >
        <div className="text-content">
          {text}
        </div>
      </div>
    );
  }

  return (
    <div className={`inline-text-editor ${className}`}>
      <div className="editor-header">
        <button onClick={handleCancel} className="btn-cancel-all" title="Cancel changes">
          <X size={16} />
          <span>Reset {componentName}</span>
        </button>
      </div>
      <textarea
        ref={textareaRef}
        value={editValue}
        onChange={handleTextareaChange}
        className="edit-textarea"
        style={{ minHeight }}
      />
    </div>
  );
}