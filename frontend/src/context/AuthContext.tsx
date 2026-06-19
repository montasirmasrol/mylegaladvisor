import { createContext, useContext, useEffect, useState, useCallback, type ReactNode } from 'react';
import { authApi, notificationApi } from '../api';
import { fetchCsrfToken } from '../api/client';
import type { User } from '../types';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  unreadCount: number;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  refreshNotifications: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [unreadCount, setUnreadCount] = useState(0);

  const refreshUser = useCallback(async () => {
    const { data } = await authApi.me();
    setUser(data.user);
  }, []);

  const refreshNotifications = useCallback(async () => {
    if (!user) return;
    try {
      const { data } = await notificationApi.list();
      setUnreadCount(data.unread_count);
    } catch {
      setUnreadCount(0);
    }
  }, [user]);

  useEffect(() => {
    fetchCsrfToken()
      .then(() => authApi.me())
      .then(({ data }) => setUser(data.user))
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (user) refreshNotifications();
  }, [user, refreshNotifications]);

  const login = async (username: string, password: string) => {
    const { data } = await authApi.login(username, password);
    setUser(data.user);
  };

  const logout = async () => {
    await authApi.logout();
    setUser(null);
    setUnreadCount(0);
  };

  return (
    <AuthContext.Provider
      value={{ user, loading, unreadCount, login, logout, refreshUser, refreshNotifications }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
