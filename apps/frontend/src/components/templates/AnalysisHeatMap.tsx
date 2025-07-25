import React from 'react';
import { AnalysisDiagram } from './AnalysisDiagram';

interface HeatMapCell {
  row: string;
  col: string;
  value: number;
  label?: string;
  tooltip?: string;
  data?: any; // Additional data for click handling
}

interface HeatMapConfig {
  rows: string[];
  cols: string[];
  cells: HeatMapCell[];
  colorScale?: {
    min: { value: number; color: string; label?: string };
    low?: { value: number; color: string; label?: string };
    medium?: { value: number; color: string; label?: string };
    high?: { value: number; color: string; label?: string };
    max: { value: number; color: string; label?: string };
  };
  xAxisLabel?: string;
  yAxisLabel?: string;
}

interface AnalysisHeatMapProps {
  id: string;
  title: string;
  config: HeatMapConfig;
  onSave?: (id: string, data: any) => void;
  onCellClick?: (cell: HeatMapCell) => void;
}

export function AnalysisHeatMap({
  id,
  title,
  config,
  onSave,
  onCellClick
}: AnalysisHeatMapProps) {
  const { rows, cols, cells, colorScale, xAxisLabel, yAxisLabel } = config;

  // Default color scale if not provided
  const defaultColorScale = {
    min: { value: 1, color: '#27ae60', label: 'Very Low' },
    low: { value: 2, color: '#2ecc71', label: 'Low' },
    medium: { value: 3, color: '#f1c40f', label: 'Medium' },
    high: { value: 4, color: '#f39c12', label: 'High' },
    max: { value: 5, color: '#e74c3c', label: 'Critical' }
  };

  const scale = colorScale || defaultColorScale;

  // Get color for a value
  const getColor = (value: number) => {
    if (value <= scale.min.value) return scale.min.color;
    if (scale.low && value <= scale.low.value) return scale.low.color;
    if (scale.medium && value <= scale.medium.value) return scale.medium.color;
    if (scale.high && value <= scale.high.value) return scale.high.color;
    return scale.max.color;
  };

  // Create a map for quick cell lookup
  const cellMap = new Map<string, HeatMapCell>();
  cells.forEach(cell => {
    cellMap.set(`${cell.row}-${cell.col}`, cell);
  });

  return (
    <AnalysisDiagram id={id} title={title} onSave={onSave}>
      <div style={{ marginTop: '20px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: `120px repeat(${cols.length}, 1fr)`, gap: '2px', backgroundColor: '#f5f5f5', padding: '10px' }}>
          {/* Empty corner cell */}
          <div></div>
          
          {/* Column headers */}
          {cols.map(col => (
            <div
              key={col}
              style={{
                textAlign: 'center',
                fontWeight: 'bold',
                fontSize: '12px',
                padding: '10px 5px',
                backgroundColor: 'white'
              }}
            >
              {col}
            </div>
          ))}
          
          {/* Rows */}
          {rows.map(row => (
            <React.Fragment key={row}>
              {/* Row label */}
              <div
                style={{
                  fontWeight: 'bold',
                  fontSize: '12px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'flex-end',
                  paddingRight: '10px',
                  backgroundColor: 'white'
                }}
              >
                {row}
              </div>
              
              {/* Cells */}
              {cols.map(col => {
                const cell = cellMap.get(`${row}-${col}`);
                if (!cell) {
                  return (
                    <div
                      key={`${row}-${col}`}
                      style={{
                        backgroundColor: '#f0f0f0',
                        minHeight: '60px'
                      }}
                    />
                  );
                }
                
                return (
                  <div
                    key={`${row}-${col}`}
                    style={{
                      backgroundColor: getColor(cell.value),
                      minHeight: '60px',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center',
                      cursor: (onCellClick && cell.label && cell.label !== '0') ? 'pointer' : 'default',
                      position: 'relative',
                      transition: 'opacity 0.2s'
                    }}
                    title={cell.tooltip}
                    onClick={() => {
                      if (onCellClick && cell.label && cell.label !== '0') {
                        onCellClick(cell);
                      }
                    }}
                    onMouseEnter={(e) => {
                      if (onCellClick && cell.label && cell.label !== '0') {
                        e.currentTarget.style.opacity = '0.8';
                      }
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.opacity = '1';
                    }}
                  >
                    {cell.label && (
                      <span style={{ fontSize: '20px', fontWeight: 'bold', color: 'white' }}>
                        {cell.label}
                      </span>
                    )}
                    {onCellClick && cell.label && cell.label !== '0' && (
                      <span style={{ fontSize: '11px', color: 'white', marginTop: '2px' }}>
                        Click for details
                      </span>
                    )}
                  </div>
                );
              })}
            </React.Fragment>
          ))}
        </div>
        
        {/* Axes labels */}
        <div style={{ marginTop: '20px', textAlign: 'center' }}>
          {xAxisLabel && (
            <div style={{ fontWeight: 'bold', fontSize: '14px' }}>
              {xAxisLabel}
            </div>
          )}
        </div>
        
        {yAxisLabel && (
          <div
            style={{
              position: 'absolute',
              left: '-40px',
              top: '50%',
              transform: 'rotate(-90deg)',
              transformOrigin: 'center',
              fontWeight: 'bold',
              fontSize: '14px'
            }}
          >
            {yAxisLabel}
          </div>
        )}
        
        {/* Legend */}
        <div style={{ marginTop: '20px', display: 'flex', justifyContent: 'center', gap: '20px', fontSize: '12px' }}>
          {Object.entries(scale).map(([key, config]) => (
            config && (
              <div key={key} style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                <div style={{ width: '20px', height: '20px', backgroundColor: config.color, border: '1px solid #ddd' }} />
                <span>{config.label || `${key} (${config.value})`}</span>
              </div>
            )
          ))}
        </div>
      </div>
    </AnalysisDiagram>
  );
}