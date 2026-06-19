import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Bell, CheckCheck, Calendar, MessageSquare } from 'lucide-react';
import { notificationApi } from '../api';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../hooks/useToast';
import type { Notification } from '../types';

const typeIcons: Record<string, typeof Bell> = {
  message: MessageSquare,
  appointment_request: Calendar,
  appointment_update: Calendar,
};

export default function NotificationsPage() {
  const { refreshNotifications } = useAuth();
  const { show, Toast } = useToast();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);

  const load = () => {
    notificationApi.list()
      .then(({ data }) => setNotifications(data.notifications))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const markRead = async (id: number) => {
    await notificationApi.markRead(id);
    setNotifications((prev) => prev.map((n) => n.id === id ? { ...n, is_read: true } : n));
    refreshNotifications();
  };

  const markAllRead = async () => {
    await notificationApi.markAllRead();
    setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
    refreshNotifications();
    show('All notifications marked as read');
  };

  const getLink = (n: Notification) => {
    if (n.type === 'message' && n.related_id) return `/chat`;
    if (n.type.startsWith('appointment') && n.related_id) return `/appointments/${n.related_id}`;
    return null;
  };

  return (
    <div className="mx-auto max-w-2xl px-4 py-10 sm:px-6 lg:px-8">
      {Toast}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Notifications</h1>
          <p className="mt-2 text-slate-500">Stay updated on your legal matters</p>
        </div>
        {notifications.some((n) => !n.is_read) && (
          <button onClick={markAllRead} className="btn-outline !py-2 text-xs">
            <CheckCheck className="h-4 w-4" /> Mark all read
          </button>
        )}
      </div>

      {loading ? (
        <div className="flex justify-center py-20">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      ) : notifications.length > 0 ? (
        <div className="space-y-2">
          {notifications.map((n) => {
            const Icon = typeIcons[n.type] || Bell;
            const link = getLink(n);
            const content = (
              <div
                className={`card flex items-start gap-4 !p-4 transition ${!n.is_read ? 'border-primary/30 bg-primary/5' : ''}`}
                onClick={() => !n.is_read && markRead(n.id)}
              >
                <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${!n.is_read ? 'bg-primary text-white' : 'bg-slate-100 text-slate-500'}`}>
                  <Icon className="h-5 w-5" />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-slate-500">{n.type_display}</p>
                  <p className="text-slate-900">{n.message}</p>
                  <p className="mt-1 text-xs text-slate-400">{new Date(n.created_at).toLocaleString()}</p>
                </div>
                {!n.is_read && <span className="mt-2 h-2.5 w-2.5 shrink-0 rounded-full bg-primary" />}
              </div>
            );
            return link ? <Link key={n.id} to={link}>{content}</Link> : <div key={n.id}>{content}</div>;
          })}
        </div>
      ) : (
        <div className="card py-16 text-center">
          <Bell className="mx-auto mb-4 h-12 w-12 text-slate-300" />
          <p className="text-slate-500">No notifications yet.</p>
        </div>
      )}
    </div>
  );
}
