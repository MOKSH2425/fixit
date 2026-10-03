import React from 'react';
import TaskCard from './TaskCard';
import { Database, CheckCircle2 } from 'lucide-react';

export default function TaskList({ tasks = [], onToggleTask, updatingTaskId = null }) {
  const completedCount = tasks.filter((t) => t.completed).length;

  return (
    <div className="task-list-section">
      <div className="task-list-header">
        <div className="task-list-title-group">
          <Database size={18} className="db-icon" />
          <h3 className="section-title">Persistent Application Tasks</h3>
          <span className="task-count-badge">
            {tasks.length} {tasks.length === 1 ? 'task' : 'tasks'}
          </span>
        </div>

        {tasks.length > 0 && (
          <div className="task-stats">
            <CheckCircle2 size={14} className="stats-check" />
            <span>
              {completedCount} of {tasks.length} completed
            </span>
          </div>
        )}
      </div>

      <p className="task-list-subtitle">
        Backed by local SQLite database. Survives browser refresh and app restart.
      </p>

      {tasks.length === 0 ? (
        <div className="empty-tasks-card">
          <p className="empty-text">No tasks yet.</p>
          <p className="empty-subtext">
            Upload an image or notice above, then click "Create Tasks" to persist action items.
          </p>
        </div>
      ) : (
        <div className="task-cards-grid">
          {tasks.map((task) => (
            <TaskCard
              key={task.id}
              task={task}
              onToggleComplete={onToggleTask}
              isUpdating={updatingTaskId === task.id}
            />
          ))}
        </div>
      )}
    </div>
  );
}
