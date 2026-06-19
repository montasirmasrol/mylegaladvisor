import { Link } from 'react-router-dom';
import { Scale, Menu, X, Bell, LogOut, User, MessageSquare, Calendar, Shield } from 'lucide-react';
import { useState } from 'react';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, logout, unreadCount } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);

  const navLinks = user ? [
    { to: '/lawyers', label: 'Lawyers', icon: Scale },
  ...(user.user_type === 'user' ? [{ to: '/appointments', label: 'Appointments', icon: Calendar }] : []),
  ...(user.user_type === 'lawyer' ? [{ to: '/appointments', label: 'Requests', icon: Calendar }] : []),
    { to: '/chat', label: 'Chat', icon: MessageSquare },
    ...(user.is_superuser ? [{ to: '/admin', label: 'Admin', icon: Shield }] : []),
  ] : [
    { to: '/lawyers', label: 'Lawyers', icon: Scale },
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-slate-200/80 bg-white/90 backdrop-blur-md">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
        <Link to="/" className="flex items-center gap-2 text-lg font-bold text-slate-900">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-secondary text-white">
            <Scale className="h-5 w-5" />
          </div>
          <span className="hidden sm:inline">MyLegalAdvisor</span>
        </Link>

        <div className="hidden items-center gap-1 md:flex">
          {navLinks.map(({ to, label }) => (
            <Link
              key={to}
              to={to}
              className="rounded-lg px-3 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-100 hover:text-slate-900"
            >
              {label}
            </Link>
          ))}
        </div>

        <div className="hidden items-center gap-2 md:flex">
          {user ? (
            <>
              <Link
                to="/notifications"
                className="relative rounded-lg p-2 text-slate-600 transition hover:bg-slate-100"
              >
                <Bell className="h-5 w-5" />
                {unreadCount > 0 && (
                  <span className="absolute -right-0.5 -top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-red-500 px-1 text-[10px] font-bold text-white">
                    {unreadCount > 9 ? '9+' : unreadCount}
                  </span>
                )}
              </Link>
              <Link to="/profile" className="btn-outline !py-2 !px-3">
                <User className="h-4 w-4" />
                {user.full_name}
              </Link>
              <button onClick={() => logout()} className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 hover:text-red-600">
                <LogOut className="h-5 w-5" />
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn-outline !py-2">Log in</Link>
              <Link to="/register" className="btn-primary !py-2">Sign up</Link>
            </>
          )}
        </div>

        <button
          className="rounded-lg p-2 text-slate-600 md:hidden"
          onClick={() => setMobileOpen(!mobileOpen)}
        >
          {mobileOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </nav>

      {mobileOpen && (
        <div className="border-t border-slate-100 bg-white px-4 py-4 md:hidden">
          <div className="flex flex-col gap-1">
            {navLinks.map(({ to, label, icon: Icon }) => (
              <Link
                key={to}
                to={to}
                onClick={() => setMobileOpen(false)}
                className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
              >
                <Icon className="h-4 w-4 text-primary" />
                {label}
              </Link>
            ))}
            {user ? (
              <>
                <Link to="/notifications" onClick={() => setMobileOpen(false)} className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50">
                  <Bell className="h-4 w-4 text-primary" />
                  Notifications {unreadCount > 0 && `(${unreadCount})`}
                </Link>
                <Link to="/profile" onClick={() => setMobileOpen(false)} className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50">
                  <User className="h-4 w-4 text-primary" />
                  Profile
                </Link>
                <button onClick={() => { logout(); setMobileOpen(false); }} className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-red-600 hover:bg-red-50">
                  <LogOut className="h-4 w-4" />
                  Log out
                </button>
              </>
            ) : (
              <div className="mt-2 flex flex-col gap-2">
                <Link to="/login" onClick={() => setMobileOpen(false)} className="btn-outline w-full">Log in</Link>
                <Link to="/register" onClick={() => setMobileOpen(false)} className="btn-primary w-full">Sign up</Link>
              </div>
            )}
          </div>
        </div>
      )}
    </header>
  );
}
