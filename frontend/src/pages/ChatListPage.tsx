import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { MessageSquare, User, ChevronRight, ArrowLeft } from 'lucide-react';
import { chatApi } from '../api';
import type { ChatUser } from '../types';

export default function ChatListPage() {
  const navigate = useNavigate();
  const [users, setUsers] = useState<ChatUser[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    chatApi.users()
      .then(({ data }) => setUsers(data.users))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="mx-auto max-w-2xl px-4 py-10 sm:px-6 lg:px-8">
      <div className="mb-8 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Messages</h1>
          <p className="mt-2 text-slate-500">Select a conversation to start chatting</p>
        </div>
        <button type="button" onClick={() => navigate(-1)} className="btn-secondary w-full sm:w-auto">
          <ArrowLeft className="h-4 w-4" /> Back
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center py-20">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      ) : users.length > 0 ? (
        <div className="space-y-2">
          {users.map((u) => (
            <Link
              key={u.id}
              to={`/chat/${u.id}`}
              className="card flex items-center gap-4 !p-4 transition hover:-translate-y-0.5 hover:shadow-md"
            >
              {u.photo_url ? (
                <img src={u.photo_url} alt={u.full_name} className="h-12 w-12 rounded-full object-cover" />
              ) : (
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
                  <User className="h-6 w-6 text-primary" />
                </div>
              )}
              <div className="min-w-0 flex-1">
                <p className="font-semibold text-slate-900">{u.full_name}</p>
                <p className="text-sm capitalize text-slate-500">{u.user_type}</p>
              </div>
              <ChevronRight className="h-5 w-5 text-slate-300" />
            </Link>
          ))}
        </div>
      ) : (
        <div className="card py-16 text-center">
          <MessageSquare className="mx-auto mb-4 h-12 w-12 text-slate-300" />
          <p className="text-slate-500">No conversations available.</p>
        </div>
      )}
    </div>
  );
}
