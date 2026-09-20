import { useEffect, useState } from 'react';
import { History, MessageSquare, Trash2, Search, X } from 'lucide-react';
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
  const [searchQuery, setSearchQuery] = useState('');

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
        { id: '3', title: 'Configure Nginx Server', timestamp: new Date(Date.now() - 259200000).toISOString() },
      ];
      setConversations(mock);
      localStorage.setItem('galaxy_conversations', JSON.stringify(mock));
    }
  }, []);

  const clearHistory = () => {
    if (confirm('Are you sure you want to clear all history?')) {
      setConversations([]);
      localStorage.setItem('galaxy_conversations', '[]');
    }
  };

  const deleteConversation = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    const updated = conversations.filter(c => c.id !== id);
    setConversations(updated);
    localStorage.setItem('galaxy_conversations', JSON.stringify(updated));
  };

  const loadConversation = () => {
    navigate('/');
  };

  const filteredConversations = conversations.filter(c => 
    c.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="p-6 h-full overflow-y-auto fade-in" style={{ background: colors.bg }}>
      <div className="max-w-4xl mx-auto">
        <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
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
              className="flex items-center gap-2 px-4 py-2 rounded-lg border transition-colors hover:bg-red-500/10 text-sm shrink-0"
              style={{ backgroundColor: colors.card, borderColor: colors.border, color: '#f87171' }}
            >
              <Trash2 className="w-4 h-4" /> Clear All
            </button>
          )}
        </div>

        {conversations.length > 0 && (
          <div className="mb-6 relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-4 w-4" style={{ color: colors.textMuted }} />
            </div>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search conversations..."
              className="block w-full pl-10 pr-3 py-2.5 border rounded-xl leading-5 bg-transparent outline-none transition-shadow focus-visible:ring-2 focus-visible:ring-indigo-500"
              style={{ 
                borderColor: colors.border, 
                backgroundColor: colors.card,
                color: colors.text 
              }}
            />
            {searchQuery && (
              <button 
                onClick={() => setSearchQuery('')}
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
              >
                <X className="h-4 w-4" style={{ color: colors.textMuted }} />
              </button>
            )}
          </div>
        )}

        <div className="space-y-3">
          {conversations.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-20 text-center border rounded-xl border-dashed" style={{ borderColor: colors.border }}>
              <History className="w-12 h-12 mb-4 opacity-50" style={{ color: colors.textDim }} />
              <h2 className="text-lg font-medium mb-1" style={{ color: colors.text }}>No conversations yet</h2>
              <p className="text-sm" style={{ color: colors.textMuted }}>Start chatting with Galaxy to see your history here.</p>
              <button 
                onClick={() => navigate('/')}
                className="mt-6 px-6 py-2 rounded-lg text-white font-medium transition-colors"
                style={{ backgroundColor: colors.accent }}
              >
                Start New Chat
              </button>
            </div>
          ) : filteredConversations.length === 0 ? (
            <div className="text-center py-12" style={{ color: colors.textDim }}>
              No conversations found matching "{searchQuery}"
            </div>
          ) : (
            filteredConversations.map(conv => (
              <div 
                key={conv.id}
                onClick={() => loadConversation()}
                className="p-4 rounded-xl border flex items-center justify-between cursor-pointer transition-colors shadow-sm hover:bg-white/5 group"
                style={{ 
                  backgroundColor: colors.card, 
                  borderColor: colors.border
                }}
              >
                <div className="flex items-center gap-4 min-w-0 flex-1">
                  <div className="w-10 h-10 rounded-full flex items-center justify-center shrink-0" style={{ backgroundColor: `${colors.accent}20` }}>
                    <MessageSquare className="w-5 h-5" style={{ color: colors.accent }} />
                  </div>
                  <div className="min-w-0">
                    <h3 className="font-medium truncate" style={{ color: colors.text }}>{conv.title}</h3>
                    <p className="text-xs mt-1" style={{ color: colors.textDim }}>
                      {new Date(conv.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
                
                <button
                  onClick={(e) => deleteConversation(e, conv.id)}
                  className="p-2 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-500/10"
                  style={{ color: colors.textMuted }}
                  title="Delete conversation"
                >
                  <Trash2 className="w-4 h-4 hover:text-red-400 transition-colors" />
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
