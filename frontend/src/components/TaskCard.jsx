import React from 'react';
import { Calendar, Tag, CheckCircle2, Circle } from 'lucide-react';

export default function TaskCard({ task, onToggleComplete, isUpdating = false }) {
  const isDone = task.completed;

  const categoryColors = {
    Academic: 'cat-academic',
    Technical: 'cat-technical',
    Campus: 'cat-campus',
    Personal: 'cat-personal',
    Other: 'cat-other',
  };

  return (
    <div className={`task-card ${isDone ? 'task-completed' : ''}`}>
      <button
        type="button"
        className="task-toggle-btn"
        onClick={() => onToggleComplete(task.id, !isDone)}
        disabled={isUpdating}
        aria-label={isDone ? 'Mark task incomplete' : 'Mark task complete'}
      >
        {isDone ? (
          <CheckCircle2 size={20} className="task-check-done" />
        ) : (
          <Circle size={20} className="task-check-empty" />
        )}
      </button>

      <div className="task-content">
        <div className="task-header-row">
          <h4 className="task-title">{task.title}</h4>
          <span className={`task-cat-badge ${categoryColors[task.category] || 'cat-other'}`}>
            <Tag size={10} />
            {task.category || 'Other'}
          </span>
        </div>

        {task.description && <p className="task-desc">{task.description}</p>}

        {task.deadline && (
          <div className="task-deadline">
            <Calendar size={12} />
            <span>Due: {task.deadline}</span>
          </div>
        )}
      </div>
    </div>
  );
}
