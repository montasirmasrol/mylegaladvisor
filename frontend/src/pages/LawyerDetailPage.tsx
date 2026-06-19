import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Star, User, MapPin, Phone, Calendar, MessageSquare, Award } from 'lucide-react';
import { lawyerApi } from '../api';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../hooks/useToast';
import type { Lawyer, LawyerRating } from '../types';

export default function LawyerDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const navigate = useNavigate();
  const { show, Toast } = useToast();
  const [lawyer, setLawyer] = useState<Lawyer | null>(null);
  const [ratings, setRatings] = useState<LawyerRating[]>([]);
  const [loading, setLoading] = useState(true);
  const [booking, setBooking] = useState({
    appointment_date: '', appointment_time: '', message: '', consultation_type: 'offline' as 'offline' | 'online',
  });
  const [rating, setRating] = useState({ rating: 5, comment: '' });
  const [caseFiles, setCaseFiles] = useState<FileList | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!id) return;
    lawyerApi.detail(Number(id))
      .then(({ data }) => {
        setLawyer(data.lawyer);
        setRatings(data.ratings);
        if (data.user_rating) {
          setRating({ rating: data.user_rating.rating, comment: data.user_rating.comment });
        }
      })
      .finally(() => setLoading(false));
  }, [id]);

  const handleBook = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) { navigate('/login'); return; }
    setSubmitting(true);
    const form = new FormData();
    form.append('action', 'appointment');
    Object.entries(booking).forEach(([k, v]) => form.append(k, v));
    if (caseFiles) Array.from(caseFiles).forEach((f) => form.append('case_files', f));
    try {
      const { data } = await lawyerApi.bookAppointment(Number(id), form);
      show(data.message);
      navigate('/appointments');
    } catch {
      show('Failed to book appointment', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  const handleRate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) { navigate('/login'); return; }
    try {
      const { data } = await lawyerApi.rate(Number(id), rating.rating, rating.comment);
      show(data.message);
    } catch {
      show('Failed to submit rating', 'error');
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (!lawyer) return <div className="py-20 text-center text-slate-500">Lawyer not found</div>;

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
      {Toast}
      <div className="grid gap-8 lg:grid-cols-3">
        {/* Profile */}
        <div className="lg:col-span-1">
          <div className="card sticky top-24">
            {lawyer.photo_url ? (
              <img src={lawyer.photo_url} alt={lawyer.full_name} className="mx-auto mb-4 h-32 w-32 rounded-2xl object-cover ring-4 ring-primary/10" />
            ) : (
              <div className="mx-auto mb-4 flex h-32 w-32 items-center justify-center rounded-2xl bg-gradient-to-br from-primary/10 to-secondary/10">
                <User className="h-16 w-16 text-primary" />
              </div>
            )}
            <h1 className="text-center text-xl font-bold text-slate-900">{lawyer.full_name}</h1>
            <p className="text-center text-sm text-primary">{lawyer.lawyer_type_display}</p>
            <div className="mt-3 flex items-center justify-center gap-1">
              {[1, 2, 3, 4, 5].map((s) => (
                <Star key={s} className={`h-4 w-4 ${s <= Math.round(lawyer.avg_rating) ? 'fill-amber-400 text-amber-400' : 'text-slate-200'}`} />
              ))}
              <span className="ml-1 text-sm font-medium">{lawyer.avg_rating.toFixed(1)}</span>
            </div>
            <div className="mt-4 space-y-2 text-sm text-slate-600">
              <div className="flex items-center gap-2"><Award className="h-4 w-4 text-primary" /> {lawyer.experience_years} years experience</div>
              {lawyer.phone_number && <div className="flex items-center gap-2"><Phone className="h-4 w-4 text-primary" /> {lawyer.phone_number}</div>}
              {lawyer.address && <div className="flex items-center gap-2"><MapPin className="h-4 w-4 text-primary" /> {lawyer.address}</div>}
            </div>
            {user && (
              <Link to={`/chat/${lawyer.id}`} className="btn-outline mt-6 w-full">
                <MessageSquare className="h-4 w-4" /> Start Chat
              </Link>
            )}
          </div>
        </div>

        {/* Main content */}
        <div className="space-y-8 lg:col-span-2">
          <div className="card">
            <h2 className="mb-3 text-lg font-semibold text-slate-900">About</h2>
            <p className="text-slate-600 leading-relaxed">{lawyer.bio || 'No bio provided yet.'}</p>
          </div>

          {/* Booking */}
          {user?.user_type === 'user' && (
            <div className="card">
              <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-slate-900">
                <Calendar className="h-5 w-5 text-primary" /> Book Appointment
              </h2>
              <form onSubmit={handleBook} className="space-y-4">
                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <label className="mb-1.5 block text-sm font-medium">Date</label>
                    <input type="date" className="input-field" required value={booking.appointment_date} onChange={(e) => setBooking({ ...booking, appointment_date: e.target.value })} min={new Date().toISOString().split('T')[0]} />
                  </div>
                  <div>
                    <label className="mb-1.5 block text-sm font-medium">Time</label>
                    <input type="time" className="input-field" required value={booking.appointment_time} onChange={(e) => setBooking({ ...booking, appointment_time: e.target.value })} />
                  </div>
                </div>
                <div>
                  <label className="mb-1.5 block text-sm font-medium">Consultation Type</label>
                  <div className="flex gap-3">
                    {(['offline', 'online'] as const).map((t) => (
                      <button key={t} type="button" onClick={() => setBooking({ ...booking, consultation_type: t })}
                        className={`flex-1 rounded-xl border-2 p-3 text-sm font-medium capitalize transition ${booking.consultation_type === t ? 'border-primary bg-primary/5 text-primary' : 'border-slate-200'}`}>
                        {t} Meeting
                      </button>
                    ))}
                  </div>
                </div>
                <div>
                  <label className="mb-1.5 block text-sm font-medium">Message</label>
                  <textarea className="input-field min-h-[80px]" value={booking.message} onChange={(e) => setBooking({ ...booking, message: e.target.value })} placeholder="Describe your legal matter..." />
                </div>
                <div>
                  <label className="mb-1.5 block text-sm font-medium">Case Files (optional)</label>
                  <input type="file" multiple className="input-field" onChange={(e) => setCaseFiles(e.target.files)} />
                </div>
                <button type="submit" disabled={submitting} className="btn-primary">
                  {submitting ? 'Sending...' : 'Request Appointment'}
                </button>
              </form>
            </div>
          )}

          {/* Rating */}
          {user?.user_type === 'user' && (
            <div className="card">
              <h2 className="mb-4 text-lg font-semibold text-slate-900">Rate this Lawyer</h2>
              <form onSubmit={handleRate} className="space-y-4">
                <div className="flex gap-1">
                  {[1, 2, 3, 4, 5].map((s) => (
                    <button key={s} type="button" onClick={() => setRating({ ...rating, rating: s })}>
                      <Star className={`h-7 w-7 transition ${s <= rating.rating ? 'fill-amber-400 text-amber-400' : 'text-slate-200 hover:text-amber-200'}`} />
                    </button>
                  ))}
                </div>
                <textarea className="input-field min-h-[60px]" placeholder="Your review (optional)" value={rating.comment} onChange={(e) => setRating({ ...rating, comment: e.target.value })} />
                <button type="submit" className="btn-secondary">Submit Rating</button>
              </form>
            </div>
          )}

          {/* Reviews */}
          <div className="card">
            <h2 className="mb-4 text-lg font-semibold text-slate-900">Reviews ({ratings.length})</h2>
            {ratings.length > 0 ? (
              <div className="space-y-4">
                {ratings.map((r) => (
                  <div key={r.id} className="border-b border-slate-100 pb-4 last:border-0">
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-slate-900">{r.user_name}</span>
                      <div className="flex">{[1,2,3,4,5].map((s) => <Star key={s} className={`h-3.5 w-3.5 ${s <= r.rating ? 'fill-amber-400 text-amber-400' : 'text-slate-200'}`} />)}</div>
                    </div>
                    {r.comment && <p className="mt-1 text-sm text-slate-600">{r.comment}</p>}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-slate-500">No reviews yet.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
