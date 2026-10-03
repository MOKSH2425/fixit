import React from 'react';
import { CheckCircle2, Loader2, Cpu } from 'lucide-react';

export default function AgentActivity({ activities = [], isProcessing = false }) {
  if (!isProcessing && (!activities || activities.length === 0)) {
    return null;
  }

  const standardSteps = [
    'Image understood',
    'Problem identified',
    'Action plan generated',
    'Checklist generated',
    'Task created',
  ];

  const hasActivity = (stepText) => {
    return activities.some((act) => act.toLowerCase().includes(stepText.toLowerCase()));
  };

  return (
    <div className="agent-activity-card">
      <div className="activity-header">
        <div className="activity-title-group">
          <Cpu size={16} className="activity-icon" />
          <span className="activity-title">Gemma 4 Multimodal Agent Execution</span>
        </div>
        {isProcessing && (
          <span className="activity-status-badge running">
            <Loader2 size={12} className="spin-icon" /> Processing
          </span>
        )}
      </div>

      <div className="activity-steps-grid">
        {activities.map((act, idx) => (
          <div key={idx} className="activity-step-item completed">
            <CheckCircle2 size={16} className="step-check" />
            <span className="step-text">{act.replace(/^[✓\s]+/, '')}</span>
          </div>
        ))}

        {isProcessing && (
          <div className="activity-step-item pending">
            <Loader2 size={16} className="step-spinner spin-icon" />
            <span className="step-text">Orchestrating tools...</span>
          </div>
        )}
      </div>
    </div>
  );
}
