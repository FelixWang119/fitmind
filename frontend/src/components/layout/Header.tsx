import { Bell, Search, Home, LogOut } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';
import { Link } from 'react-router-dom';

export default function Header() {
  const { user, logout } = useAuthStore();

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-30">
      <div className="flex items-center justify-between px-4 lg:px-8 py-4">
        {/* Search */}
        <div className="flex items-center flex-1 max-w-xl">
          <div className="relative w-full max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="搜索功能、记录或建议..."
              className="w-full pl-10 pr-4 py-2 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all outline-none"
            />
          </div>
        </div>

        {/* Right section */}
        <div className="flex items-center space-x-4">
          {/* Points display */}
          <div className="hidden md:flex items-center bg-gradient-to-r from-yellow-400 to-orange-500 text-white px-4 py-2 rounded-full">
            <span className="text-sm font-semibold">积分: 1,250</span>
          </div>

          {/* Notifications */}
          <button className="relative p-2 rounded-xl hover:bg-gray-100 transition-colors">
            <Bell className="w-5 h-5 text-gray-600" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>

          {/* Home */}
          <Link
            to="/dashboard"
            className="p-2 rounded-xl hover:bg-gray-100 transition-colors"
            title="返回首页"
          >
            <Home className="w-5 h-5 text-gray-600" />
          </Link>

          {/* Logout */}
          <button
            onClick={logout}
            className="p-2 rounded-xl hover:bg-gray-100 transition-colors text-red-600"
            title="退出登录"
          >
            <LogOut className="w-5 h-5" />
          </button>
        </div>
      </div>
    </header>
  );
}