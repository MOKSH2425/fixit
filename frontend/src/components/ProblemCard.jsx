import React from 'react';
import { AlertTriangle, Tag, Layers, CheckCircle } from 'lucide-react';

export default function ProblemCard({ title, problem, category, importantDetails = [] }) {
  if (!title && !problem) return null;

  const categoryLabels = {
    technical_error: 'Technical Error',
    campus_notice: 'Campus Notice',
    assignment: 'Assignment',
    instructions: 'Instructions',
    document: 'Document',
    general_problem: 'Problem',
    unknown: 'General',
  };

  const formattedCategory = categoryLabels[category] || category || 'Identified Issue';

  return (
    <div className="card problem-card">
      <div className="card-header">
        <div className="badge-group">
          <span className={`category-badge category-${category || 'default'}`}>
            <Layers size={13} />
            {formattedCategory}
          </span>
        </div>
      </div>

      <h3 className="problem-title">{title}</h3>
      <p className="problem-description">{problem}</p>

      {importantDetails && importantDetails.length > 0 && (
        <div className="details-container">
          <span className="details-label">Key Details:</span>
          <div className="tags-flex">
            {importantDetails.map((detail, i) => (
              <span key={i} className="detail-tag">
                <Tag size={11} />
                {detail}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
