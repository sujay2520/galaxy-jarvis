import { useEffect, useState } from 'react';
import { AuditEntry } from '../types';
import { getAuditLog } from '../services/api';
import { ScrollText } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

export default function AuditLog() {
  const { colors } = useTheme();
  const [logs, setLogs] = useState<AuditEntry[]>([]);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const data = await getAuditLog(100);
        setLogs(Array.isArray(data) ? data : []);
      } catch (err) {
        console.error('Failed to fetch audit logs:', err);
      }
    };
    fetchLogs();
    const interval = setInterval(fetchLogs, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-6 h-full overflow-y-auto" style={{ background: colors.bg }}>
      <div className="mb-8">
        <h1 className="text-2xl font-bold mb-1 flex items-center gap-2" style={{ color: colors.text }}>
          <ScrollText className="w-6 h-6" style={{ color: colors.accentLight }} />
          Audit Log
        </h1>
        <p className="text-sm" style={{ color: colors.textMuted }}>Track all agent activities and permissions</p>
      </div>

      <div 
        className="border rounded-xl overflow-hidden shadow-xl"
        style={{ backgroundColor: colors.card, borderColor: colors.border }}
      >
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead style={{ backgroundColor: colors.bg, color: colors.textDim }}>
              <tr>
                <th className="px-6 py-4 font-medium border-b" style={{ borderColor: colors.border }}>Time</th>
                <th className="px-6 py-4 font-medium border-b" style={{ borderColor: colors.border }}>Agent</th>
                <th className="px-6 py-4 font-medium border-b" style={{ borderColor: colors.border }}>Action</th>
                <th className="px-6 py-4 font-medium border-b" style={{ borderColor: colors.border }}>Result</th>
                <th className="px-6 py-4 font-medium border-b" style={{ borderColor: colors.border }}>Scope/Permission</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {logs.map((log, idx) => (
                <tr key={idx} className="transition-colors hover:bg-white/5">
                  <td className="px-6 py-4 whitespace-nowrap" style={{ color: colors.textMuted }}>{log.iso_time || new Date(log.timestamp * 1000).toLocaleString()}</td>
                  <td className="px-6 py-4 font-medium" style={{ color: colors.text }}>{log.agent_id}</td>
                  <td className="px-6 py-4 font-mono break-all" style={{ color: colors.accentLight }}>{log.action}</td>
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
                  <td className="px-6 py-4 font-mono text-xs truncate max-w-xs break-all" style={{ color: colors.textMuted }}>
                    {log.permission && <div className="mb-1">Perm: {log.permission}</div>}
                    {log.scope && <div>Scope: {log.scope}</div>}
                  </td>
                </tr>
              ))}
              {logs.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center" style={{ color: colors.textDim }}>
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
