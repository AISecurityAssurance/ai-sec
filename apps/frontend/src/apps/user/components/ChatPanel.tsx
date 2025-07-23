import { useState, useRef, useEffect } from 'react';
import { Send, Paperclip, AlertCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { ChatMessage } from '@security-platform/types';
import { useAnalysisStore } from '../../../stores/analysisStore';
import { apiFetch } from '../../../config/api';
import './ChatPanel.css';

interface ChatPanelProps {
  projectId?: string;
  activeAnalysis: string;
  selectedElement?: { element: any; type: string } | null;
  analysisId?: string;
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
    case 'dread-threat':
      return [
        `🎯 Explain DREAD scores for ${element.threat}`,
        `🛡️ Detail mitigation for ${element.threat}`,
        `📊 Compare with similar ${element.category} threats`,
        `🔍 Show attack scenarios for ${element.threat}`
      ];
    case 'pasta-objective':
      return [
        `📊 Analyze impact of compromising ${element.name}`,
        `🔍 Show threats to ${element.name}`,
        `🛡️ Suggest controls for ${element.name}`,
        `🎯 Map ${element.name} to technical requirements`
      ];
    case 'pasta-scope':
      return [
        `🔍 Show vulnerabilities in ${element.name}`,
        `📊 Analyze attack surface of ${element.name}`,
        `🛡️ List security controls for ${element.name}`,
        `🔗 Show dependencies of ${element.name}`
      ];
    case 'pasta-threat-actor':
      return [
        `🎯 Detail capabilities of ${element.name}`,
        `📊 Show attack patterns for ${element.type}`,
        `🔍 List assets targeted by ${element.name}`,
        `🛡️ Suggest defenses against ${element.name}`
      ];
    case 'pasta-scenario':
      return [
        `📊 Explain attack path: ${element.name}`,
        `🎯 Detail impact of ${element.name}`,
        `🛡️ Show countermeasures for ${element.attackVector}`,
        `🔍 Find similar ${element.risk} risk scenarios`
      ];
    case 'pasta-risk':
      return [
        `📊 Explain risk calculation for ${element.asset}`,
        `🎯 Show all threats to ${element.asset}`,
        `🛡️ Prioritize mitigations for ${element.asset}`,
        `🔍 Compare with other ${element.priority} priority risks`
      ];
    case 'stride-threat':
      return [
        `🎯 Explain ${element.threatType} threat: ${element.description}`,
        `🛡️ Detail mitigations for ${element.component}`,
        `📊 Analyze attack vector: ${element.attackVector}`,
        `🔍 Show similar ${element.threatType} threats`
      ];
    case 'maestro-agent':
      return [
        `🤖 Explain ${element.name} capabilities and risks`,
        `🔍 Show all threats for ${element.name}`,
        `🛡️ List security controls for this ${element.type}`,
        `📊 Analyze trust level: ${element.trustLevel}`
      ];
    case 'maestro-threat':
      return [
        `⚠️ Explain ${element.category} threat: ${element.threat}`,
        `🎯 Detail attack scenario: ${element.scenario}`,
        `🛡️ Show mitigations and monitoring`,
        `📊 Analyze detection difficulty: ${element.detectionDifficulty}`
      ];
    case 'maestro-control':
      return [
        `🛡️ Explain how ${element.name} works`,
        `📊 Show effectiveness: ${element.effectiveness}`,
        `🔍 List covered agents`,
        `⚙️ Implementation details`
      ];
    case 'linddun-category':
      return [
        `📊 Explain ${element.name} privacy threats`,
        `🔍 Show all ${element.threatCount} threats in this category`,
        `🛡️ Best practices for ${element.name} mitigation`,
        `⚖️ GDPR implications of ${element.name}`
      ];
    case 'linddun-dataflow':
      return [
        `🔍 Analyze privacy risks in ${element.name}`,
        `📊 Show all threats for this data flow`,
        `⚖️ GDPR compliance for ${element.purpose}`,
        `🛡️ Recommend privacy controls`
      ];
    case 'linddun-threat':
      return [
        `⚠️ Explain ${element.category}: ${element.threat}`,
        `📊 Analyze privacy impact on ${element.affectedParties?.join(', ')}`,
        `🛡️ Detail mitigations for ${element.id}`,
        `⚖️ GDPR requirements for this threat`
      ];
    case 'linddun-control':
      return [
        `🛡️ How does ${element.name} protect privacy?`,
        `📊 Show ${element.effectiveness} effectiveness details`,
        `🔍 Which threats does this control mitigate?`,
        `⚙️ Implementation guide for ${element.type} control`
      ];
    case 'hazop-node':
      return [
        `🔍 Analyze deviations for ${element.name}`,
        `📊 Show all ${element.parameters?.length} parameters`,
        `⚠️ List critical deviations for this ${element.type}`,
        `🛡️ Recommend additional safeguards`
      ];
    case 'hazop-deviation':
      return [
        `⚠️ Explain ${element.guideWord} deviation: ${element.deviation}`,
        `📊 Analyze risk: ${element.severity} severity, ${element.likelihood} likelihood`,
        `🛡️ Detail safeguards and recommendations`,
        `🎯 Show all related action items`
      ];
    case 'hazop-action':
      return [
        `📋 Explain action: ${element.action}`,
        `🎯 Why is this ${element.priority} priority?`,
        `👤 Contact ${element.responsible} for status`,
        `📅 Impact if missed: ${element.dueDate}`
      ];
    case 'octave-asset':
      return [
        `🎯 Why is ${element.name} critical to operations?`,
        `🔍 Show all threats to this ${element.type}`,
        `📊 Analyze CIA requirements: C:${element.securityRequirements?.confidentiality} I:${element.securityRequirements?.integrity} A:${element.securityRequirements?.availability}`,
        `🛡️ Recommend additional protections`
      ];
    case 'octave-threat':
      return [
        `⚠️ Explain threat: ${element.actor} - ${element.outcome}`,
        `📊 Analyze ${element.source} threat probability`,
        `🎯 Detail impact across all categories`,
        `🛡️ Show control gaps and recommendations`
      ];
    case 'octave-vulnerability':
      return [
        `🔍 Explain ${element.type} vulnerability: ${element.description}`,
        `⚠️ Why is this ${element.severity} severity?`,
        `🎯 Which threats exploit this vulnerability?`,
        `🛡️ Remediation plan (effort: ${element.remediationEffort})`
      ];
    case 'octave-risk':
      return [
        `📊 Explain risk: ${element.description}`,
        `🎯 Why ${element.likelihood} likelihood, ${element.impact} impact?`,
        `🛡️ Detail ${element.strategy} strategy`,
        `📈 Analyze residual risk: ${element.residualRisk || 'Not assessed'}`
      ];
    case 'octave-strategy':
      return [
        `🛡️ How does ${element.name} protect assets?`,
        `📊 Why ${element.effectiveness} effectiveness?`,
        `💰 Justify ${element.cost} cost for ${element.timeframe}`,
        `🎯 Which assets benefit from this strategy?`
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

export default function ChatPanel({ projectId, activeAnalysis, selectedElement, analysisId: propAnalysisId }: ChatPanelProps) {
  // Get current analysis ID from store if not provided via props
  const currentAnalysisId = useAnalysisStore((state) => state.currentAnalysisId);
  const analysisId = propAnalysisId || currentAnalysisId;
  
  const isComparison = activeAnalysis === 'comparison';
  const suggestionChips = selectedElement 
    ? getElementSuggestions(selectedElement.element, selectedElement.type)
    : isComparison 
      ? comparisonSuggestions 
      : analysisSuggestions;
  
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load chat history on mount or when analysisId changes
  useEffect(() => {
    if (analysisId) {
      loadChatHistory();
    }
  }, [analysisId]);

  const loadChatHistory = async () => {
    if (!analysisId) return;
    
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await apiFetch(`/api/v1/chat/history?analysis_id=${analysisId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to load chat history: ${response.statusText}`);
      }

      const data = await response.json();
      
      // Convert the API response to our ChatMessage format
      const formattedMessages: ChatMessage[] = data.messages.map((msg: any) => ({
        id: msg.id,
        sessionId: 'session-1', // We'll use a static session for now
        role: msg.message ? 'user' : 'assistant',
        content: msg.message || msg.response,
        timestamp: new Date(msg.timestamp),
      }));

      setMessages(formattedMessages);
    } catch (err) {
      console.error('Error loading chat history:', err);
      setError('Failed to load chat history');
    } finally {
      setIsLoading(false);
    }
  };

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
      } else if (type === 'dread-threat') {
        const prompt = `Analyze ${element.id}: ${element.threat} (${element.category}, Risk: ${element.riskLevel})`;
        setInputValue(prompt);
      } else if (type.startsWith('pasta-')) {
        let prompt = '';
        switch (type) {
          case 'pasta-objective':
            prompt = `Analyze business objective: ${element.name} (Priority: ${element.priority})`;
            break;
          case 'pasta-scope':
            prompt = `Analyze technical component: ${element.name} (${element.type})`;
            break;
          case 'pasta-threat-actor':
            prompt = `Analyze threat actor: ${element.name} (${element.type}, Sophistication: ${element.sophistication})`;
            break;
          case 'pasta-scenario':
            prompt = `Analyze attack scenario: ${element.name} (${element.attackVector}, Risk: ${element.risk})`;
            break;
          case 'pasta-risk':
            prompt = `Analyze risk assessment for: ${element.asset} (Priority: ${element.priority}, Overall Risk: ${element.overallRisk})`;
            break;
        }
        setInputValue(prompt);
      } else if (type === 'stride-threat') {
        const prompt = `Analyze STRIDE threat ${element.id}: ${element.description} (${element.threatType} on ${element.component}, Risk: ${element.riskLevel})`;
        setInputValue(prompt);
      } else if (type === 'maestro-agent') {
        const prompt = `Analyze AI agent: ${element.name} (${element.type}, Trust Level: ${element.trustLevel})`;
        setInputValue(prompt);
      } else if (type === 'maestro-threat') {
        const prompt = `Analyze AI threat ${element.id}: ${element.threat} (${element.category}, Impact: ${element.impact})`;
        setInputValue(prompt);
      } else if (type === 'maestro-control') {
        const prompt = `Explain control ${element.id}: ${element.name} (${element.type}, Effectiveness: ${element.effectiveness})`;
        setInputValue(prompt);
      } else if (type === 'linddun-category') {
        const prompt = `Analyze LINDDUN category: ${element.name} (${element.threatCount} threats)`;
        setInputValue(prompt);
      } else if (type === 'linddun-dataflow') {
        const prompt = `Analyze data flow ${element.id}: ${element.name} (${element.source} → ${element.destination})`;
        setInputValue(prompt);
      } else if (type === 'linddun-threat') {
        const prompt = `Analyze privacy threat ${element.id}: ${element.threat} (${element.category}, Impact: ${element.privacyImpact})`;
        setInputValue(prompt);
      } else if (type === 'linddun-control') {
        const prompt = `Explain privacy control ${element.id}: ${element.name} (${element.type}, Effectiveness: ${element.effectiveness})`;
        setInputValue(prompt);
      } else if (type === 'hazop-node') {
        const prompt = `Analyze HAZOP node ${element.id}: ${element.name} (${element.type})`;
        setInputValue(prompt);
      } else if (type === 'hazop-deviation') {
        const prompt = `Analyze HAZOP deviation ${element.id}: ${element.guideWord} - ${element.deviation} (Risk: ${element.riskRating})`;
        setInputValue(prompt);
      } else if (type === 'hazop-action') {
        const prompt = `Review action ${element.id}: ${element.action} (Priority: ${element.priority}, Status: ${element.status})`;
        setInputValue(prompt);
      } else if (type === 'octave-asset') {
        const prompt = `Analyze critical asset ${element.id}: ${element.name} (${element.type}, Criticality: ${element.criticality})`;
        setInputValue(prompt);
      } else if (type === 'octave-threat') {
        const prompt = `Analyze threat ${element.id}: ${element.actor} - ${element.outcome} (Source: ${element.source})`;
        setInputValue(prompt);
      } else if (type === 'octave-vulnerability') {
        const prompt = `Analyze vulnerability ${element.id}: ${element.description} (${element.type}, Severity: ${element.severity})`;
        setInputValue(prompt);
      } else if (type === 'octave-risk') {
        const prompt = `Analyze risk ${element.id}: ${element.description} (Level: ${element.riskLevel}, Strategy: ${element.strategy})`;
        setInputValue(prompt);
      } else if (type === 'octave-strategy') {
        const prompt = `Explain strategy ${element.id}: ${element.name} (${element.type}, Status: ${element.status})`;
        setInputValue(prompt);
      } else {
        const prompt = `Tell me more about ${type.toUpperCase()} ${element.id}: ${element.description || element.name || ''}`;
        setInputValue(prompt);
      }
    }
  }, [selectedElement]);

  const handleSend = async () => {
    if (!inputValue.trim()) return;

    const messageContent = inputValue.trim();
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      sessionId: 'session-1',
      role: 'user',
      content: messageContent,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);
    setError(null);

    try {
      const response = await apiFetch('/api/v1/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: messageContent,
          analysis_id: analysisId || null,
        }),
      });

      if (!response.ok) {
        throw new Error(`Chat request failed: ${response.statusText}`);
      }

      const data = await response.json();
      
      const assistantMessage: ChatMessage = {
        id: data.id,
        sessionId: 'session-1',
        role: 'assistant',
        content: data.response,
        timestamp: new Date(data.timestamp),
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      console.error('Error sending message:', err);
      setError('Failed to send message. Please try again.');
      
      // Remove the user message on error
      setMessages(prev => prev.filter(msg => msg.id !== userMessage.id));
    } finally {
      setIsTyping(false);
    }
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
    <aside className="chat-panel" ref={panelRef}>
      <div className="chat-messages">
        {error && (
          <div className="chat-error">
            <AlertCircle size={16} />
            <span>{error}</span>
            <button onClick={() => setError(null)}>×</button>
          </div>
        )}
        {isLoading && (
          <div className="chat-loading">
            Loading chat history...
          </div>
        )}
        {messages.length === 0 && !isLoading && (
          <div className="suggestion-chips-container in-chat">
            <div className="message assistant">
              <div className="message-avatar">🤖</div>
              <div className="message-content">
                <p>
                  {isComparison 
                    ? 'Ready to help analyze the comparison results. Would you like to '
                    : 'Ready to help analyze your security findings. Would you like to '}
                  {suggestionChips.slice(0, 2).map((suggestion, idx) => {
                    const cleanSuggestion = suggestion.replace(/^[🔍⚠️🛡️🔌📊🎯⚡➡️⬅️❓🗑️✏️🔗🤖📋👤📅💰📈⚙️⚖️]\s*/, '');
                    return (
                      <span key={idx}>
                        <a 
                          href="#" 
                          className="suggestion-link"
                          onClick={(e) => {
                            e.preventDefault();
                            handleSuggestionClick(suggestion);
                          }}
                        >
                          {cleanSuggestion.toLowerCase()}
                        </a>
                        {idx === 0 ? ' or ' : ''}
                      </span>
                    );
                  })}
                  {' '}or ask me something else?
                </p>
              </div>
            </div>
          </div>
        )}
        {messages.map(message => (
              <div key={message.id} className={`message ${message.role}`}>
                {message.role === 'assistant' && (
                  <div className="message-avatar">🤖</div>
                )}
                <div className="message-content">
                  {message.role === 'assistant' ? (
                    <div className="markdown-content">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {message.content}
                      </ReactMarkdown>
                    </div>
                  ) : (
                    <p>{message.content}</p>
                  )}
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