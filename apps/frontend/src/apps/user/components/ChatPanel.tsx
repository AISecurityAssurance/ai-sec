import { useState, useRef, useEffect } from 'react';
import { Send, Paperclip } from 'lucide-react';
import type { ChatMessage } from '@security-platform/types';
import './ChatPanel.css';

interface ChatPanelProps {
  projectId?: string;
  activeAnalysis: string;
  selectedElement?: { element: any; type: string } | null;
}

const analysisSuggestions = [
  '🔍 Explore financial breach scenarios',
  '⚠️ Show critical vulnerabilities',
  '🛡️ Suggest mitigations',
  '🔌 Focus on API security',
];

const comparisonSuggestions = [
  '📊 Summarize key differences',
  '🎯 Highlight critical findings',
  '⚡ Compare performance metrics',
  '🔍 Explain variant B improvements',
];

const getElementSuggestions = (element: any, type: string) => {
  switch (type) {
    case 'loss':
      return [
        `🔍 Show all hazards leading to ${element.id}`,
        `📊 Analyze impact on ${element.stakeholders?.[0] || 'stakeholders'}`,
        `🛡️ Suggest controls to prevent ${element.id}`,
        `🔗 Trace ${element.id} to causal scenarios`
      ];
    case 'hazard':
      return [
        `⚠️ Explain how ${element.id} occurs`,
        `📈 Show worst-case scenario for ${element.id}`,
        `🔍 Find all UCAs related to ${element.id}`,
        `🛡️ List mitigations for ${element.id}`
      ];
    case 'uca':
      return [
        `🎯 Show causal factors for ${element.id}`,
        `🔗 Trace ${element.id} to losses`,
        `📊 Analyze ${element.type} pattern`,
        `🛡️ Recommend controls for ${element.id}`
      ];
    case 'scenario':
      return [
        `📊 Explain attack path for ${element.id}`,
        `🎯 Show D4 analysis for ${element.id}`,
        `🛡️ Detail mitigations for ${element.id}`,
        `🔍 Find similar scenarios`
      ];
    case 'system-item':
      const itemType = element.type;
      if (itemType.startsWith('goal')) {
        return [
          `❓ Why is this a system goal?`,
          `🔍 Show related constraints`,
          `📊 Analyze goal achievement`,
          `✏️ Suggest goal refinements`
        ];
      } else if (itemType.startsWith('constraint')) {
        return [
          `❓ Why is this constraint necessary?`,
          `🔍 Show violations of this constraint`,
          `📊 Analyze constraint impact`,
          `✏️ Refine constraint wording`
        ];
      } else if (itemType.startsWith('boundary-included')) {
        return [
          `➡️ Move to excluded boundaries`,
          `❓ Why is this included?`,
          `🔍 Show dependencies`,
          `📊 Analyze security implications`
        ];
      } else if (itemType.startsWith('boundary-excluded')) {
        return [
          `⬅️ Move to included boundaries`,
          `❓ Why is this excluded?`,
          `🔍 Show potential risks`,
          `📊 Analyze if inclusion needed`
        ];
      } else if (itemType.startsWith('assumption')) {
        return [
          `❓ Validate this assumption`,
          `🗑️ Remove this assumption`,
          `✏️ Edit assumption text`,
          `📊 Analyze assumption risks`
        ];
      }
      return analysisSuggestions;
    default:
      return analysisSuggestions;
  }
};

export default function ChatPanel({ projectId, activeAnalysis, selectedElement }: ChatPanelProps) {
  const isComparison = activeAnalysis === 'comparison';
  const suggestionChips = selectedElement 
    ? getElementSuggestions(selectedElement.element, selectedElement.type)
    : isComparison 
      ? comparisonSuggestions 
      : analysisSuggestions;
  
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      sessionId: 'session-1',
      role: 'assistant',
      content: isComparison 
        ? 'Ready to help analyze the comparison results. I can summarize differences, explain findings, or answer questions about the variants.'
        : 'Ready to help analyze your security findings. Choose a suggestion below or ask me anything about the analysis.',
      timestamp: new Date(),
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [width, setWidth] = useState(350);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);
  const isResizing = useRef(false);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (selectedElement) {
      const { element, type } = selectedElement;
      if (type === 'system-item') {
        const itemType = element.type;
        if (itemType.startsWith('goal')) {
          setInputValue(`Why is "${element.description}" a system goal?`);
        } else if (itemType.startsWith('constraint')) {
          setInputValue(`Why do we have the constraint: "${element.description}"?`);
        } else if (itemType.startsWith('boundary-included')) {
          setInputValue(`Why is "${element.description}" included in the system boundary?`);
        } else if (itemType.startsWith('boundary-excluded')) {
          setInputValue(`Why is "${element.description}" excluded from the system boundary?`);
        } else if (itemType.startsWith('assumption')) {
          setInputValue(`Is this assumption valid: "${element.description}"?`);
        }
      } else {
        const prompt = `Tell me more about ${type.toUpperCase()} ${element.id}: ${element.description || element.name || ''}`;
        setInputValue(prompt);
      }
    }
  }, [selectedElement]);

  const handleMouseDown = (e: React.MouseEvent) => {
    isResizing.current = true;
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing.current) return;
      
      const newWidth = window.innerWidth - e.clientX;
      if (newWidth >= 300 && newWidth <= 600) {
        setWidth(newWidth);
      }
    };

    const handleMouseUp = () => {
      isResizing.current = false;
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, []);

  const handleSend = async () => {
    if (!inputValue.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      sessionId: 'session-1',
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    // Simulate assistant response
    setTimeout(() => {
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sessionId: 'session-1',
        role: 'assistant',
        content: `I understand you're asking about "${inputValue}". Let me analyze that in the context of your ${activeAnalysis} analysis...`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMessage]);
      setIsTyping(false);
    }, 1500);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInputValue(suggestion.replace(/^[🔍⚠️🛡️🔌]\s*/, ''));
  };

  return (
    <aside className="chat-panel" ref={panelRef} style={{ width: `${width}px` }}>
      <div className="resize-handle" onMouseDown={handleMouseDown} />
      
      <div className="chat-header">
        <h3 className="chat-title">Security Analyst</h3>
      </div>
      
      <div className="suggestion-chips-container">
        {suggestionChips.map((suggestion, idx) => (
          <button
            key={idx}
            className="chip"
            onClick={() => handleSuggestionClick(suggestion)}
          >
            {suggestion}
          </button>
        ))}
      </div>
      
      <div className="chat-messages">
        {messages.map(message => (
          <div key={message.id} className={`message ${message.role}`}>
            {message.role === 'assistant' && (
              <div className="message-avatar">🤖</div>
            )}
            <div className="message-content">
              <p>{message.content}</p>
            </div>
          </div>
        ))}
        {isTyping && (
          <div className="message assistant">
            <div className="message-avatar">🤖</div>
            <div className="message-content typing">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="chat-input">
        <div className="input-wrapper">
          <button className="attach-btn" title="Attach file">
            <Paperclip size={20} />
          </button>
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about the analysis or request refinements..."
            className="chat-input-field"
            rows={2}
          />
          <button 
            className="send-btn"
            onClick={handleSend}
            disabled={!inputValue.trim()}
          >
            <Send size={20} />
          </button>
        </div>
      </div>
    </aside>
  );
}