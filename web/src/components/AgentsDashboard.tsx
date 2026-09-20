import { useEffect, useState } from 'react';
import { Agent } from '../types';
import { Bot, Activity, Users } from 'lucide-react';
import { getAgents } from '../services/api';
import { useTheme } from '../context/ThemeContext';

export default function AgentsDashboard() {
  const { colors } = useTheme();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    const fetchAgents = async () => {
      try {
        const data = await getAgents();
        if (mounted) {
          setAgents(Array.isArray(data) ? data : []);
          setLoading(false);
        }
      } catch (err) {
        if (mounted) {
          console.error('Failed to fetch agents:', err);
          setLoading(false);
        }
      }
    };
    fetchAgents();
    const interval = setInterval(fetchAgents, 3000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  const getRoleColor = (role: string) => {
    const r = role.toLowerCase();
    if (r.includes('coder')) return '#22d3ee';
    if (r.includes('tester')) return '#4ade80';
    if (r.includes('researcher')) return '#fb923c';
    if (r.includes('devops')) return '#f472b6';
    if (r.includes('reviewer')) return '#a78bfa';
    return colors.accent;
  };

  return (
    <div className="p-6 h-full overflow-y-auto fade-in" style={{ background: colors.bg }}>
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold mb-1 flex items-center gap-2" style={{ color: colors.text }}>
            <Bot className="w-6 h-6" style={{ color: colors.accentLight }} />
            Agents Fleet
          </h1>
          <p className="text-sm" style={{ color: colors.textMuted }}>Monitor and manage your autonomous agents</p>
        </div>
        <div 
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg border"
          style={{ backgroundColor: colors.card, borderColor: colors.border }}
        >
          <Users className="w-4 h-4" style={{ color: colors.textDim }} />
          <span className="font-semibold" style={{ color: colors.text }}>{agents.length}</span>
          <span className="text-sm" style={{ color: colors.textMuted }}>Total</span>
        </div>
      </div>
      
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map(i => (
            <div 
              key={i} 
              className="border rounded-xl p-5 shadow-lg animate-pulse"
              style={{ backgroundColor: colors.card, borderColor: colors.border }}
            >
              <div className="flex justify-between items-start mb-4">
                <div className="h-6 w-32 rounded bg-gray-700/50"></div>
                <div className="h-6 w-20 rounded bg-gray-700/50"></div>
              </div>
              <div className="h-4 w-24 rounded bg-gray-700/50 mb-3"></div>
              <div className="h-10 w-full rounded bg-gray-700/50 mt-2"></div>
            </div>
          ))}
        </div>
      ) : agents.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center fade-in">
          <div className="w-24 h-24 mb-6 rounded-full flex items-center justify-center" style={{ backgroundColor: `${colors.accent}15` }}>
            <Bot className="w-12 h-12" style={{ color: colors.accentLight }} />
          </div>
          <h2 className="text-xl font-bold mb-2" style={{ color: colors.text }}>No Active Agents</h2>
          <p className="max-w-md text-sm" style={{ color: colors.textMuted }}>
            Agents will appear here automatically when they are assigned tasks by the orchestrator. Start a new task in the Chat view to see them in action.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 fade-in">
          {agents.map(agent => (
            <div 
              key={agent.id} 
              style={{ backgroundColor: colors.card, borderColor: colors.border }}
              className="border rounded-xl p-5 shadow-lg flex flex-col gap-3 transition-transform hover:-translate-y-1 duration-300"
            >
              <div className="flex justify-between items-start">
                <h3 className="text-lg font-semibold" style={{ color: colors.text }}>{agent.name}</h3>
                <span 
                  className="px-2 py-1 rounded text-xs font-medium border"
                  style={{ 
                    color: getRoleColor(agent.role), 
                    borderColor: getRoleColor(agent.role),
                    backgroundColor: `${getRoleColor(agent.role)}20`
                  }}
                >
                  {agent.role}
                </span>
              </div>
              <div className="flex items-center gap-2 text-sm" style={{ color: colors.textMuted }}>
                {agent.status === 'working' ? (
                  <Activity className="w-4 h-4 text-yellow-500 animate-pulse" />
                ) : (
                  <Activity className="w-4 h-4" />
                )}
                <span className="capitalize">{agent.status}</span>
              </div>
              {agent.current_task && (
                <div className="mt-2 text-sm p-3 rounded-lg border" style={{ backgroundColor: colors.bg, borderColor: colors.border, color: colors.textMuted }}>
                  <strong style={{ color: colors.text }}>Task:</strong> {agent.current_task}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
