import React, { useEffect, useState } from 'react';
import { AuditEntry } from '../types';
import { getAuditLog } from '../services/api';
import { ScrollText, ChevronDown, ChevronRight, FileSearch } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

export default function AuditLog() {
  const { colors } = useTheme();
  const [logs, setLogs] = useState<AuditEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedRow, setExpandedRow] = useState<number | null>(null);

  useEffect(() => {
    let mounted = true;
    const fetchLogs = async () => {
      try {
        const data = await getAuditLog(100);
        if (mounted) {
          setLogs(Array.isArray(data) ? data : []);
          setLoading(false);
        }
      } catch (err) {
        if (mounted) {
          console.error('Failed to fetch audit logs:', err);
          setLoading(false);
        }
      }
    };
    fetchLogs();
    const interval = setInterval(fetchLogs, 5000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  const toggleRow = (idx: number) => {
    setExpandedRow(prev => prev === idx ? null : idx);
  };

  return (
    <div className="p-6 h-full overflow-y-auto fade-in" style={{ background: colors.bg }}>
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
                <th className="px-4 py-4 w-10 border-b" style={{ borderColor: colors.border }}></th>
                <th className="px-4 py-4 font-medium border-b" style={{ borderColor: colors.border }}>Time</th>
                <th className="px-4 py-4 font-medium border-b" style={{ borderColor: colors.border }}>Agent</th>
                <th className="px-4 py-4 font-medium border-b" style={{ borderColor: colors.border }}>Action</th>
                <th className="px-4 py-4 font-medium border-b" style={{ borderColor: colors.border }}>Result</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                // Loading Skeleton
                [1, 2, 3, 4, 5].map(i => (
                  <tr key={i} className="animate-pulse">
                    <td className="px-4 py-4"><div className="w-4 h-4 rounded bg-gray-700/50"></div></td>
                    <td className="px-4 py-4"><div className="w-24 h-4 rounded bg-gray-700/50"></div></td>
                    <td className="px-4 py-4"><div className="w-20 h-4 rounded bg-gray-700/50"></div></td>
                    <td className="px-4 py-4"><div className="w-48 h-4 rounded bg-gray-700/50"></div></td>
                    <td className="px-4 py-4"><div className="w-16 h-6 rounded-full bg-gray-700/50"></div></td>
                  </tr>
                ))
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-16 text-center">
                    <div className="flex flex-col items-center justify-center">
                      <FileSearch className="w-12 h-12 mb-4 opacity-50" style={{ color: colors.textDim }} />
                      <span className="text-lg font-medium" style={{ color: colors.text }}>No audit logs found</span>
                      <p className="text-sm mt-1" style={{ color: colors.textMuted }}>Activities will be recorded here once agents start working.</p>
                    </div>
                  </td>
                </tr>
              ) : (
                logs.map((log, idx) => (
                  <React.Fragment key={idx}>
                    <tr 
                      onClick={() => toggleRow(idx)}
                      className="transition-colors cursor-pointer hover:bg-white/5"
                    >
                      <td className="px-4 py-4">
                        {expandedRow === idx ? (
                          <ChevronDown className="w-4 h-4" style={{ color: colors.textMuted }} />
                        ) : (
                          <ChevronRight className="w-4 h-4" style={{ color: colors.textMuted }} />
                        )}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap" style={{ color: colors.textMuted }}>
                        {log.iso_time || new Date(log.timestamp * 1000).toLocaleString()}
                      </td>
                      <td className="px-4 py-4 font-medium" style={{ color: colors.text }}>{log.agent_id}</td>
                      <td className="px-4 py-4 font-mono truncate max-w-xs" style={{ color: colors.accentLight }}>{log.action}</td>
                      <td className="px-4 py-4">
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
                    </tr>
                    {expandedRow === idx && (
                      <tr className="bg-black/10">
                        <td colSpan={5} className="px-8 py-4 text-sm" style={{ borderTop: `1px solid ${colors.border}20` }}>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                              <strong className="block mb-1" style={{ color: colors.text }}>Full Action</strong>
                              <div className="font-mono p-2 rounded text-xs break-all" style={{ backgroundColor: colors.bg, color: colors.textMuted }}>
                                {log.action}
                              </div>
                            </div>
                            <div>
                              <strong className="block mb-1" style={{ color: colors.text }}>Scope / Permissions</strong>
                              <div className="font-mono p-2 rounded text-xs break-all" style={{ backgroundColor: colors.bg, color: colors.textMuted }}>
                                {log.permission && <div className="mb-1">Perm: {log.permission}</div>}
                                {log.scope ? <div>Scope: {log.scope}</div> : <span className="opacity-50">No specific scope</span>}
                              </div>
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
