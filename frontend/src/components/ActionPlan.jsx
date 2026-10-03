import React from 'react';
import { ListOrdered, ShieldAlert, ArrowRight } from 'lucide-react';

export default function ActionPlan({ actions = [], summary, priority = 'medium' }) {
  if (!actions || actions.length === 0) return null;

  const priorityClasses = {
    critical: 'priority-critical',
    high: 'priority-high',
    medium: 'priority-medium',
    low: 'priority-low',
  };

  return (
    <div className="card action-plan-card">
      <div className="card-header">
        <div className="card-title-group">
          <ListOrdered size={18} className="card-icon" />
          <h3 className="card-title">Action Plan</h3>
        </div>
        <span className={`priority-badge ${priorityClasses[priority] || 'priority-medium'}`}>
          <ShieldAlert size={12} />
          {priority.toUpperCase()} PRIORITY
        </span>
      </div>

      {summary && <p className="action-plan-summary">{summary}</p>}

      <ol className="action-steps-list">
        {actions.map((action, index) => (
          <li key={index} className="action-step-item">
            <span className="step-number">{index + 1}</span>
            <span className="step-content">{action}</span>
          </li>
        ))}
      </ol>
    </div>
  );
}
