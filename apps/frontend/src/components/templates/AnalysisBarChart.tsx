import React, { useState } from 'react';
import { Edit2, Download, X, Check } from 'lucide-react';

interface BarChartDataItem {
  label: string;
  value: number;
  color?: string;
}

interface AnalysisBarChartProps {
  id: string;
  title: string;
  data: BarChartDataItem[];
  xAxisLabel?: string;
  yAxisLabel?: string;
  horizontal?: boolean;
  useColors?: boolean;
  defaultColor?: string;
  showPercentage?: boolean;
  onSave?: (id: string, data: any) => void;
}

export function AnalysisBarChart({
  id,
  title,
  data,
  xAxisLabel,
  yAxisLabel,
  horizontal = true,
  useColors = false,
  defaultColor = '#3498db',
  showPercentage = false,
  onSave
}: AnalysisBarChartProps) {
  const [isEditing, setIsEditing] = useState(false);
  const maxValue = Math.max(...data.map(item => item.value));
  const totalValue = data.reduce((sum, item) => sum + item.value, 0);
  
  const handleExport = () => {
    console.log('Export chart:', id);
  };

  const handleSave = () => {
    setIsEditing(false);
    if (onSave) {
      onSave(id, data);
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
  };

  const renderHorizontalBars = () => {
    return (
      <div style={{ marginTop: '20px' }}>
        {/* X-axis label */}
        {xAxisLabel && (
          <div style={{ 
            textAlign: 'center', 
            marginBottom: '10px',
            fontSize: '12px',
            fontWeight: 'bold',
            color: 'var(--text-primary, #000)'
          }}>
            {xAxisLabel}
          </div>
        )}
        
        {/* Bar chart container */}
        <div style={{ position: 'relative' }}>
          {/* Y-axis label */}
          {yAxisLabel && (
            <div style={{
              position: 'absolute',
              left: '-40px',
              top: '50%',
              transform: 'rotate(-90deg) translateX(-50%)',
              transformOrigin: 'center',
              fontSize: '12px',
              fontWeight: 'bold',
              whiteSpace: 'nowrap',
              color: 'var(--text-primary, #000)'
            }}>
              {yAxisLabel}
            </div>
          )}
          
          {/* Bars */}
          <div style={{ paddingLeft: '20px', paddingRight: '20px' }}>
            {data.map((item, index) => {
              const percentage = (item.value / maxValue) * 100;
              return (
                <div key={index} style={{ 
                  display: 'flex', 
                  alignItems: 'center',
                  marginBottom: '10px',
                  minHeight: '30px'
                }}>
                  {/* Label */}
                  <div style={{ 
                    width: '150px',
                    paddingRight: '15px',
                    textAlign: 'right',
                    fontSize: '12px',
                    flexShrink: 0,
                    color: 'var(--text-primary, #000)'
                  }}>
                    {item.label}
                  </div>
                  
                  {/* Bar */}
                  <div style={{ 
                    flex: 1,
                    display: 'flex',
                    alignItems: 'center',
                    position: 'relative'
                  }}>
                    <div style={{
                      height: '24px',
                      width: `${percentage}%`,
                      backgroundColor: useColors && item.color ? item.color : defaultColor,
                      borderRadius: '2px',
                      position: 'relative',
                      minWidth: '2px',
                      transition: 'width 0.3s ease'
                    }}>
                      {/* Value label */}
                      <span style={{
                        position: 'absolute',
                        right: '-5px',
                        top: '50%',
                        transform: 'translateY(-50%) translateX(100%)',
                        fontSize: '11px',
                        fontWeight: 'bold',
                        paddingLeft: '5px',
                        whiteSpace: 'nowrap',
                        color: 'var(--text-primary, #000)'
                      }}>
                        {showPercentage 
                          ? `${((item.value / totalValue) * 100).toFixed(1)}%`
                          : item.value
                        }
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
          
          {/* Grid lines */}
          <div style={{
            position: 'absolute',
            top: 0,
            left: '170px',
            right: '70px',
            bottom: 0,
            pointerEvents: 'none'
          }}>
            {[0, 25, 50, 75, 100].map(percent => (
              <div key={percent} style={{
                position: 'absolute',
                left: `${percent}%`,
                top: 0,
                bottom: 0,
                borderLeft: '1px solid var(--border-color, #e0e0e0)',
                zIndex: -1
              }} />
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderVerticalBars = () => {
    // Vertical bar implementation (if needed later)
    return <div>Vertical bars not implemented yet</div>;
  };

  return (
    <div style={{
      backgroundColor: 'var(--bg-primary, white)',
      border: '1px solid var(--border-color, #ddd)',
      borderRadius: 'var(--radius-lg, 8px)',
      padding: 'var(--space-4, 20px)',
      marginBottom: 'var(--space-4, 16px)'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '16px'
      }}>
        <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 'bold', color: 'var(--text-primary, #000)' }}>{title}</h3>
        <div style={{ display: 'flex', gap: '8px' }}>
          {isEditing ? (
            <>
              <button 
                onClick={handleSave} 
                style={{
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  padding: '4px',
                  color: 'var(--text-secondary, #666)'
                }}
                title="Save"
              >
                <Check size={16} />
              </button>
              <button 
                onClick={handleCancel} 
                style={{
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  padding: '4px',
                  color: 'var(--text-secondary, #666)'
                }}
                title="Cancel"
              >
                <X size={16} />
              </button>
            </>
          ) : (
            <>
              <button 
                onClick={() => setIsEditing(true)} 
                style={{
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  padding: '4px',
                  color: 'var(--text-secondary, #666)'
                }}
                title="Edit"
              >
                <Edit2 size={16} />
              </button>
              <button 
                onClick={handleExport} 
                style={{
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  padding: '4px',
                  color: 'var(--text-secondary, #666)'
                }}
                title="Export"
              >
                <Download size={16} />
              </button>
            </>
          )}
        </div>
      </div>
      
      {horizontal ? renderHorizontalBars() : renderVerticalBars()}
    </div>
  );
}