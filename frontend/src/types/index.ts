export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  user_type: 'admin' | 'lawyer' | 'user';
  is_suspended: boolean;
  is_superuser: boolean;
  photo_url: string | null;
}

export interface Lawyer {
  id: number;
  username: string;
  full_name: string;
  lawyer_type: string | null;
  lawyer_type_display: string | null;
  bio: string;
  experience_years: number;
  phone_number?: string;
  address?: string;
  photo_url: string | null;
  avg_rating: number;
}

export interface LawyerRating {
  id: number;
  rating: number;
  comment: string;
  user_name: string;
  created_at: string;
}

export interface Appointment {
  id: number;
  user: number;
  lawyer: number;
  user_name: string;
  lawyer_name: string;
  appointment_date: string;
  appointment_time: string;
  message: string;
  status: 'pending' | 'accepted' | 'rejected';
  status_display: string;
  consultation_type: 'offline' | 'online';
  consultation_type_display: string;
  meeting_link: string | null;
  created_at: string;
  updated_at: string;
}

export interface CaseFile {
  id: number;
  file_url: string;
  file_type: string;
  description: string;
  uploaded_at: string;
}

export interface ChatUser {
  id: number;
  username: string;
  full_name: string;
  user_type: string;
  photo_url: string | null;
}

export interface ChatMessage {
  id: number;
  sender_name: string;
  message: string;
  created_at: string;
  attachment_url: string | null;
  attachment_type: string;
}

export interface Notification {
  id: number;
  type: string;
  type_display: string;
  message: string;
  is_read: boolean;
  created_at: string;
  related_id: number | null;
}

export interface LawyerProfile {
  lawyer_type: string;
  lawyer_type_display: string;
  bio: string;
  experience_years: number;
  phone_number: string;
  address: string;
  photo: string | null;
  photo_url: string | null;
}

export interface UserProfile {
  phone_number: string;
  address: string;
  date_of_birth: string | null;
  photo: string | null;
  photo_url: string | null;
}

export interface Category {
  value: string;
  label: string;
}

export interface AdminUser {
  id: number;
  username: string;
  email: string;
  full_name: string;
  user_type: string;
  is_suspended: boolean;
  date_joined: string;
}
