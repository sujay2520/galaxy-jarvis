import { useState, useRef, useEffect, useCallback } from 'react';
import { Send, Mic, MicOff, Loader2, Zap } from 'lucide-react';
import ChatMessage from './ChatMessage';
import { ChatMessage as IChatMessage } from '../types';
import { chatAPI, createTask, WS_URL } from '../services/api';

const TASK_KEYWORDS = ['build', 'create', 'make', 'write', 'fix', 'deploy', 'install',
  'setup', 'test', 'run', 'delete', 'update', 'implement', 'generate', 'code'];

function isTask(text: string) {
  return TASK_KEYWORDS.some(k => text.toLowerCase().startsWith(k));
}

export default function ChatView() {
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

  // ── WebSocket: receive live agent events ──────────────────────
  useEffect(() => {
    function connect() {
      try {
        const ws = new WebSocket(WS_URL);
        wsRef.current = ws;

        ws.onmessage = (e) => {
          try {
            const evt = JSON.parse(e.data);
            if (evt.type === 'AgentStarted') {
              addMessage({
                role: 'agent',
                agentName: evt.payload?.agent || 'Agent',
                agentRole: 'Working',
                content: `Started: ${evt.payload?.task || '...'}`,
              });
            } else if (evt.type === 'AgentCompleted') {
              const output = evt.payload?.result?.output || 'Task completed.';
              addMessage({
                role: 'agent',
                agentName: evt.payload?.agent || 'Agent',
                agentRole: 'Done',
                content: typeof output === 'string' ? output : JSON.stringify(output, null, 2),
              });
            } else if (evt.type === 'AgentError') {
              addMessage({
                role: 'system',
                content: `Agent error: ${evt.payload?.error || 'Unknown error'}`,
              });
            } else if (evt.type === 'ChatResponse') {
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

    // Add user message
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
        // Route to multi-agent orchestrator
        const res = await createTask(trimmed);
        addMessage({
          role: 'system',
          content: `Task dispatched to agents. Status: ${res.status}. Agents are working — watch the Agents tab for live progress.`,
        });
      } else {
        // Direct LLM chat
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
        content: `Connection error. Make sure the Galaxy server is running (start_galaxy.bat).`,
      });
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  // ── Voice input ───────────────────────────────────────────────
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
    <div className="flex flex-col h-full" style={{ background: '#0d0d1a' }}>
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-1">
        {messages.map(msg => (
          <ChatMessage key={msg.id} msg={msg} />
        ))}
        {loading && (
          <div className="flex items-center gap-3 p-3">
            <div className="w-7 h-7 rounded-full bg-purple-600 flex items-center justify-center">
              <Loader2 className="w-4 h-4 text-white animate-spin" />
            </div>
            <span className="text-sm text-gray-400 italic">Galaxy is thinking...</span>
          </div>
        )}
        <div ref={endRef} />
      </div>

      {/* Input bar — Antigravity style */}
      <div className="px-4 pb-4 pt-2" style={{ borderTop: '1px solid #1e1e3a' }}>
        <div className="flex items-center gap-2 max-w-4xl mx-auto">
          <div className="relative flex-1">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send(input)}
              placeholder="Type your message..."
              className="w-full py-3 pl-4 pr-12 rounded-xl text-white text-sm outline-none transition-all"
              style={{
                background: '#1a1a2e',
                border: '1px solid #2a2a4a',
                caretColor: '#818cf8',
              }}
              disabled={loading}
            />
            {/* Zap icon — hint for task mode */}
            {isTask(input) && (
              <div className="absolute right-3 top-1/2 -translate-y-1/2">
                <span title="This will run as an agent task">
                  <Zap className="w-4 h-4 text-yellow-400" />
                </span>
              </div>
            )}
          </div>

          {/* Voice */}
          <button
            onClick={toggleVoice}
            className="p-3 rounded-xl transition-colors"
            style={{
              background: listening ? '#4f46e5' : '#1a1a2e',
              border: '1px solid #2a2a4a',
            }}
            title={listening ? 'Stop listening' : 'Voice input'}
          >
            {listening
              ? <MicOff className="w-4 h-4 text-white animate-pulse" />
              : <Mic className="w-4 h-4 text-gray-400" />
            }
          </button>

          {/* Send */}
          <button
            onClick={() => send(input)}
            disabled={!input.trim() || loading}
            className="p-3 rounded-xl transition-all"
            style={{
              background: input.trim() && !loading ? '#4f46e5' : '#1a1a2e',
              border: '1px solid #2a2a4a',
            }}
          >
            <Send className="w-4 h-4 text-white" />
          </button>
        </div>

        <p className="text-center text-xs mt-2" style={{ color: '#3d3d6b' }}>
          Start with "build", "create", "write" etc. to dispatch an autonomous agent task
        </p>
      </div>
    </div>
  );
}
