import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Edit3, Save, AlertTriangle, ShieldAlert, Users, Zap, Target } from 'lucide-react';
import { useState, useEffect } from 'react';
import { useAnalysisStore } from '../../../stores/analysisStore';
import { useBroadcastSync } from '../hooks/useBroadcastChannel';
import { getRelatedData } from '../mockData/stpaSecData';
import type { Loss, Hazard, Controller, ControlAction, UCA, CausalScenario } from '../mockData/stpaSecData';
import './FocusedItemView.css';

// Type guards for each item type
function isLoss(item: any): item is Loss {
  return item && 'severity' in item && 'category' in item && 'stakeholders' in item;
}

function isHazard(item: any): item is Hazard {
  return item && 'severity' in item && 'relatedLosses' in item && 'worstCase' in item;
}

function isController(item: any): item is Controller {
  return item && 'name' in item && 'type' in item && 'responsibilities' in item;
}

function isControlAction(item: any): item is ControlAction {
  return item && 'action' in item && 'controllerId' in item && 'targetProcess' in item;
}

function isUCA(item: any): item is UCA {
  return item && 'controlActionId' in item && 'type' in item && 'hazards' in item;
}

function isCausalScenario(item: any): item is CausalScenario {
  return item && 'ucaId' in item && 'strideCategory' in item && 'confidence' in item;
}

export default function FocusedItemView() {
  const { itemType, itemId } = useParams<{ itemType: string; itemId: string }>();
  const [isEditMode, setIsEditMode] = useState(false);
  
  const {
    losses,
    hazards,
    controllers,
    controlActions,
    ucas,
    scenarios,
    updateLosses,
    updateHazards,
    updateControllers,
    updateControlActions,
    updateUcas,
    updateScenarios
  } = useAnalysisStore();
  
  useBroadcastSync();
  
  // Get the item data based on type
  const getItemData = () => {
    switch (itemType) {
      case 'loss':
        return losses.find(l => l.id === itemId);
      case 'hazard':
        return hazards.find(h => h.id === itemId);
      case 'controller':
        return controllers.find(c => c.id === itemId);
      case 'control-action':
        return controlActions.find(ca => ca.id === itemId);
      case 'uca':
        return ucas.find(u => u.id === itemId);
      case 'scenario':
        return scenarios.find(s => s.id === itemId);
      default:
        return null;
    }
  };
  
  const item = getItemData();
  const [editedItem, setEditedItem] = useState<Loss | Hazard | Controller | ControlAction | UCA | CausalScenario | null | undefined>(item);
  
  useEffect(() => {
    setEditedItem(item);
  }, [item]);
  
  if (!item || !itemId || !itemType) {
    return (
      <div className="focused-item-view">
        <div className="focused-item-header">
          <Link to="/analysis" className="back-link">
            <ArrowLeft size={20} />
            <span>Back to Analysis</span>
          </Link>
        </div>
        <div className="focused-item-not-found">
          <p>Item not found</p>
        </div>
      </div>
    );
  }
  
  const getIcon = () => {
    switch (itemType) {
      case 'loss':
        return <AlertTriangle size={24} />;
      case 'hazard':
        return <ShieldAlert size={24} />;
      case 'controller':
        return <Users size={24} />;
      case 'control-action':
      case 'uca':
        return <Zap size={24} />;
      case 'scenario':
        return <Target size={24} />;
      default:
        return null;
    }
  };
  
  const getItemTypeLabel = () => {
    switch (itemType) {
      case 'loss':
        return 'Loss';
      case 'hazard':
        return 'Hazard/Vulnerability';
      case 'controller':
        return 'Controller';
      case 'control-action':
        return 'Control Action';
      case 'uca':
        return 'Unsafe/Unsecure Control Action';
      case 'scenario':
        return 'Causal Scenario';
      default:
        return 'Item';
    }
  };
  
  const handleSave = () => {
    if (!editedItem) return;
    
    switch (itemType) {
      case 'loss':
        if (isLoss(editedItem)) {
          updateLosses(losses.map(l => l.id === itemId ? editedItem : l));
        }
        break;
      case 'hazard':
        if (isHazard(editedItem)) {
          updateHazards(hazards.map(h => h.id === itemId ? editedItem : h));
        }
        break;
      case 'controller':
        if (isController(editedItem)) {
          updateControllers(controllers.map(c => c.id === itemId ? editedItem : c));
        }
        break;
      case 'control-action':
        if (isControlAction(editedItem)) {
          updateControlActions(controlActions.map(ca => ca.id === itemId ? editedItem : ca));
        }
        break;
      case 'uca':
        if (isUCA(editedItem)) {
          updateUcas(ucas.map(u => u.id === itemId ? editedItem : u));
        }
        break;
      case 'scenario':
        if (isCausalScenario(editedItem)) {
          updateScenarios(scenarios.map(s => s.id === itemId ? editedItem : s));
        }
        break;
    }
    
    setIsEditMode(false);
  };
  
  const handleCancel = () => {
    setEditedItem(item);
    setIsEditMode(false);
  };
  
  const related = itemType === 'controller' || itemType === 'control-action' 
    ? { losses: [], hazards: [], ucas: [], scenarios: [] }
    : getRelatedData(itemId, itemType as 'loss' | 'hazard' | 'uca' | 'scenario');
  
  return (
    <div className="focused-item-view">
      <div className="focused-item-header">
        <Link to="/analysis" className="back-link">
          <ArrowLeft size={20} />
          <span>Back to Analysis</span>
        </Link>
        
        <div className="focused-item-actions">
          {isEditMode ? (
            <>
              <button className="btn btn-primary" onClick={handleSave}>
                <Save size={16} />
                <span>Save</span>
              </button>
              <button className="btn btn-secondary" onClick={handleCancel}>
                <span>Cancel</span>
              </button>
            </>
          ) : (
            <button className="btn btn-secondary" onClick={() => setIsEditMode(true)}>
              <Edit3 size={16} />
              <span>Edit</span>
            </button>
          )}
        </div>
      </div>
      
      <div className="focused-item-content">
        <div className="focused-item-main">
          <div className="focused-item-title">
            {getIcon()}
            <div>
              <span className="item-type-label">{getItemTypeLabel()}</span>
              <h2>{itemId}</h2>
            </div>
          </div>
          
          <div className="focused-item-details">
            {renderItemDetails()}
          </div>
        </div>
        
        <div className="focused-item-sidebar">
          <h3>Related Items</h3>
          
          {related.losses.length > 0 && (
            <div className="related-section">
              <h4>Related Losses ({related.losses.length})</h4>
              {related.losses.map(l => (
                <Link 
                  key={l.id} 
                  to={`/analysis/item/loss/${l.id}`}
                  className="related-item"
                >
                  <span className="related-id">{l.id}</span>
                  <span className="related-desc">{l.description}</span>
                </Link>
              ))}
            </div>
          )}
          
          {related.hazards.length > 0 && (
            <div className="related-section">
              <h4>Related Hazards ({related.hazards.length})</h4>
              {related.hazards.map(h => (
                <Link 
                  key={h.id} 
                  to={`/analysis/item/hazard/${h.id}`}
                  className="related-item"
                >
                  <span className="related-id">{h.id}</span>
                  <span className="related-desc">{h.description}</span>
                </Link>
              ))}
            </div>
          )}
          
          {related.ucas.length > 0 && (
            <div className="related-section">
              <h4>Related UCAs ({related.ucas.length})</h4>
              {related.ucas.map(u => (
                <Link 
                  key={u.id} 
                  to={`/analysis/item/uca/${u.id}`}
                  className="related-item"
                >
                  <span className="related-id">{u.id}</span>
                  <span className="related-desc">{u.description}</span>
                </Link>
              ))}
            </div>
          )}
          
          {related.scenarios.length > 0 && (
            <div className="related-section">
              <h4>Related Scenarios ({related.scenarios.length})</h4>
              {related.scenarios.map(s => (
                <Link 
                  key={s.id} 
                  to={`/analysis/item/scenario/${s.id}`}
                  className="related-item"
                >
                  <span className="related-id">{s.id}</span>
                  <span className="related-desc">{s.description}</span>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
  
  function renderItemDetails() {
    if (!editedItem) return null;
    
    const renderField = (label: string, value: any, key: string, options?: Array<{value: string, label: string}>, isArray?: boolean) => {
      if (isEditMode && key !== 'id') {
        if (options) {
          return (
            <div className="detail-field">
              <label>{label}:</label>
              <select 
                value={value} 
                onChange={(e) => setEditedItem({...editedItem, [key]: e.target.value})}
                className="detail-select"
              >
                {options.map(opt => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>
          );
        }
        
        if (typeof value === 'string' && value.length > 100) {
          return (
            <div className="detail-field">
              <label>{label}:</label>
              <textarea 
                value={value} 
                onChange={(e) => {
                  if (isArray) {
                    // Convert comma-separated string back to array
                    const newValue = e.target.value.split(',').map(s => s.trim()).filter(s => s);
                    setEditedItem({...editedItem, [key]: newValue});
                  } else {
                    setEditedItem({...editedItem, [key]: e.target.value});
                  }
                }}
                className="detail-textarea"
                rows={4}
              />
            </div>
          );
        }
        
        return (
          <div className="detail-field">
            <label>{label}:</label>
            <input 
              type="text" 
              value={value} 
              onChange={(e) => {
                if (isArray) {
                  // Convert comma-separated string back to array
                  const newValue = e.target.value.split(',').map(s => s.trim()).filter(s => s);
                  setEditedItem({...editedItem, [key]: newValue});
                } else {
                  setEditedItem({...editedItem, [key]: e.target.value});
                }
              }}
              className="detail-input"
            />
          </div>
        );
      }
      
      return (
        <div className="detail-field">
          <label>{label}:</label>
          <span className="detail-value">{value}</span>
        </div>
      );
    };
    
    const severityOptions = [
      { value: 'critical', label: 'Critical' },
      { value: 'high', label: 'High' },
      { value: 'medium', label: 'Medium' },
      { value: 'low', label: 'Low' }
    ];
    
    switch (itemType) {
      case 'loss':
        if (isLoss(editedItem)) {
          return (
            <>
              {renderField('ID', editedItem.id, 'id')}
              {renderField('Description', editedItem.description, 'description')}
              {renderField('Severity', editedItem.severity, 'severity', severityOptions)}
              {renderField('Category', editedItem.category, 'category')}
              {renderField('Stakeholders', editedItem.stakeholders.join(', '), 'stakeholders', undefined, true)}
            </>
          );
        }
        break;
        
      case 'hazard':
        if (isHazard(editedItem)) {
          return (
            <>
              {renderField('ID', editedItem.id, 'id')}
              {renderField('Description', editedItem.description, 'description')}
              {renderField('Severity', editedItem.severity, 'severity', severityOptions)}
              {renderField('Related Losses', editedItem.relatedLosses.join(', '), 'relatedLosses', undefined, true)}
              {renderField('Worst Case Scenario', editedItem.worstCase, 'worstCase')}
            </>
          );
        }
        break;
        
      case 'controller':
        if (isController(editedItem)) {
          return (
            <>
              {renderField('ID', editedItem.id, 'id')}
              {renderField('Name', editedItem.name, 'name')}
              {renderField('Type', editedItem.type, 'type')}
              {renderField('Responsibilities', editedItem.responsibilities.join(', '), 'responsibilities', undefined, true)}
            </>
          );
        }
        break;
        
      case 'control-action':
        if (isControlAction(editedItem)) {
          return (
            <>
              {renderField('ID', editedItem.id, 'id')}
              {renderField('Action', editedItem.action, 'action')}
              {renderField('Controller', editedItem.controllerId, 'controllerId')}
              {renderField('Target Process', editedItem.targetProcess, 'targetProcess')}
              {renderField('Constraints', editedItem.constraints.join(', '), 'constraints', undefined, true)}
            </>
          );
        }
        break;
        
      case 'uca':
        if (isUCA(editedItem)) {
          const ucaTypeOptions = [
            { value: 'not-provided', label: 'Not Provided' },
            { value: 'provided', label: 'Provided Causes Hazard/Vulnerability' },
            { value: 'wrong-timing', label: 'Wrong Timing/Order' },
            { value: 'wrong-duration', label: 'Wrong Duration/Applied Too Long' }
          ];
          
          return (
            <>
              {renderField('ID', editedItem.id, 'id')}
              {renderField('Control Action', editedItem.controlActionId, 'controlActionId')}
              {renderField('Type', editedItem.type, 'type', ucaTypeOptions)}
              {renderField('Description', editedItem.description, 'description')}
              {renderField('Context', editedItem.context, 'context')}
              {renderField('Hazards/Vulnerabilities', editedItem.hazards.join(', '), 'hazards', undefined, true)}
              {renderField('Severity', editedItem.severity, 'severity', severityOptions)}
            </>
          );
        }
        break;
        
      case 'scenario':
        if (isCausalScenario(editedItem)) {
          return (
            <>
              {renderField('ID', editedItem.id, 'id')}
              {renderField('UCA', editedItem.ucaId, 'ucaId')}
              {renderField('Description', editedItem.description, 'description')}
              {renderField('STRIDE Category', editedItem.strideCategory, 'strideCategory')}
              {renderField('Confidence', `${editedItem.confidence}%`, 'confidence')}
              {editedItem.mitigations && editedItem.mitigations.length > 0 && (
                <div className="detail-field">
                  <label>Mitigations:</label>
                  <ul className="mitigations-list">
                    {editedItem.mitigations.map((m: string, idx: number) => (
                      <li key={idx}>{m}</li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          );
        }
        break;
        
      default:
        return null;
    }
    
    return null; // Return null if type guard fails
  }
}