import React from 'react';
import { X, FileText } from 'lucide-react';

export default function ImagePreview({ previewUrl, fileName, fileSize, onClear }) {
  if (!previewUrl) return null;

  return (
    <div className="image-preview-card">
      <div className="preview-img-wrapper">
        <img src={previewUrl} alt={fileName || 'Uploaded Preview'} className="preview-img-tag" />
      </div>
      <div className="preview-info-row">
        <div className="file-meta">
          <FileText size={14} className="file-meta-icon" />
          <span className="file-name">{fileName || 'Uploaded image'}</span>
          {fileSize && <span className="file-size">({(fileSize / 1024).toFixed(1)} KB)</span>}
        </div>
        {onClear && (
          <button type="button" className="clear-img-btn" onClick={onClear} title="Remove image">
            <X size={14} /> Clear
          </button>
        )}
      </div>
    </div>
  );
}
