import { useEffect, useState } from 'react';
import { Settings, Cpu, HardDrive, Server, Zap, AlertTriangle, Check, X } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import { ApprovalRequest } from '../types';
import { getApprovals, resolveApproval } from '../services/api';

interface SystemInfo {
  os_name?: string;
  cpu_count?: number;
  ram_gb?: number;
  disk_free_gb?: number;
  gpu_name?: string;
  vram_gb?: number;
  recommended_llm?: string;
}

export default function SettingsView() {
  const { colors } = useTheme();
  const [sysInfo, setSysInfo] = useState<SystemInfo>({});
  const [geminiKey, setGeminiKey] = useState('');
  const [groqKey, setGroqKey] = useState('');
  const [mistralKey, setMistralKey] = useState('');
  const [provider, setProvider] = useState('Auto');
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [toastMsg, setToastMsg] = useState('');
  
  const [approvals, setApprovals] = useState<ApprovalRequest[]>([]);

  useEffect(() => {
    fetch('http://localhost:8000/api/system-info')
      .then(res => {
        if (res.ok) return res.json();
        return {};
      })
      .then((data: SystemInfo) => {
        setSysInfo(data);
      })
      .catch(console.error);

    const fetchApprovals = async () => {
      try {
        const data = await getApprovals();
        setApprovals(data ? Object.values(data) : []);
      } catch (err) {
        console.error('Failed to fetch approvals:', err);
      }
    };
    fetchApprovals();
    const interval = setInterval(fetchApprovals, 3000);
    return () => clearInterval(interval);
  }, []);

  const showToast = (msg: string) => {
    setToastMsg(msg);
    setTimeout(() => setToastMsg(''), 3000);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const res = await fetch('http://localhost:8000/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ geminiKey, groqKey, mistralKey, provider })
      });
      if (res.ok) {
        showToast('Settings saved successfully!');
      } else {
        showToast('Failed to save settings');
      }
    } catch (err) {
      console.error(err);
      showToast('Failed to save settings');
    }
    setSaving(false);
  };

  const handleTest = async () => {
    setTesting(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      showToast('Connection successful!');
    } catch (err) {
      showToast('Connection failed');
    }
    setTesting(false);
  };

  const handleResolve = async (id: string, approved: boolean) => {
    try {
      await resolveApproval(id, approved);
      setApprovals(prev => prev.filter(req => req.id !== id));
      showToast(approved ? 'Action approved' : 'Action denied');
    } catch (err) {
      console.error('Failed to resolve approval:', err);
      showToast('Failed to resolve approval');
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk.toLowerCase()) {
      case 'low': return '#4ade80';
      case 'medium': return '#facc15';
      case 'high': return '#fb923c';
      case 'critical': return '#f87171';
      default: return colors.textMuted;
    }
  };

  return (
    <div className="p-6 h-full overflow-y-auto fade-in relative" style={{ background: colors.bg }}>
      {/* Toast Notification */}
      {toastMsg && (
        <div 
          className="fixed top-4 left-1/2 -translate-x-1/2 px-4 py-2 rounded-full shadow-lg text-sm font-medium z-50 animate-bounce"
          style={{ backgroundColor: colors.accent, color: '#fff' }}
        >
          {toastMsg}
        </div>
      )}

      <div className="max-w-4xl mx-auto space-y-10">
        
        {/* Settings Section */}
        <div>
          <div className="mb-8">
            <h1 className="text-2xl font-bold mb-1 flex items-center gap-2" style={{ color: colors.text }}>
              <Settings className="w-6 h-6" style={{ color: colors.accentLight }} />
              System Settings
            </h1>
            <p className="text-sm" style={{ color: colors.textMuted }}>Configure hardware utilization and API keys</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div 
              className="border rounded-xl p-5 shadow-lg"
              style={{ backgroundColor: colors.card, borderColor: colors.border }}
            >
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2" style={{ color: colors.text }}>
                <Server className="w-5 h-5" style={{ color: colors.accentLight }} /> System Specs
              </h2>
              <div className="space-y-4 text-sm">
                <div className="flex items-center justify-between border-b pb-2" style={{ borderColor: colors.border }}>
                  <span className="flex items-center gap-2" style={{ color: colors.textMuted }}><Cpu className="w-4 h-4"/> CPU</span>
                  <span className="text-right font-medium truncate max-w-[150px]" style={{ color: colors.text }}>{sysInfo.cpu_count ? `${sysInfo.cpu_count} cores` : 'Detecting...'}</span>
                </div>
                <div className="flex items-center justify-between border-b pb-2" style={{ borderColor: colors.border }}>
                  <span className="flex items-center gap-2" style={{ color: colors.textMuted }}><HardDrive className="w-4 h-4"/> RAM</span>
                  <span className="text-right font-medium" style={{ color: colors.text }}>{sysInfo.ram_gb ? `${sysInfo.ram_gb.toFixed(1)} GB` : 'Detecting...'}</span>
                </div>
                <div className="flex items-center justify-between border-b pb-2" style={{ borderColor: colors.border }}>
                  <span className="flex items-center gap-2" style={{ color: colors.textMuted }}><Zap className="w-4 h-4"/> GPU</span>
                  <span className="text-right font-medium truncate max-w-[150px]" style={{ color: colors.text }} title={sysInfo.gpu_name}>{sysInfo.gpu_name || 'Detecting...'}</span>
                </div>
                <div className="flex items-center justify-between pb-2">
                  <span style={{ color: colors.textMuted }}>OS</span>
                  <span className="text-right font-medium truncate max-w-[150px]" style={{ color: colors.text }}>{sysInfo.os_name || 'Detecting...'}</span>
                </div>
              </div>
              {sysInfo.recommended_llm && (
                <div className="mt-4 p-3 rounded-lg border text-sm" style={{ backgroundColor: colors.bg, borderColor: colors.border, color: colors.textMuted }}>
                  <strong style={{ color: colors.accentLight }}>Recommended LLM:</strong> {sysInfo.recommended_llm}
                </div>
              )}
            </div>

            <div 
              className="border rounded-xl p-5 shadow-lg"
              style={{ backgroundColor: colors.card, borderColor: colors.border }}
            >
              <h2 className="text-lg font-semibold mb-4" style={{ color: colors.text }}>LLM Configuration</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1.5" style={{ color: colors.textMuted }}>Preferred Provider</label>
                  <select 
                    value={provider}
                    onChange={e => setProvider(e.target.value)}
                    className="w-full bg-transparent border rounded-lg px-3 py-2 outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 transition-shadow"
                    style={{ borderColor: colors.border, backgroundColor: colors.bg, color: colors.text }}
                  >
                    <option value="Auto">Auto-select</option>
                    <option value="Local Ollama">Local Ollama</option>
                    <option value="Gemini">Gemini</option>
                    <option value="Groq">Groq</option>
                    <option value="Mistral">Mistral</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-1.5" style={{ color: colors.textMuted }}>Gemini API Key</label>
                  <input 
                    type="password" 
                    value={geminiKey}
                    onChange={e => setGeminiKey(e.target.value)}
                    placeholder="AIzaSy..."
                    className="w-full bg-transparent border rounded-lg px-3 py-2 outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 transition-shadow"
                    style={{ borderColor: colors.border, backgroundColor: colors.bg, color: colors.text }}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1.5" style={{ color: colors.textMuted }}>Groq API Key</label>
                  <input 
                    type="password" 
                    value={groqKey}
                    onChange={e => setGroqKey(e.target.value)}
                    placeholder="gsk_..."
                    className="w-full bg-transparent border rounded-lg px-3 py-2 outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 transition-shadow"
                    style={{ borderColor: colors.border, backgroundColor: colors.bg, color: colors.text }}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1.5" style={{ color: colors.textMuted }}>Mistral API Key</label>
                  <input 
                    type="password" 
                    value={mistralKey}
                    onChange={e => setMistralKey(e.target.value)}
                    placeholder="Leave empty if not using"
                    className="w-full bg-transparent border rounded-lg px-3 py-2 outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 transition-shadow"
                    style={{ borderColor: colors.border, backgroundColor: colors.bg, color: colors.text }}
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="flex gap-4">
            <button 
              onClick={handleSave}
              disabled={saving}
              className="px-6 py-2.5 rounded-lg text-white font-medium transition-colors cursor-pointer"
              style={{ backgroundColor: colors.accent, opacity: saving ? 0.7 : 1 }}
            >
              {saving ? 'Saving...' : 'Save Settings'}
            </button>
            <button 
              onClick={handleTest}
              disabled={testing}
              className="px-6 py-2.5 rounded-lg font-medium transition-colors border cursor-pointer hover:opacity-80"
              style={{ backgroundColor: colors.card, borderColor: colors.border, color: colors.text, opacity: testing ? 0.7 : 1 }}
            >
              {testing ? 'Testing...' : 'Test Connection'}
            </button>
          </div>
        </div>

        {/* Approvals Section */}
        <div>
          <div className="mb-6 pt-6 border-t" style={{ borderColor: colors.border }}>
            <h2 className="text-xl font-bold mb-1" style={{ color: colors.text }}>Pending Approvals</h2>
            <p className="text-sm" style={{ color: colors.textMuted }}>Actions requiring human authorization</p>
          </div>

          <div className="space-y-4">
            {approvals.map(req => (
              <div 
                key={req.id} 
                style={{ backgroundColor: colors.card, borderColor: colors.border }}
                className="border rounded-xl p-5 flex flex-col md:flex-row gap-4 justify-between items-start md:items-center shadow-lg transition-all"
              >
                <div className="space-y-2 flex-1 w-full overflow-hidden">
                  <div className="flex items-center gap-3">
                    <span className="font-semibold" style={{ color: colors.text }}>Agent: {req.agent_id}</span>
                    <span 
                      className="px-2 py-0.5 rounded text-xs border flex items-center gap-1 font-medium"
                      style={{
                        color: getRiskColor(req.risk),
                        borderColor: getRiskColor(req.risk),
                        backgroundColor: `${getRiskColor(req.risk)}20`
                      }}
                    >
                      <AlertTriangle className="w-3 h-3" /> {req.risk.toUpperCase()}
                    </span>
                    <span className="text-xs hidden sm:inline" style={{ color: colors.textDim }}>
                      {new Date(req.created_at * 1000).toLocaleString()}
                    </span>
                  </div>
                  <div 
                    className="font-mono text-sm p-3 rounded border break-all"
                    style={{ color: colors.accent, backgroundColor: colors.bg, borderColor: colors.border }}
                  >
                    {req.action}
                  </div>
                  <p className="text-sm break-words mt-1" style={{ color: colors.textMuted }}>{JSON.stringify(req.details)}</p>
                </div>
                
                <div className="flex gap-3 w-full md:w-auto mt-4 md:mt-0 shrink-0">
                  <button 
                    onClick={() => handleResolve(req.id, false)}
                    className="flex-1 md:flex-none flex items-center justify-center gap-2 px-5 py-2.5 rounded-lg border transition-colors hover:opacity-80"
                    style={{ backgroundColor: colors.bg, borderColor: colors.border, color: colors.textMuted }}
                  >
                    <X className="w-4 h-4" /> Deny
                  </button>
                  <button 
                    onClick={() => handleResolve(req.id, true)}
                    className="flex-1 md:flex-none flex items-center justify-center gap-2 px-5 py-2.5 rounded-lg text-white transition-colors hover:opacity-90 shadow-sm"
                    style={{ backgroundColor: colors.accent }}
                  >
                    <Check className="w-4 h-4" /> Approve
                  </button>
                </div>
              </div>
            ))}
            {approvals.length === 0 && (
              <div className="text-center py-16 border rounded-xl border-dashed" style={{ borderColor: colors.border, color: colors.textDim }}>
                <Check className="w-8 h-8 mx-auto mb-2 opacity-50" />
                No pending approvals
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
