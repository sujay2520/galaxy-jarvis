import { NavLink } from 'react-router-dom';
import { MessageSquare, Bot, Shield, CheckSquare, ScrollText, Settings } from 'lucide-react';
import { clsx } from 'clsx';

export default function BottomNav() {
  const navItems = [
    { to: '/', icon: MessageSquare },
    { to: '/agents', icon: Bot },
    { to: '/permissions', icon: Shield },
    { to: '/approvals', icon: CheckSquare },
    { to: '/audit', icon: ScrollText },
    { to: '/settings', icon: Settings },
  ];

  return (
    <nav className="md:hidden flex items-center justify-around bg-galaxy-900 border-t border-galaxy-800 pb-safe pt-2 px-2 shrink-0">
      {navItems.map(item => (
        <NavLink
          key={item.to}
          to={item.to}
          className={({ isActive }) => clsx(
            "p-3 rounded-xl transition-colors",
            isActive ? "text-galaxy-accent bg-galaxy-800" : "text-gray-500 hover:text-gray-300"
          )}
        >
          <item.icon className="w-6 h-6" />
        </NavLink>
      ))}
    </nav>
  );
}
