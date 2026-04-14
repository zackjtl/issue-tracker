import { create } from 'zustand';
import type { User, Project, Issue, IssueDetail, SearchParams } from '../types';
import { projectApi, issueApi, authApi } from '../api';
import { supabase } from '../lib/supabase';

interface AppState {
  // User
  user: User | null;
  isAuthenticated: boolean;
  setUser: (user: User | null) => void;
  logout: () => Promise<void>;
  fetchUser: () => Promise<void>;

  // Projects
  projects: Project[];
  selectedProjectPath: string | null;
  fetchProjects: () => Promise<void>;
  selectProject: (path: string | null) => void;

  // Issues
  issues: Issue[];
  selectedIssue: IssueDetail | null;
  searchParams: SearchParams;
  fetchIssues: (params?: SearchParams) => Promise<void>;
  selectIssue: (key: string | null) => void;
  createIssue: (issue: any) => Promise<Issue>;
  updateIssue: (key: string, issue: any) => Promise<void>;

  // UI State
  viewMode: 'list' | 'board';
  sidebarOpen: boolean;
  detailDrawerOpen: boolean;
  setViewMode: (mode: 'list' | 'board') => void;
  toggleSidebar: () => void;
  openDetailDrawer: () => void;
  closeDetailDrawer: () => void;

  // Loading states
  isLoading: boolean;
  setLoading: (loading: boolean) => void;
}

export const useAppStore = create<AppState>((set, get) => ({
  // User state
  user: null,
  isAuthenticated: !!localStorage.getItem('supabase_token'),

  setUser: (user: User | null) => set({ user }),

  logout: async () => {
    await supabase.auth.signOut();
    localStorage.removeItem('supabase_token');
    set({ user: null, isAuthenticated: false });
  },

  fetchUser: async () => {
    const token = localStorage.getItem('supabase_token');
    if (token) {
      try {
        const user = await authApi.syncUser(token);
        set({ user, isAuthenticated: true });
      } catch {
        localStorage.removeItem('supabase_token');
        set({ user: null, isAuthenticated: false });
      }
    } else {
      set({ user: null, isAuthenticated: false });
    }
  },

  // Projects state
  projects: [],
  selectedProjectPath: null,

  fetchProjects: async () => {
    const projects = await projectApi.list();
    set({ projects });
  },

  selectProject: (path: string | null) => {
    set({ selectedProjectPath: path });
    get().fetchIssues({ project_path: path || undefined });
  },

  // Issues state
  issues: [],
  selectedIssue: null,
  searchParams: {},

  fetchIssues: async (params?: SearchParams) => {
    set({ isLoading: true });
    try {
      const issues = await issueApi.list(params);
      set({ issues, searchParams: params || {} });
    } finally {
      set({ isLoading: false });
    }
  },

  selectIssue: async (key: string | null) => {
    if (!key) {
      set({ selectedIssue: null, detailDrawerOpen: false });
      return;
    }
    set({ isLoading: true });
    try {
      const issue = await issueApi.get(key);
      set({ selectedIssue: issue, detailDrawerOpen: true });
    } finally {
      set({ isLoading: false });
    }
  },

  createIssue: async (issue) => {
    const newIssue = await issueApi.create(issue);
    set((state) => ({ issues: [newIssue, ...state.issues] }));
    return newIssue;
  },

  updateIssue: async (key: string, issue) => {
    const updated = await issueApi.update(key, issue);
    set((state) => ({
      issues: state.issues.map((i) => (i.issue_key === key ? updated : i)),
      selectedIssue: state.selectedIssue?.issue_key === key
        ? { ...state.selectedIssue, ...updated }
        : state.selectedIssue,
    }));
  },

  // UI State
  viewMode: 'list',
  sidebarOpen: true,
  detailDrawerOpen: false,

  setViewMode: (mode) => set({ viewMode: mode }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  openDetailDrawer: () => set({ detailDrawerOpen: true }),
  closeDetailDrawer: () => set({ detailDrawerOpen: false }),

  // Loading
  isLoading: false,
  setLoading: (loading) => set({ isLoading: loading }),
}));
