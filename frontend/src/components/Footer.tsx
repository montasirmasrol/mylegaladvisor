import { Link } from 'react-router-dom';
import { Scale } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-slate-900 text-slate-300">
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid gap-8 md:grid-cols-3">
          <div>
            <div className="mb-4 flex items-center gap-2 text-white">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
                <Scale className="h-4 w-4" />
              </div>
              <span className="font-bold">MyLegalAdvisor</span>
            </div>
            <p className="text-sm leading-relaxed text-slate-400">
              Connecting clients with qualified legal professionals for expert guidance and representation.
            </p>
          </div>
          <div>
            <h4 className="mb-3 text-sm font-semibold uppercase tracking-wider text-white">Quick Links</h4>
            <ul className="space-y-2 text-sm">
              <li><Link to="/lawyers" className="hover:text-white">Find a Lawyer</Link></li>
              <li><Link to="/register" className="hover:text-white">Register</Link></li>
              <li><Link to="/login" className="hover:text-white">Login</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="mb-3 text-sm font-semibold uppercase tracking-wider text-white">Contact</h4>
            <p className="text-sm text-slate-400">support@mylegaladvisor.com</p>
            <p className="mt-1 text-sm text-slate-400">Available 24/7 for support</p>
          </div>
        </div>
        <div className="mt-10 border-t border-slate-800 pt-6 text-center text-sm text-slate-500">
          &copy; {new Date().getFullYear()} MyLegalAdvisor. All rights reserved.
        </div>
      </div>
    </footer>
  );
}
