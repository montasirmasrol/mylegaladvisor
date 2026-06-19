import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, Save } from 'lucide-react';
import { profileApi } from '../api';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../hooks/useToast';
import type { LawyerProfile, UserProfile } from '../types';

const lawyerTypes = [
  { value: 'criminal', label: 'Criminal Law' },
  { value: 'civil', label: 'Civil Law' },
  { value: 'family', label: 'Family Law' },
  { value: 'corporate', label: 'Corporate Law' },
  { value: 'immigration', label: 'Immigration Law' },
  { value: 'tax', label: 'Tax Law' },
  { value: 'employment', label: 'Employment Law' },
  { value: 'real_estate', label: 'Real Estate Law' },
  { value: 'personal_injury', label: 'Personal Injury Law' },
  { value: 'other', label: 'Other' },
];

export default function ProfilePage() {
  const { user, refreshUser } = useAuth();
  const navigate = useNavigate();
  const { show, Toast } = useToast();
  const [profileType, setProfileType] = useState('');
  const [userFields, setUserFields] = useState({ first_name: '', last_name: '', email: '' });
  const [lawyerProfile, setLawyerProfile] = useState<Partial<LawyerProfile>>({});
  const [userProfile, setUserProfile] = useState<Partial<UserProfile>>({});
  const [photo, setPhoto] = useState<File | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (user?.is_superuser) {
      navigate('/admin');
      return;
    }
    profileApi.get()
      .then(({ data }) => {
        setProfileType(data.profile_type);
        setUserFields({
          first_name: data.user.first_name,
          last_name: data.user.last_name,
          email: data.user.email,
        });
        if (data.profile_type === 'lawyer') setLawyerProfile(data.profile as LawyerProfile);
        else setUserProfile(data.profile as UserProfile);
      })
      .finally(() => setLoading(false));
  }, [user, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    const form = new FormData();
    Object.entries(userFields).forEach(([k, v]) => form.append(k, v));
    if (profileType === 'lawyer') {
      Object.entries(lawyerProfile).forEach(([k, v]) => {
        if (k !== 'photo_url' && k !== 'lawyer_type_display' && v != null) form.append(k, String(v));
      });
    } else {
      Object.entries(userProfile).forEach(([k, v]) => {
        if (k !== 'photo_url' && v != null) form.append(k, String(v));
      });
    }
    if (photo) form.append('photo', photo);
    try {
      const { data } = await profileApi.update(form);
      show(data.message);
      await refreshUser();
    } catch {
      show('Failed to update profile', 'error');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  const photoUrl = profileType === 'lawyer' ? lawyerProfile.photo_url : userProfile.photo_url;

  return (
    <div className="mx-auto max-w-2xl px-4 py-10 sm:px-6 lg:px-8">
      {Toast}
      <h1 className="mb-8 text-3xl font-bold text-slate-900">My Profile</h1>
      <form onSubmit={handleSubmit} className="card space-y-6">
        <div className="flex items-center gap-4">
          {photoUrl ? (
            <img src={photoUrl} alt="Profile" className="h-20 w-20 rounded-2xl object-cover" />
          ) : (
            <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-primary/10">
              <User className="h-10 w-10 text-primary" />
            </div>
          )}
          <div>
            <label className="mb-1 block text-sm font-medium">Profile Photo</label>
            <input
              type="file"
              accept="image/*"
              className="input-field max-w-sm"
              onChange={(e) => setPhoto(e.target.files?.[0] || null)}
            />
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="mb-1.5 block text-sm font-medium">First Name</label>
            <input className="input-field" value={userFields.first_name} onChange={(e) => setUserFields({ ...userFields, first_name: e.target.value })} />
          </div>
          <div>
            <label className="mb-1.5 block text-sm font-medium">Last Name</label>
            <input className="input-field" value={userFields.last_name} onChange={(e) => setUserFields({ ...userFields, last_name: e.target.value })} />
          </div>
        </div>
        <div>
          <label className="mb-1.5 block text-sm font-medium">Email</label>
          <input className="input-field" type="email" value={userFields.email} onChange={(e) => setUserFields({ ...userFields, email: e.target.value })} />
        </div>

        {profileType === 'lawyer' ? (
          <>
            <div>
              <label className="mb-1.5 block text-sm font-medium">Specialty</label>
              <select className="input-field" value={lawyerProfile.lawyer_type || ''} onChange={(e) => setLawyerProfile({ ...lawyerProfile, lawyer_type: e.target.value })}>
                {lawyerTypes.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
              </select>
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium">Years of Experience</label>
              <input type="number" className="input-field" value={lawyerProfile.experience_years || 0} onChange={(e) => setLawyerProfile({ ...lawyerProfile, experience_years: Number(e.target.value) })} />
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium">Phone</label>
              <input className="input-field" value={lawyerProfile.phone_number || ''} onChange={(e) => setLawyerProfile({ ...lawyerProfile, phone_number: e.target.value })} />
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium">Address</label>
              <textarea className="input-field" value={lawyerProfile.address || ''} onChange={(e) => setLawyerProfile({ ...lawyerProfile, address: e.target.value })} />
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium">Bio</label>
              <textarea className="input-field min-h-[100px]" value={lawyerProfile.bio || ''} onChange={(e) => setLawyerProfile({ ...lawyerProfile, bio: e.target.value })} />
            </div>
          </>
        ) : (
          <>
            <div>
              <label className="mb-1.5 block text-sm font-medium">Phone</label>
              <input className="input-field" value={userProfile.phone_number || ''} onChange={(e) => setUserProfile({ ...userProfile, phone_number: e.target.value })} />
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium">Address</label>
              <textarea className="input-field" value={userProfile.address || ''} onChange={(e) => setUserProfile({ ...userProfile, address: e.target.value })} />
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium">Date of Birth</label>
              <input type="date" className="input-field" value={userProfile.date_of_birth || ''} onChange={(e) => setUserProfile({ ...userProfile, date_of_birth: e.target.value })} />
            </div>
          </>
        )}

        <button type="submit" disabled={saving} className="btn-primary">
          <Save className="h-4 w-4" /> {saving ? 'Saving...' : 'Save Changes'}
        </button>
      </form>
    </div>
  );
}
