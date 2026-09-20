import { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import { MessageSquare, Bot, ScrollText, Settings, PlusCircle, History, Sun, Moon, X } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import { getStatus } from '../services/api';

const navItems = [
  { to: '/', icon: MessageSquare, label: 'Chat' },
  { to: '/agents', icon: Bot, label: 'Agents' },
  { to: '/audit', icon: ScrollText, label: 'Audit Log' },
];

interface SidebarProps {
  isMobile?: boolean;
  onClose?: () => void;
}

export default function Sidebar({ isMobile = false, onClose }: SidebarProps) {
  const { theme, colors, toggleTheme } = useTheme();
  const [connected, setConnected] = useState(false);
  const [version, setVersion] = useState('v1.0.0');

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const res = await getStatus();
        setConnected(true);
        if (res?.version) setVersion(res.version);
      } catch (e) {
        setConnected(false);
      }
    };
    fetchStatus();
    const interval = setInterval(fetchStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <aside
      className={`${isMobile ? 'flex' : 'hidden md:flex'} flex-col h-full shrink-0`}
      style={{
        width: '260px',
        background: colors.bg,
        borderRight: `1px solid ${colors.border}`,
      }}
    >
      {/* Logo */}
      <div className="flex items-center justify-between px-5 py-4" style={{ borderBottom: `1px solid ${colors.border}` }}>
        <div className="flex items-center gap-3 relative">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center relative"
            style={{ background: `linear-gradient(135deg, ${colors.accent}, ${colors.accentLight})` }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
                stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            <div 
              className="absolute -top-1 -right-1 w-3 h-3 rounded-full border-2"
              style={{ 
                backgroundColor: connected ? '#4ade80' : '#f87171',
                borderColor: colors.bg
              }}
              title={connected ? "Connected to Server" : "Disconnected"}
            />
          </div>
          <span className="text-base font-semibold" style={{ color: colors.text }}>Galaxy</span>
        </div>
        
        {isMobile && onClose && (
          <button onClick={onClose} className="p-1 rounded-lg hover:opacity-80 transition-opacity" style={{ color: colors.textMuted }}>
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      <div className="px-3 py-4 space-y-2" style={{ borderBottom: `1px solid ${colors.border}` }}>
        <NavLink
          to="/"
          onClick={isMobile ? onClose : undefined}
          className="flex items-center justify-center gap-2 w-full py-2.5 rounded-lg text-sm font-medium text-white transition-all shadow-sm hover:opacity-90"
          style={{ background: colors.accent }}
        >
          <PlusCircle className="w-4 h-4" />
          New Conversation
        </NavLink>
        <NavLink
          to="/conversations"
          onClick={isMobile ? onClose : undefined}
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150"
          style={({ isActive }) => ({
            background: isActive ? colors.cardHover : 'transparent',
            color: isActive ? colors.accent : colors.textMuted,
          })}
        >
          <History className="w-4 h-4 shrink-0" />
          <span>Conversation History</span>
        </NavLink>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navItems.map(item => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            onClick={isMobile ? onClose : undefined}
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150"
            style={({ isActive }) => ({
              background: isActive ? colors.cardHover : 'transparent',
              color: isActive ? colors.accent : colors.textMuted,
            })}
          >
            <item.icon className="w-4 h-4 shrink-0" />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-3 space-y-1" style={{ borderTop: `1px solid ${colors.border}` }}>
        <button
          onClick={toggleTheme}
          className="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm font-medium transition-all hover:opacity-80"
          style={{ color: colors.textMuted }}
        >
          {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          <span>{theme === 'dark' ? 'Light Mode' : 'Dark Mode'}</span>
        </button>

        <NavLink
          to="/settings"
          onClick={isMobile ? onClose : undefined}
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all"
          style={({ isActive }) => ({
            background: isActive ? colors.cardHover : 'transparent',
            color: isActive ? colors.accent : colors.textMuted,
          })}
        >
          <Settings className="w-4 h-4" />
          <span>Settings</span>
        </NavLink>
        
        <div className="pt-2 px-3 pb-1 flex items-center justify-between text-xs" style={{ color: colors.textDim }}>
          <span>Galaxy IDE</span>
          <span>{version}</span>
        </div>
      </div>
    </aside>
  );
}
