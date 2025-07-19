import { useState } from 'react';
import { Link } from 'react-router-dom';
import './AnalysisTable.css';

interface TableColumn {
  key: string;
  label: string;
  width?: string;
}

interface TableRow {
  id: string;
  [key: string]: any;
}

interface AnalysisTableProps {
  columns: TableColumn[];
  data: TableRow[];
  onRowSelect?: (row: TableRow) => void;
  selectedRowId?: string | null;
  title?: string;
  enableMultiSelect?: boolean;
  itemType?: string;
  linkable?: boolean;
  getRowClassName?: (row: TableRow) => string;
}

export default function AnalysisTable({ 
  columns, 
  data, 
  onRowSelect, 
  selectedRowId,
  title,
  enableMultiSelect = false,
  itemType,
  linkable = false,
  getRowClassName
}: AnalysisTableProps) {
  const [selectedRows, setSelectedRows] = useState<Set<string>>(new Set());
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  const handleRowClick = (row: TableRow) => {
    if (enableMultiSelect) {
      const newSelected = new Set(selectedRows);
      if (newSelected.has(row.id)) {
        newSelected.delete(row.id);
      } else {
        newSelected.add(row.id);
      }
      setSelectedRows(newSelected);
    }
    onRowSelect?.(row);
  };

  const handleSort = (key: string) => {
    if (sortKey === key) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortDirection('asc');
    }
  };

  const sortedData = [...data].sort((a, b) => {
    if (!sortKey) return 0;
    
    const aVal = a[sortKey];
    const bVal = b[sortKey];
    
    if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
    if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
    return 0;
  });

  return (
    <div className="analysis-table-container">
      {title && <h4 className="table-title">{title}</h4>}
      <div className="table-wrapper">
        <table className="analysis-table">
          <thead>
            <tr>
              {columns.map(col => (
                <th 
                  key={col.key} 
                  style={{ width: col.width }}
                  onClick={() => handleSort(col.key)}
                  className="sortable"
                >
                  <span>{col.label}</span>
                  {sortKey === col.key && (
                    <span className="sort-indicator">
                      {sortDirection === 'asc' ? ' ↑' : ' ↓'}
                    </span>
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sortedData.map(row => {
              const rowContent = (
                <>
                  {columns.map(col => (
                    <td key={col.key}>
                      {renderCellContent(row[col.key], col.key)}
                    </td>
                  ))}
                </>
              );
              
              if (linkable && itemType) {
                const rowClass = [
                  selectedRowId === row.id || selectedRows.has(row.id) ? 'selected' : '',
                  getRowClassName?.(row) || ''
                ].filter(Boolean).join(' ');
                
                return (
                  <tr key={row.id} className={rowClass}>
                    <td colSpan={columns.length} className="linkable-row">
                      <Link
                        to={`/analysis/item/${itemType}/${row.id}`}
                        className="row-link"
                        onClick={(e) => {
                          if (!e.ctrlKey && !e.metaKey && e.button === 0) {
                            e.preventDefault();
                            handleRowClick(row);
                          }
                        }}
                      >
                        {columns.map(col => (
                          <span key={col.key} className="row-cell" style={{ width: col.width }}>
                            {renderCellContent(row[col.key], col.key)}
                          </span>
                        ))}
                      </Link>
                    </td>
                  </tr>
                );
              }
              
              const rowClass = [
                selectedRowId === row.id || selectedRows.has(row.id) ? 'selected' : '',
                onRowSelect ? 'clickable' : '',
                getRowClassName?.(row) || ''
              ].filter(Boolean).join(' ');
              
              return (
                <tr 
                  key={row.id}
                  onClick={() => handleRowClick(row)}
                  className={rowClass}
                >
                  {rowContent}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      {selectedRows.size > 0 && enableMultiSelect && (
        <div className="selection-info">
          {selectedRows.size} items selected
        </div>
      )}
    </div>
  );
}

function renderCellContent(value: any, key: string): React.ReactNode {
  if (key === 'severity' || key === 'likelihood' || key === 'priority') {
    const colorClass = 
      value === 'high' || value === 'critical' ? 'severity-high' :
      value === 'medium' ? 'severity-medium' : 'severity-low';
    return <span className={`badge ${colorClass}`}>{value}</span>;
  }
  
  if (key === 'confidence') {
    return <span className="confidence">{value}%</span>;
  }
  
  if (Array.isArray(value)) {
    return value.join(', ');
  }
  
  if (typeof value === 'boolean') {
    return value ? '✓' : '✗';
  }
  
  return value;
}