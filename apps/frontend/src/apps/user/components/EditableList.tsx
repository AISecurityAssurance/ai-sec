import { useState, useEffect, useRef } from 'react';
import { Plus, Trash2, Edit2, GripVertical, Check, X } from 'lucide-react';
import './EditableList.css';

interface EditableListProps {
  items: string[];
  onUpdate: (items: string[]) => void;
  onItemClick?: (item: string, index: number) => void;
  isEditMode?: boolean;
  itemIcon?: string;
  itemClassName?: string;
  placeholder?: string;
  selectedIndex?: number | null;
  componentName?: string;
}

export default function EditableList({
  items,
  onUpdate,
  onItemClick,
  isEditMode = false,
  itemIcon,
  itemClassName = '',
  placeholder = 'Add new item...',
  selectedIndex = null,
  componentName = 'Items'
}: EditableListProps) {
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [editValue, setEditValue] = useState('');
  const [newItemValue, setNewItemValue] = useState('');
  const [showNewItem, setShowNewItem] = useState(false);
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null);
  const originalItemsRef = useRef<string[]>([]);

  // Track original items when entering edit mode
  useEffect(() => {
    if (isEditMode) {
      originalItemsRef.current = [...items];
    }
  }, [isEditMode]);

  const handleEdit = (index: number) => {
    setEditingIndex(index);
    setEditValue(items[index]);
  };

  const handleSave = (index: number) => {
    if (editValue.trim()) {
      const newItems = [...items];
      newItems[index] = editValue.trim();
      onUpdate(newItems);
    }
    setEditingIndex(null);
    setEditValue('');
  };

  const handleDelete = (index: number) => {
    const newItems = items.filter((_, i) => i !== index);
    onUpdate(newItems);
  };

  const handleAddNew = () => {
    if (newItemValue.trim()) {
      onUpdate([...items, newItemValue.trim()]);
      setNewItemValue('');
      setShowNewItem(false);
    }
  };

  const handleDragStart = (index: number) => {
    setDraggedIndex(index);
  };

  const handleDragOver = (e: React.DragEvent, index: number) => {
    e.preventDefault();
    if (draggedIndex === null || draggedIndex === index) return;

    const newItems = [...items];
    const draggedItem = newItems[draggedIndex];
    newItems.splice(draggedIndex, 1);
    newItems.splice(index, 0, draggedItem);
    
    onUpdate(newItems);
    setDraggedIndex(index);
  };

  const handleDragEnd = () => {
    setDraggedIndex(null);
  };

  const handleCancelAll = () => {
    // Restore original items
    onUpdate(originalItemsRef.current);
    // Reset any editing state
    setEditingIndex(null);
    setEditValue('');
    setNewItemValue('');
    setShowNewItem(false);
  };

  return (
    <div className="editable-list">
      {isEditMode && (
        <div className="list-header">
          <button onClick={handleCancelAll} className="btn-cancel-all">
            <X size={16} />
            <span>Reset {componentName}</span>
          </button>
        </div>
      )}
      <ul className={`list-items ${itemClassName}`}>
        {items.map((item, index) => (
          <li
            key={index}
            className={`list-item ${selectedIndex === index ? 'selected' : ''} ${draggedIndex === index ? 'dragging' : ''}`}
            onClick={() => !isEditMode && onItemClick?.(item, index)}
            draggable={isEditMode}
            onDragStart={() => handleDragStart(index)}
            onDragOver={(e) => handleDragOver(e, index)}
            onDragEnd={handleDragEnd}
          >
            {isEditMode && (
              <GripVertical size={16} className="drag-handle" />
            )}
            
            {/* Icon is handled by CSS for non-edit mode */}
            
            {editingIndex === index ? (
              <div className="edit-inline">
                <input
                  type="text"
                  value={editValue}
                  onChange={(e) => setEditValue(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') handleSave(index);
                    if (e.key === 'Escape') setEditingIndex(null);
                  }}
                  autoFocus
                  className="edit-input"
                />
                <button
                  onClick={() => handleSave(index)}
                  className="btn-inline btn-save"
                >
                  <Check size={14} />
                </button>
                <button
                  onClick={() => setEditingIndex(null)}
                  className="btn-inline btn-cancel"
                >
                  <X size={14} />
                </button>
              </div>
            ) : (
              <>
                <span className="item-text">{item}</span>
                {isEditMode && (
                  <div className="item-actions">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleEdit(index);
                      }}
                      className="btn-icon"
                      title="Edit"
                    >
                      <Edit2 size={14} />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(index);
                      }}
                      className="btn-icon btn-delete"
                      title="Delete"
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

      {isEditMode && (
        <div className="add-new-section">
          {showNewItem ? (
            <div className="new-item-input">
              <input
                type="text"
                value={newItemValue}
                onChange={(e) => setNewItemValue(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleAddNew();
                  if (e.key === 'Escape') {
                    setShowNewItem(false);
                    setNewItemValue('');
                  }
                }}
                placeholder={placeholder}
                autoFocus
                className="edit-input"
              />
              <button
                onClick={handleAddNew}
                className="btn-inline btn-save"
              >
                <Check size={14} />
              </button>
              <button
                onClick={() => {
                  setShowNewItem(false);
                  setNewItemValue('');
                }}
                className="btn-inline btn-cancel"
              >
                <X size={14} />
              </button>
            </div>
          ) : (
            <button
              onClick={() => setShowNewItem(true)}
              className="btn-add-new"
            >
              <Plus size={16} />
              <span>Add new</span>
            </button>
          )}
        </div>
      )}
    </div>
  );
}