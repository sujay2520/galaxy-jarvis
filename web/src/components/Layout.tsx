import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import BottomNav from './BottomNav';
import { useTheme } from '../context/ThemeContext';

export default function Layout() {
  const { colors } = useTheme();

  return (
    <div 
      className="flex h-screen w-full overflow-hidden font-sans"
      style={{ background: colors.bg, color: colors.text }}
    >
      <Sidebar />
      <main className="flex-1 flex flex-col min-w-0 h-full relative">
        <div 
          className="md:hidden p-4 flex justify-center items-center shrink-0"
          style={{ borderBottom: `1px solid ${colors.border}` }}
        >
           <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-500">
             Galaxy
           </span>
        </div>
        <div className="flex-1 overflow-y-auto w-full">
          <Outlet />
        </div>
        <BottomNav />
      </main>
    </div>
  );
}
