import React, { useState, useEffect } from 'react';
import ImageUploader from './components/ImageUploader';
import AgentActivity from './components/AgentActivity';
import ProblemCard from './components/ProblemCard';
import ActionPlan from './components/ActionPlan';
import Checklist from './components/Checklist';
import TaskList from './components/TaskList';
import { analyzeFile, getTasks, createTask, updateTask } from './services/api';
import { Zap, Wrench, ShieldCheck } from 'lucide-react';

export default function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState('');
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [agentActivity, setAgentActivity] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [updatingTaskId, setUpdatingTaskId] = useState(null);
  const [isCreatingTasks, setIsCreatingTasks] = useState(false);
  const [chatInput, setChatInput] = useState('');
  const [isChatting, setIsChatting] = useState(false);

  // Fetch persisted SQLite tasks on mount
  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      const data = await getTasks();
      setTasks(data);
    } catch (err) {
      console.error('Failed to load tasks:', err);
    }
  };

  const handleFileSelected = (file) => {
    setError('');
    setResult(null);
    setAgentActivity([]);
    setTasksCreatedCount(0);

    if (!file) {
      setSelectedFile(null);
      setPreviewUrl('');
      return;
    }

    // Validate size (20MB)
    if (file.size > 20 * 1024 * 1024) {
      setError('File is too large. Maximum supported size is 20MB.');
      return;
    }

    setSelectedFile(file);
    if (file.type.startsWith('image/')) {
      const objectUrl = URL.createObjectURL(file);
      setPreviewUrl(objectUrl);
    } else {
      // PDF or document preview
      setPreviewUrl('/demo/pdf-icon.png'); // fallback icon for document
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setError('Please upload a file first.');
      return;
    }

    setIsLoading(true);
    setError('');
    setTasksCreatedCount(0);
    setResult(null);
    setAgentActivity(['✓ File received by FixIt agent']);

    try {
      const response = await analyzeFile(selectedFile, message);
      if (!response.success) {
        setError(response.error || response.final_response || 'Analysis could not be completed.');
        setResult(response);
        if (response.agent_activity && response.agent_activity.length > 0) {
          setAgentActivity(response.agent_activity);
        }
      } else {
        setResult(response);
        setAgentActivity(response.agent_activity || ['✓ Image understood', '✓ Action plan generated']);
        // If agent already persisted tasks via tool:
        if (response.created_tasks && response.created_tasks.length > 0) {
          setTasksCreatedCount(response.created_tasks.length);
          await loadTasks();
        }
      }
    } catch (err) {
      setError(err.message || 'FixIt could not process this image right now. Check the AI configuration and try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFollowUp = async (e) => {
    e.preventDefault();
    if (!chatInput.trim() || !selectedFile || !result) return;

    setIsChatting(true);
    setAgentActivity((prev) => [...prev, '✓ Processing follow-up request...']);
    
    try {
      const response = await analyzeFile(selectedFile, chatInput, result);
      if (response.success) {
        setResult(response);
        setAgentActivity((prev) => [...prev, '✓ Action plan updated based on chat']);
      } else {
        setError(response.error || 'Follow-up analysis failed.');
      }
    } catch (err) {
      setError(err.message || 'Failed to process follow-up.');
    } finally {
      setIsChatting(false);
      setChatInput('');
    }
  };

  const handleCreateTasksFromChecklist = async (items) => {
    if (!items || items.length === 0) return;
    setIsCreatingTasks(true);
    let createdCount = 0;

    // Determine category based on current analysis
    let cat = 'Other';
    if (result?.category === 'campus_notice' || result?.category === 'assignment') {
      cat = 'Academic';
    } else if (result?.category === 'technical_error') {
      cat = 'Technical';
    }

    try {
      for (const item of items) {
        await createTask({
          title: item,
          description: result?.title ? `Derived from: ${result.title}` : undefined,
          category: cat,
          deadline: result?.important_details?.find((d) => /\d{4}|oct|nov|dec|jan|feb|mar|apr|may|jun|jul|aug|sep/i.test(d)),
        });
        createdCount++;
      }
      setTasksCreatedCount(createdCount);
      setAgentActivity((prev) => {
        if (!prev.includes('✓ Task created')) {
          return [...prev, '✓ Task created'];
        }
        return prev;
      });
      await loadTasks();
    } catch (err) {
      setError(`Your analysis succeeded, but the task could not be saved: ${err.message}`);
    } finally {
      setIsCreatingTasks(false);
    }
  };

  const handleToggleTask = async (taskId, newStatus) => {
    setUpdatingTaskId(taskId);
    try {
      const updated = await updateTask(taskId, { completed: newStatus });
      setTasks((prev) => prev.map((t) => (t.id === taskId ? updated : t)));
    } catch (err) {
      console.error('Failed to toggle task completion:', err);
    } finally {
      setUpdatingTaskId(null);
    }
  };

  return (
    <div className="app-container">
      {/* Top Navigation */}
      <header className="app-header">
        <div className="header-brand">
          <div className="brand-logo-badge">
            <Zap size={22} className="brand-logo-icon" />
          </div>
          <div>
            <div className="brand-name-row">
              <h1 className="brand-title">FIXIT</h1>
              <span className="brand-tag">Gemma 4 Action Agent</span>
            </div>
            <p className="brand-tagline">See a problem. Get an action.</p>
          </div>
        </div>

        <div className="header-badges">
          <span className="hack-badge">MLH Hacktoberfest '26</span>
          <span className="safety-badge">
            <ShieldCheck size={14} /> Safe Execution Sandbox
          </span>
        </div>
      </header>

      {/* Main Content Layout */}
      <main className="main-content">
        <div className="grid-layout">
          {/* Left Column: Multimodal Input & Agent Activity */}
          <section className="left-panel">
            <div className="panel-card">
              <div className="panel-header">
                <Wrench size={18} className="panel-icon" />
                <h2 className="panel-title">Multimodal Input</h2>
              </div>
              <p className="panel-subtitle">
                Feed FixIt an error screenshot, academic notice, or assignment sheet to receive immediate next steps.
              </p>

              <ImageUploader
                onFileSelected={handleFileSelected}
                selectedFile={selectedFile}
                previewUrl={previewUrl}
                message={message}
                onMessageChange={setMessage}
                onAnalyze={handleAnalyze}
                isLoading={isLoading}
                error={error}
              />
            </div>

            {/* Observable Agent Activity */}
            <AgentActivity activities={agentActivity} isProcessing={isLoading} />
          </section>

          {/* Right Column: Structured Results & Persistent Tasks */}
          <section className="right-panel">
            {/* When result exists */}
            {result && result.success && (
              <div className="results-container">
                <ProblemCard
                  title={result.title}
                  problem={result.problem}
                  category={result.category}
                  importantDetails={result.important_details}
                />

                <ActionPlan
                  actions={result.actions}
                  summary={result.final_response}
                  priority={result.category === 'technical_error' ? 'high' : 'medium'}
                />

                <Checklist
                  items={result.checklist}
                  onCreateTasks={handleCreateTasksFromChecklist}
                  isCreatingTasks={isCreatingTasks}
                  tasksCreatedCount={tasksCreatedCount}
                />

                {/* Follow-up Chat Box */}
                <div className="card chat-card" style={{ marginTop: '24px' }}>
                  <div className="card-header" style={{ marginBottom: '12px' }}>
                    <div className="card-title-group">
                      <Zap size={18} className="card-icon" />
                      <h3 className="card-title">Refine &amp; Chat</h3>
                    </div>
                  </div>
                  <form onSubmit={handleFollowUp} style={{ display: 'flex', gap: '10px' }}>
                    <input
                      type="text"
                      className="instruction-input"
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      placeholder="e.g. 'Make deadlines tighter', 'Skip step 3'"
                      style={{ flex: 1, marginTop: 0 }}
                      disabled={isChatting}
                    />
                    <button
                      type="submit"
                      className="action-btn"
                      style={{ width: 'auto', marginTop: 0, padding: '10px 16px' }}
                      disabled={isChatting || !chatInput.trim()}
                    >
                      {isChatting ? 'Updating...' : 'Send'}
                    </button>
                  </form>
                </div>
              </div>
            )}

            {/* When empty / initial */}
            {(!result || !result.success) && !isLoading && (
              <div className="initial-placeholder-card">
                <div className="placeholder-icon-circle">
                  <Zap size={32} />
                </div>
                <h3>Visual Action Agent Ready</h3>
                <p>
                  Upload an image on the left, or click one of the quick demo buttons (Demo 1: Error Screenshot or Demo 2: College Notice) to see Gemma 4 diagnose the problem and produce verified actions.
                </p>
                <div className="flow-steps-diagram">
                  <div className="diagram-step">
                    <span className="step-badge">1</span>
                    <span>SEE</span>
                  </div>
                  <span className="diagram-arrow">→</span>
                  <div className="diagram-step">
                    <span className="step-badge">2</span>
                    <span>UNDERSTAND</span>
                  </div>
                  <span className="diagram-arrow">→</span>
                  <div className="diagram-step">
                    <span className="step-badge">3</span>
                    <span>DECIDE</span>
                  </div>
                  <span className="diagram-arrow">→</span>
                  <div className="diagram-step">
                    <span className="step-badge">4</span>
                    <span>ACT</span>
                  </div>
                </div>
              </div>
            )}

            {/* Persistent SQLite Tasks Section */}
            <TaskList
              tasks={tasks}
              onToggleTask={handleToggleTask}
              updatingTaskId={updatingTaskId}
            />
          </section>
        </div>
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <div className="footer-content">
          <span>FixIt — Built with Gemma 4 &amp; Google GenAI for MLH Hack Day Surat 2026</span>
          <div className="footer-links">
            <span className="license-tag">MIT Open Source</span>
            <span className="rule-tag">The Model Decides • The Backend Executes</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
