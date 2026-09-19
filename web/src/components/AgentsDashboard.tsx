import { useEffect, useState } from 'react';
import { Agent } from '../types';
import { Bot, Activity } from 'lucide-react';
import { getAgents } from '../services/api';

export default function AgentsDashboard() {
  const [agents, setAgents] = useState<Agent[]>([]);

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const data = await getAgents();
        setAgents(data);
      } catch (err) {
        console.error('Failed to fetch agents:', err);
      }
    };
    fetchAgents();
    const interval = setInterval(fetchAgents, 3000);
    return () => clearInterval(interval);
  }, []);

  const getRoleColor = (role: string) => {
    const r = role.toLowerCase();
    if (r.includes('coder')) return '#22d3ee';
    if (r.includes('tester')) return '#4ade80';
    if (r.includes('researcher')) return '#fb923c';
    if (r.includes('devops')) return '#f472b6';
    if (r.includes('reviewer')) return '#a78bfa';
    return '#94a3b8';
  };

  return (
    <div className="p-6 h-full overflow-y-auto" style={{ background: '#0a0a18' }}>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-1 flex items-center gap-2">
          <Bot className="w-6 h-6 text-indigo-400" />
          Agents Fleet
        </h1>
        <p className="text-gray-400 text-sm">Monitor and manage your autonomous agents</p>
      </div>
      
      {agents.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          No active agents
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {agents.map(agent => (
            <div 
              key={agent.id} 
              style={{ backgroundColor: '#12122a', borderColor: '#1e1e3a' }}
              className="border rounded-xl p-5 shadow-lg flex flex-col gap-3"
            >
              <div className="flex justify-between items-start">
                <h3 className="text-lg font-semibold text-white">{agent.name}</h3>
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
              <div className="flex items-center gap-2 text-sm text-gray-400">
                <Activity className="w-4 h-4" />
                <span className="capitalize">{agent.status}</span>
              </div>
              {agent.current_task && (
                <div className="mt-2 text-sm p-3 rounded-lg border" style={{ backgroundColor: '#0a0a18', borderColor: '#1e1e3a', color: '#94a3b8' }}>
                  <strong className="text-gray-300">Task:</strong> {agent.current_task}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
