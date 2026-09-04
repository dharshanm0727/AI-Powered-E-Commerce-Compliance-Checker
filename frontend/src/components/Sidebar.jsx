import React, { useContext } from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, PlusCircle, History, BookOpen, Shield, LogOut } from 'lucide-react';
import { AuthContext } from '../context/AuthContext';

const Sidebar = () => {
  const { user, logout } = useContext(AuthContext);

  const navItems = [
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/submit', label: 'Submit Product', icon: PlusCircle },
    { to: '/history', label: 'Scan History', icon: History },
    { to: '/rules', label: 'Rule Explorer', icon: BookOpen },
  ];

  if (user && user.role === 'admin') {
    navItems.push({ to: '/admin', label: 'Admin Panel', icon: Shield });
  }

  return (
    <aside className="w-64 glass-panel border-r border-slate-800 flex flex-col justify-between min-h-screen p-4">
      <div>
        <div className="flex items-center gap-3 px-2 py-4 mb-6 border-b border-slate-800">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center font-bold text-white shadow-lg shadow-cyan-500/20">
            LM
          </div>
          <div>
            <h1 className="font-bold text-slate-100 text-sm tracking-tight">Compliance AI</h1>
            <p className="text-[11px] text-cyan-400 font-medium">Legal Metrology Rules</p>
          </div>
        </div>

        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`
                }
              >
                <Icon className="w-4 h-4" />
                {item.label}
              </NavLink>
            );
          })}
        </nav>
      </div>

      <div className="pt-4 border-t border-slate-800">
        <div className="px-3 py-2 mb-2">
          <p className="text-xs font-semibold text-slate-200">{user?.full_name || user?.email}</p>
          <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-slate-800 text-cyan-400">
            {user?.role}
          </span>
        </div>
        <button
          onClick={logout}
          className="w-full flex items-center gap-3 px-3 py-2 text-sm text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors"
        >
          <LogOut className="w-4 h-4" />
          Sign Out
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
