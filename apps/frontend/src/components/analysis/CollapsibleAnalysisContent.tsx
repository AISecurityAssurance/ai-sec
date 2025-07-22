import { useState } from 'react';
import { ChevronRight, ChevronDown, FileText, Users, AlertTriangle, ShieldAlert, GitBranch, Zap, Target, Shield } from 'lucide-react';
import CollapsibleTable from './CollapsibleTable';
import './CollapsibleAnalysisContent.css';

interface SubSection {
  id: string;
  label: string;
  icon: any;
}

interface CollapsibleAnalysisContentProps {
  analysisId: string;
  enabledAnalyses: Record<string, boolean>;
}

// Define subsections for each analysis type
const analysisSubsections: Record<string, SubSection[]> = {
  'stpa-sec': [
    { id: 'system-description', label: 'System Description', icon: FileText },
    { id: 'stakeholders', label: 'Stakeholders', icon: Users },
    { id: 'losses', label: 'Losses', icon: AlertTriangle },
    { id: 'hazards', label: 'Hazards/Vulnerabilities', icon: ShieldAlert },
    { id: 'control-diagram', label: 'Control Diagram', icon: GitBranch },
    { id: 'controllers', label: 'Controllers', icon: Users },
    { id: 'control-actions', label: 'Control Actions', icon: Zap },
    { id: 'ucas', label: 'Unsafe/Unsecure Control Actions', icon: Zap },
    { id: 'scenarios', label: 'Causal Scenarios', icon: Target },
    { id: 'wargaming', label: 'Wargaming', icon: Shield },
  ],
  'stride': [
    { id: 'overview', label: 'STRIDE Overview', icon: FileText },
    { id: 'threats', label: 'Threat Analysis', icon: ShieldAlert },
    { id: 'mitigations', label: 'Mitigations', icon: Shield },
  ],
  'pasta': [
    { id: 'overview', label: 'PASTA Overview', icon: FileText },
    { id: 'stages', label: 'Attack Stages', icon: Target },
    { id: 'mitigations', label: 'Countermeasures', icon: Shield },
  ],
  'dread': [
    { id: 'overview', label: 'DREAD Overview', icon: FileText },
    { id: 'ratings', label: 'Risk Ratings', icon: AlertTriangle },
    { id: 'distribution', label: 'Risk Distribution', icon: Target },
  ],
  'maestro': [
    { id: 'overview', label: 'MAESTRO Overview', icon: FileText },
    { id: 'analysis', label: 'Threat Analysis', icon: ShieldAlert },
  ],
  'linddun': [
    { id: 'overview', label: 'LINDDUN Overview', icon: FileText },
    { id: 'privacy-threats', label: 'Privacy Threats', icon: ShieldAlert },
  ],
  'hazop': [
    { id: 'overview', label: 'HAZOP Overview', icon: FileText },
    { id: 'deviations', label: 'Deviations', icon: AlertTriangle },
  ],
  'octave': [
    { id: 'overview', label: 'OCTAVE Overview', icon: FileText },
    { id: 'assets', label: 'Critical Assets', icon: Shield },
  ],
};

export default function CollapsibleAnalysisContent({
  analysisId,
  enabledAnalyses
}: CollapsibleAnalysisContentProps) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());
  const [expandedTables, setExpandedTables] = useState<Set<string>>(new Set());
  const subsections = analysisSubsections[analysisId] || [];

  const toggleSection = (sectionId: string) => {
    setExpandedSections(prev => {
      const newSet = new Set(prev);
      if (newSet.has(sectionId)) {
        newSet.delete(sectionId);
      } else {
        newSet.add(sectionId);
      }
      return newSet;
    });
  };

  const toggleTable = (tableId: string) => {
    setExpandedTables(prev => {
      const newSet = new Set(prev);
      if (newSet.has(tableId)) {
        newSet.delete(tableId);
      } else {
        newSet.add(tableId);
      }
      return newSet;
    });
  };

  // Render subsection content based on analysis type and subsection
  const renderSubsectionContent = (
    analysisId: string, 
    subsectionId: string, 
    expandedTables: Set<string>, 
    toggleTable: (id: string) => void
  ) => {
    // For demo purposes, show placeholder content with collapsible tables
    // In a real implementation, this would render the actual analysis content
    
    if (analysisId === 'stpa-sec') {
      switch (subsectionId) {
        case 'losses':
          return (
            <CollapsibleTable
              title="Identified Losses"
              isExpanded={expandedTables.has('losses-table')}
              onToggle={() => toggleTable('losses-table')}
            >
              <div style={{ padding: 'var(--space-3)' }}>
                <p>Loss table content would go here...</p>
              </div>
            </CollapsibleTable>
          );
        case 'hazards':
          return (
            <CollapsibleTable
              title="Security Hazards/Vulnerabilities"
              isExpanded={expandedTables.has('hazards-table')}
              onToggle={() => toggleTable('hazards-table')}
            >
              <div style={{ padding: 'var(--space-3)' }}>
                <p>Hazards table content would go here...</p>
              </div>
            </CollapsibleTable>
          );
        case 'system-description':
          return (
            <div style={{ padding: 'var(--space-3)' }}>
              <p>System description content (no table)...</p>
            </div>
          );
        default:
          return (
            <div style={{ padding: 'var(--space-3)' }}>
              <p>{subsectionId} content placeholder...</p>
            </div>
          );
      }
    }
    
    // Default placeholder for other analysis types
    return (
      <CollapsibleTable
        title={`${subsectionId} Table`}
        isExpanded={expandedTables.has(`${analysisId}-${subsectionId}-table`)}
        onToggle={() => toggleTable(`${analysisId}-${subsectionId}-table`)}
      >
        <div style={{ padding: 'var(--space-3)' }}>
          <p>{analysisId} - {subsectionId} content would go here...</p>
        </div>
      </CollapsibleTable>
    );
  };

  return (
    <div className="collapsible-analysis-content">
      {subsections.map(subsection => {
        const Icon = subsection.icon;
        const sectionKey = `${analysisId}-${subsection.id}`;
        const isExpanded = expandedSections.has(sectionKey);

        return (
          <div key={subsection.id} className="analysis-subsection">
            <div 
              className="subsection-header"
              onClick={() => toggleSection(sectionKey)}
            >
              {isExpanded ? 
                <ChevronDown size={14} className="subsection-expand-icon" /> : 
                <ChevronRight size={14} className="subsection-expand-icon" />
              }
              <Icon size={16} className="subsection-icon" />
              <span className="subsection-label">{subsection.label}</span>
            </div>
            
            {isExpanded && (
              <div className="subsection-content">
                {/* Render subsection content based on type */}
                {renderSubsectionContent(analysisId, subsection.id, expandedTables, toggleTable)}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}