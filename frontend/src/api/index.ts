import axios from 'axios';

// Use environment variable for backend URL in production.
// Falls back to '/api' for local development, where vite.config.ts
// proxies /api → http://localhost:8000.
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

// Log the resolved base URL once at module load time so it is visible
// in the browser console and helps diagnose CORS / misconfiguration issues.
console.log(
  `[API] VITE_API_URL = ${import.meta.env.VITE_API_URL ?? '(not set)'} → using baseURL: ${API_BASE_URL}`
);

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add Supabase token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('supabase_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid, clear and redirect to login
      localStorage.removeItem('supabase_token');
      window.location.reload();
    }
    return Promise.reject(error);
  }
);

// ============ API Functions ============

// Auth APIs (using Supabase directly in components)
// But we still need to sync user with backend

export const authApi = {
  // Sync Supabase user to backend and get/create user record
  syncUser: async (supabaseToken: string) => {
    const { data } = await api.post('/auth/sync', {}, {
      headers: { Authorization: `Bearer ${supabaseToken}` }
    });
    return data;
  },
};

// Project APIs
export const projectApi = {
  list: async () => {
    const { data } = await api.get('/projects');
    return data;
  },

  getTree: async () => {
    const { data } = await api.get('/projects/tree');
    return data;
  },

  get: async (path: string) => {
    const { data } = await api.get(`/projects/${path}`);
    return data;
  },

  create: async (project: any) => {
    const { data } = await api.post('/projects', project);
    return data;
  },

  update: async (id: number, project: any) => {
    const { data } = await api.put(`/projects/${id}`, project);
    return data;
  },
};

// Issue APIs
export const issueApi = {
  list: async (params?: any) => {
    const { data } = await api.get('/issues', { params });
    return data;
  },

  get: async (issueKey: string) => {
    const { data } = await api.get(`/issues/${issueKey}`);
    return data;
  },

  create: async (issue: any) => {
    const { data } = await api.post('/issues', issue);
    return data;
  },

  update: async (issueKey: string, issue: any) => {
    const { data } = await api.put(`/issues/${issueKey}`, issue);
    return data;
  },

  changeStatus: async (issueKey: string, status: string) => {
    const { data } = await api.post(`/issues/${issueKey}/status`, { status });
    return data;
  },

  assign: async (issueKey: string, assigneeId: number) => {
    const { data } = await api.post(`/issues/${issueKey}/assign`, { assignee_id: assigneeId });
    return data;
  },

  getComments: async (issueKey: string) => {
    const { data } = await api.get(`/issues/${issueKey}/comments`);
    return data;
  },

  addComment: async (issueKey: string, body: string) => {
    const { data } = await api.post(`/issues/${issueKey}/comments`, { body });
    return data;
  },

  getEvents: async (issueKey: string) => {
    const { data } = await api.get(`/issues/${issueKey}/events`);
    return data;
  },
};

export default api;
