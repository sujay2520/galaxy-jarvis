import { NavLink } from 'react-router-dom';
import { MessageSquare, Bot, ScrollText, Settings, PlusCircle, History, Sun, Moon } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

const navItems = [
  { to: '/', icon: MessageSquare, label: 'Chat' },
  { to: '/agents', icon: Bot, label: 'Agents' },
  { to: '/audit', icon: ScrollText, label: 'Audit Log' },
];

export default function Sidebar() {
  const { theme, colors, toggleTheme } = useTheme();

  return (
    <aside
      className="hidden md:flex flex-col h-screen shrink-0"
      style={{
        width: '260px',
        background: colors.bg,
        borderRight: `1px solid ${colors.border}`,
      }}
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 py-4" style={{ borderBottom: `1px solid ${colors.border}` }}>
        <div className="w-8 h-8 rounded-lg flex items-center justify-center"
          style={{ background: `linear-gradient(135deg, ${colors.accent}, ${colors.accentLight})` }}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
              stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </div>
        <span className="text-base font-semibold" style={{ color: colors.text }}>Galaxy</span>
      </div>

      <div className="px-3 py-4 space-y-2" style={{ borderBottom: `1px solid ${colors.border}` }}>
        <NavLink
          to="/"
          className="flex items-center justify-center gap-2 w-full py-2.5 rounded-lg text-sm font-medium text-white transition-all shadow-sm hover:opacity-90"
          style={{ background: colors.accent }}
        >
          <PlusCircle className="w-4 h-4" />
          New Conversation
        </NavLink>
        <NavLink
          to="/conversations"
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
          className="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm font-medium transition-all"
          style={{ color: colors.textMuted }}
        >
          {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          <span>{theme === 'dark' ? 'Light Mode' : 'Dark Mode'}</span>
        </button>

        <NavLink
          to="/settings"
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all"
          style={({ isActive }) => ({
            background: isActive ? colors.cardHover : 'transparent',
            color: isActive ? colors.accent : colors.textMuted,
          })}
        >
          <Settings className="w-4 h-4" />
          <span>Settings</span>
        </NavLink>
      </div>
    </aside>
  );
}
