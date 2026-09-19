export interface Agent {
  id: string;
  name: string;
  role: string;
  status: 'idle' | 'working' | 'waiting_approval' | 'completed' | 'error';
  current_task?: string;
}

export interface ApprovalRequest {
  id: string;
  agent_id: string;
  action: string;
  risk: 'low' | 'medium' | 'high' | 'critical';
  details: Record<string, string>;
  status: string;
  created_at: number;
}

export interface AuditEntry {
  timestamp: number;
  iso_time: string;
  agent_id: string;
  action: string;
  permission: string | null;
  scope: string | null;
  result: 'allowed' | 'denied' | 'error';
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'agent' | 'system' | 'thinking';
  agentName?: string;
  agentRole?: string;
  content: string;
  timestamp: string;
  isTask?: boolean;
}

export interface SystemStatus {
  status: string;
  version: string;
  agents: { total: number; working: number };
  llm: { local_ollama: string; gemini_api: string; groq_api: string };
  pending_approvals: number;
}
