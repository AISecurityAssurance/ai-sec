import React, { useState } from 'react';
import { Edit2, X, Save, Download, Plus, Trash2 } from 'lucide-react';
import './AnalysisList.css';

interface AnalysisListProps {
  id: string;
  title: string;
  items: string[];
  editable?: boolean;
  placeholder?: string;
  onSave?: (id: string, data: any) => void;
}

export function AnalysisList({
  id,
  title,
  items: initialItems,
  editable = true,
  placeholder = 'Add new item...',
  onSave
}: AnalysisListProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [items, setItems] = useState(initialItems);
  const [newItem, setNewItem] = useState('');
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [editValue, setEditValue] = useState('');

  const handleEdit = () => setIsEditing(true);
  const handleCancel = () => {
    setIsEditing(false);
    setItems(initialItems);
    setNewItem('');
    setEditingIndex(null);
  };

  const handleSave = () => {
    if (onSave) onSave(id, { items });
    setIsEditing(false);
  };

  const handleExport = () => {
    const data = {
      title,
      items
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${id}-list.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleAddItem = () => {
    if (newItem.trim()) {
      setItems([...items, newItem.trim()]);
      setNewItem('');
    }
  };

  const handleDeleteItem = (index: number) => {
    setItems(items.filter((_, i) => i !== index));
  };

  const handleEditItem = (index: number) => {
    setEditingIndex(index);
    setEditValue(items[index]);
  };

  const handleSaveItem = () => {
    if (editingIndex !== null && editValue.trim()) {
      const newItems = [...items];
      newItems[editingIndex] = editValue.trim();
      setItems(newItems);
      setEditingIndex(null);
      setEditValue('');
    }
  };

  const handleCancelEdit = () => {
    setEditingIndex(null);
    setEditValue('');
  };

  return (
    <div className={`analysis-list-template ${isEditing ? 'editing' : ''}`}>
      <div className="list-header">
        <a 
          href={`/analysis/list/${id}`}
          className="list-title-link"
          onClick={(e) => e.preventDefault()}
        >
          <h4 className="list-title">{title}</h4>
        </a>
        
        {editable && (
          <div className="list-toolbar">
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
                  title={`Edit ${title}`}
                  aria-label={`Edit ${title}`}
                >
                  <Edit2 size={16} />
                </button>
                <button 
                  className="toolbar-btn export" 
                  onClick={handleExport}
                  title={`Export ${title}`}
                  aria-label={`Export ${title}`}
                >
                  <Download size={16} />
                </button>
              </>
            )}
          </div>
        )}
      </div>

      <div className="list-content">
        <ul className="items-list">
          {items.map((item, index) => (
            <li key={index} className="list-item">
              {isEditing && editingIndex === index ? (
                <div className="item-edit">
                  <input
                    type="text"
                    value={editValue}
                    onChange={(e) => setEditValue(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSaveItem()}
                    className="item-input"
                    autoFocus
                  />
                  <button 
                    className="item-btn save"
                    onClick={handleSaveItem}
                    title="Save item"
                  >
                    <Save size={14} />
                  </button>
                  <button 
                    className="item-btn cancel"
                    onClick={handleCancelEdit}
                    title="Cancel edit"
                  >
                    <X size={14} />
                  </button>
                </div>
              ) : (
                <>
                  <span className="item-text">{item}</span>
                  {isEditing && (
                    <div className="item-actions">
                      <button 
                        className="item-btn edit"
                        onClick={() => handleEditItem(index)}
                        title="Edit item"
                      >
                        <Edit2 size={14} />
                      </button>
                      <button 
                        className="item-btn delete"
                        onClick={() => handleDeleteItem(index)}
                        title="Delete item"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  )}
                </>
              )}
            </li>
          ))}
        </ul>
        
        {isEditing && (
          <div className="add-item">
            <input
              type="text"
              value={newItem}
              onChange={(e) => setNewItem(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddItem()}
              placeholder={placeholder}
              className="new-item-input"
            />
            <button 
              className="toolbar-btn add"
              onClick={handleAddItem}
              title="Add item"
              aria-label="Add item"
            >
              <Plus size={16} />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}