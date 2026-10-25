const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const USER_ID = 'demo-user';

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || `Request failed (${response.status})`);
  }
  return data;
}

export function getDashboardData() {
  return request('/api/dashboard/summary');
}

export function sendChatMessage(message) {
  return request('/api/assistant/chat', {
    method: 'POST',
    body: JSON.stringify({ user_id: USER_ID, message }),
  });
}

export function getMemoryLabData() {
  return request(`/api/memory-lab?user_id=${encodeURIComponent(USER_ID)}`);
}

export function saveMemory(memory) {
  return request('/api/memories', {
    method: 'POST',
    body: JSON.stringify({ ...memory, user_id: USER_ID }),
  });
}

export function deleteMemory(id) {
  return request(`/api/memories/${encodeURIComponent(id)}`, {
    method: 'DELETE',
  });
}
