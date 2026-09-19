import { NavLink } from 'react-router-dom';
import { MessageSquare, Bot, ScrollText, Settings, History } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

export default function BottomNav() {
  const { colors } = useTheme();

  const navItems = [
    { to: '/', icon: MessageSquare },
    { to: '/agents', icon: Bot },
    { to: '/conversations', icon: History },
    { to: '/audit', icon: ScrollText },
    { to: '/settings', icon: Settings },
  ];

  return (
    <nav 
      className="md:hidden flex items-center justify-around pb-safe pt-2 px-2 shrink-0"
      style={{ 
        background: colors.bg,
        borderTop: `1px solid ${colors.border}`
      }}
    >
      {navItems.map(item => (
        <NavLink
          key={item.to}
          to={item.to}
          className="p-3 rounded-xl transition-colors"
          style={({ isActive }) => ({
            background: isActive ? colors.cardHover : 'transparent',
            color: isActive ? colors.accent : colors.textMuted
          })}
        >
          <item.icon className="w-6 h-6" />
        </NavLink>
      ))}
    </nav>
  );
}
