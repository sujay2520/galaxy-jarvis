import os

base_dir = r"c:\Users\jarvis\Desktop\Jarvis AG\web"

files = {
    "tailwind.config.js": """/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        galaxy: {
          900: '#0a0a1a',
          800: '#11112b',
          700: '#1a1a3a',
          accent: '#3b82f6',
          highlight: '#8b5cf6'
        }
      },
      animation: {
        'pulse-fast': 'pulse 1s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}
""",
    "src/index.css": """@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  @apply bg-galaxy-900 text-gray-100;
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
""",
    "src/types/index.ts": """export interface Agent {
  id: string;
  name: string;
  role: string;
  status: 'idle' | 'working' | 'waiting' | 'error';
  currentTask?: string;
  permissions: string[];
}

export interface Permission {
  permission: string;
  scope?: string;
  expires_in_minutes?: number;
}

export interface ApprovalRequest {
  id: string;
  agentId: string;
  agentName: string;
  action: string;
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  details: string;
}

export interface AuditEvent {
  id: string;
  timestamp: string;
  agent: string;
  action: string;
  permission: string;
  result: 'allowed' | 'denied';
  target: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'agent' | 'system';
  agentName?: string;
  agentRole?: string;
  content: string;
  timestamp: string;
}
""",
    "src/services/api.ts": """const API_BASE = 'http://localhost:8000/api';

export const api = {
  getAgents: async () => {
    const res = await fetch(`${API_BASE}/agents`);
    return res.json();
  },
  getAgent: async (id: string) => {
    const res = await fetch(`${API_BASE}/agents/${id}`);
    return res.json();
  },
  grantPermission: async (id: string, permission: any) => {
    const res = await fetch(`${API_BASE}/agents/${id}/permissions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(permission)
    });
    return res.json();
  },
  revokePermission: async (id: string, permission: string) => {
    const res = await fetch(`${API_BASE}/agents/${id}/permissions/${permission}`, {
      method: 'DELETE'
    });
    return res.json();
  },
  getAudit: async () => {
    const res = await fetch(`${API_BASE}/audit`);
    return res.json();
  },
  sendChat: async (message: string) => {
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    return res.json();
  },
  approveAction: async (id: string) => {
    const res = await fetch(`${API_BASE}/approve/${id}`, { method: 'POST' });
    return res.json();
  },
  createTask: async (description: string) => {
    const res = await fetch(`${API_BASE}/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description })
    });
    return res.json();
  }
};
""",
    "src/hooks/useWebSocket.ts": """import { useState, useEffect, useRef } from 'react';

export function useWebSocket(url: string) {
  const [messages, setMessages] = useState<any[]>([]);
  const [status, setStatus] = useState<'connecting' | 'connected' | 'disconnected'>('connecting');
  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<number | null>(null);
  const reconnectAttempts = useRef(0);

  useEffect(() => {
    function connect() {
      setStatus('connecting');
      ws.current = new WebSocket(url);

      ws.current.onopen = () => {
        setStatus('connected');
        reconnectAttempts.current = 0;
      };

      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setMessages(prev => [...prev, data]);
        } catch (e) {
          console.error("WS parse error", e);
        }
      };

      ws.current.onclose = () => {
        setStatus('disconnected');
        const timeout = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
        reconnectAttempts.current += 1;
        reconnectTimeout.current = window.setTimeout(connect, timeout);
      };
      
      ws.current.onerror = () => {
        ws.current?.close();
      };
    }

    connect();

    return () => {
      if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
      ws.current?.close();
    };
  }, [url]);

  return { messages, status, ws: ws.current };
}
""",
    "src/hooks/useVoiceInput.ts": """import { useState, useEffect, useRef } from 'react';

export function useVoiceInput(onComplete: (text: string) => void) {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const recognition = useRef<any>(null);
  const silenceTimer = useRef<number | null>(null);

  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      recognition.current = new SpeechRecognition();
      recognition.current.continuous = true;
      recognition.current.interimResults = true;

      recognition.current.onresult = (event: any) => {
        let currentTranscript = '';
        for (let i = 0; i < event.results.length; i++) {
          currentTranscript += event.results[i][0].transcript;
        }
        setTranscript(currentTranscript);
        
        if (silenceTimer.current) clearTimeout(silenceTimer.current);
        silenceTimer.current = window.setTimeout(() => {
          stopListening(currentTranscript);
        }, 2000);
      };

      recognition.current.onend = () => {
        setIsListening(false);
      };
    }
    
    return () => {
      if (silenceTimer.current) clearTimeout(silenceTimer.current);
      if (recognition.current) recognition.current.stop();
    };
  }, []);

  const startListening = () => {
    setTranscript('');
    setIsListening(true);
    recognition.current?.start();
  };

  const stopListening = (finalText: string = transcript) => {
    setIsListening(false);
    recognition.current?.stop();
    if (finalText.trim()) {
      onComplete(finalText.trim());
    }
  };

  const toggle = () => {
    if (isListening) stopListening();
    else startListening();
  };

  return { isListening, transcript, toggle, supported: !!recognition.current };
}
""",
    "src/components/VoiceInput.tsx": """import { Mic, MicOff } from 'lucide-react';
import { clsx } from 'clsx';
import { useVoiceInput } from '../hooks/useVoiceInput';

export default function VoiceInput({ onSend }: { onSend: (text: string) => void }) {
  const { isListening, toggle, transcript, supported } = useVoiceInput((text) => {
    onSend(text);
  });

  if (!supported) return null;

  return (
    <div className="relative">
      <button 
        type="button"
        onClick={toggle}
        className={clsx(
          "p-3 rounded-full transition-all duration-300",
          isListening ? "bg-galaxy-accent text-white animate-pulse" : "bg-galaxy-800 text-gray-400 hover:text-white"
        )}
      >
        {isListening ? <Mic className="w-5 h-5" /> : <MicOff className="w-5 h-5" />}
      </button>
      {isListening && transcript && (
        <div className="absolute bottom-full mb-2 right-0 bg-galaxy-800 text-sm text-gray-200 p-2 rounded-lg whitespace-nowrap overflow-hidden text-ellipsis max-w-xs border border-galaxy-700">
          {transcript}
        </div>
      )}
    </div>
  );
}
""",
    "src/components/ChatMessage.tsx": """import { clsx } from 'clsx';
import { ChatMessage as IChatMessage } from '../types';
import { User, Bot, ShieldAlert } from 'lucide-react';

export default function ChatMessage({ msg }: { msg: IChatMessage }) {
  const isUser = msg.role === 'user';
  
  return (
    <div className={clsx("flex gap-4 p-4 rounded-xl", isUser ? "bg-transparent" : "bg-galaxy-800 border border-galaxy-700 shadow-lg")}>
      <div className={clsx("w-8 h-8 rounded-full flex items-center justify-center shrink-0", 
        isUser ? "bg-galaxy-accent text-white" : "bg-galaxy-highlight text-white")}>
        {isUser ? <User size={18} /> : (msg.role === 'system' ? <ShieldAlert size={18} /> : <Bot size={18} />)}
      </div>
      <div className="flex-1 space-y-1">
        <div className="flex items-center gap-2">
          <span className="font-medium text-gray-200">
            {isUser ? 'You' : (msg.agentName || 'System')}
          </span>
          {msg.agentRole && (
            <span className="text-xs px-2 py-0.5 rounded-full bg-galaxy-700 text-galaxy-accent">
              {msg.agentRole}
            </span>
          )}
          <span className="text-xs text-gray-500">{new Date(msg.timestamp).toLocaleTimeString()}</span>
        </div>
        <div className="text-gray-300 leading-relaxed whitespace-pre-wrap">
          {msg.content}
        </div>
      </div>
    </div>
  );
}
""",
    "src/components/ChatView.tsx": """import { useState, useRef, useEffect } from 'react';
import { Send } from 'lucide-react';
import ChatMessage from './ChatMessage';
import VoiceInput from './VoiceInput';
import { ChatMessage as IChatMessage } from '../types';

export default function ChatView() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<IChatMessage[]>([
    { id: '1', role: 'system', content: 'Welcome to Galaxy Jarvis. How can I assist you today?', timestamp: new Date().toISOString() }
  ]);
  const endRef = useRef<HTMLDivElement>(null);

  const handleSend = (text: string) => {
    if (!text.trim()) return;
    const newMsg: IChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, newMsg]);
    setInput('');
    // Simulate agent reply
    setTimeout(() => {
      setMessages(prev => [...prev, {
        id: (Date.now()+1).toString(),
        role: 'agent',
        agentName: 'CoderAgent',
        agentRole: 'Developer',
        content: `I received your request: "${text}". Processing...`,
        timestamp: new Date().toISOString()
      }]);
    }, 1000);
  };

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex flex-col h-full bg-galaxy-900">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map(msg => (
          <ChatMessage key={msg.id} msg={msg} />
        ))}
        <div ref={endRef} />
      </div>
      <div className="p-4 bg-galaxy-900 border-t border-galaxy-800">
        <div className="flex items-center gap-2 max-w-4xl mx-auto">
          <input 
            type="text" 
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSend(input)}
            placeholder="Type your message..."
            className="flex-1 bg-galaxy-800 border border-galaxy-700 rounded-full px-6 py-3 text-white focus:outline-none focus:border-galaxy-accent transition-colors shadow-inner"
          />
          <VoiceInput onSend={handleSend} />
          <button 
            onClick={() => handleSend(input)}
            className="p-3 bg-galaxy-accent text-white rounded-full hover:bg-blue-400 transition-colors shadow-lg shadow-blue-500/20"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
""",
    "src/components/AgentCard.tsx": """import { Agent } from '../types';
import { Bot, Activity } from 'lucide-react';
import { clsx } from 'clsx';

export default function AgentCard({ agent }: { agent: Agent }) {
  const statusColors = {
    idle: 'bg-green-500',
    working: 'bg-blue-500',
    waiting: 'bg-yellow-500',
    error: 'bg-red-500'
  };

  return (
    <div className="bg-galaxy-800/50 backdrop-blur-md border border-galaxy-700 rounded-xl p-5 hover:border-galaxy-accent/50 transition-all cursor-pointer group shadow-lg">
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-galaxy-900 rounded-lg group-hover:scale-110 transition-transform">
            <Bot className="w-6 h-6 text-galaxy-highlight" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-100">{agent.name}</h3>
            <p className="text-xs text-gray-400">{agent.role}</p>
          </div>
        </div>
        <div className="flex items-center gap-1.5">
          <span className={clsx("w-2.5 h-2.5 rounded-full animate-pulse", statusColors[agent.status])}></span>
          <span className="text-xs text-gray-300 capitalize">{agent.status}</span>
        </div>
      </div>
      
      {agent.currentTask && (
        <div className="mt-4 mb-4 bg-galaxy-900/50 p-3 rounded-lg border border-galaxy-700/50">
          <div className="flex items-center gap-2 text-xs text-gray-400 mb-1">
            <Activity className="w-3 h-3" /> Current Task
          </div>
          <p className="text-sm text-gray-200 truncate">{agent.currentTask}</p>
        </div>
      )}

      <div className="flex flex-wrap gap-2 mt-4">
        {agent.permissions.map(p => (
          <span key={p} className="px-2.5 py-1 rounded-full text-xs bg-galaxy-700/50 text-galaxy-accent border border-galaxy-600/50">
            {p}
          </span>
        ))}
      </div>
    </div>
  );
}
""",
    "src/components/AgentsDashboard.tsx": """import AgentCard from './AgentCard';
import { Agent } from '../types';
import { Plus } from 'lucide-react';

const mockAgents: Agent[] = [
  { id: '1', name: 'DevBot', role: 'Software Engineer', status: 'working', currentTask: 'Building Web UI components', permissions: ['fs.read', 'fs.write', 'shell'] },
  { id: '2', name: 'TestBot', role: 'QA Engineer', status: 'idle', permissions: ['fs.read', 'shell'], currentTask: undefined },
  { id: '3', name: 'DeployBot', role: 'DevOps', status: 'waiting', currentTask: 'Awaiting approval for prod deploy', permissions: ['aws.deploy', 'github.commit'] }
];

export default function AgentsDashboard() {
  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white mb-1">Agents Fleet</h1>
          <p className="text-gray-400 text-sm">Monitor and manage your autonomous agents</p>
        </div>
        <button className="flex items-center gap-2 bg-galaxy-accent hover:bg-blue-400 text-white px-4 py-2 rounded-lg transition-colors shadow-lg shadow-blue-500/20">
          <Plus className="w-4 h-4" />
          <span>Spawn Agent</span>
        </button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {mockAgents.map(agent => (
          <AgentCard key={agent.id} agent={agent} />
        ))}
      </div>
    </div>
  );
}
""",
    "src/components/PermissionsManager.tsx": """import { Shield, Key, Check, X } from 'lucide-react';

export default function PermissionsManager() {
  const agents = ['DevBot', 'TestBot', 'DeployBot'];
  const permissionsList = ['fs.read', 'fs.write', 'shell', 'net.http', 'aws.deploy'];

  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-1">Permissions Manager</h1>
        <p className="text-gray-400 text-sm">Control what your agents are allowed to do</p>
      </div>

      <div className="bg-galaxy-800 border border-galaxy-700 rounded-xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-galaxy-900 text-gray-300">
              <tr>
                <th className="px-6 py-4 font-medium flex items-center gap-2"><Shield className="w-4 h-4" /> Permission</th>
                {agents.map(a => <th key={a} className="px-6 py-4 font-medium text-center">{a}</th>)}
              </tr>
            </thead>
            <tbody className="divide-y divide-galaxy-700">
              {permissionsList.map((perm, i) => (
                <tr key={perm} className="hover:bg-galaxy-800/80 transition-colors">
                  <td className="px-6 py-4 font-mono text-galaxy-accent flex items-center gap-2">
                    <Key className="w-3 h-3 text-gray-500" /> {perm}
                  </td>
                  {agents.map((a, j) => {
                    const hasPerm = (i + j) % 2 === 0;
                    return (
                      <td key={a} className="px-6 py-4 text-center">
                        <button className={`w-8 h-8 rounded-full inline-flex items-center justify-center transition-colors ${hasPerm ? 'bg-galaxy-accent/20 text-galaxy-accent' : 'bg-galaxy-900 text-gray-600 hover:bg-galaxy-700'}`}>
                          {hasPerm ? <Check className="w-4 h-4" /> : <X className="w-4 h-4" />}
                        </button>
                      </td>
                    )
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
""",
    "src/components/ApprovalQueue.tsx": """import { ApprovalRequest } from '../types';
import { AlertTriangle, Check, X } from 'lucide-react';
import { clsx } from 'clsx';

const mockApprovals: ApprovalRequest[] = [
  { id: '1', agentId: '3', agentName: 'DeployBot', action: 'Execute prod-deploy.sh', riskLevel: 'HIGH', details: 'Will deploy current branch to production server.' },
  { id: '2', agentId: '1', agentName: 'DevBot', action: 'rm -rf ./temp', riskLevel: 'MEDIUM', details: 'Deleting temporary directory.' }
];

export default function ApprovalQueue() {
  const riskColors = {
    LOW: 'text-green-400 border-green-400/30 bg-green-400/10',
    MEDIUM: 'text-yellow-400 border-yellow-400/30 bg-yellow-400/10',
    HIGH: 'text-orange-400 border-orange-400/30 bg-orange-400/10',
    CRITICAL: 'text-red-400 border-red-400/30 bg-red-400/10',
  };

  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-1">Pending Approvals</h1>
        <p className="text-gray-400 text-sm">Actions requiring human authorization</p>
      </div>

      <div className="space-y-4">
        {mockApprovals.map(req => (
          <div key={req.id} className="bg-galaxy-800 border border-galaxy-700 rounded-xl p-5 flex flex-col md:flex-row gap-4 justify-between items-start md:items-center shadow-lg">
            <div className="space-y-2 flex-1">
              <div className="flex items-center gap-3">
                <span className="font-semibold text-white">{req.agentName}</span>
                <span className={clsx("px-2 py-0.5 rounded text-xs border flex items-center gap-1", riskColors[req.riskLevel])}>
                  <AlertTriangle className="w-3 h-3" /> {req.riskLevel}
                </span>
              </div>
              <div className="font-mono text-sm text-galaxy-accent bg-galaxy-900 p-2 rounded border border-galaxy-700">
                {req.action}
              </div>
              <p className="text-sm text-gray-400">{req.details}</p>
            </div>
            
            <div className="flex gap-3 w-full md:w-auto">
              <button className="flex-1 md:flex-none flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-galaxy-900 text-gray-300 hover:text-white hover:bg-red-500/20 border border-galaxy-700 transition-colors">
                <X className="w-4 h-4" /> Deny
              </button>
              <button className="flex-1 md:flex-none flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-galaxy-accent hover:bg-blue-400 text-white shadow-lg shadow-blue-500/20 transition-colors">
                <Check className="w-4 h-4" /> Approve
              </button>
            </div>
          </div>
        ))}
        {mockApprovals.length === 0 && (
          <div className="text-center py-12 text-gray-500">No pending approvals</div>
        )}
      </div>
    </div>
  );
}
""",
    "src/components/AuditLog.tsx": """import { AuditEvent } from '../types';
import { Search, Download } from 'lucide-react';

const mockAudit: AuditEvent[] = [
  { id: '1', timestamp: '2026-09-19T10:00:00Z', agent: 'DevBot', action: 'read_file', permission: 'fs.read', result: 'allowed', target: 'src/App.tsx' },
  { id: '2', timestamp: '2026-09-19T10:05:00Z', agent: 'DevBot', action: 'exec', permission: 'shell', result: 'denied', target: 'rm -rf /' },
];

export default function AuditLog() {
  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white mb-1">Audit Log</h1>
          <p className="text-gray-400 text-sm">Track all agent activities</p>
        </div>
        <button className="flex items-center gap-2 bg-galaxy-800 hover:bg-galaxy-700 border border-galaxy-700 text-white px-4 py-2 rounded-lg transition-colors">
          <Download className="w-4 h-4" /> Export JSON
        </button>
      </div>

      <div className="mb-6 relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 w-5 h-5" />
        <input 
          type="text" 
          placeholder="Search logs..." 
          className="w-full bg-galaxy-800 border border-galaxy-700 rounded-lg pl-10 pr-4 py-2 text-white focus:outline-none focus:border-galaxy-accent transition-colors"
        />
      </div>

      <div className="bg-galaxy-800 border border-galaxy-700 rounded-xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-galaxy-900 text-gray-300">
              <tr>
                <th className="px-6 py-4 font-medium">Timestamp</th>
                <th className="px-6 py-4 font-medium">Agent</th>
                <th className="px-6 py-4 font-medium">Action</th>
                <th className="px-6 py-4 font-medium">Result</th>
                <th className="px-6 py-4 font-medium">Target</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-galaxy-700">
              {mockAudit.map(log => (
                <tr key={log.id} className="hover:bg-galaxy-900/50 transition-colors">
                  <td className="px-6 py-4 text-gray-400">{new Date(log.timestamp).toLocaleString()}</td>
                  <td className="px-6 py-4 font-medium text-white">{log.agent}</td>
                  <td className="px-6 py-4 font-mono text-galaxy-accent">{log.action}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded text-xs border ${log.result === 'allowed' ? 'bg-green-500/10 text-green-400 border-green-500/20' : 'bg-red-500/10 text-red-400 border-red-500/20'}`}>
                      {log.result}
                    </span>
                  </td>
                  <td className="px-6 py-4 font-mono text-gray-300 text-xs truncate max-w-xs">{log.target}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
""",
    "src/components/Sidebar.tsx": """import { NavLink } from 'react-router-dom';
import { MessageSquare, Bot, Shield, CheckSquare, ScrollText, Settings, Rocket } from 'lucide-react';
import { clsx } from 'clsx';

export default function Sidebar() {
  const navItems = [
    { to: '/', icon: MessageSquare, label: 'Chat' },
    { to: '/agents', icon: Bot, label: 'Agents' },
    { to: '/permissions', icon: Shield, label: 'Permissions' },
    { to: '/approvals', icon: CheckSquare, label: 'Approvals' },
    { to: '/audit', icon: ScrollText, label: 'Audit Log' },
  ];

  return (
    <aside className="hidden md:flex flex-col w-64 bg-galaxy-900 border-r border-galaxy-800 h-screen shrink-0">
      <div className="p-6 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-galaxy-accent to-galaxy-highlight flex items-center justify-center shadow-lg shadow-galaxy-accent/20">
          <Rocket className="w-6 h-6 text-white" />
        </div>
        <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">Galaxy</span>
      </div>
      
      <nav className="flex-1 px-4 py-2 space-y-1">
        {navItems.map(item => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) => clsx(
              "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200",
              isActive 
                ? "bg-galaxy-800 text-galaxy-accent shadow-inner border border-galaxy-700/50" 
                : "text-gray-400 hover:text-white hover:bg-galaxy-800/50"
            )}
          >
            <item.icon className="w-5 h-5" />
            <span className="font-medium">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="p-4 mt-auto">
        <NavLink to="/settings" className="flex items-center gap-3 px-4 py-3 text-gray-400 hover:text-white rounded-xl hover:bg-galaxy-800/50 transition-colors">
          <Settings className="w-5 h-5" />
          <span className="font-medium">Settings</span>
        </NavLink>
      </div>
    </aside>
  );
}
""",
    "src/components/BottomNav.tsx": """import { NavLink } from 'react-router-dom';
import { MessageSquare, Bot, Shield, CheckSquare, ScrollText } from 'lucide-react';
import { clsx } from 'clsx';

export default function BottomNav() {
  const navItems = [
    { to: '/', icon: MessageSquare },
    { to: '/agents', icon: Bot },
    { to: '/permissions', icon: Shield },
    { to: '/approvals', icon: CheckSquare },
    { to: '/audit', icon: ScrollText },
  ];

  return (
    <nav className="md:hidden flex items-center justify-around bg-galaxy-900 border-t border-galaxy-800 pb-safe pt-2 px-2 shrink-0">
      {navItems.map(item => (
        <NavLink
          key={item.to}
          to={item.to}
          className={({ isActive }) => clsx(
            "p-3 rounded-xl transition-colors",
            isActive ? "text-galaxy-accent bg-galaxy-800" : "text-gray-500 hover:text-gray-300"
          )}
        >
          <item.icon className="w-6 h-6" />
        </NavLink>
      ))}
    </nav>
  );
}
""",
    "src/components/Layout.tsx": """import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import BottomNav from './BottomNav';
import { useWebSocket } from '../hooks/useWebSocket';

export default function Layout() {
  useWebSocket('ws://localhost:8000/ws'); // Initialize WS connection globally

  return (
    <div className="flex h-screen w-full bg-galaxy-900 overflow-hidden font-sans text-gray-100">
      <Sidebar />
      <main className="flex-1 flex flex-col min-w-0 h-full relative">
        <div className="md:hidden p-4 border-b border-galaxy-800 flex justify-center items-center shrink-0">
           <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">Galaxy Jarvis</span>
        </div>
        <div className="flex-1 overflow-y-auto w-full">
          <Outlet />
        </div>
        <BottomNav />
      </main>
    </div>
  );
}
""",
    "src/App.tsx": """import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import ChatView from './components/ChatView';
import AgentsDashboard from './components/AgentsDashboard';
import PermissionsManager from './components/PermissionsManager';
import ApprovalQueue from './components/ApprovalQueue';
import AuditLog from './components/AuditLog';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<ChatView />} />
        <Route path="agents" element={<AgentsDashboard />} />
        <Route path="permissions" element={<PermissionsManager />} />
        <Route path="approvals" element={<ApprovalQueue />} />
        <Route path="audit" element={<AuditLog />} />
        <Route path="settings" element={<div className="p-6 text-white">Settings (TBD)</div>} />
      </Route>
    </Routes>
  );
}

export default App;
""",
    "src/main.tsx": """import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
)
"""
}

for filepath, content in files.items():
    full_path = os.path.join(base_dir, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Files generated.")
