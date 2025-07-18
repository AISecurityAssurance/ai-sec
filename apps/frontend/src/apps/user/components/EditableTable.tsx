import { useState, useEffect, useRef } from 'react';
import { Plus, Trash2, Edit2, Check, X, ChevronUp, ChevronDown } from 'lucide-react';
import type { TableColumn, TableRow } from './AnalysisTable';
import './EditableTable.css';

interface EnumOption {
  value: string;
  label: string;
}

interface ExtendedTableColumn extends TableColumn {
  editable?: boolean;
  editType?: 'text' | 'select' | 'multiselect';
  options?: EnumOption[];
}

interface EditableTableProps {
  columns: ExtendedTableColumn[];
  data: TableRow[];
  onUpdate: (data: TableRow[]) => void;
  onRowSelect?: (row: TableRow) => void;
  selectedRowId?: string | null;
  title?: string;
  isEditMode?: boolean;
}

export default function EditableTable({
  columns,
  data,
  onUpdate,
  onRowSelect,
  selectedRowId,
  title,
  isEditMode = false
}: EditableTableProps) {
  const [editingCell, setEditingCell] = useState<{ rowId: string; columnKey: string } | null>(null);
  const [editValue, setEditValue] = useState('');
  const [sortColumn, setSortColumn] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [newRow, setNewRow] = useState<TableRow | null>(null);
  const originalDataRef = useRef<TableRow[]>([]);

  // Track original data when entering edit mode
  useEffect(() => {
    if (isEditMode) {
      originalDataRef.current = JSON.parse(JSON.stringify(data));
    }
  }, [isEditMode]);

  const handleSort = (columnKey: string) => {
    if (sortColumn === columnKey) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(columnKey);
      setSortDirection('asc');
    }
  };

  const sortedData = [...data].sort((a, b) => {
    if (!sortColumn) return 0;
    const aVal = a[sortColumn]?.toString() || '';
    const bVal = b[sortColumn]?.toString() || '';
    const comparison = aVal.localeCompare(bVal);
    return sortDirection === 'asc' ? comparison : -comparison;
  });

  const startEdit = (rowId: string, columnKey: string, currentValue: any) => {
    setEditingCell({ rowId, columnKey });
    setEditValue(currentValue?.toString() || '');
  };

  const saveEdit = () => {
    if (!editingCell) return;
    
    const newData = data.map(row => {
      if (row.id === editingCell.rowId) {
        return { ...row, [editingCell.columnKey]: editValue };
      }
      return row;
    });
    
    onUpdate(newData);
    setEditingCell(null);
    setEditValue('');
  };

  const cancelEdit = () => {
    setEditingCell(null);
    setEditValue('');
  };

  const deleteRow = (rowId: string) => {
    const newData = data.filter(row => row.id !== rowId);
    onUpdate(newData);
  };

  const startAddRow = () => {
    const newRowTemplate: TableRow = { id: `new-${Date.now()}` };
    columns.forEach(col => {
      if (col.key !== 'id') {
        newRowTemplate[col.key] = '';
      }
    });
    setNewRow(newRowTemplate);
  };

  const saveNewRow = () => {
    if (newRow) {
      onUpdate([...data, newRow]);
      setNewRow(null);
    }
  };

  const handleCancelAll = () => {
    // Restore original data
    onUpdate(originalDataRef.current);
    // Reset any editing state
    setEditingCell(null);
    setEditValue('');
    setNewRow(null);
  };

  const renderCell = (row: TableRow, column: ExtendedTableColumn) => {
    const isEditing = editingCell?.rowId === row.id && editingCell?.columnKey === column.key;
    const value = row[column.key];

    if (isEditing) {
      // Check if this column has dropdown options
      if (column.editType === 'select' && column.options) {
        return (
          <div className="cell-edit">
            <select
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') saveEdit();
                if (e.key === 'Escape') cancelEdit();
              }}
              autoFocus
              className="cell-select"
            >
              <option value="">Select...</option>
              {column.options.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <button onClick={saveEdit} className="btn-cell btn-save">
              <Check size={14} />
            </button>
            <button onClick={cancelEdit} className="btn-cell btn-cancel">
              <X size={14} />
            </button>
          </div>
        );
      }

      // Default text input
      return (
        <div className="cell-edit">
          <input
            type="text"
            value={editValue}
            onChange={(e) => setEditValue(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') saveEdit();
              if (e.key === 'Escape') cancelEdit();
            }}
            autoFocus
            className="cell-input"
          />
          <button onClick={saveEdit} className="btn-cell btn-save">
            <Check size={14} />
          </button>
          <button onClick={cancelEdit} className="btn-cell btn-cancel">
            <X size={14} />
          </button>
        </div>
      );
    }

    const displayValue = Array.isArray(value) ? value.join(', ') : value;
    const isEditable = column.editable !== false;

    return (
      <div className="cell-content">
        <span>{displayValue}</span>
        {isEditMode && column.key !== 'id' && isEditable && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              startEdit(row.id, column.key, value);
            }}
            className="btn-cell-edit"
          >
            <Edit2 size={14} />
          </button>
        )}
      </div>
    );
  };

  return (
    <div className="editable-table-container">
      <div className="table-header">
        {title && <h3 className="table-title">{title}</h3>}
        {isEditMode && (
          <button onClick={handleCancelAll} className="btn-cancel-all">
            <X size={16} />
            <span>Reset {title || 'Table'}</span>
          </button>
        )}
      </div>
      
      <div className="table-wrapper">
        <table className="editable-table">
          <thead>
            <tr>
              {columns.map(column => (
                <th
                  key={column.key}
                  style={{ width: column.width }}
                  onClick={() => handleSort(column.key)}
                  className="sortable"
                >
                  <div className="th-content">
                    <span>{column.label}</span>
                    {sortColumn === column.key && (
                      sortDirection === 'asc' ? <ChevronUp size={14} /> : <ChevronDown size={14} />
                    )}
                  </div>
                </th>
              ))}
              {isEditMode && <th className="actions-column">Actions</th>}
            </tr>
          </thead>
          <tbody>
            {sortedData.map(row => (
              <tr
                key={row.id}
                onClick={() => !isEditMode && onRowSelect?.(row)}
                className={`${selectedRowId === row.id ? 'selected' : ''} ${!isEditMode ? 'clickable' : ''}`}
              >
                {columns.map(column => (
                  <td key={column.key}>
                    {renderCell(row, column)}
                  </td>
                ))}
                {isEditMode && (
                  <td className="actions-cell">
                    <button
                      onClick={() => deleteRow(row.id)}
                      className="btn-delete"
                      title="Delete row"
                    >
                      <Trash2 size={14} />
                    </button>
                  </td>
                )}
              </tr>
            ))}
            
            {isEditMode && newRow && (
              <tr className="new-row">
                {columns.map(column => (
                  <td key={column.key}>
                    <input
                      type="text"
                      value={newRow[column.key] || ''}
                      onChange={(e) => setNewRow({ ...newRow, [column.key]: e.target.value })}
                      placeholder={column.label}
                      className="cell-input"
                    />
                  </td>
                ))}
                <td className="actions-cell">
                  <button onClick={saveNewRow} className="btn-cell btn-save">
                    <Check size={14} />
                  </button>
                  <button onClick={() => setNewRow(null)} className="btn-cell btn-cancel">
                    <X size={14} />
                  </button>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {isEditMode && !newRow && (
        <button onClick={startAddRow} className="btn-add-row">
          <Plus size={16} />
          <span>Add new row</span>
        </button>
      )}
    </div>
  );
}