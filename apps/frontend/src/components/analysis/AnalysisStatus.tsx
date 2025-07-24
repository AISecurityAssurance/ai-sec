import './AnalysisStatus.css';

export type AnalysisStatusType = 'completed' | 'running' | 'queued' | 'not-started';

interface AnalysisStatusProps {
  status: AnalysisStatusType;
  timestamp?: string;
}

const statusLabels: Record<AnalysisStatusType, string> = {
  'completed': 'Completed',
  'running': 'Running',
  'queued': 'Queued',
  'not-started': 'Not started'
};

export default function AnalysisStatus({ status, timestamp }: AnalysisStatusProps) {
  return (
    <span className={`analysis-status ${status}`}>
      <span className="status-dot" />
      {statusLabels[status]}
      {timestamp && status === 'completed' && (
        <span className="status-time"> • {timestamp}</span>
      )}
    </span>
  );
}