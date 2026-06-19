import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Calendar, Clock, User, ChevronRight } from 'lucide-react';
import { appointmentApi } from '../api';
import { useAuth } from '../context/AuthContext';
import type { Appointment } from '../types';

const statusColors: Record<string, string> = {
  pending: 'bg-amber-100 text-amber-700',
  accepted: 'bg-emerald-100 text-emerald-700',
  rejected: 'bg-red-100 text-red-700',
};

export default function AppointmentsPage() {
  const { user } = useAuth();
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    appointmentApi.list()
      .then(({ data }) => setAppointments(data.appointments))
      .finally(() => setLoading(false));
  }, []);

  const isLawyer = user?.user_type === 'lawyer';

  return (
    <div className="mx-auto max-w-4xl px-4 py-10 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">
          {isLawyer ? 'Appointment Requests' : 'My Appointments'}
        </h1>
        <p className="mt-2 text-slate-500">
          {isLawyer ? 'Review and manage incoming appointment requests' : 'Track your legal consultations'}
        </p>
      </div>

      {loading ? (
        <div className="flex justify-center py-20">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      ) : appointments.length > 0 ? (
        <div className="space-y-4">
          {appointments.map((a) => (
            <Link
              key={a.id}
              to={`/appointments/${a.id}`}
              className="card flex items-center gap-4 transition hover:-translate-y-0.5 hover:shadow-md"
            >
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
                <Calendar className="h-6 w-6" />
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-semibold text-slate-900">
                    {isLawyer ? a.user_name : a.lawyer_name}
                  </span>
                  <span className={`badge ${statusColors[a.status]}`}>{a.status_display}</span>
                </div>
                <div className="mt-1 flex flex-wrap gap-3 text-sm text-slate-500">
                  <span className="flex items-center gap-1"><Calendar className="h-3.5 w-3.5" /> {a.appointment_date}</span>
                  <span className="flex items-center gap-1"><Clock className="h-3.5 w-3.5" /> {a.appointment_time}</span>
                  <span className="flex items-center gap-1"><User className="h-3.5 w-3.5" /> {a.consultation_type_display}</span>
                </div>
              </div>
              <ChevronRight className="h-5 w-5 shrink-0 text-slate-300" />
            </Link>
          ))}
        </div>
      ) : (
        <div className="card py-16 text-center">
          <Calendar className="mx-auto mb-4 h-12 w-12 text-slate-300" />
          <p className="text-slate-500">No appointments yet.</p>
          {!isLawyer && (
            <Link to="/lawyers" className="btn-primary mt-4 inline-flex">Find a Lawyer</Link>
          )}
        </div>
      )}
    </div>
  );
}
