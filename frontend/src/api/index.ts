import api from './client';
import type {
  User, Lawyer, LawyerRating, Appointment, CaseFile,
  ChatUser, ChatMessage, Notification, LawyerProfile, UserProfile,
  Category, AdminUser,
} from '../types';

export const authApi = {
  me: () => api.get<{ user: User | null }>('/auth/me/'),
  login: (username: string, password: string) =>
    api.post<{ user: User; message: string }>('/auth/login/', { username, password }),
  logout: () => api.post('/auth/logout/'),
  register: (data: FormData) =>
    api.post<{ message: string; user: User }>('/auth/register/', data),
};

export const homeApi = {
  getData: () => api.get<{ top_lawyers: Lawyer[] }>('/home/'),
  contact: (data: { name: string; email: string; subject: string; message: string }) =>
    api.post<{ message: string }>('/contact/', data),
};

export const lawyerApi = {
  list: (category?: string) =>
    api.get<{ lawyers: Lawyer[]; categories: Category[]; selected_category: string | null }>(
      '/lawyers/',
      { params: category ? { category } : {} },
    ),
  detail: (id: number) =>
    api.get<{ lawyer: Lawyer; ratings: LawyerRating[]; user_rating: LawyerRating | null }>(
      `/lawyers/${id}/`,
    ),
  bookAppointment: (id: number, data: FormData) =>
    api.post(`/lawyers/${id}/`, data),
  rate: (id: number, rating: number, comment: string) =>
    api.post(`/lawyers/${id}/`, { action: 'rate', rating, comment }),
};

export const profileApi = {
  get: () =>
    api.get<{ user: User; profile: LawyerProfile | UserProfile; profile_type: string }>('/profile/'),
  update: (data: FormData) => api.patch('/profile/', data),
};

export const appointmentApi = {
  list: () => api.get<{ appointments: Appointment[] }>('/appointments/'),
  detail: (id: number) =>
    api.get<{
      appointment: Appointment;
      case_files: CaseFile[];
      can_upload: boolean;
      can_manage: boolean;
    }>(`/appointments/${id}/`),
  accept: (id: number) => api.patch(`/appointments/${id}/`, { action: 'accept' }),
  reject: (id: number) => api.patch(`/appointments/${id}/`, { action: 'reject' }),
  uploadFiles: (id: number, files: FileList) => {
    const form = new FormData();
    Array.from(files).forEach((f) => form.append('case_files', f));
    return api.post(`/appointments/${id}/`, form);
  },
};

export const chatApi = {
  users: () => api.get<{ users: ChatUser[] }>('/chat/users/'),
  room: (userId: number) =>
    api.get<{ room_id: number; other_user: ChatUser }>(`/chat/room/${userId}/`),
  messages: (roomId: number, lastId = 0) =>
    api.get<{ messages: ChatMessage[] }>(`/chat/messages/${roomId}/`, { params: { last_id: lastId } }),
  send: (roomId: number, message: string, attachment?: File) => {
    const form = new FormData();
    form.append('message', message);
    if (attachment) form.append('attachment', attachment);
    return api.post(`/chat/send/${roomId}/`, form);
  },
  publicRoom: () => api.get<{ room_id: number }>('/public-chat/room/'),
  sendPublic: (message: string) => api.post('/public-chat/send/', { message }),
};

export const notificationApi = {
  list: () => api.get<{ notifications: Notification[]; unread_count: number }>('/notifications/'),
  markRead: (id: number) => api.post(`/notifications/${id}/read/`),
  markAllRead: () => api.post('/notifications/'),
};

export const adminApi = {
  dashboard: () => api.get<{ users: AdminUser[]; lawyers: AdminUser[] }>('/admin/dashboard/'),
  suspend: (id: number) => api.post(`/admin/suspend/${id}/`),
  unsuspend: (id: number) => api.post(`/admin/unsuspend/${id}/`),
  deleteUser: (id: number) => api.post(`/admin/delete/${id}/`),
};
