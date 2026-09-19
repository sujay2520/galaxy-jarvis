import { useEffect, useState } from 'react';
import { ApprovalRequest } from '../types';
import { AlertTriangle, Check, X } from 'lucide-react';
import { getApprovals, resolveApproval } from '../services/api';

export default function ApprovalQueue() {
  const [approvals, setApprovals] = useState<ApprovalRequest[]>([]);

  useEffect(() => {
    const fetchApprovals = async () => {
      try {
        const data = await getApprovals();
        setApprovals(data);
      } catch (err) {
        console.error('Failed to fetch approvals:', err);
      }
    };
    fetchApprovals();
    const interval = setInterval(fetchApprovals, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleResolve = async (id: string, approved: boolean) => {
    try {
      await resolveApproval(id, approved);
      setApprovals(prev => prev.filter(req => req.id !== id));
    } catch (err) {
      console.error('Failed to resolve approval:', err);
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk.toLowerCase()) {
      case 'low': return '#4ade80';
      case 'medium': return '#facc15';
      case 'high': return '#fb923c';
      case 'critical': return '#f87171';
      default: return '#94a3b8';
    }
  };

  return (
    <div className="p-6 h-full overflow-y-auto" style={{ background: '#0a0a18' }}>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-1">Pending Approvals</h1>
        <p className="text-gray-400 text-sm">Actions requiring human authorization</p>
      </div>

      <div className="space-y-4">
        {approvals.map(req => (
          <div 
            key={req.id} 
            style={{ backgroundColor: '#12122a', borderColor: '#1e1e3a' }}
            className="border rounded-xl p-5 flex flex-col md:flex-row gap-4 justify-between items-start md:items-center shadow-lg"
          >
            <div className="space-y-2 flex-1 w-full overflow-hidden">
              <div className="flex items-center gap-3">
                <span className="font-semibold text-white">Agent: {req.agent_id}</span>
                <span 
                  className="px-2 py-0.5 rounded text-xs border flex items-center gap-1"
                  style={{
                    color: getRiskColor(req.risk),
                    borderColor: getRiskColor(req.risk),
                    backgroundColor: `${getRiskColor(req.risk)}20`
                  }}
                >
                  <AlertTriangle className="w-3 h-3" /> {req.risk.toUpperCase()}
                </span>
                <span className="text-xs text-gray-500 hidden sm:inline">
                  {new Date(req.created_at * 1000).toLocaleString()}
                </span>
              </div>
              <div 
                className="font-mono text-sm p-2 rounded border break-all"
                style={{ color: '#818cf8', backgroundColor: '#0a0a18', borderColor: '#1e1e3a' }}
              >
                {req.action}
              </div>
              <p className="text-sm text-gray-400 break-words">{JSON.stringify(req.details)}</p>
            </div>
            
            <div className="flex gap-3 w-full md:w-auto mt-4 md:mt-0 shrink-0">
              <button 
                onClick={() => handleResolve(req.id, false)}
                className="flex-1 md:flex-none flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-gray-300 hover:text-white border transition-colors"
                style={{ backgroundColor: '#0a0a18', borderColor: '#1e1e3a' }}
              >
                <X className="w-4 h-4" /> Deny
              </button>
              <button 
                onClick={() => handleResolve(req.id, true)}
                className="flex-1 md:flex-none flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-white transition-colors"
                style={{ backgroundColor: '#4f46e5' }}
              >
                <Check className="w-4 h-4" /> Approve
              </button>
            </div>
          </div>
        ))}
        {approvals.length === 0 && (
          <div className="text-center py-12 text-gray-500">No pending approvals</div>
        )}
      </div>
    </div>
  );
}
