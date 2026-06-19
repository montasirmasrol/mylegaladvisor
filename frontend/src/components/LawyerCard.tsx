import { Star, User } from 'lucide-react';
import { Link } from 'react-router-dom';
import type { Lawyer } from '../types';

interface Props {
  lawyer: Lawyer;
}

export default function LawyerCard({ lawyer }: Props) {
  return (
    <Link
      to={`/lawyers/${lawyer.id}`}
      className="group card flex flex-col transition hover:-translate-y-1 hover:shadow-md"
    >
      <div className="mb-4 flex items-start gap-4">
        {lawyer.photo_url ? (
          <img
            src={lawyer.photo_url}
            alt={lawyer.full_name}
            className="h-16 w-16 rounded-2xl object-cover ring-2 ring-slate-100"
          />
        ) : (
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-primary/10 to-secondary/10 text-primary">
            <User className="h-8 w-8" />
          </div>
        )}
        <div className="min-w-0 flex-1">
          <h3 className="truncate font-semibold text-slate-900 group-hover:text-primary">
            {lawyer.full_name}
          </h3>
          <p className="text-sm text-primary">{lawyer.lawyer_type_display || 'Legal Professional'}</p>
          <div className="mt-1 flex items-center gap-1">
            <Star className="h-4 w-4 fill-amber-400 text-amber-400" />
            <span className="text-sm font-medium text-slate-700">
              {lawyer.avg_rating ? lawyer.avg_rating.toFixed(1) : 'New'}
            </span>
            <span className="text-xs text-slate-400">· {lawyer.experience_years} yrs exp.</span>
          </div>
        </div>
      </div>
      <p className="line-clamp-2 flex-1 text-sm text-slate-500">
        {lawyer.bio || 'Experienced legal professional ready to help with your case.'}
      </p>
      <span className="mt-4 text-sm font-semibold text-primary group-hover:underline">
        View Profile →
      </span>
    </Link>
  );
}
