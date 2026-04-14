import { format } from 'date-fns';
import clsx from 'clsx';
import type { Issue } from '../types';
import { useAppStore } from '../stores/appStore';

// Status badge colors
const statusColors: Record<string, string> = {
  new: 'bg-gray-100 text-gray-700',
  triaged: 'bg-blue-100 text-blue-700',
  assigned: 'bg-purple-100 text-purple-700',
  in_progress: 'bg-yellow-100 text-yellow-700',
  resolved: 'bg-green-100 text-green-700',
  reopened: 'bg-orange-100 text-orange-700',
  closed: 'bg-slate-100 text-slate-700',
  rejected: 'bg-red-100 text-red-700',
  duplicate: 'bg-pink-100 text-pink-700',
};

const priorityColors: Record<string, string> = {
  low: 'text-gray-400',
  medium: 'text-blue-500',
  high: 'text-orange-500',
  urgent: 'text-red-500',
};

const typeIcons: Record<string, string> = {
  bug: '🐛',
  task: '📋',
  request: '✨',
  question: '❓',
  incident: '🚨',
};

export function IssueList() {
  const { issues, selectIssue, viewMode, isLoading } = useAppStore();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (issues.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-gray-500">
        <p className="text-lg">No issues found</p>
        <p className="text-sm mt-1">Create a new issue to get started</p>
      </div>
    );
  }

  if (viewMode === 'board') {
    return <BoardView issues={issues} onSelect={selectIssue} />;
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <table className="w-full">
        <thead className="bg-gray-50 border-b border-gray-200">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
              Key
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
              Type
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
              Title
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
              Status
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
              Priority
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
              Assignee
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
              Updated
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {issues.map((issue) => (
            <tr
              key={issue.issue_key}
              onClick={() => selectIssue(issue.issue_key)}
              className="hover:bg-gray-50 cursor-pointer transition-colors"
            >
              <td className="px-4 py-3">
                <span className="text-sm font-mono text-primary-600">
                  {issue.issue_key}
                </span>
              </td>
              <td className="px-4 py-3">
                <span className="text-lg" title={issue.issue_type}>
                  {typeIcons[issue.issue_type] || '📋'}
                </span>
              </td>
              <td className="px-4 py-3">
                <span className="text-sm text-gray-900">{issue.title}</span>
              </td>
              <td className="px-4 py-3">
                <span
                  className={clsx(
                    'px-2 py-0.5 rounded-full text-xs font-medium',
                    statusColors[issue.status] || statusColors.new
                  )}
                >
                  {issue.status.replace('_', ' ')}
                </span>
              </td>
              <td className="px-4 py-3">
                <span className={clsx('text-sm', priorityColors[issue.priority])}>
                  {issue.priority === 'urgent' ? '🔴' : 
                   issue.priority === 'high' ? '🟠' : 
                   issue.priority === 'medium' ? '🔵' : '⚪'}
                </span>
              </td>
              <td className="px-4 py-3">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 bg-gray-200 rounded-full flex items-center justify-center text-xs text-gray-600">
                    {issue.assignee_name?.charAt(0).toUpperCase() || '-'}
                  </div>
                </div>
              </td>
              <td className="px-4 py-3">
                <span className="text-sm text-gray-500">
                  {format(new Date(issue.updated_at), 'MMM d, HH:mm')}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function BoardView({ issues, onSelect }: { issues: Issue[]; onSelect: (key: string) => void }) {
  const columns = ['new', 'triaged', 'assigned', 'in_progress', 'resolved', 'closed'] as const;
  const columnTitles: Record<string, string> = {
    new: 'New',
    triaged: 'Triaged',
    assigned: 'Assigned',
    in_progress: 'In Progress',
    resolved: 'Resolved',
    closed: 'Closed',
  };

  return (
    <div className="flex gap-4 overflow-x-auto pb-4">
      {columns.map((status) => {
        const columnIssues = issues.filter((i) => i.status === status);
        return (
          <div key={status} className="flex-shrink-0 w-72">
            <div className="bg-gray-100 rounded-lg p-3">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-medium text-gray-700">
                  {columnTitles[status]}
                </h3>
                <span className="text-xs bg-gray-200 text-gray-600 px-2 py-0.5 rounded-full">
                  {columnIssues.length}
                </span>
              </div>
              <div className="space-y-2">
                {columnIssues.map((issue) => (
                  <div
                    key={issue.issue_key}
                    onClick={() => onSelect(issue.issue_key)}
                    className="bg-white rounded-lg p-3 shadow-sm hover:shadow-md cursor-pointer transition-shadow"
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-sm">{typeIcons[issue.issue_type]}</span>
                      <span className="text-xs font-mono text-gray-500">
                        {issue.issue_key}
                      </span>
                    </div>
                    <p className="text-sm text-gray-900 line-clamp-2">{issue.title}</p>
                    <div className="flex items-center gap-2 mt-2">
                      <span className={clsx('text-sm', priorityColors[issue.priority])}>
                        {issue.priority}
                      </span>
                    </div>
                  </div>
                ))}
                {columnIssues.length === 0 && (
                  <p className="text-sm text-gray-400 text-center py-4">No issues</p>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
