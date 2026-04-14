import { Fragment } from 'react';
import { Menu, Transition } from '@headlessui/react';
import {
  Bars3Icon,
  MagnifyingGlassIcon,
  PlusIcon,
  ViewColumnsIcon,
  ListBulletIcon,
} from '@heroicons/react/24/outline';
import clsx from 'clsx';
import { useAppStore } from '../stores/appStore';

export function Header() {
  const {
    viewMode,
    setViewMode,
    toggleSidebar,
    user,
    logout,
  } = useAppStore();

  return (
    <header className="h-14 bg-white border-b border-gray-200 flex items-center justify-between px-4">
      {/* Left side */}
      <div className="flex items-center gap-4">
        <button
          onClick={toggleSidebar}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <Bars3Icon className="w-5 h-5 text-gray-600" />
        </button>

        <div className="flex items-center gap-2">
          <span className="font-semibold text-lg text-gray-900">Issue Tracker</span>
        </div>
      </div>

      {/* Center - Search */}
      <div className="flex-1 max-w-xl mx-4">
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search issues..."
            className="w-full pl-10 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Right side */}
      <div className="flex items-center gap-3">
        {/* View mode toggle */}
        <div className="flex items-center bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setViewMode('list')}
            className={clsx(
              'p-1.5 rounded-md transition-colors',
              viewMode === 'list' ? 'bg-white shadow-sm' : 'hover:bg-gray-200'
            )}
          >
            <ListBulletIcon className="w-5 h-5 text-gray-600" />
          </button>
          <button
            onClick={() => setViewMode('board')}
            className={clsx(
              'p-1.5 rounded-md transition-colors',
              viewMode === 'board' ? 'bg-white shadow-sm' : 'hover:bg-gray-200'
            )}
          >
            <ViewColumnsIcon className="w-5 h-5 text-gray-600" />
          </button>
        </div>

        {/* Create Issue button */}
        <button className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors">
          <PlusIcon className="w-5 h-5" />
          <span>Create Issue</span>
        </button>

        {/* User menu */}
        <Menu as="div" className="relative">
          <Menu.Button className="flex items-center gap-2 p-2 hover:bg-gray-100 rounded-lg">
            <div className="w-8 h-8 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center font-medium">
              {user?.username?.charAt(0).toUpperCase() || 'U'}
            </div>
          </Menu.Button>
          <Transition
            as={Fragment}
            enter="transition ease-out duration-100"
            enterFrom="transform opacity-0 scale-95"
            enterTo="transform opacity-100 scale-100"
            leave="transition ease-in duration-75"
            leaveFrom="transform opacity-100 scale-100"
            leaveTo="transform opacity-0 scale-95"
          >
            <Menu.Items className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
              <div className="px-4 py-2 border-b border-gray-100">
                <p className="font-medium text-gray-900">{user?.username}</p>
                <p className="text-sm text-gray-500">{user?.email}</p>
              </div>
              <Menu.Item>
                {({ active }) => (
                  <button
                    onClick={logout}
                    className={clsx(
                      'w-full text-left px-4 py-2 text-sm',
                      active ? 'bg-gray-100' : ''
                    )}
                  >
                    Sign out
                  </button>
                )}
              </Menu.Item>
            </Menu.Items>
          </Transition>
        </Menu>
      </div>
    </header>
  );
}
