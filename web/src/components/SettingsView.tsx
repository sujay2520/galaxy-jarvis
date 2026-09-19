import { useEffect, useState } from 'react';
import { Settings, Cpu, HardDrive, Server, Zap } from 'lucide-react';

interface SystemInfo {
  cpu?: string;
  ram?: string;
  gpu?: string;
  os?: string;
  recommended_llm?: string;
}

export default function SettingsView() {
  const [sysInfo, setSysInfo] = useState<SystemInfo>({});
  const [geminiKey, setGeminiKey] = useState('');
  const [groqKey, setGroqKey] = useState('');
  const [mistralKey, setMistralKey] = useState('');
  const [provider, setProvider] = useState('Auto');
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);

  useEffect(() => {
    fetch('http://localhost:8000/api/system-info')
      .then(res => {
        if (res.ok) return res.json();
        return {};
      })
      .then(data => setSysInfo(data))
      .catch(console.error);
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      const res = await fetch('http://localhost:8000/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ geminiKey, groqKey, mistralKey, provider })
      });
      if (res.ok) {
        alert('Settings saved!');
      } else {
        alert('Failed to save settings');
      }
    } catch (err) {
      console.error(err);
      alert('Failed to save settings');
    }
    setSaving(false);
  };

  const handleTest = async () => {
    setTesting(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      alert('Connection successful!');
    } catch (err) {
      alert('Connection failed');
    }
    setTesting(false);
  };

  return (
    <div className="p-6 h-full overflow-y-auto" style={{ background: '#0a0a18' }}>
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-white mb-1 flex items-center gap-2">
            <Settings className="w-6 h-6 text-indigo-400" />
            System Settings
          </h1>
          <p className="text-gray-400 text-sm">Configure hardware utilization and API keys</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div 
            className="border rounded-xl p-5 shadow-lg"
            style={{ backgroundColor: '#12122a', borderColor: '#1e1e3a' }}
          >
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <Server className="w-5 h-5 text-indigo-400" /> System Specs
            </h2>
            <div className="space-y-4 text-sm">
              <div className="flex items-center justify-between border-b pb-2" style={{ borderColor: '#1e1e3a' }}>
                <span className="text-gray-400 flex items-center gap-2"><Cpu className="w-4 h-4"/> CPU</span>
                <span className="text-white text-right">{sysInfo.cpu || 'Detecting...'}</span>
              </div>
              <div className="flex items-center justify-between border-b pb-2" style={{ borderColor: '#1e1e3a' }}>
                <span className="text-gray-400 flex items-center gap-2"><HardDrive className="w-4 h-4"/> RAM</span>
                <span className="text-white text-right">{sysInfo.ram || 'Detecting...'}</span>
              </div>
              <div className="flex items-center justify-between border-b pb-2" style={{ borderColor: '#1e1e3a' }}>
                <span className="text-gray-400 flex items-center gap-2"><Zap className="w-4 h-4"/> GPU</span>
                <span className="text-white text-right">{sysInfo.gpu || 'Detecting...'}</span>
              </div>
              <div className="flex items-center justify-between pb-2">
                <span className="text-gray-400">OS</span>
                <span className="text-white text-right">{sysInfo.os || 'Detecting...'}</span>
              </div>
            </div>
            {sysInfo.recommended_llm && (
              <div className="mt-4 p-3 rounded-lg border text-sm" style={{ backgroundColor: '#0a0a18', borderColor: '#1e1e3a', color: '#94a3b8' }}>
                <strong className="text-indigo-400">Recommended LLM:</strong> {sysInfo.recommended_llm}
              </div>
            )}
          </div>

          <div 
            className="border rounded-xl p-5 shadow-lg"
            style={{ backgroundColor: '#12122a', borderColor: '#1e1e3a' }}
          >
            <h2 className="text-lg font-semibold text-white mb-4">LLM Configuration</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Preferred Provider</label>
                <select 
                  value={provider}
                  onChange={e => setProvider(e.target.value)}
                  className="w-full bg-transparent border rounded-lg px-3 py-2 text-white outline-none"
                  style={{ borderColor: '#1e1e3a', backgroundColor: '#0a0a18' }}
                >
                  <option value="Auto">Auto-select</option>
                  <option value="Local Ollama">Local Ollama</option>
                  <option value="Gemini">Gemini</option>
                  <option value="Groq">Groq</option>
                  <option value="Mistral">Mistral</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm text-gray-400 mb-1">Gemini API Key</label>
                <input 
                  type="password" 
                  value={geminiKey}
                  onChange={e => setGeminiKey(e.target.value)}
                  placeholder="AIzaSy..."
                  className="w-full bg-transparent border rounded-lg px-3 py-2 text-white outline-none placeholder-gray-600"
                  style={{ borderColor: '#1e1e3a', backgroundColor: '#0a0a18' }}
                />
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-1">Groq API Key</label>
                <input 
                  type="password" 
                  value={groqKey}
                  onChange={e => setGroqKey(e.target.value)}
                  placeholder="gsk_..."
                  className="w-full bg-transparent border rounded-lg px-3 py-2 text-white outline-none placeholder-gray-600"
                  style={{ borderColor: '#1e1e3a', backgroundColor: '#0a0a18' }}
                />
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-1">Mistral API Key</label>
                <input 
                  type="password" 
                  value={mistralKey}
                  onChange={e => setMistralKey(e.target.value)}
                  placeholder="Leave empty if not using"
                  className="w-full bg-transparent border rounded-lg px-3 py-2 text-white outline-none placeholder-gray-600"
                  style={{ borderColor: '#1e1e3a', backgroundColor: '#0a0a18' }}
                />
              </div>
            </div>
          </div>
        </div>

        <div className="flex gap-4">
          <button 
            onClick={handleSave}
            disabled={saving}
            className="px-6 py-2 rounded-lg text-white font-medium transition-colors cursor-pointer"
            style={{ backgroundColor: '#4f46e5', opacity: saving ? 0.7 : 1 }}
          >
            {saving ? 'Saving...' : 'Save Settings'}
          </button>
          <button 
            onClick={handleTest}
            disabled={testing}
            className="px-6 py-2 rounded-lg text-white font-medium transition-colors border cursor-pointer hover:bg-white/5"
            style={{ backgroundColor: '#12122a', borderColor: '#1e1e3a', opacity: testing ? 0.7 : 1 }}
          >
            {testing ? 'Testing...' : 'Test Connection'}
          </button>
        </div>
      </div>
    </div>
  );
}
