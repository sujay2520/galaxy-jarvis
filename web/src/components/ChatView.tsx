import { useState, useRef, useEffect, useCallback } from 'react';
import { Send, Mic, MicOff, Loader2, Zap } from 'lucide-react';
import ChatMessage from './ChatMessage';
import { ChatMessage as IChatMessage } from '../types';
import { chatAPI, createTask, WS_URL } from '../services/api';
import { useTheme } from '../context/ThemeContext';

const TASK_KEYWORDS = ['build', 'create', 'make', 'write', 'fix', 'deploy', 'install',
  'setup', 'test', 'run', 'delete', 'update', 'implement', 'generate', 'code'];

function isTask(text: string) {
  return TASK_KEYWORDS.some(k => text.toLowerCase().startsWith(k));
}

export default function ChatView() {
  const { colors } = useTheme();
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [listening, setListening] = useState(false);
  const [messages, setMessages] = useState<IChatMessage[]>([
    {
      id: 'welcome',
      role: 'system',
      content: 'Welcome to Galaxy Jarvis. How can I assist you today?',
      timestamp: new Date().toISOString(),
    },
  ]);
  const endRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    function connect() {
      try {
        const ws = new WebSocket(WS_URL);
        wsRef.current = ws;

        ws.onmessage = (e) => {
          try {
            const evt = JSON.parse(e.data);

            if (evt.type === 'TaskAssigned' && evt.source === 'orchestrator') {
              addMessage({
                role: 'system',
                content: `Agents assigned to task: "${evt.payload?.description || '...'}"`,
              });
            } else if (evt.type === 'TaskCompleted' && evt.source === 'orchestrator') {
              addMessage({
                role: 'system',
                content: 'Task completed! Check the Agents tab for detailed results.',
              });
            } else if (evt.type === 'ApprovalRequired') {
              addMessage({
                role: 'system',
                content: `[Approval Required] Agent needs permission for: ${evt.payload?.action || 'unknown action'} (${evt.payload?.risk || 'high'} risk). Go to Approvals tab to approve/deny.`,
              });
            }
            else if (evt.type === 'ChatResponse') {
              addMessage({
                role: 'agent',
                agentName: 'Galaxy',
                agentRole: 'AI',
                content: evt.payload?.message || '',
              });
            }
          } catch { /* ignore parse errors */ }
        };

        ws.onclose = () => {
          setTimeout(connect, 3000);
        };
      } catch { /* server not ready yet */ }
    }

    connect();
    return () => wsRef.current?.close();
  }, []);

  const addMessage = useCallback((partial: Partial<IChatMessage>) => {
    setMessages(prev => [
      ...prev,
      {
        id: Date.now().toString() + Math.random(),
        role: 'agent',
        content: '',
        timestamp: new Date().toISOString(),
        ...partial,
      } as IChatMessage,
    ]);
  }, []);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const send = async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || loading) return;

    setMessages(prev => [...prev, {
      id: Date.now().toString(),
      role: 'user',
      content: trimmed,
      timestamp: new Date().toISOString(),
    }]);
    setInput('');
    setLoading(true);

    try {
      if (isTask(trimmed)) {
        const res = await createTask(trimmed);
        addMessage({
          role: 'system',
          content: `Task dispatched to agents. Status: ${res.status}.\nAgents are working on it -- watch the Agents tab for live progress.`,
        });
      } else {
        const res = await chatAPI(trimmed);
        addMessage({
          role: 'agent',
          agentName: 'Galaxy',
          agentRole: 'AI',
          content: res.response || '(no response)',
          isTask: res.is_task,
        });
      }
    } catch (err) {
      addMessage({
        role: 'system',
        content: 'Connection error. Make sure the Galaxy server is running (start_galaxy.bat).',
      });
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const toggleVoice = () => {
    const SR = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SR) return;

    if (listening) {
      recognitionRef.current?.stop();
      setListening(false);
      return;
    }

    const rec = new SR();
    recognitionRef.current = rec;
    rec.continuous = false;
    rec.interimResults = false;
    rec.lang = 'en-US';
    rec.onresult = (e: any) => {
      const transcript = e.results[0][0].transcript;
      setInput(transcript);
      setListening(false);
    };
    rec.onerror = () => setListening(false);
    rec.onend = () => setListening(false);
    rec.start();
    setListening(true);
  };

  return (
    <div className="flex flex-col h-full" style={{ background: colors.bg }}>
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-1">
        {messages.map(msg => (
          <ChatMessage key={msg.id} msg={msg} />
        ))}
        {loading && (
          <div className="flex items-center gap-3 p-3">
            <div className="w-7 h-7 rounded-full flex items-center justify-center" style={{ background: colors.accent }}>
              <Loader2 className="w-4 h-4 text-white animate-spin" />
            </div>
            <span className="text-sm italic" style={{ color: colors.textMuted }}>Galaxy is thinking...</span>
          </div>
        )}
        <div ref={endRef} />
      </div>

      <div className="px-4 pb-4 pt-2" style={{ borderTop: `1px solid ${colors.border}` }}>
        <div className="flex items-center gap-2 max-w-4xl mx-auto">
          <div className="relative flex-1">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send(input)}
              placeholder="Type your message..."
              className="w-full py-3 pl-4 pr-12 rounded-xl text-sm outline-none transition-all"
              style={{
                background: colors.card,
                border: `1px solid ${colors.border}`,
                color: colors.text,
                caretColor: colors.accent,
              }}
              disabled={loading}
            />
            {isTask(input) && (
              <div className="absolute right-3 top-1/2 -translate-y-1/2">
                <span title="This will run as an agent task">
                  <Zap className="w-4 h-4 text-yellow-500" />
                </span>
              </div>
            )}
          </div>

          <button
            onClick={toggleVoice}
            className="p-3 rounded-xl transition-colors"
            style={{
              background: listening ? colors.accent : colors.card,
              border: `1px solid ${colors.border}`,
            }}
            title={listening ? 'Stop listening' : 'Voice input'}
          >
            {listening
              ? <MicOff className="w-4 h-4 text-white animate-pulse" />
              : <Mic className="w-4 h-4" style={{ color: colors.textMuted }} />
            }
          </button>

          <button
            onClick={() => send(input)}
            disabled={!input.trim() || loading}
            className="p-3 rounded-xl transition-all"
            style={{
              background: input.trim() && !loading ? colors.accent : colors.card,
              border: `1px solid ${colors.border}`,
            }}
          >
            <Send className="w-4 h-4" style={{ color: input.trim() && !loading ? '#fff' : colors.textMuted }} />
          </button>
        </div>

        <p className="text-center text-xs mt-2" style={{ color: colors.textDim }}>
          Start with "build", "create", "write" etc. to dispatch an autonomous agent task
        </p>
      </div>
    </div>
  );
}
