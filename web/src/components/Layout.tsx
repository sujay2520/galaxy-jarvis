import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import BottomNav from './BottomNav';

export default function Layout() {
  return (
    <div className="flex h-screen w-full bg-galaxy-900 overflow-hidden font-sans text-gray-100">
      <Sidebar />
      <main className="flex-1 flex flex-col min-w-0 h-full relative">
        <div className="md:hidden p-4 border-b border-galaxy-800 flex justify-center items-center shrink-0">
           <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">Galaxy Jarvis</span>
        </div>
        <div className="flex-1 overflow-y-auto w-full">
          <Outlet />
        </div>
        <BottomNav />
      </main>
    </div>
  );
}
