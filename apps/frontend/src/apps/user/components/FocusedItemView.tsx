import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Edit3, Save, AlertTriangle, ShieldAlert, Users, Zap, Target } from 'lucide-react';
import { useState, useEffect } from 'react';
import { useAnalysisStore } from '../stores/analysisStore';
import { useBroadcastSync } from '../hooks/useBroadcastChannel';
import { getRelatedData } from '../mockData/stpaSecData';
import './FocusedItemView.css';

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
  const [editedItem, setEditedItem] = useState(item);
  
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
        updateLosses(losses.map(l => l.id === itemId ? editedItem : l));
        break;
      case 'hazard':
        updateHazards(hazards.map(h => h.id === itemId ? editedItem : h));
        break;
      case 'controller':
        updateControllers(controllers.map(c => c.id === itemId ? editedItem : c));
        break;
      case 'control-action':
        updateControlActions(controlActions.map(ca => ca.id === itemId ? editedItem : ca));
        break;
      case 'uca':
        updateUcas(ucas.map(u => u.id === itemId ? editedItem : u));
        break;
      case 'scenario':
        updateScenarios(scenarios.map(s => s.id === itemId ? editedItem : s));
        break;
    }
    
    setIsEditMode(false);
  };
  
  const handleCancel = () => {
    setEditedItem(item);
    setIsEditMode(false);
  };
  
  const related = getRelatedData(itemId, itemType);
  
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
    
    const renderField = (label: string, value: any, key: string, options?: Array<{value: string, label: string}>) => {
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
                onChange={(e) => setEditedItem({...editedItem, [key]: e.target.value})}
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
              onChange={(e) => setEditedItem({...editedItem, [key]: e.target.value})}
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
        return (
          <>
            {renderField('ID', editedItem.id, 'id')}
            {renderField('Description', editedItem.description, 'description')}
            {renderField('Severity', editedItem.severity, 'severity', severityOptions)}
            {renderField('Category', editedItem.category, 'category')}
            {renderField('Stakeholders', editedItem.stakeholders, 'stakeholders')}
          </>
        );
        
      case 'hazard':
        return (
          <>
            {renderField('ID', editedItem.id, 'id')}
            {renderField('Description', editedItem.description, 'description')}
            {renderField('Severity', editedItem.severity, 'severity', severityOptions)}
            {renderField('Related Losses', editedItem.relatedLosses, 'relatedLosses')}
            {renderField('Worst Case Scenario', editedItem.worstCase, 'worstCase')}
          </>
        );
        
      case 'controller':
        return (
          <>
            {renderField('ID', editedItem.id, 'id')}
            {renderField('Name', editedItem.name, 'name')}
            {renderField('Type', editedItem.type, 'type')}
            {renderField('Responsibilities', editedItem.responsibilities, 'responsibilities')}
          </>
        );
        
      case 'control-action':
        return (
          <>
            {renderField('ID', editedItem.id, 'id')}
            {renderField('Action', editedItem.action, 'action')}
            {renderField('Controller', editedItem.controllerId, 'controllerId')}
            {renderField('Target Process', editedItem.targetProcess, 'targetProcess')}
            {renderField('Constraints', editedItem.constraints, 'constraints')}
          </>
        );
        
      case 'uca':
        const ucaTypeOptions = [
          { value: 'not-provided', label: 'Not Provided' },
          { value: 'provided-causes-hazard', label: 'Provided Causes Hazard/Vulnerability' },
          { value: 'wrong-timing', label: 'Wrong Timing/Order' },
          { value: 'stopped-too-soon', label: 'Stopped Too Soon/Applied Too Long' }
        ];
        
        return (
          <>
            {renderField('ID', editedItem.id, 'id')}
            {renderField('Control Action', editedItem.controlActionId, 'controlActionId')}
            {renderField('Type', editedItem.type, 'type', ucaTypeOptions)}
            {renderField('Description', editedItem.description, 'description')}
            {renderField('Context', editedItem.context, 'context')}
            {renderField('Hazards/Vulnerabilities', editedItem.hazards, 'hazards')}
            {renderField('Severity', editedItem.severity, 'severity', severityOptions)}
          </>
        );
        
      case 'scenario':
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
                  {editedItem.mitigations.map((m: any, idx: number) => (
                    <li key={idx}>
                      <strong>{m.type}:</strong> {m.description}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </>
        );
        
      default:
        return null;
    }
  }
}