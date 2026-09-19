import { NavLink } from 'react-router-dom';
import { MessageSquare, Bot, Shield, CheckSquare, ScrollText, Settings } from 'lucide-react';

const navItems = [
  { to: '/', icon: MessageSquare, label: 'Chat' },
  { to: '/agents', icon: Bot, label: 'Agents' },
  { to: '/permissions', icon: Shield, label: 'Permissions' },
  { to: '/approvals', icon: CheckSquare, label: 'Approvals' },
  { to: '/audit', icon: ScrollText, label: 'Audit Log' },
];

export default function Sidebar() {
  return (
    <aside
      className="hidden md:flex flex-col h-screen shrink-0"
      style={{
        width: '220px',
        background: '#0a0a18',
        borderRight: '1px solid #1a1a2e',
      }}
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 py-4" style={{ borderBottom: '1px solid #1a1a2e' }}>
        <div className="w-8 h-8 rounded-lg flex items-center justify-center"
          style={{ background: 'linear-gradient(135deg, #4f46e5, #7c3aed)' }}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
              stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </div>
        <span className="text-sm font-semibold text-white">Galaxy</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-2 py-3 space-y-0.5">
        {navItems.map(item => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 ` +
              (isActive
                ? 'text-white'
                : 'text-gray-500 hover:text-gray-300 hover:bg-white/5')
            }
            style={({ isActive }) => isActive
              ? { background: '#1e1e3a', color: '#818cf8' }
              : {}
            }
          >
            {({ isActive }) => (
              <>
                <item.icon className="w-4 h-4 shrink-0" style={isActive ? { color: '#818cf8' } : {}} />
                <span>{item.label}</span>
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Settings */}
      <div className="px-2 py-3" style={{ borderTop: '1px solid #1a1a2e' }}>
        <NavLink
          to="/settings"
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-500 hover:text-gray-300 hover:bg-white/5 transition-all"
        >
          <Settings className="w-4 h-4" />
          <span>Settings</span>
        </NavLink>
      </div>
    </aside>
  );
}
