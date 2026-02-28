import { NavLink } from 'react-router-dom';
import { useState, useEffect } from 'react';
import {
  LayoutDashboard,
  User,
  Target,
  Utensils,
  Trophy,
  MessageCircle,
  ChevronLeft,
  ChevronRight,
  Activity,
  BarChart3,
  ClipboardCheck,
} from 'lucide-react';

const navigation = [
  { name: '仪表板', href: '/dashboard', icon: LayoutDashboard },
  { name: '饮食记录', href: '/diet-tracking', icon: Utensils },
  { name: '运动打卡', href: '/exercise-checkin', icon: Activity },
  { name: 'AI 助手', href: '/chat', icon: MessageCircle },
  { name: '习惯追踪', href: '/habits', icon: Target },
  { name: '习惯分析', href: '/habits-stats', icon: BarChart3 },
  { name: '健康记录', href: '/health', icon: Activity },
  { name: '健康评估', href: '/health/assessment', icon: ClipboardCheck },
  { name: '成就中心', href: '/gamification', icon: Trophy },
  { name: '个人资料', href: '/profile', icon: User },
];

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(() => {
    // 从 localStorage 获取初始状态，这样用户重新访问时保持之前的展开/收起状态
    const saved = localStorage.getItem('sidebar-collapsed');
    return saved === 'true' || false;
  });

  // 当状态变化时，保存到 localStorage
  useEffect(() => {
    localStorage.setItem('sidebar-collapsed', collapsed.toString());
  }, [collapsed]);

  // 使用 document.documentElement 来更新一个 CSS 变量，这样主内容区可以响应
  useEffect(() => {
    document.documentElement.style.setProperty('--sidebar-width', collapsed ? '80px' : '256px');
  }, [collapsed]);

  return (
    <>
      {/* Mobile overlay */}
      <div className="lg:hidden">
        {/* Mobile sidebar would go here */}
      </div>

      {/* Desktop sidebar */}
      <aside
        className={`hidden lg:flex flex-col fixed left-0 top-0 h-full bg-white border-r border-gray-200 transition-all duration-300 z-40 ${
          collapsed ? 'w-20' : 'w-64'
        }`}
      >
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className={`flex items-center ${collapsed ? 'justify-center' : ''}`}>
            <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center">
              <span className="text-white text-xl font-bold">AI</span>
            </div>
            {!collapsed && (
              <span className="ml-3 text-lg font-semibold text-gray-900">体重管家</span>
            )}
          </div>
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="p-1 rounded-lg hover:bg-gray-100 transition-colors"
          >
            {collapsed ? (
              <ChevronRight className="w-5 h-5 text-gray-600" />
            ) : (
              <ChevronLeft className="w-5 h-5 text-gray-600" />
            )}
          </button>
        </div>

        <nav className="flex-1 py-6 px-3">
          <ul className="space-y-1">
            {navigation.map((item) => (
              <li key={item.name}>
                <NavLink
                  to={item.href}
                  className={({ isActive }) =>
                    `flex items-center px-3 py-3 rounded-xl transition-all duration-200 group ${
                      isActive
                        ? 'bg-blue-50 text-blue-600'
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }`
                  }
                >
                  <item.icon
                    className={`w-5 h-5 flex-shrink-0 ${
                      collapsed ? '' : 'mr-3'
                    }`}
                  />
                  {!collapsed && (
                    <span className="font-medium">{item.name}</span>
                  )}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        <div className="p-4 border-t border-gray-200">
          <div className={`flex items-center ${collapsed ? 'justify-center' : ''}`}>
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white font-semibold">
              U
            </div>
            {!collapsed && (
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900">用户</p>
                <p className="text-xs text-gray-500">Pro会员</p>
              </div>
            )}
          </div>
        </div>
      </aside>
    </>
  );
}