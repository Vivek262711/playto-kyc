import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

// Normalize error responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ---- Auth ----
export const authAPI = {
  login: (data) => api.post('/auth/login/', data),
  register: (data) => api.post('/auth/register/', data),
  me: () => api.get('/auth/me/'),
};

// ---- Merchant ----
export const merchantAPI = {
  listSubmissions: () => api.get('/merchant/submissions/'),
  createSubmission: (data) => api.post('/merchant/submissions/', data),
  getSubmission: (id) => api.get(`/merchant/submissions/${id}/`),
  updateSubmission: (id, data) => api.put(`/merchant/submissions/${id}/`, data),
  submitSubmission: (id) => api.post(`/merchant/submissions/${id}/submit/`),
  resubmitSubmission: (id) => api.post(`/merchant/submissions/${id}/resubmit/`),
  uploadDocument: (id, formData) =>
    api.post(`/merchant/submissions/${id}/documents/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  listDocuments: (id) => api.get(`/merchant/submissions/${id}/documents/`),
  getNotifications: () => api.get('/notifications/'),
};

// ---- Reviewer ----
export const reviewerAPI = {
  getQueue: () => api.get('/reviewer/queue/'),
  getSubmission: (id) => api.get(`/reviewer/submissions/${id}/`),
  pickSubmission: (id) => api.post(`/reviewer/submissions/${id}/pick/`),
  approveSubmission: (id) => api.post(`/reviewer/submissions/${id}/approve/`),
  rejectSubmission: (id, data) => api.post(`/reviewer/submissions/${id}/reject/`, data),
  requestInfo: (id, data) => api.post(`/reviewer/submissions/${id}/request-info/`, data),
};

export default api;
