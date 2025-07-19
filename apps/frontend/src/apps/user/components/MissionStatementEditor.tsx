import { useState, useEffect, useRef } from 'react';
import { AlertCircle, X } from 'lucide-react';
import './MissionStatementEditor.css';

interface MissionStatementEditorProps {
  purpose: string;
  method: string;
  goals: string[];
  onChange: (data: { purpose: string; method: string; why?: string }) => void;
  onClick?: () => void;
  isEditing?: boolean;
  onReset?: () => void;
  onValidationChange?: (isValid: boolean) => void;
}

export default function MissionStatementEditor({
  purpose,
  method,
  goals,
  onChange,
  onClick,
  isEditing = false,
  onReset,
  onValidationChange
}: MissionStatementEditorProps) {
  const [fullText, setFullText] = useState('');
  const [parseError, setParseError] = useState('');
  const [parsedData, setParsedData] = useState<{ purpose: string; method: string; why: string } | null>(null);
  const [isResetting, setIsResetting] = useState(false);
  const [resetCounter, setResetCounter] = useState(0);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const highlightRef = useRef<HTMLDivElement>(null);
  const originalTextRef = useRef<string>('');
  const originalDataRef = useRef<{ purpose: string; method: string; goals: string[] } | undefined>(undefined);

  // Initialize full text from components
  useEffect(() => {
    // Don't update if we're in the middle of resetting
    if (isResetting) {
      setIsResetting(false);
      return;
    }
    
    const goalsText = goals.join(', ');
    const text = `A system to ${purpose} by means of ${method} in order to ${goalsText}`;
    setFullText(text);
    
    // Also initialize original data on mount
    if (!originalDataRef.current) {
      originalDataRef.current = { purpose, method, goals };
      originalTextRef.current = text;
    }
  }, [purpose, method, goals, resetCounter]);

  // Track original text when entering edit mode
  useEffect(() => {
    if (isEditing) {
      const goalsText = goals.join(', ');
      const text = `A system to ${purpose} by means of ${method} in order to ${goalsText}`;
      originalTextRef.current = text;
      originalDataRef.current = { purpose, method, goals };
      // Clear any lingering errors when entering edit mode
      setParseError('');
      onValidationChange?.(true);
    }
  }, [isEditing]);

  const parseMissionStatement = (text: string) => {
    setParseError('');
    
    // Pattern 1: Full pattern with "in order to"
    const fullPattern = /^.*?A system to\s+(.+?)\s+by means of\s+(.+?)\s+in order to\s+(.+)$/i;
    const fullMatch = text.match(fullPattern);
    
    if (fullMatch) {
      const [, parsedPurpose, parsedMethod, parsedWhy] = fullMatch;
      const data = {
        purpose: parsedPurpose.trim(),
        method: parsedMethod.trim(),
        why: parsedWhy.trim()
      };
      setParsedData(data);
      onValidationChange?.(true);
      return data;
    }
    
    // Pattern 2: Without "in order to"
    const simplePattern = /^.*?A system to\s+(.+?)\s+by means of\s+(.+)$/i;
    const simpleMatch = text.match(simplePattern);
    
    if (simpleMatch) {
      const [, parsedPurpose, parsedMethod] = simpleMatch;
      const data = {
        purpose: parsedPurpose.trim(),
        method: parsedMethod.trim(),
        why: ''
      };
      setParsedData(data);
      onValidationChange?.(true);
      return data;
    }
    
    // Pattern 3: Try to extract purpose if text starts correctly
    if (text.toLowerCase().startsWith('a system to')) {
      setParseError('Please use the format: "A system to [PURPOSE] by means of [METHOD] in order to [GOALS]"');
    } else {
      setParseError('Mission statement must start with "A system to..."');
    }
    
    setParsedData(null);
    onValidationChange?.(false);
    return null;
  };

  const getHighlightedText = (text: string) => {
    // Pattern to match the full mission statement structure
    const fullPattern = /^(.*?)(A system to)\s+(.*?)\s+(by means of)\s+(.*?)(\s+in order to\s+(.*))?$/i;
    const match = text.match(fullPattern);
    
    if (match) {
      const [, , aSystemTo, purpose, byMeans, method, inOrderTo, why] = match;
      return (
        <>
          <span>{aSystemTo} </span>
          <span className="highlight-purpose">{purpose}</span>
          <span> {byMeans} </span>
          <span className="highlight-method">{method}</span>
          {inOrderTo && (
            <>
              <span>{inOrderTo.replace(why || '', '')}</span>
              <span className="highlight-why">{why}</span>
            </>
          )}
        </>
      );
    }
    
    // If no match, return plain text
    return <span>{text}</span>;
  };

  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const text = e.target.value;
    setFullText(text);
    
    // Always parse for display purposes
    const parsed = parseMissionStatement(text);
    
    // Auto-save parsed data when text changes - only if successfully parsed
    if (parsed) {
      onChange(parsed);
    }
    
    // Sync scroll position between textarea and highlight overlay
    if (highlightRef.current && textareaRef.current) {
      highlightRef.current.scrollTop = textareaRef.current.scrollTop;
      highlightRef.current.scrollLeft = textareaRef.current.scrollLeft;
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Special handling for space at the end
    if (e.key === ' ' && textareaRef.current) {
      const start = textareaRef.current.selectionStart;
      const end = textareaRef.current.selectionEnd;
      
      // If cursor is at the end
      if (start === fullText.length && end === fullText.length) {
        e.preventDefault();
        const newText = fullText + ' ';
        setFullText(newText);
        
        // Parse and save
        const parsed = parseMissionStatement(newText);
        if (parsed) {
          onChange(parsed);
        }
        
        // Restore cursor position
        setTimeout(() => {
          if (textareaRef.current) {
            textareaRef.current.selectionStart = start + 1;
            textareaRef.current.selectionEnd = start + 1;
          }
        }, 0);
      }
    }
  };

  const handleScroll = () => {
    if (highlightRef.current && textareaRef.current) {
      highlightRef.current.scrollTop = textareaRef.current.scrollTop;
      highlightRef.current.scrollLeft = textareaRef.current.scrollLeft;
    }
  };

  const handleCancel = () => {
    // Always clear errors and reset internal state
    setParseError('');
    setParsedData(null);
    setIsResetting(true);
    onValidationChange?.(true); // Reset is always valid
    
    if (onReset) {
      // Use parent's reset function if provided
      onReset();
      // Also reset the full text to original
      setFullText(originalTextRef.current);
    } else {
      // Fallback to internal reset logic
      // Reset to original text immediately
      setFullText(originalTextRef.current);
      
      // Force update the parent component with original values
      if (originalDataRef.current) {
        const resetData = {
          purpose: originalDataRef.current.purpose,
          method: originalDataRef.current.method,
          why: originalDataRef.current.goals.join(', ')
        };
        onChange(resetData);
        
        // Increment reset counter to force re-render
        setResetCounter(prev => prev + 1);
      }
    }
  };

  if (!isEditing) {
    return (
      <div 
        className="mission-statement-display"
        onClick={onClick}
      >
        {fullText}
      </div>
    );
  }

  return (
    <div className="mission-statement-editor">
      <div className="editor-header">
        <div className="editor-help">
          <p>Format: A system to <span className="highlight-purpose">[PURPOSE]</span> by means of <span className="highlight-method">[METHOD]</span> in order to <span className="highlight-why">[GOALS]</span></p>
        </div>
        <button onClick={handleCancel} className="btn-cancel-all">
          <X size={16} />
          <span>Reset Mission Statement</span>
        </button>
      </div>
      
      <div className="textarea-container">
        <div 
          ref={highlightRef}
          className="highlight-overlay"
          aria-hidden="true"
        >
          <div className="highlight-content">
            {getHighlightedText(fullText)}
          </div>
        </div>
        <textarea
          ref={textareaRef}
          value={fullText}
          onChange={handleTextChange}
          onKeyDown={handleKeyDown}
          onScroll={handleScroll}
          className="mission-textarea"
          rows={4}
          placeholder="A system to [PURPOSE] by means of [METHOD] in order to [GOALS]"
          spellCheck={false}
        />
      </div>
      
      {parseError && (
        <div className="parse-error">
          <AlertCircle size={16} />
          <span>{parseError}</span>
        </div>
      )}
      
      {parsedData && (
        <div className="parsed-preview">
          <h4>Parsed Components:</h4>
          <div className="parsed-item">
            <label>Purpose (What):</label>
            <span className="highlight-purpose">{parsedData.purpose}</span>
          </div>
          <div className="parsed-item">
            <label>Method (How):</label>
            <span className="highlight-method">{parsedData.method}</span>
          </div>
          {parsedData.why && (
            <div className="parsed-item">
              <label>Goals (Why):</label>
              <span className="highlight-why">{parsedData.why}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}