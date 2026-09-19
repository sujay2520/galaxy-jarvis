import { useEffect, useState } from 'react';
import { History, MessageSquare, Trash2 } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import { useNavigate } from 'react-router-dom';

interface Conversation {
  id: string;
  title: string;
  timestamp: string;
}

export default function ConversationHistory() {
  const { colors } = useTheme();
  const navigate = useNavigate();
  const [conversations, setConversations] = useState<Conversation[]>([]);

  useEffect(() => {
    // Load from localStorage
    const saved = localStorage.getItem('galaxy_conversations');
    if (saved) {
      try {
        setConversations(JSON.parse(saved));
      } catch (e) {
        setConversations([]);
      }
    } else {
      // Mock data if empty for demo
      const mock = [
        { id: '1', title: 'Setup React Project', timestamp: new Date(Date.now() - 86400000).toISOString() },
        { id: '2', title: 'Debug Python Script', timestamp: new Date(Date.now() - 172800000).toISOString() },
      ];
      setConversations(mock);
      localStorage.setItem('galaxy_conversations', JSON.stringify(mock));
    }
  }, []);

  const clearHistory = () => {
    if (confirm('Are you sure you want to clear history?')) {
      setConversations([]);
      localStorage.setItem('galaxy_conversations', '[]');
    }
  };

  const loadConversation = () => {
    // In a real app, this would load the messages into ChatView.
    // For now, we'll just navigate to home.
    navigate('/');
  };

  return (
    <div className="p-6 h-full overflow-y-auto" style={{ background: colors.bg }}>
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold mb-1 flex items-center gap-2" style={{ color: colors.text }}>
              <History className="w-6 h-6" style={{ color: colors.accentLight }} />
              Conversation History
            </h1>
            <p className="text-sm" style={{ color: colors.textMuted }}>Review your past chats with Galaxy</p>
          </div>
          {conversations.length > 0 && (
            <button 
              onClick={clearHistory}
              className="flex items-center gap-2 px-4 py-2 rounded-lg border transition-colors hover:bg-red-500/10 text-sm"
              style={{ backgroundColor: colors.card, borderColor: colors.border, color: '#f87171' }}
            >
              <Trash2 className="w-4 h-4" /> Clear All
            </button>
          )}
        </div>

        <div className="space-y-3">
          {conversations.length === 0 ? (
            <div className="text-center py-12" style={{ color: colors.textDim }}>
              No previous conversations
            </div>
          ) : (
            conversations.map(conv => (
              <div 
                key={conv.id}
                onClick={() => loadConversation()}
                className="p-4 rounded-xl border flex items-center justify-between cursor-pointer transition-colors shadow-sm hover:bg-white/5"
                style={{ 
                  backgroundColor: colors.card, 
                  borderColor: colors.border
                }}
              >
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{ backgroundColor: `${colors.accent}20` }}>
                    <MessageSquare className="w-5 h-5" style={{ color: colors.accent }} />
                  </div>
                  <div>
                    <h3 className="font-medium" style={{ color: colors.text }}>{conv.title}</h3>
                    <p className="text-xs mt-1" style={{ color: colors.textDim }}>
                      {new Date(conv.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
