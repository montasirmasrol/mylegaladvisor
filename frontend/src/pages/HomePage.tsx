import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Shield, Users, Clock, MessageCircle, ChevronDown } from 'lucide-react';
import { homeApi } from '../api';
import LawyerCard from '../components/LawyerCard';
import { useToast } from '../hooks/useToast';
import type { Lawyer } from '../types';

const faqs = [
  { q: 'How do I book an appointment with a lawyer?', a: 'Browse our lawyer directory, select a lawyer, and use the booking form on their profile page to request an appointment.' },
  { q: 'Can I consult with a lawyer online?', a: 'Yes! Many lawyers offer online consultations via Google Meet. Select "Online Meeting" when booking.' },
  { q: 'How are lawyers verified?', a: 'All lawyers on our platform are registered professionals. Admin reviews profiles before they appear publicly.' },
  { q: 'Is my information kept confidential?', a: 'Absolutely. All communications and case files are protected and only shared between you and your chosen lawyer.' },
];

export default function HomePage() {
  const [lawyers, setLawyers] = useState<Lawyer[]>([]);
  const [openFaq, setOpenFaq] = useState<number | null>(null);
  const [contact, setContact] = useState({ name: '', email: '', subject: '', message: '' });
  const [submitting, setSubmitting] = useState(false);
  const { show, Toast } = useToast();

  useEffect(() => {
    homeApi.getData().then(({ data }) => setLawyers(data.top_lawyers));
  }, []);

  const handleContact = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const { data } = await homeApi.contact(contact);
      show(data.message);
      setContact({ name: '', email: '', subject: '', message: '' });
    } catch {
      show('Failed to send message. Please try again.', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      {Toast}
      {/* Hero */}
      <section className="relative overflow-hidden bg-gradient-to-br from-slate-900 via-primary/90 to-secondary">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wMyI+PHBhdGggIGQ9Ik0zNiAzNGg0djJoLTR6bTAgNGg0djJoLTR6bTAtNGg0djJoLTR6bTAtNGg0djJoLTR6Ii8+PC9nPjwvZz48L3N2Zz4=')] opacity-50" />
        <div className="relative mx-auto max-w-7xl px-4 py-20 sm:px-6 sm:py-28 lg:px-8">
          <div className="max-w-2xl animate-slide-up">
            <span className="mb-4 inline-block rounded-full bg-white/10 px-4 py-1.5 text-sm font-medium text-white backdrop-blur">
              Trusted Legal Platform
            </span>
            <h1 className="text-4xl font-extrabold tracking-tight text-white sm:text-5xl lg:text-6xl">
              Expert Legal Advice,{' '}
              <span className="bg-gradient-to-r from-blue-200 to-purple-200 bg-clip-text text-transparent">
                When You Need It
              </span>
            </h1>
            <p className="mt-6 text-lg leading-relaxed text-blue-100">
              Connect with qualified lawyers, book consultations, and manage your legal matters — all in one modern platform.
            </p>
            <div className="mt-8 flex flex-wrap gap-4">
              <Link to="/lawyers" className="btn-primary !bg-white !text-primary hover:!bg-blue-50">
                Find a Lawyer <ArrowRight className="h-4 w-4" />
              </Link>
              <Link to="/register" className="inline-flex items-center gap-2 rounded-xl border border-white/30 px-5 py-2.5 text-sm font-semibold text-white backdrop-blur transition hover:bg-white/10">
                Get Started Free
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {[
            { icon: Shield, title: 'Verified Lawyers', desc: 'All professionals are vetted and verified' },
            { icon: Users, title: 'Expert Network', desc: 'Specialists across all legal fields' },
            { icon: Clock, title: 'Flexible Scheduling', desc: 'Book online or in-person meetings' },
            { icon: MessageCircle, title: 'Secure Chat', desc: 'Private messaging with your lawyer' },
          ].map(({ icon: Icon, title, desc }) => (
            <div key={title} className="card text-center">
              <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary">
                <Icon className="h-6 w-6" />
              </div>
              <h3 className="font-semibold text-slate-900">{title}</h3>
              <p className="mt-1 text-sm text-slate-500">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Top Lawyers */}
      <section className="bg-white py-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mb-10 flex items-end justify-between">
            <div>
              <h2 className="text-2xl font-bold text-slate-900 sm:text-3xl">Top Rated Lawyers</h2>
              <p className="mt-2 text-slate-500">Highly recommended by our community</p>
            </div>
            <Link to="/lawyers" className="hidden text-sm font-semibold text-primary hover:underline sm:block">
              View all →
            </Link>
          </div>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {lawyers.map((l) => <LawyerCard key={l.id} lawyer={l} />)}
          </div>
          {lawyers.length === 0 && (
            <p className="text-center text-slate-500">No lawyers available yet. Check back soon!</p>
          )}
        </div>
      </section>

      {/* FAQ */}
      <section className="mx-auto max-w-3xl px-4 py-16 sm:px-6 lg:px-8">
        <h2 className="mb-8 text-center text-2xl font-bold text-slate-900 sm:text-3xl">Frequently Asked Questions</h2>
        <div className="space-y-3">
          {faqs.map((faq, i) => (
            <div key={i} className="card !p-0 overflow-hidden">
              <button
                className="flex w-full items-center justify-between px-6 py-4 text-left"
                onClick={() => setOpenFaq(openFaq === i ? null : i)}
              >
                <span className="font-medium text-slate-900">{faq.q}</span>
                <ChevronDown className={`h-5 w-5 text-slate-400 transition ${openFaq === i ? 'rotate-180' : ''}`} />
              </button>
              {openFaq === i && (
                <div className="border-t border-slate-100 px-6 py-4 text-sm text-slate-600">{faq.a}</div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* Contact */}
      <section className="bg-slate-100 py-16">
        <div className="mx-auto max-w-xl px-4 sm:px-6 lg:px-8">
          <h2 className="mb-2 text-center text-2xl font-bold text-slate-900">Contact Us</h2>
          <p className="mb-8 text-center text-slate-500">Have questions? We&apos;d love to hear from you.</p>
          <form onSubmit={handleContact} className="card space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <input className="input-field" placeholder="Your name" required value={contact.name} onChange={(e) => setContact({ ...contact, name: e.target.value })} />
              <input className="input-field" type="email" placeholder="Email" required value={contact.email} onChange={(e) => setContact({ ...contact, email: e.target.value })} />
            </div>
            <input className="input-field" placeholder="Subject" required value={contact.subject} onChange={(e) => setContact({ ...contact, subject: e.target.value })} />
            <textarea className="input-field min-h-[120px] resize-y" placeholder="Your message" required value={contact.message} onChange={(e) => setContact({ ...contact, message: e.target.value })} />
            <button type="submit" disabled={submitting} className="btn-primary w-full">
              {submitting ? 'Sending...' : 'Send Message'}
            </button>
          </form>
        </div>
      </section>
    </>
  );
}
