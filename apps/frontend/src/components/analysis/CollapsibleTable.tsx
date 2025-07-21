import { ChevronRight, ChevronDown } from 'lucide-react';
import './CollapsibleAnalysisContent.css';

interface CollapsibleTableProps {
  title: string;
  isExpanded: boolean;
  onToggle: () => void;
  children: React.ReactNode;
}

export default function CollapsibleTable({
  title,
  isExpanded,
  onToggle,
  children
}: CollapsibleTableProps) {
  return (
    <div className="collapsible-table">
      <div className="table-header" onClick={onToggle}>
        {isExpanded ? 
          <ChevronDown size={14} className="table-expand-icon" /> : 
          <ChevronRight size={14} className="table-expand-icon" />
        }
        <span className="table-title">{title}</span>
      </div>
      {isExpanded && (
        <div className="table-content">
          {children}
        </div>
      )}
    </div>
  );
}