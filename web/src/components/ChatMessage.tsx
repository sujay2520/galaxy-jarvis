import { ChatMessage as IChatMessage } from '../types';
import { User, Bot, Info } from 'lucide-react';

export default function ChatMessage({ msg }: { msg: IChatMessage }) {
  const isUser = msg.role === 'user';
  const isSystem = msg.role === 'system';

  if (isSystem) {
    return (
      <div className="flex items-start gap-3 py-2 px-3 rounded-lg my-1"
        style={{ background: '#12122a', border: '1px solid #1e1e3a' }}>
        <div className="w-6 h-6 rounded-full flex items-center justify-center shrink-0 mt-0.5"
          style={{ background: '#1e1e4a' }}>
          <Info className="w-3.5 h-3.5" style={{ color: '#6366f1' }} />
        </div>
        <div>
          <div className="flex items-center gap-2 mb-0.5">
            <span className="text-xs font-semibold" style={{ color: '#6366f1' }}>System</span>
            <span className="text-xs" style={{ color: '#3d3d6b' }}>
              {new Date(msg.timestamp).toLocaleTimeString()}
            </span>
          </div>
          <p className="text-sm leading-relaxed" style={{ color: '#a5b4fc' }}>
            {msg.content}
          </p>
        </div>
      </div>
    );
  }

  if (isUser) {
    return (
      <div className="flex items-start gap-3 py-2 px-3 rounded-lg my-1">
        <div className="w-7 h-7 rounded-full flex items-center justify-center shrink-0 mt-0.5"
          style={{ background: '#1e3a5f' }}>
          <User className="w-4 h-4 text-blue-300" />
        </div>
        <div>
          <div className="flex items-center gap-2 mb-0.5">
            <span className="text-xs font-semibold text-blue-300">You</span>
            <span className="text-xs" style={{ color: '#3d3d6b' }}>
              {new Date(msg.timestamp).toLocaleTimeString()}
            </span>
          </div>
          <p className="text-sm text-gray-200 leading-relaxed">{msg.content}</p>
        </div>
      </div>
    );
  }

  // Agent message
  const roleColor: Record<string, string> = {
    coder: '#22d3ee',
    tester: '#4ade80',
    researcher: '#fb923c',
    devops: '#f472b6',
    reviewer: '#a78bfa',
    AI: '#818cf8',
    Done: '#4ade80',
    Working: '#fbbf24',
  };
  const role = msg.agentRole || 'AI';
  const color = roleColor[role] || '#818cf8';

  return (
    <div className="flex items-start gap-3 py-3 px-3 rounded-lg my-1"
      style={{ background: '#12122a', border: '1px solid #1e1e3a' }}>
      <div className="w-7 h-7 rounded-full flex items-center justify-center shrink-0 mt-0.5"
        style={{ background: '#1e1e4a' }}>
        <Bot className="w-4 h-4" style={{ color }} />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-xs font-semibold text-gray-200">{msg.agentName || 'Galaxy'}</span>
          {msg.agentRole && (
            <span className="text-xs px-1.5 py-0.5 rounded font-medium"
              style={{ background: color + '22', color }}>
              {msg.agentRole}
            </span>
          )}
          <span className="text-xs" style={{ color: '#3d3d6b' }}>
            {new Date(msg.timestamp).toLocaleTimeString()}
          </span>
        </div>
        <p className="text-sm text-gray-300 leading-relaxed whitespace-pre-wrap break-words">
          {msg.content}
        </p>
      </div>
    </div>
  );
}
