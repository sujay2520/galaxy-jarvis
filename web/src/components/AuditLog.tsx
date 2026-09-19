import { useEffect, useState } from 'react';
import { AuditEntry } from '../types';
import { getAuditLog } from '../services/api';
import { ScrollText } from 'lucide-react';

export default function AuditLog() {
  const [logs, setLogs] = useState<AuditEntry[]>([]);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const data = await getAuditLog(100);
        setLogs(data);
      } catch (err) {
        console.error('Failed to fetch audit logs:', err);
      }
    };
    fetchLogs();
    const interval = setInterval(fetchLogs, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-6 h-full overflow-y-auto" style={{ background: '#0a0a18' }}>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-1 flex items-center gap-2">
          <ScrollText className="w-6 h-6 text-indigo-400" />
          Audit Log
        </h1>
        <p className="text-gray-400 text-sm">Track all agent activities and permissions</p>
      </div>

      <div 
        className="border rounded-xl overflow-hidden shadow-xl"
        style={{ backgroundColor: '#12122a', borderColor: '#1e1e3a' }}
      >
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead style={{ backgroundColor: '#0a0a18' }} className="text-gray-300">
              <tr>
                <th className="px-6 py-4 font-medium border-b" style={{ borderColor: '#1e1e3a' }}>Time</th>
                <th className="px-6 py-4 font-medium border-b" style={{ borderColor: '#1e1e3a' }}>Agent</th>
                <th className="px-6 py-4 font-medium border-b" style={{ borderColor: '#1e1e3a' }}>Action</th>
                <th className="px-6 py-4 font-medium border-b" style={{ borderColor: '#1e1e3a' }}>Result</th>
                <th className="px-6 py-4 font-medium border-b" style={{ borderColor: '#1e1e3a' }}>Scope/Permission</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {logs.map((log, idx) => (
                <tr key={idx} className="transition-colors hover:bg-white/5">
                  <td className="px-6 py-4 text-gray-400 whitespace-nowrap">{log.iso_time || new Date(log.timestamp * 1000).toLocaleString()}</td>
                  <td className="px-6 py-4 font-medium text-white">{log.agent_id}</td>
                  <td className="px-6 py-4 font-mono text-indigo-400 break-all">{log.action}</td>
                  <td className="px-6 py-4">
                    <span 
                      className="px-2 py-1 rounded text-xs border whitespace-nowrap"
                      style={{
                        color: log.result === 'allowed' ? '#4ade80' : '#f87171',
                        borderColor: log.result === 'allowed' ? '#4ade80' : '#f87171',
                        backgroundColor: log.result === 'allowed' ? '#4ade8020' : '#f8717120'
                      }}
                    >
                      {log.result}
                    </span>
                  </td>
                  <td className="px-6 py-4 font-mono text-gray-300 text-xs truncate max-w-xs break-all">
                    {log.permission && <div className="text-gray-400 mb-1">Perm: {log.permission}</div>}
                    {log.scope && <div>Scope: {log.scope}</div>}
                  </td>
                </tr>
              ))}
              {logs.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-gray-500">
                    No audit logs found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
