import { ChevronRightIcon, FolderIcon, PlusIcon } from '@heroicons/react/24/outline';
import clsx from 'clsx';
import { useAppStore } from '../stores/appStore';
import type { ProjectTree } from '../types';

interface ProjectItemProps {
  project: ProjectTree;
  level: number;
}

function ProjectItem({ project, level }: ProjectItemProps) {
  const { selectedProjectPath, selectProject } = useAppStore();
  const isSelected = selectedProjectPath === project.path;

  return (
    <div>
      <button
        onClick={() => selectProject(project.path)}
        className={clsx(
          'w-full flex items-center gap-2 px-3 py-1.5 rounded-md text-sm transition-colors',
          isSelected
            ? 'bg-primary-50 text-primary-700'
            : 'text-gray-700 hover:bg-gray-100'
        )}
        style={{ paddingLeft: `${12 + level * 16}px` }}
      >
        <FolderIcon className="w-4 h-4 flex-shrink-0" />
        <span className="truncate">{project.name}</span>
        {project.children.length > 0 && (
          <ChevronRightIcon className="w-4 h-4 ml-auto flex-shrink-0" />
        )}
      </button>
      {project.children.map((child) => (
        <ProjectItem key={child.id} project={child} level={level + 1} />
      ))}
    </div>
  );
}

export function Sidebar() {
  const { sidebarOpen, projects, selectedProjectPath, selectProject } = useAppStore();

  // Build tree from flat projects list
  const buildTree = (): ProjectTree[] => {
    const map = new Map<string, ProjectTree>();
    const roots: ProjectTree[] = [];

    projects.forEach((p) => {
      map.set(p.path, { ...p, children: [] });
    });

    projects.forEach((p) => {
      const node = map.get(p.path)!;
      if (p.parent_path && map.has(p.parent_path)) {
        map.get(p.parent_path)!.children.push(node);
      } else {
        roots.push(node);
      }
    });

    return roots;
  };

  const projectTree = buildTree();

  if (!sidebarOpen) return null;

  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col h-full">
      {/* All Issues */}
      <div className="p-3 border-b border-gray-100">
        <button
          onClick={() => selectProject(null)}
          className={clsx(
            'w-full flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors',
            selectedProjectPath === null
              ? 'bg-gray-100 text-gray-900'
              : 'text-gray-600 hover:bg-gray-50'
          )}
        >
          All Issues
        </button>
      </div>

      {/* Projects */}
      <div className="flex-1 overflow-y-auto p-3">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
            Projects
          </h3>
          <button className="p-1 hover:bg-gray-100 rounded">
            <PlusIcon className="w-4 h-4 text-gray-500" />
          </button>
        </div>
        <div className="space-y-0.5">
          {projectTree.map((project) => (
            <ProjectItem key={project.id} project={project} level={0} />
          ))}
          {projectTree.length === 0 && (
            <p className="text-sm text-gray-500 px-3 py-2">No projects yet</p>
          )}
        </div>
      </div>
    </aside>
  );
}
