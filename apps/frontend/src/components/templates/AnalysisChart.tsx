import { useState, useEffect } from 'react';
import { Edit2, Download, X, Check } from 'lucide-react';
import './AnalysisChart.css';

interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string | string[];
    borderColor?: string | string[];
  }[];
}

interface AnalysisChartProps {
  id: string;
  title: string;
  type: 'bar' | 'pie' | 'line' | 'doughnut' | 'radar';
  data: ChartData;
  editable?: boolean;
  onSave?: (id: string, data: ChartData) => void;
}

export function AnalysisChart({
  id,
  title,
  type,
  data: initialData,
  editable = true,
  onSave
}: AnalysisChartProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [data, setData] = useState(initialData);

  useEffect(() => {
    setData(initialData);
  }, [initialData]);

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleCancel = () => {
    setIsEditing(false);
    setData(initialData);
  };

  const handleSave = () => {
    setIsEditing(false);
    if (onSave) {
      onSave(id, data);
    }
  };

  const handleExport = () => {
    // Export as JSON for now
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${id}-chart-data.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Simple chart rendering (in production, use a library like Chart.js or Recharts)
  const renderChart = () => {
    if (type === 'bar') {
      const maxValue = Math.max(...data.datasets[0].data);
      return (
        <div className="chart-container bar-chart">
          {data.labels.map((label, i) => (
            <div key={i} className="bar-group">
              <div className="bar-label">{label}</div>
              <div className="bar-wrapper">
                <div 
                  className="bar"
                  style={{
                    width: `${(data.datasets[0].data[i] / maxValue) * 100}%`,
                    backgroundColor: Array.isArray(data.datasets[0].backgroundColor) 
                      ? data.datasets[0].backgroundColor[i] 
                      : data.datasets[0].backgroundColor || 'var(--primary)'
                  }}
                >
                  <span className="bar-value">{data.datasets[0].data[i]}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      );
    }

    if (type === 'pie' || type === 'doughnut') {
      const total = data.datasets[0].data.reduce((a, b) => a + b, 0);
      return (
        <div className="chart-container pie-chart">
          <div className="pie-legend">
            {data.labels.map((label, i) => (
              <div key={i} className="legend-item">
                <div 
                  className="legend-color"
                  style={{
                    backgroundColor: Array.isArray(data.datasets[0].backgroundColor) 
                      ? data.datasets[0].backgroundColor[i] 
                      : data.datasets[0].backgroundColor || 'var(--primary)'
                  }}
                />
                <span className="legend-label">{label}</span>
                <span className="legend-value">
                  {data.datasets[0].data[i]} ({((data.datasets[0].data[i] / total) * 100).toFixed(1)}%)
                </span>
              </div>
            ))}
          </div>
        </div>
      );
    }

    return <div className="chart-placeholder">Chart visualization for {type} chart</div>;
  };

  return (
    <div className="analysis-chart">
      <div className="analysis-chart-header">
        <h3>{title}</h3>
        {editable && (
          <div className="analysis-chart-toolbar">
            {isEditing ? (
              <>
                <button 
                  onClick={handleSave} 
                  className="icon-button"
                  title="Save"
                  aria-label="Save"
                >
                  <Check size={16} />
                </button>
                <button 
                  onClick={handleCancel} 
                  className="icon-button"
                  title="Cancel"
                  aria-label="Cancel"
                >
                  <X size={16} />
                </button>
              </>
            ) : (
              <>
                <button 
                  onClick={handleEdit} 
                  className="icon-button"
                  title="Edit"
                  aria-label="Edit"
                >
                  <Edit2 size={16} />
                </button>
                <button 
                  onClick={handleExport} 
                  className="icon-button"
                  title="Export"
                  aria-label="Export"
                >
                  <Download size={16} />
                </button>
              </>
            )}
          </div>
        )}
      </div>
      <div className="analysis-chart-content">
        {renderChart()}
      </div>
    </div>
  );
}