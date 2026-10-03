import React, { useState } from 'react';
import { CheckSquare, Square, PlusCircle, Check, Loader2 } from 'lucide-react';

export default function Checklist({
  items = [],
  onCreateTasks,
  isCreatingTasks = false,
  tasksCreatedCount = 0,
}) {
  const [checkedMap, setCheckedMap] = useState({});

  if (!items || items.length === 0) return null;

  const toggleCheck = (index) => {
    setCheckedMap((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  return (
    <div className="card checklist-card">
      <div className="card-header">
        <div className="card-title-group">
          <CheckSquare size={18} className="card-icon" />
          <h3 className="card-title">Verification Checklist</h3>
        </div>

        {tasksCreatedCount > 0 && (
          <span className="tasks-created-badge">
            <Check size={14} /> ✓ {tasksCreatedCount} task{tasksCreatedCount > 1 ? 's' : ''} created
          </span>
        )}
      </div>

      <div className="checklist-items">
        {items.map((item, idx) => {
          const isChecked = !!checkedMap[idx];
          return (
            <div
              key={idx}
              className={`checklist-item ${isChecked ? 'item-checked' : ''}`}
              onClick={() => toggleCheck(idx)}
            >
              <div className="check-box">
                {isChecked ? (
                  <CheckSquare size={18} className="checked-icon" />
                ) : (
                  <Square size={18} className="unchecked-icon" />
                )}
              </div>
              <span className="checklist-text">{item}</span>
            </div>
          );
        })}
      </div>

      <div className="checklist-actions">
        <button
          type="button"
          className="create-tasks-btn"
          onClick={() => onCreateTasks(items)}
          disabled={isCreatingTasks}
        >
          {isCreatingTasks ? (
            <>
              <Loader2 size={16} className="spin-icon" />
              Creating SQLite Tasks...
            </>
          ) : (
            <>
              <PlusCircle size={16} />
              Create Tasks in Application ({items.length})
            </>
          )}
        </button>
      </div>
    </div>
  );
}
