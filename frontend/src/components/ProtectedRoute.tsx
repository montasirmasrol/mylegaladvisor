import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

interface Props {
  children: React.ReactNode;
  roles?: Array<'user' | 'lawyer' | 'admin'>;
}

export default function ProtectedRoute({ children, roles }: Props) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (!user) return <Navigate to="/login" replace />;

  if (roles) {
    const role = user.is_superuser ? 'admin' : user.user_type;
    if (!roles.includes(role as 'user' | 'lawyer' | 'admin')) {
      return <Navigate to="/" replace />;
    }
  }

  return <>{children}</>;
}
