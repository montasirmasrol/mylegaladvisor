import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Search, Filter } from 'lucide-react';
import { lawyerApi } from '../api';
import LawyerCard from '../components/LawyerCard';
import type { Lawyer, Category } from '../types';

export default function LawyersPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const category = searchParams.get('category') || '';
  const [lawyers, setLawyers] = useState<Lawyer[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    lawyerApi.list(category || undefined)
      .then(({ data }) => {
        setLawyers(data.lawyers);
        setCategories(data.categories);
      })
      .finally(() => setLoading(false));
  }, [category]);

  const filtered = lawyers.filter((l) =>
    l.full_name.toLowerCase().includes(search.toLowerCase()) ||
    (l.lawyer_type_display || '').toLowerCase().includes(search.toLowerCase()),
  );

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">Find a Lawyer</h1>
        <p className="mt-2 text-slate-500">Browse our network of qualified legal professionals</p>
      </div>

      <div className="mb-8 flex flex-col gap-4 sm:flex-row">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            className="input-field pl-10"
            placeholder="Search by name or specialty..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="relative">
          <Filter className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <select
            className="input-field appearance-none pl-10 pr-8"
            value={category}
            onChange={(e) => setSearchParams(e.target.value ? { category: e.target.value } : {})}
          >
            <option value="">All Specialties</option>
            {categories.map((c) => (
              <option key={c.value} value={c.value}>{c.label}</option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-20">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      ) : filtered.length > 0 ? (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((l) => <LawyerCard key={l.id} lawyer={l} />)}
        </div>
      ) : (
        <div className="py-20 text-center text-slate-500">No lawyers found matching your criteria.</div>
      )}
    </div>
  );
}
