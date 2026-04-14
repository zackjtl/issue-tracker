import { useState } from 'react';
import { format } from 'date-fns';
import ReactMarkdown from 'react-markdown';
import {
  XMarkIcon,
  PaperClipIcon,
  UserIcon,
  CalendarIcon,
} from '@heroicons/react/24/outline';
import clsx from 'clsx';
import { useAppStore } from '../stores/appStore';

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

export function IssueDetail() {
  const { selectedIssue, detailDrawerOpen, closeDetailDrawer } = useAppStore();
  const [activeTab, setActiveTab] = useState<'description' | 'activity' | 'attachments'>('description');

  if (!detailDrawerOpen || !selectedIssue) return null;

  return (
    <div className="fixed inset-y-0 right-0 w-[600px] bg-white shadow-xl z-40 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <span className="font-mono text-primary-600 font-medium">
            {selectedIssue.issue_key}
          </span>
          <span
            className={clsx(
              'px-2 py-0.5 rounded-full text-xs font-medium',
              statusColors[selectedIssue.status]
            )}
          >
            {selectedIssue.status.replace('_', ' ')}
          </span>
        </div>
        <button
          onClick={closeDetailDrawer}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <XMarkIcon className="w-5 h-5 text-gray-500" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        {/* Title */}
        <div className="p-4 border-b border-gray-100">
          <h2 className="text-xl font-semibold text-gray-900">{selectedIssue.title}</h2>
          <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
            <div className="flex items-center gap-1">
              <UserIcon className="w-4 h-4" />
              <span>{selectedIssue.creator_name || 'Unknown'}</span>
            </div>
            <div className="flex items-center gap-1">
              <CalendarIcon className="w-4 h-4" />
              <span>{format(new Date(selectedIssue.created_at), 'MMM d, yyyy HH:mm')}</span>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <div className="flex gap-4 px-4">
            {(['description', 'activity', 'attachments'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={clsx(
                  'py-3 px-1 text-sm font-medium border-b-2 transition-colors capitalize',
                  activeTab === tab
                    ? 'border-primary-600 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                )}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <div className="p-4">
          {activeTab === 'description' && (
            <div className="prose prose-sm max-w-none">
              {selectedIssue.issue_content ? (
                <ReactMarkdown>{selectedIssue.issue_content}</ReactMarkdown>
              ) : (
                <p className="text-gray-500 italic">No description provided.</p>
              )}
            </div>
          )}

          {activeTab === 'activity' && (
            <div className="space-y-4">
              {/* Events */}
              {selectedIssue.events.map((event) => (
                <div key={event.event_id} className="flex gap-3">
                  <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center text-sm">
                    {event.user_name?.charAt(0).toUpperCase() || 'S'}
                  </div>
                  <div className="flex-1">
                    <p className="text-sm text-gray-900">
                      <span className="font-medium">{event.user_name || 'System'}</span>
                      <span className="text-gray-500 ml-1">
                        {event.event_type.replace(/_/g, ' ')}
                      </span>
                    </p>
                    {event.details && (
                      <p className="text-xs text-gray-500 mt-0.5">
                        {JSON.stringify(event.details)}
                      </p>
                    )}
                    <p className="text-xs text-gray-400 mt-0.5">
                      {format(new Date(event.created_at), 'MMM d, HH:mm')}
                    </p>
                  </div>
                </div>
              ))}

              {/* Comments */}
              {selectedIssue.comments.map((comment) => (
                <div key={comment.comment_id} className="flex gap-3">
                  <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center text-sm text-primary-700">
                    {comment.user_name?.charAt(0).toUpperCase()}
                  </div>
                  <div className="flex-1 bg-gray-50 rounded-lg p-3">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium text-sm text-gray-900">
                        {comment.user_name}
                      </span>
                      <span className="text-xs text-gray-400">
                        {format(new Date(comment.created_at), 'MMM d, HH:mm')}
                      </span>
                    </div>
                    <p className="text-sm text-gray-700">{comment.body}</p>
                  </div>
                </div>
              ))}

              {selectedIssue.events.length === 0 && selectedIssue.comments.length === 0 && (
                <p className="text-sm text-gray-500 text-center py-4">No activity yet.</p>
              )}
            </div>
          )}

          {activeTab === 'attachments' && (
            <div className="space-y-2">
              {selectedIssue.attachments.map((attachment) => (
                <div
                  key={attachment.attachment_id}
                  className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg"
                >
                  <PaperClipIcon className="w-5 h-5 text-gray-400" />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">
                      {attachment.original_filename}
                    </p>
                    <p className="text-xs text-gray-500">
                      {(attachment.size / 1024).toFixed(1)} KB
                    </p>
                  </div>
                </div>
              ))}
              {selectedIssue.attachments.length === 0 && (
                <p className="text-sm text-gray-500 text-center py-4">No attachments.</p>
              )}
            </div>
          )}
        </div>

        {/* Metadata */}
        <div className="p-4 bg-gray-50 border-t border-gray-200">
          <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">
            Details
          </h4>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <span className="text-gray-500">Type:</span>
              <span className="ml-2 text-gray-900 capitalize">{selectedIssue.issue_type}</span>
            </div>
            <div>
              <span className="text-gray-500">Priority:</span>
              <span className={clsx('ml-2 capitalize', priorityColors[selectedIssue.priority])}>
                {selectedIssue.priority}
              </span>
            </div>
            <div>
              <span className="text-gray-500">Assignee:</span>
              <span className="ml-2 text-gray-900">
                {selectedIssue.assignee_name || 'Unassigned'}
              </span>
            </div>
            <div>
              <span className="text-gray-500">Project:</span>
              <span className="ml-2 text-gray-900">{selectedIssue.project_path}</span>
            </div>
            {selectedIssue.tags.length > 0 && (
              <div className="col-span-2">
                <span className="text-gray-500">Tags:</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {selectedIssue.tags.map((tag) => (
                    <span
                      key={tag}
                      className="px-2 py-0.5 bg-gray-200 text-gray-700 text-xs rounded"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
