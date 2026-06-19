import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Calendar, Clock, Video, MapPin, FileText, Check, X, Upload, ExternalLink } from 'lucide-react';
import { appointmentApi } from '../api';
import { useToast } from '../hooks/useToast';
import type { Appointment, CaseFile } from '../types';

export default function AppointmentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { show, Toast } = useToast();
  const [appointment, setAppointment] = useState<Appointment | null>(null);
  const [caseFiles, setCaseFiles] = useState<CaseFile[]>([]);
  const [canUpload, setCanUpload] = useState(false);
  const [canManage, setCanManage] = useState(false);
  const [loading, setLoading] = useState(true);
  const [files, setFiles] = useState<FileList | null>(null);

  const load = () => {
    if (!id) return;
    appointmentApi.detail(Number(id))
      .then(({ data }) => {
        setAppointment(data.appointment);
        setCaseFiles(data.case_files);
        setCanUpload(data.can_upload);
        setCanManage(data.can_manage);
      })
      .finally(() => setLoading(false));
  };

  useEffect(load, [id]);

  const handleAction = async (action: 'accept' | 'reject') => {
    try {
      const fn = action === 'accept' ? appointmentApi.accept : appointmentApi.reject;
      const { data } = await fn(Number(id));
      show(data.message);
      load();
    } catch {
      show('Action failed', 'error');
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!files?.length) return;
    try {
      const { data } = await appointmentApi.uploadFiles(Number(id), files);
      show(data.message);
      setFiles(null);
      load();
    } catch {
      show('Upload failed', 'error');
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (!appointment) return <div className="py-20 text-center text-slate-500">Appointment not found</div>;

  const statusColor = { pending: 'bg-amber-100 text-amber-700', accepted: 'bg-emerald-100 text-emerald-700', rejected: 'bg-red-100 text-red-700' }[appointment.status];

  return (
    <div className="mx-auto max-w-3xl px-4 py-10 sm:px-6 lg:px-8">
      {Toast}
      <Link to="/appointments" className="mb-6 inline-block text-sm text-primary hover:underline">← Back to appointments</Link>

      <div className="card mb-6">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <h1 className="text-2xl font-bold text-slate-900">Appointment Details</h1>
          <span className={`badge ${statusColor} !text-sm`}>{appointment.status_display}</span>
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="flex items-center gap-3 rounded-xl bg-slate-50 p-4">
            <Calendar className="h-5 w-5 text-primary" />
            <div><p className="text-xs text-slate-500">Date</p><p className="font-medium">{appointment.appointment_date}</p></div>
          </div>
          <div className="flex items-center gap-3 rounded-xl bg-slate-50 p-4">
            <Clock className="h-5 w-5 text-primary" />
            <div><p className="text-xs text-slate-500">Time</p><p className="font-medium">{appointment.appointment_time}</p></div>
          </div>
          <div className="flex items-center gap-3 rounded-xl bg-slate-50 p-4">
            {appointment.consultation_type === 'online' ? <Video className="h-5 w-5 text-primary" /> : <MapPin className="h-5 w-5 text-primary" />}
            <div><p className="text-xs text-slate-500">Type</p><p className="font-medium">{appointment.consultation_type_display}</p></div>
          </div>
          <div className="flex items-center gap-3 rounded-xl bg-slate-50 p-4">
            <FileText className="h-5 w-5 text-primary" />
            <div><p className="text-xs text-slate-500">Client</p><p className="font-medium">{appointment.user_name}</p></div>
          </div>
        </div>
        <div className="mt-4 rounded-xl bg-slate-50 p-4">
          <p className="text-xs text-slate-500">Lawyer</p>
          <p className="font-medium">{appointment.lawyer_name}</p>
        </div>
        {appointment.message && (
          <div className="mt-4 rounded-xl bg-slate-50 p-4">
            <p className="text-xs text-slate-500">Message</p>
            <p className="text-slate-700">{appointment.message}</p>
          </div>
        )}
        {appointment.meeting_link && (
          <a href={appointment.meeting_link} target="_blank" rel="noopener noreferrer" className="btn-primary mt-4 inline-flex">
            <ExternalLink className="h-4 w-4" /> Join Google Meet
          </a>
        )}
      </div>

      {canManage && appointment.status === 'pending' && (
        <div className="card mb-6 flex gap-3">
          <button onClick={() => handleAction('accept')} className="btn-primary flex-1"><Check className="h-4 w-4" /> Accept</button>
          <button onClick={() => handleAction('reject')} className="flex-1 rounded-xl border border-red-200 bg-red-50 px-5 py-2.5 text-sm font-semibold text-red-600 hover:bg-red-100"><X className="inline h-4 w-4" /> Reject</button>
        </div>
      )}

      {caseFiles.length > 0 && (
        <div className="card mb-6">
          <h2 className="mb-4 font-semibold text-slate-900">Case Files</h2>
          <div className="space-y-2">
            {caseFiles.map((f) => (
              <a key={f.id} href={f.file_url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-3 rounded-xl bg-slate-50 p-3 text-sm hover:bg-slate-100">
                <FileText className="h-4 w-4 text-primary" />
                <span className="flex-1 truncate">{f.file_url.split('/').pop()}</span>
                <span className="badge bg-slate-200 text-slate-600">{f.file_type}</span>
              </a>
            ))}
          </div>
        </div>
      )}

      {canUpload && (
        <div className="card">
          <h2 className="mb-4 flex items-center gap-2 font-semibold text-slate-900">
            <Upload className="h-5 w-5 text-primary" /> Upload Case Files
          </h2>
          <form onSubmit={handleUpload} className="space-y-4">
            <input type="file" multiple className="input-field" onChange={(e) => setFiles(e.target.files)} />
            <button type="submit" className="btn-primary" disabled={!files?.length}>Upload Files</button>
          </form>
        </div>
      )}
    </div>
  );
}
