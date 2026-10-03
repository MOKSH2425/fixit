import React, { useRef } from 'react';
import { Upload, Image as ImageIcon, Sparkles, AlertCircle } from 'lucide-react';

export default function ImageUploader({
  onFileSelected,
  selectedFile,
  previewUrl,
  message,
  onMessageChange,
  onAnalyze,
  isLoading,
  error,
}) {
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      onFileSelected(file);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    const file = e.dataTransfer.files?.[0];
    if (file) {
      onFileSelected(file);
    }
  };

  const loadDemoFile = async (path, filename, defaultMessage = '') => {
    try {
      const response = await fetch(path);
      const blob = await response.blob();
      const file = new File([blob], filename, { type: blob.type || 'image/png' });
      onFileSelected(file);
      if (defaultMessage) {
        onMessageChange(defaultMessage);
      }
    } catch (err) {
      console.error('Failed to load demo file:', err);
    }
  };

  return (
    <div className="uploader-container">
      {/* Quick Demo Pickers */}
      <div className="demo-presets">
        <span className="demo-presets-label">Quick Demos:</span>
        <button
          type="button"
          className="demo-btn demo-btn-error"
          onClick={() => loadDemoFile('/demo/technical_error.png', 'technical_error.png', 'Diagnose this error')}
          disabled={isLoading}
        >
          ⚡ Demo 1: Error Screenshot
        </button>
        <button
          type="button"
          className="demo-btn demo-btn-notice"
          onClick={() => loadDemoFile('/demo/sample_notice.png', 'sample_notice.png', 'Turn this notice into actionable items')}
          disabled={isLoading}
        >
          📋 Demo 2: College Notice
        </button>
      </div>

      {/* Dropzone */}
      <div
        className={`dropzone ${previewUrl ? 'has-preview' : ''}`}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={() => !previewUrl && fileInputRef.current?.click()}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept="image/png,image/jpeg,image/jpg,image/webp,application/pdf"
          style={{ display: 'none' }}
        />

        {!previewUrl ? (
          <div className="dropzone-empty">
            <div className="dropzone-icon-ring">
              <Upload className="dropzone-icon" size={28} />
            </div>
            <p className="dropzone-title">Upload a screenshot, photo, or PDF</p>
            <p className="dropzone-subtitle">Drag and drop or browse • PNG, JPG, WEBP, PDF (up to 20MB)</p>
          </div>
        ) : (
          <div className="preview-container">
            <img src={previewUrl} alt="Preview" className="preview-image" />
            <button
              type="button"
              className="change-image-btn"
              onClick={(e) => {
                e.stopPropagation();
                fileInputRef.current?.click();
              }}
              disabled={isLoading}
            >
              <ImageIcon size={14} /> Change File
            </button>
          </div>
        )}
      </div>

      {/* User Instruction Input */}
      <div className="input-group">
        <label htmlFor="user-instruction" className="input-label">
          Optional Instruction
        </label>
        <input
          id="user-instruction"
          type="text"
          value={message}
          onChange={(e) => onMessageChange(e.target.value)}
          placeholder="e.g. 'What should I do next?' or 'Extract deadlines and actions'"
          className="instruction-input"
          disabled={isLoading}
        />
      </div>

      {/* Error notification */}
      {error && (
        <div className="error-alert">
          <AlertCircle size={18} className="error-icon" />
          <span>{error}</span>
        </div>
      )}

      {/* Action Button */}
      <button
        type="button"
        className={`action-btn ${isLoading ? 'loading' : ''}`}
        onClick={onAnalyze}
        disabled={isLoading || !selectedFile}
      >
        {isLoading ? (
          <>
            <span className="spinner"></span>
            FixIt is analyzing...
          </>
        ) : (
          <>
            <Sparkles size={18} />
            Analyze &amp; Generate Action
          </>
        )}
      </button>
    </div>
  );
}
