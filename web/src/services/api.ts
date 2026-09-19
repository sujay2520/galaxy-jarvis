const API = 'http://localhost:8000';

export async function chatAPI(message: string) {
  const res = await fetch(`${API}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  });
  if (!res.ok) throw new Error('Chat API error');
  return res.json();
}

export async function createTask(description: string) {
  const res = await fetch(`${API}/api/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ description }),
  });
  if (!res.ok) throw new Error('Task API error');
  return res.json();
}

export async function getAgents() {
  const res = await fetch(`${API}/api/agents`);
  if (!res.ok) throw new Error('Agents API error');
  return res.json();
}

export async function getStatus() {
  const res = await fetch(`${API}/api/status`);
  if (!res.ok) throw new Error('Status API error');
  return res.json();
}

export async function getApprovals() {
  const res = await fetch(`${API}/api/approvals`);
  if (!res.ok) throw new Error('Approvals API error');
  return res.json();
}

export async function resolveApproval(requestId: string, approved: boolean) {
  const res = await fetch(`${API}/api/approve/${requestId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ approved }),
  });
  if (!res.ok) throw new Error('Approval resolve error');
  return res.json();
}

export async function getAuditLog(limit = 100) {
  const res = await fetch(`${API}/api/audit?limit=${limit}`);
  if (!res.ok) throw new Error('Audit API error');
  return res.json();
}

export const WS_URL = 'ws://localhost:8000/ws';
