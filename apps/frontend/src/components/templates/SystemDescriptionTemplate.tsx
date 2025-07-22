import React, { useState } from 'react';
import { Edit2, X, Save, Download } from 'lucide-react';
import MissionStatementEditor from '../../apps/user/components/MissionStatementEditor';
import { AnalysisList } from './AnalysisList';
import { AnalysisText } from './AnalysisText';
import { getSectionUrl } from './utils';
import './SystemDescriptionTemplate.css';

interface SystemDescriptionTemplateProps {
  id: string;
  missionStatement: {
    purpose: string;
    method: string;
    goals: string[];
    constraints: string[];
  };
  fullDescription?: string;
  systemGoals: string[];
  systemConstraints: string[];
  assumptions: string[];
  boundariesIncluded: string[];
  boundariesExcluded: string[];
  onSave?: (id: string, data: any) => void;
}

export function SystemDescriptionTemplate({
  id,
  missionStatement,
  fullDescription = '',
  systemGoals,
  systemConstraints,
  assumptions,
  boundariesIncluded,
  boundariesExcluded,
  onSave
}: SystemDescriptionTemplateProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [data, setData] = useState({
    missionStatement,
    fullDescription,
    systemGoals,
    systemConstraints,
    assumptions,
    boundariesIncluded,
    boundariesExcluded
  });

  const handleEdit = () => setIsEditing(true);
  const handleCancel = () => {
    setIsEditing(false);
    setData({
      missionStatement,
      fullDescription,
      systemGoals,
      systemConstraints,
      assumptions,
      boundariesIncluded,
      boundariesExcluded
    });
  };
  
  const handleSave = () => {
    if (onSave) onSave(id, data);
    setIsEditing(false);
  };
  
  const handleExport = () => console.log('Export system description:', id);

  const updateMissionStatement = (updates: Partial<typeof missionStatement>) => {
    setData(prev => ({
      ...prev,
      missionStatement: { ...prev.missionStatement, ...updates }
    }));
  };

  return (
    <div className={`system-description-template ${isEditing ? 'editing' : ''}`}>
      <div className="system-header">
        <a 
          href={getSectionUrl(id)}
          className="system-title-link"
          onClick={(e) => e.preventDefault()}
        >
          <h4 className="system-title">System Description</h4>
        </a>
        
        <div className="system-toolbar">
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
                title="Edit system description"
                aria-label="Edit system description"
              >
                <Edit2 size={16} />
              </button>
              <button 
                className="toolbar-btn export" 
                onClick={handleExport}
                title="Export system description"
                aria-label="Export system description"
              >
                <Download size={16} />
              </button>
            </>
          )}
        </div>
      </div>

      <div className="system-content">
        <div className="mission-section">
          <h5>Mission Statement</h5>
          <MissionStatementEditor
            purpose={data.missionStatement.purpose}
            method={data.missionStatement.method}
            goals={data.missionStatement.goals}
            constraints={data.missionStatement.constraints}
            onUpdate={updateMissionStatement}
            isEditing={isEditing}
          />
        </div>

        <div className="full-description-section">
          <AnalysisText
            id={`${id}-full-description`}
            title="Full System Description"
            content={data.fullDescription}
            onSave={(id, textData) => setData(prev => ({ ...prev, fullDescription: textData.content }))}
            editable={isEditing}
          />
        </div>

        <div className="lists-section">
          <AnalysisList
            id={`${id}-system-goals`}
            title="System Goals"
            items={data.systemGoals}
            placeholder="Add system goal"
            onSave={(id, listData) => setData(prev => ({ ...prev, systemGoals: listData.items }))}
          />

          <AnalysisList
            id={`${id}-system-constraints`}
            title="System Constraints"
            items={data.systemConstraints}
            placeholder="Add constraint"
            onSave={(id, listData) => setData(prev => ({ ...prev, systemConstraints: listData.items }))}
          />

          <AnalysisList
            id={`${id}-assumptions`}
            title="Assumptions"
            items={data.assumptions}
            placeholder="Add assumption"
            onSave={(id, listData) => setData(prev => ({ ...prev, assumptions: listData.items }))}
          />

          <div className="boundaries-section">
            <AnalysisList
              id={`${id}-boundaries-included`}
              title="Included in System Boundary"
              items={data.boundariesIncluded}
              placeholder="Add included boundary"
              onSave={(id, listData) => setData(prev => ({ ...prev, boundariesIncluded: listData.items }))}
            />

            <AnalysisList
              id={`${id}-boundaries-excluded`}
              title="Excluded from System Boundary"
              items={data.boundariesExcluded}
              placeholder="Add excluded boundary"
              onSave={(id, listData) => setData(prev => ({ ...prev, boundariesExcluded: listData.items }))}
            />
          </div>
        </div>
      </div>
    </div>
  );
}