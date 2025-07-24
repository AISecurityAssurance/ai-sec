import { useState, useEffect } from 'react';
import { Folder, File, ChevronRight, ChevronDown, Check, Minus } from 'lucide-react';
import { useSettingsStore, calculateTokens } from '../../stores/settingsStore';
import { useAnalysisStore } from '../../stores/analysisStore';
import './InputSelectionPanel.css';

interface FileNode {
  name: string;
  path: string;
  type: 'file' | 'directory';
  size?: number;
  children?: FileNode[];
  selected?: boolean;
  partiallySelected?: boolean;
  tokens?: number;
}

// Mock file structure - replace with actual file system integration
const mockFileStructure: FileNode[] = [
  {
    name: 'src',
    path: '/src',
    type: 'directory',
    children: [
      {
        name: 'components',
        path: '/src/components',
        type: 'directory',
        children: [
          { name: 'Header.tsx', path: '/src/components/Header.tsx', type: 'file', size: 2048 },
          { name: 'Footer.tsx', path: '/src/components/Footer.tsx', type: 'file', size: 1024 },
          { name: 'Navigation.tsx', path: '/src/components/Navigation.tsx', type: 'file', size: 3072 },
        ]
      },
      {
        name: 'utils',
        path: '/src/utils',
        type: 'directory',
        children: [
          { name: 'auth.ts', path: '/src/utils/auth.ts', type: 'file', size: 4096 },
          { name: 'api.ts', path: '/src/utils/api.ts', type: 'file', size: 5120 },
        ]
      },
      { name: 'App.tsx', path: '/src/App.tsx', type: 'file', size: 8192 },
      { name: 'index.tsx', path: '/src/index.tsx', type: 'file', size: 512 },
    ]
  },
  {
    name: 'docs',
    path: '/docs',
    type: 'directory',
    children: [
      { name: 'README.md', path: '/docs/README.md', type: 'file', size: 16384 },
      { name: 'API.md', path: '/docs/API.md', type: 'file', size: 8192 },
    ]
  },
  { name: 'package.json', path: '/package.json', type: 'file', size: 1024 },
  { name: 'tsconfig.json', path: '/tsconfig.json', type: 'file', size: 512 },
];

// Analysis plugin options
const analysisPlugins = [
  { id: 'stpa-sec', label: 'STPA-Sec' },
  { id: 'stride', label: 'STRIDE' },
  { id: 'pasta', label: 'PASTA' },
  { id: 'dread', label: 'DREAD' },
  { id: 'maestro', label: 'MAESTRO' },
  { id: 'linddun', label: 'LINDDUN' },
  { id: 'hazop', label: 'HAZOP' },
  { id: 'octave', label: 'OCTAVE' },
];

export default function InputSelectionPanel() {
  const { tokenEstimation } = useSettingsStore();
  const { enabledAnalyses, setEnabledAnalyses, demoMode, setDemoMode } = useAnalysisStore();
  const [fileTree, setFileTree] = useState<FileNode[]>(mockFileStructure);
  const [expandedPaths, setExpandedPaths] = useState<Set<string>>(new Set());
  const [totalTokens, setTotalTokens] = useState(0);
  const [selectedTokens, setSelectedTokens] = useState(0);
  const [inputSelectionExpanded, setInputSelectionExpanded] = useState(false);
  const [analysisPluginsExpanded, setAnalysisPluginsExpanded] = useState(false);

  // Toggle demo mode
  const toggleDemoMode = () => {
    const newDemoMode = !demoMode;
    setDemoMode(newDemoMode);
    
    // Dispatch custom event for AnalysisCanvas
    window.dispatchEvent(new CustomEvent('demoModeChanged', { 
      detail: { enabled: newDemoMode } 
    }));
  };

  // Toggle analysis plugin
  const toggleAnalysisPlugin = (pluginId: string) => {
    const newEnabledAnalyses = {
      ...enabledAnalyses,
      [pluginId]: !enabledAnalyses[pluginId]
    };
    setEnabledAnalyses(newEnabledAnalyses);
  };

  // Calculate tokens for a file
  const calculateFileTokens = (size: number): number => {
    // Simulate file content based on size
    const mockContent = 'x'.repeat(size);
    return calculateTokens(mockContent, tokenEstimation);
  };

  // Initialize token calculations
  useEffect(() => {
    const calculateTreeTokens = (nodes: FileNode[]): number => {
      return nodes.reduce((total, node) => {
        if (node.type === 'file' && node.size) {
          node.tokens = calculateFileTokens(node.size);
          return total + node.tokens;
        } else if (node.children) {
          return total + calculateTreeTokens(node.children);
        }
        return total;
      }, 0);
    };

    const total = calculateTreeTokens(fileTree);
    setTotalTokens(total);
  }, [fileTree, tokenEstimation]);

  // Calculate selected tokens
  useEffect(() => {
    const calculateSelectedTokens = (nodes: FileNode[]): number => {
      return nodes.reduce((total, node) => {
        if (node.type === 'file' && node.selected && node.tokens) {
          return total + node.tokens;
        } else if (node.children) {
          return total + calculateSelectedTokens(node.children);
        }
        return total;
      }, 0);
    };

    const selected = calculateSelectedTokens(fileTree);
    setSelectedTokens(selected);
  }, [fileTree]);

  const toggleExpanded = (path: string) => {
    setExpandedPaths(prev => {
      const newSet = new Set(prev);
      if (newSet.has(path)) {
        newSet.delete(path);
      } else {
        newSet.add(path);
      }
      return newSet;
    });
  };

  const updateNodeSelection = (nodes: FileNode[], path: string, selected: boolean): FileNode[] => {
    return nodes.map(node => {
      if (node.path === path) {
        const updatedNode = { ...node, selected };
        
        // If it's a directory, update all children
        if (node.type === 'directory' && node.children) {
          updatedNode.children = updateAllChildren(node.children, selected);
        }
        
        return updatedNode;
      } else if (node.children) {
        const updatedChildren = updateNodeSelection(node.children, path, selected);
        const hasSelectedChild = updatedChildren.some(child => 
          child.selected || child.partiallySelected
        );
        const allChildrenSelected = updatedChildren.every(child => 
          child.type === 'directory' ? child.selected && !child.partiallySelected : child.selected
        );
        
        return {
          ...node,
          children: updatedChildren,
          selected: allChildrenSelected,
          partiallySelected: hasSelectedChild && !allChildrenSelected
        };
      }
      return node;
    });
  };

  const updateAllChildren = (nodes: FileNode[], selected: boolean): FileNode[] => {
    return nodes.map(node => ({
      ...node,
      selected,
      partiallySelected: false,
      children: node.children ? updateAllChildren(node.children, selected) : undefined
    }));
  };

  const toggleSelection = (path: string, currentSelected: boolean) => {
    setFileTree(prev => updateNodeSelection(prev, path, !currentSelected));
  };

  const renderFileNode = (node: FileNode, depth: number = 0) => {
    const isExpanded = expandedPaths.has(node.path);
    const isOverLimit = selectedTokens > tokenEstimation.maxTokens;
    const wouldExceedLimit = node.tokens && 
      selectedTokens + node.tokens > tokenEstimation.maxTokens;

    return (
      <div key={node.path} className="file-node">
        <div 
          className={`file-node-content ${node.selected ? 'selected' : ''}`}
          style={{ paddingLeft: `${depth * 20 + 8}px` }}
        >
          {node.type === 'directory' && (
            <button
              className="expand-btn"
              onClick={() => toggleExpanded(node.path)}
            >
              {isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
            </button>
          )}
          
          <div className="checkbox-wrapper">
            <input
              type="checkbox"
              ref={(el) => {
                if (el) {
                  el.indeterminate = node.partiallySelected || false;
                }
              }}
              checked={node.selected || false}
              onChange={() => toggleSelection(node.path, node.selected || false)}
              disabled={!node.selected && wouldExceedLimit && tokenEstimation.overflowBehavior === 'block'}
            />
            {node.partiallySelected && <Minus size={12} className="partial-indicator" />}
          </div>
          
          <div className="file-icon">
            {node.type === 'directory' ? 
              <Folder size={16} /> : 
              <File size={16} />
            }
          </div>
          
          <span className="file-name">{node.name}</span>
          
          {node.tokens && (
            <span className={`token-count ${wouldExceedLimit && !node.selected ? 'warning' : ''}`}>
              {node.tokens.toLocaleString()} tokens
            </span>
          )}
        </div>
        
        {node.type === 'directory' && isExpanded && node.children && (
          <div className="file-children">
            {node.children.map(child => renderFileNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  const contextPercentage = (selectedTokens / tokenEstimation.maxTokens) * 100;
  const isWarning = contextPercentage > 80;
  const isError = contextPercentage > 100;

  return (
    <div className="input-selection-panel">
      {/* Context Window Progress Bar */}
      <div className="context-window-compact">
        <div className="context-bar-thin">
          <div 
            className={`context-fill-thin ${isError ? 'error' : isWarning ? 'warning' : ''}`}
            style={{ width: `${Math.min(contextPercentage, 100)}%` }}
          />
        </div>
        <div className="context-info-compact">
          {selectedTokens.toLocaleString()} / {tokenEstimation.maxTokens.toLocaleString()} tokens
        </div>
      </div>

      {/* Input Selection Section */}
      <div className="panel-section">
        <div 
          className="section-header-link"
          onClick={() => setInputSelectionExpanded(!inputSelectionExpanded)}
        >
          {inputSelectionExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
          <span className="section-title-link">Inputs</span>
        </div>
        
        {inputSelectionExpanded && (
          <div className="section-content">
            <div className="file-tree">
              {fileTree.map(node => renderFileNode(node))}
            </div>
          </div>
        )}
      </div>

      {/* Analysis Plugins Section */}
      <div className="panel-section">
        <div 
          className="section-header-link"
          onClick={() => setAnalysisPluginsExpanded(!analysisPluginsExpanded)}
        >
          {analysisPluginsExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
          <span className="section-title-link">Analysis Plugins</span>
          <span className="section-count">({Object.values(enabledAnalyses).filter(Boolean).length})</span>
        </div>
        
        {analysisPluginsExpanded && (
          <div className="section-content">
            <div className="analysis-plugins-list">
              {analysisPlugins.map(plugin => (
                <label key={plugin.id} className="analysis-plugin-item">
                  <input
                    type="checkbox"
                    checked={enabledAnalyses[plugin.id] || false}
                    onChange={() => toggleAnalysisPlugin(plugin.id)}
                  />
                  <a 
                    href={`/analysis/plugin/${plugin.id}`}
                    className="plugin-label-link"
                    onClick={(e) => e.preventDefault()}
                  >
                    <span className="plugin-label">{plugin.label}</span>
                  </a>
                </label>
              ))}
            </div>
          </div>
        )}
      </div>
      
      <div className="demo-mode-section">
        <button 
          className={`demo-mode-btn ${demoMode ? 'active' : ''}`}
          onClick={toggleDemoMode}
        >
          {demoMode ? 'Exit Sample Results' : 'View Sample Results'}
        </button>
        {demoMode && (
          <p className="demo-mode-hint">Viewing pre-populated sample analysis (no AI processing)</p>
        )}
      </div>
    </div>
  );
}