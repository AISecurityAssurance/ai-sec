import { useState, useRef, useEffect } from 'react';
import { Send, Paperclip } from 'lucide-react';
import type { ChatMessage } from '@security-platform/types';
import './ChatPanel.css';

interface ChatPanelProps {
  projectId?: string;
  activeAnalysis: string;
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

export default function ChatPanel({ projectId, activeAnalysis }: ChatPanelProps) {
  const isComparison = activeAnalysis === 'comparison';
  const suggestionChips = isComparison ? comparisonSuggestions : analysisSuggestions;
  
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