import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import BottomNav from './BottomNav';
import { useTheme } from '../context/ThemeContext';
import { Menu } from 'lucide-react';

export default function Layout() {
  const { colors } = useTheme();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div 
      className="flex h-screen w-full overflow-hidden font-sans"
      style={{ background: colors.bg, color: colors.text }}
    >
      <Sidebar isMobile={false} />
      
      {/* Mobile Sidebar Overlay */}
      {mobileMenuOpen && (
        <div className="md:hidden fixed inset-0 z-50 flex">
          <div 
            className="fixed inset-0 bg-black/50 transition-opacity"
            onClick={() => setMobileMenuOpen(false)}
          />
          <div className="relative flex w-64 max-w-sm flex-col bg-transparent z-10 transition-transform transform translate-x-0">
            <Sidebar isMobile={true} onClose={() => setMobileMenuOpen(false)} />
          </div>
        </div>
      )}

      <main className="flex-1 flex flex-col min-w-0 h-full relative">
        <div 
          className="md:hidden p-4 flex justify-between items-center shrink-0"
          style={{ borderBottom: `1px solid ${colors.border}` }}
        >
          <button 
            onClick={() => setMobileMenuOpen(true)}
            className="p-2 -ml-2 rounded-lg"
            style={{ color: colors.text }}
          >
            <Menu className="w-6 h-6" />
          </button>
          <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-500">
            Galaxy
          </span>
          <div className="w-10"></div> {/* Spacer for center alignment */}
        </div>
        
        <div className="flex-1 overflow-y-auto w-full fade-in">
          <Outlet />
        </div>
        <BottomNav />
      </main>
    </div>
  );
}
