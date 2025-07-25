import React, { useState, useEffect } from 'react';
import { Edit2, X, Save, Download, ArrowUp, ArrowDown, Plus, Trash2 } from 'lucide-react';
import { getSectionUrl } from './utils';
import './AnalysisTable.css';

interface TableColumn {
  key: string;
  label: string;
  sortable?: boolean;
  type?: 'text' | 'dropdown';
  options?: string[];
}

interface AnalysisTableProps {
  id: string;
  title?: string;
  data: any[];
  columns: TableColumn[];
  sortable?: boolean;
  filterable?: boolean;
  pageSize?: number;
  editable?: boolean;
  onSave?: (id: string, data: any) => void;
  onRowClick?: (row: any) => void;
  clickableRows?: boolean;
}

type SortDirection = 'asc' | 'desc' | null;

export function AnalysisTable({
  id,
  title,
  data,
  columns,
  sortable = false,
  filterable = false,
  pageSize,
  editable = true,
  onSave,
  onRowClick,
  clickableRows = false
}: AnalysisTableProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [tableData, setTableData] = useState(data);
  const [filter, setFilter] = useState('');
  const [sortColumn, setSortColumn] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<SortDirection>(null);
  const [newRow, setNewRow] = useState<any>({});
  const [currentPageSize, setCurrentPageSize] = useState<number | undefined>(pageSize || undefined);

  // Sync tableData with props when data changes
  useEffect(() => {
    setTableData(data);
  }, [data]);

  const handleEdit = () => setIsEditing(true);
  const handleCancel = () => {
    setIsEditing(false);
    setTableData(data);
  };
  const handleSave = () => {
    if (onSave) onSave(id, tableData);
    setIsEditing(false);
  };
  const handleExport = () => {
    // Convert table data to CSV format
    const headers = columns.map(col => col.label).join(',');
    const rows = tableData.map(row => 
      columns.map(col => {
        const value = row[col.key] || '';
        // Escape values that contain commas or quotes
        if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
          return `"${value.replace(/"/g, '""')}"`;
        }
        return value;
      }).join(',')
    ).join('\n');
    
    const csv = `${headers}\n${rows}`;
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${id}-table.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleAddRow = () => {
    const newRowData = { ...newRow };
    // Fill in default values for columns not in newRow
    columns.forEach(col => {
      if (!(col.key in newRowData)) {
        newRowData[col.key] = '';
      }
    });
    // Generate a unique ID if not provided
    if (!newRowData.id) {
      const existingIds = tableData.map(row => row.id).filter(id => id && id.startsWith('UCA'));
      const maxId = existingIds.reduce((max, id) => {
        const match = id.match(/UCA(\d+)/);
        if (match) {
          const num = parseInt(match[1]);
          return num > max ? num : max;
        }
        return max;
      }, 0);
      newRowData.id = `UCA${maxId + 1}`;
    }
    setTableData([...tableData, newRowData]);
    setNewRow({});
    // If we're in edit mode and have onSave, save immediately
    if (isEditing && onSave) {
      onSave(id, [...tableData, newRowData]);
    }
  };

  const handleDeleteRow = (index: number) => {
    setTableData(tableData.filter((_, i) => i !== index));
  };

  const handleSort = (columnKey: string) => {
    if (!sortable) return;
    
    if (sortColumn === columnKey) {
      // Toggle between asc, desc, and no sort
      if (sortDirection === 'asc') {
        setSortDirection('desc');
      } else if (sortDirection === 'desc') {
        setSortDirection(null);
        setSortColumn(null);
      } else {
        setSortDirection('asc');
      }
    } else {
      setSortColumn(columnKey);
      setSortDirection('asc');
    }
  };

  const filteredData = filter
    ? tableData.filter(row =>
        Object.values(row).some(val =>
          String(val).toLowerCase().includes(filter.toLowerCase())
        )
      )
    : tableData;

  const sortedData = sortColumn && sortDirection
    ? [...filteredData].sort((a, b) => {
        const aVal = a[sortColumn];
        const bVal = b[sortColumn];
        
        if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
        if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
        return 0;
      })
    : filteredData;

  return (
    <div className={`analysis-table-template ${isEditing ? 'editing' : ''}`}>
      <div className="table-header">
        {title && (
          <a 
            href={getSectionUrl(id)}
            className="table-title-link"
            onClick={(e) => e.preventDefault()}
          >
            <h4 className="table-title">{title}</h4>
          </a>
        )}
        {editable && (
          <div className="table-toolbar">
            {isEditing ? (
              <>
                <button 
                  className="toolbar-btn cancel" 
                  onClick={handleCancel}
                  title="Cancel changes"
                  aria-label="Cancel changes"
                >
                  <X size={16} />
                </button>
                <button 
                  className="toolbar-btn save" 
                  onClick={handleSave}
                  title="Save changes"
                  aria-label="Save changes"
                >
                  <Save size={16} />
                </button>
              </>
            ) : (
              <>
                <button 
                  className="toolbar-btn edit" 
                  onClick={handleEdit}
                  title="Edit table"
                  aria-label="Edit table"
                >
                  <Edit2 size={16} />
                </button>
                <button 
                  className="toolbar-btn export" 
                  onClick={handleExport}
                  title="Export table"
                  aria-label="Export table"
                >
                  <Download size={16} />
                </button>
              </>
            )}
          </div>
        )}
      </div>

      {(filterable || pageSize !== undefined) && (
        <div className="table-controls">
          <div className="table-info">
            <span className="row-count">{sortedData.length} rows</span>
            {pageSize !== undefined && (
              <div className="page-size-selector">
                <label htmlFor={`${id}-page-size`}>Show:</label>
                <select
                  id={`${id}-page-size`}
                  value={currentPageSize || 'all'}
                  onChange={(e) => {
                    const value = e.target.value;
                    setCurrentPageSize(value === 'all' ? undefined : parseInt(value));
                  }}
                  className="page-size-select"
                >
                  <option value="10">10</option>
                  <option value="25">25</option>
                  <option value="50">50</option>
                  <option value="100">100</option>
                  <option value="all">All</option>
                </select>
              </div>
            )}
          </div>
          {filterable && (
            <input
              type="text"
              placeholder="Filter..."
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="filter-input"
            />
          )}
        </div>
      )}

      <div className="table-container" style={{ maxHeight: currentPageSize ? `${currentPageSize * 50 + 100}px` : 'auto', overflowY: currentPageSize ? 'auto' : 'visible' }}>
        <table className="analysis-table">
          <thead>
            <tr>
              {columns.map(col => (
                <th 
                  key={col.key}
                  className={sortable && col.sortable !== false ? 'sortable' : ''}
                  onClick={() => sortable && col.sortable !== false && handleSort(col.key)}
                >
                  <div className="th-content">
                    <span>{col.label}</span>
                    {sortable && col.sortable !== false && sortColumn === col.key && (
                      <span className="sort-indicator">
                        {sortDirection === 'asc' ? <ArrowUp size={14} /> : <ArrowDown size={14} />}
                      </span>
                    )}
                  </div>
                </th>
              ))}
              {isEditing && <th className="action-column">Actions</th>}
            </tr>
          </thead>
          <tbody>
            {(currentPageSize ? sortedData.slice(0, currentPageSize) : sortedData).map((row, idx) => {
              // Find the original index in tableData
              const originalIndex = tableData.findIndex(item => item === row);
              return (
                <tr 
                  key={idx}
                  onClick={() => !isEditing && clickableRows && onRowClick && onRowClick(row)}
                  className={!isEditing && clickableRows ? 'clickable-row' : ''}
                  style={{ cursor: !isEditing && clickableRows ? 'pointer' : 'default' }}
                >
                  {columns.map(col => (
                    <td key={col.key}>
                      {isEditing ? (
                        col.type === 'dropdown' && col.options ? (
                          <select
                            value={row[col.key] || ''}
                            onChange={(e) => {
                              const newData = [...tableData];
                              const rowIndex = tableData.findIndex(item => item === row);
                              if (rowIndex !== -1) {
                                newData[rowIndex] = { ...newData[rowIndex], [col.key]: e.target.value };
                                setTableData(newData);
                              }
                            }}
                            className="cell-select"
                          >
                            {!row[col.key] && <option value="">Select...</option>}
                            {col.options.map(option => (
                              <option key={option} value={option}>{option}</option>
                            ))}
                          </select>
                        ) : (
                          <input
                            type="text"
                            value={row[col.key] || ''}
                            onChange={(e) => {
                              const newData = [...tableData];
                              newData[originalIndex] = { ...row, [col.key]: e.target.value };
                              setTableData(newData);
                            }}
                            className="cell-input"
                          />
                        )
                      ) : (
                        row[col.key]
                      )}
                    </td>
                  ))}
                  {isEditing && (
                    <td className="action-column">
                      <button 
                        className="row-btn delete"
                        onClick={() => handleDeleteRow(originalIndex)}
                        title="Delete row"
                      >
                        <Trash2 size={14} />
                      </button>
                    </td>
                  )}
                </tr>
              );
            })}
            {isEditing && (
              <tr className="new-row">
                {columns.map(col => (
                  <td key={col.key}>
                    {col.type === 'dropdown' && col.options ? (
                      <select
                        value={newRow[col.key] || ''}
                        onChange={(e) => setNewRow({ ...newRow, [col.key]: e.target.value })}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') {
                            e.preventDefault();
                            handleAddRow();
                          }
                        }}
                        className="cell-select"
                      >
                        <option value="">Select...</option>
                        {col.options.map(option => (
                          <option key={option} value={option}>{option}</option>
                        ))}
                      </select>
                    ) : (
                      <input
                        type="text"
                        value={newRow[col.key] || ''}
                        onChange={(e) => setNewRow({ ...newRow, [col.key]: e.target.value })}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') {
                            e.preventDefault();
                            handleAddRow();
                          }
                        }}
                        placeholder={`New ${col.label}`}
                        className="cell-input"
                      />
                    )}
                  </td>
                ))}
                <td className="action-column">
                  <button 
                    className="row-btn add"
                    onClick={handleAddRow}
                    title="Add row"
                  >
                    <Plus size={14} />
                  </button>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}