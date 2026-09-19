import { ChatMessage as IChatMessage } from '../types';
import { User, Bot, Info } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

export default function ChatMessage({ msg }: { msg: IChatMessage }) {
  const { colors } = useTheme();
  const isUser = msg.role === 'user';
  const isSystem = msg.role === 'system';

  if (isSystem) {
    return (
      <div className="flex items-start gap-3 py-2 px-3 rounded-lg my-1"
        style={{ background: colors.card, border: `1px solid ${colors.border}` }}>
        <div className="w-6 h-6 rounded-full flex items-center justify-center shrink-0 mt-0.5"
          style={{ background: `${colors.accent}22` }}>
          <Info className="w-3.5 h-3.5" style={{ color: colors.accent }} />
        </div>
        <div>
          <div className="flex items-center gap-2 mb-0.5">
            <span className="text-xs font-semibold" style={{ color: colors.accent }}>System</span>
            <span className="text-xs" style={{ color: colors.textDim }}>
              {new Date(msg.timestamp).toLocaleTimeString()}
            </span>
          </div>
          <p className="text-sm leading-relaxed" style={{ color: colors.accentLight }}>
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
            <span className="text-xs font-semibold text-blue-500">You</span>
            <span className="text-xs" style={{ color: colors.textDim }}>
              {new Date(msg.timestamp).toLocaleTimeString()}
            </span>
          </div>
          <p className="text-sm leading-relaxed" style={{ color: colors.text }}>{msg.content}</p>
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
    AI: colors.accent,
    Done: '#4ade80',
    Working: '#fbbf24',
  };
  const role = msg.agentRole || 'AI';
  const color = roleColor[role] || colors.accent;

  return (
    <div className="flex items-start gap-3 py-3 px-3 rounded-lg my-1"
      style={{ background: colors.card, border: `1px solid ${colors.border}` }}>
      <div className="w-7 h-7 rounded-full flex items-center justify-center shrink-0 mt-0.5"
        style={{ background: `${color}22` }}>
        <Bot className="w-4 h-4" style={{ color }} />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-xs font-semibold" style={{ color: colors.text }}>{msg.agentName || 'Galaxy'}</span>
          {msg.agentRole && (
            <span className="text-xs px-1.5 py-0.5 rounded font-medium"
              style={{ background: color + '22', color }}>
              {msg.agentRole}
            </span>
          )}
          <span className="text-xs" style={{ color: colors.textDim }}>
            {new Date(msg.timestamp).toLocaleTimeString()}
          </span>
        </div>
        <p className="text-sm leading-relaxed whitespace-pre-wrap break-words" style={{ color: colors.text }}>
          {msg.content}
        </p>
      </div>
    </div>
  );
}
