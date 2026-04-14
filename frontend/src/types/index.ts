// Types for Issue Tracker

export type IssueStatus = 'new' | 'triaged' | 'assigned' | 'in_progress' | 'resolved' | 'reopened' | 'closed' | 'rejected' | 'duplicate';
export type IssueType = 'bug' | 'task' | 'request' | 'question' | 'incident';
export type IssuePriority = 'low' | 'medium' | 'high' | 'urgent';

export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  created_at: string;
}

export interface Project {
  id: number;
  name: string;
  path: string;
  parent_path: string | null;
  description: string | null;
  owner_id: number | null;
  default_assignee_id: number | null;
  default_priority: string;
  created_at: string;
  updated_at: string;
}

export interface ProjectTree {
  id: number;
  name: string;
  path: string;
  parent_path: string | null;
  description: string | null;
  children: ProjectTree[];
}

export interface Issue {
  id: number;
  issue_key: string;
  project_path: string;
  title: string;
  description: string | null;
  issue_type: IssueType;
  priority: IssuePriority;
  status: IssueStatus;
  creator_id: number;
  reporter_id: number | null;
  assignee_id: number | null;
  assigned_by_id: number | null;
  due_date: string | null;
  resolved_at: string | null;
  closed_at: string | null;
  source: string;
  visibility: string;
  tags: string[];
  reopen_count: number;
  created_at: string;
  updated_at: string;
  assignee_name?: string;
  creator_name?: string;
}

export interface IssueDetail extends Issue {
  issue_content: string | null;
  comments: Comment[];
  events: Event[];
  attachments: Attachment[];
  linked_issues: LinkedIssue[];
}

export interface Comment {
  comment_id: string;
  user_id: number;
  user_name: string;
  body: string;
  created_at: string;
}

export interface Event {
  event_id: string;
  event_type: string;
  user_id: number | null;
  user_name?: string;
  details: Record<string, any> | null;
  created_at: string;
}

export interface Attachment {
  attachment_id: string;
  filename: string;
  original_filename: string;
  mime_type: string;
  size: number;
  uploaded_by: number;
  uploaded_at: string;
  description: string | null;
  hash: string;
  storage_path: string;
}

export interface LinkedIssue {
  link_type: string;
  issue_key: string;
  title: string;
}

export interface CreateIssueRequest {
  title: string;
  project_path: string;
  description?: string;
  issue_type?: IssueType;
  priority?: IssuePriority;
  assignee_id?: number;
  due_date?: string;
  tags?: string[];
  visibility?: string;
}

export interface UpdateIssueRequest {
  title?: string;
  description?: string;
  issue_type?: IssueType;
  priority?: IssuePriority;
  status?: IssueStatus;
  assignee_id?: number;
  due_date?: string;
  tags?: string[];
  visibility?: string;
}

export interface CreateProjectRequest {
  name: string;
  path: string;
  parent_path?: string;
  description?: string;
  default_priority?: string;
}

export interface SearchParams {
  project_path?: string;
  status?: IssueStatus[];
  priority?: IssuePriority[];
  assignee_id?: number;
  creator_id?: number;
  issue_type?: IssueType[];
  tags?: string[];
  search?: string;
  limit?: number;
  offset?: number;
}
