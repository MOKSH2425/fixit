const API_BASE = 'http://127.0.0.1:8000';

/**
 * Send image and optional instruction to FixIt Agent
 */
export async function analyzeImage(imageFile, message = '') {
  const formData = new FormData();
  formData.append('image', imageFile);
  if (message && message.trim()) {
    formData.append('message', message.trim());
  }

  const response = await fetch(`${API_BASE}/agent`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    let errorDetail = 'Agent request failed';
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || errJson.error || errorDetail;
    } catch {
      errorDetail = response.statusText;
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

/**
 * Retrieve all persisted SQLite tasks
 */
export async function getTasks() {
  const response = await fetch(`${API_BASE}/tasks`);
  if (!response.ok) {
    throw new Error('Failed to fetch tasks from database');
  }
  return response.json();
}

/**
 * Create a new task directly in SQLite
 */
export async function createTask(taskData) {
  const response = await fetch(`${API_BASE}/tasks`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(taskData),
  });

  if (!response.ok) {
    let errMessage = 'Failed to create task';
    try {
      const err = await response.json();
      errMessage = err.detail || errMessage;
    } catch {
      // fallback
    }
    throw new Error(errMessage);
  }

  return response.json();
}

/**
 * Update task completion or other fields in SQLite
 */
export async function updateTask(taskId, updateData) {
  const response = await fetch(`${API_BASE}/tasks/${taskId}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(updateData),
  });

  if (!response.ok) {
    throw new Error(`Failed to update task #${taskId}`);
  }

  return response.json();
}
