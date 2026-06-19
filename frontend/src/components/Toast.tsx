import { AlertCircle, CheckCircle, X } from 'lucide-react';

interface Props {
  message: string;
  type: 'success' | 'error';
  onClose: () => void;
}

export default function Toast({ message, type, onClose }: Props) {
  return (
    <div className="fixed bottom-6 right-6 z-[100] animate-slide-up">
      <div
        className={`flex items-center gap-3 rounded-xl px-4 py-3 shadow-lg ${
          type === 'success' ? 'bg-emerald-600 text-white' : 'bg-red-600 text-white'
        }`}
      >
        {type === 'success' ? <CheckCircle className="h-5 w-5" /> : <AlertCircle className="h-5 w-5" />}
        <span className="text-sm font-medium">{message}</span>
        <button onClick={onClose}><X className="h-4 w-4 opacity-70" /></button>
      </div>
    </div>
  );
}
