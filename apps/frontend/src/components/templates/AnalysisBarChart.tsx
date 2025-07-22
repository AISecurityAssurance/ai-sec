import React from 'react';
import { AnalysisChart } from './AnalysisChart';

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
  onSave
}: AnalysisBarChartProps) {
  // Prepare data for Chart.js
  const chartData = {
    labels: data.map(item => item.label),
    datasets: [{
      label: yAxisLabel || 'Value',
      data: data.map(item => item.value),
      backgroundColor: useColors 
        ? data.map(item => item.color || defaultColor)
        : defaultColor,
      borderColor: useColors
        ? data.map(item => item.color || defaultColor)
        : defaultColor,
      borderWidth: 1
    }]
  };

  const options = {
    indexAxis: horizontal ? 'y' as const : 'x' as const,
    responsive: true,
    maintainAspectRatio: false,
    layout: {
      padding: {
        left: 10,
        right: 30,
        top: 10,
        bottom: 10
      }
    },
    scales: {
      x: {
        beginAtZero: true,
        grid: {
          display: true,
          drawBorder: true
        },
        ticks: {
          stepSize: 1,
          padding: 5
        },
        title: horizontal && xAxisLabel ? {
          display: true,
          text: xAxisLabel,
          padding: { top: 10 }
        } : undefined
      },
      y: {
        grid: {
          display: false
        },
        ticks: {
          padding: 10,
          font: {
            size: 12
          }
        },
        title: !horizontal && yAxisLabel ? {
          display: true,
          text: yAxisLabel,
          padding: { bottom: 10 }
        } : undefined
      }
    },
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        enabled: true,
        callbacks: {
          label: function(context: any) {
            return `${context.parsed[horizontal ? 'x' : 'y']} ${yAxisLabel || 'items'}`;
          }
        }
      }
    }
  };

  return (
    <AnalysisChart
      id={id}
      title={title}
      type="bar"
      data={chartData}
      onSave={onSave}
    />
  );
}