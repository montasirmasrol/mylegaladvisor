import { useEffect, useState } from 'react';
import { Shield, UserX, UserCheck, Trash2, Users, Briefcase } from 'lucide-react';
import { adminApi } from '../api';
import { useToast } from '../hooks/useToast';
import type { AdminUser } from '../types';

export default function AdminPage() {
  const { show, Toast } = useToast();
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [lawyers, setLawyers] = useState<AdminUser[]>([]);
  const [tab, setTab] = useState<'users' | 'lawyers'>('users');
  const [loading, setLoading] = useState(true);

  const load = () => {
    adminApi.dashboard()
      .then(({ data }) => {
        setUsers(data.users);
        setLawyers(data.lawyers);
      })
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const handleAction = async (action: 'suspend' | 'unsuspend' | 'delete', id: number) => {
    try {
      const fn = action === 'suspend' ? adminApi.suspend : action === 'unsuspend' ? adminApi.unsuspend : adminApi.deleteUser;
      const { data } = await fn(id);
      show(data.message);
      load();
    } catch {
      show('Action failed', 'error');
    }
  };

  const list = tab === 'users' ? users : lawyers;

  return (
    <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6 lg:px-8">
      {Toast}
      <div className="mb-8 flex items-center gap-3">
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-secondary text-white">
          <Shield className="h-6 w-6" />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Admin Dashboard</h1>
          <p className="text-slate-500">Manage users and lawyers</p>
        </div>
      </div>

      <div className="mb-6 flex gap-2">
        {(['users', 'lawyers'] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-medium transition ${
              tab === t ? 'bg-primary text-white' : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
            }`}
          >
            {t === 'users' ? <Users className="h-4 w-4" /> : <Briefcase className="h-4 w-4" />}
            {t === 'users' ? `Clients (${users.length})` : `Lawyers (${lawyers.length})`}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex justify-center py-20">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      ) : (
        <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
          <div className="hidden sm:grid sm:grid-cols-5 gap-4 border-b border-slate-100 bg-slate-50 px-6 py-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
            <span className="col-span-2">User</span>
            <span>Email</span>
            <span>Status</span>
            <span>Actions</span>
          </div>
          {list.map((u) => (
            <div key={u.id} className="grid gap-3 border-b border-slate-50 px-6 py-4 last:border-0 sm:grid-cols-5 sm:items-center">
              <div className="col-span-2">
                <p className="font-medium text-slate-900">{u.full_name}</p>
                <p className="text-sm text-slate-500">@{u.username}</p>
              </div>
              <p className="truncate text-sm text-slate-600">{u.email}</p>
              <span className={`badge w-fit ${u.is_suspended ? 'bg-red-100 text-red-700' : 'bg-emerald-100 text-emerald-700'}`}>
                {u.is_suspended ? 'Suspended' : 'Active'}
              </span>
              <div className="flex gap-1">
                {u.is_suspended ? (
                  <button onClick={() => handleAction('unsuspend', u.id)} className="rounded-lg p-2 text-emerald-600 hover:bg-emerald-50" title="Unsuspend">
                    <UserCheck className="h-4 w-4" />
                  </button>
                ) : (
                  <button onClick={() => handleAction('suspend', u.id)} className="rounded-lg p-2 text-amber-600 hover:bg-amber-50" title="Suspend">
                    <UserX className="h-4 w-4" />
                  </button>
                )}
                <button onClick={() => { if (confirm(`Delete ${u.username}?`)) handleAction('delete', u.id); }} className="rounded-lg p-2 text-red-600 hover:bg-red-50" title="Delete">
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
          {list.length === 0 && (
            <p className="py-12 text-center text-slate-500">No {tab} found.</p>
          )}
        </div>
      )}
    </div>
  );
}
