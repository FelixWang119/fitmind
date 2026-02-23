import { useEffect, useState } from 'react';
import { Activity, Target, Flame, Droplets, TrendingDown, Calendar, ChevronRight, Heart, TrendingUp } from 'lucide-react';
import api from '@/api/client';

interface DashboardData {
  greeting?: string;
  quick_stats?: {
    today_calories?: number;
    daily_step_count?: number;
    sleep_hours?: number;
    water_intake_ml?: number;
  };
}

export default function DashboardSimple() {
  const [data, setData] = useState<DashboardData>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const dashboardData = await api.getDashboardOverview();
      const quickStatsData = await api.getQuickStats();
      
      setData({
        ...dashboardData,
        quickStats: quickStatsData,
      });
    } catch (err) {
      console.error('加载数据失败:', err);
      // 使用模拟数据
      setData({
        greeting: '欢迎回来，测试用户！',
        quick_stats: {
          today_calories: 1850,
          daily_step_count: 8542,
          sleep_hours: 7.2,
          water_intake_ml: 1800,
        },
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 头部 */}
      <header className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 shadow-md">
        <div className="max-w-7xl mx-auto">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold">{data.greeting || '欢迎回来！'}</h1>
              <p className="text-blue-100 mt-1">今日健康进度概览</p>
            </div>
            <div className="text-right">
              <p className="font-semibold">{new Date().toLocaleDateString('zh-CN', { weekday: 'long' })}</p>
              <p className="text-sm opacity-80">{new Date().toLocaleDateString('zh-CN')}</p>
            </div>
          </div>
        </div>
      </header>

      {/* 主内容区 */}
      <main className="max-w-7xl mx-auto p-6">
        {/* 快速统计 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow p-6">
            <div className="flex items-center mb-4">
              <div className="bg-green-100 p-3 rounded-full mr-4">
                <TrendingUp className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">今日热量</p>
                <p className="text-2xl font-bold text-gray-900">
                  {data.quick_stats?.today_calories || 0} 卡
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow p-6">
            <div className="flex items-center mb-4">
              <div className="bg-blue-100 p-3 rounded-full mr-4">
                <Activity className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">今日步数</p>
                <p className="text-2xl font-bold text-gray-900">
                  {data.quick_stats?.daily_step_count?.toLocaleString() || 0} 步
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow p-6">
            <div className="flex items-center mb-4">
              <div className="bg-purple-100 p-3 rounded-full mr-4">
                <Heart className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">睡眠时长</p>
                <p className="text-2xl font-bold text-gray-900">
                  {data.quick_stats?.sleep_hours || 0} 小时
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow p-6">
            <div className="flex items-center mb-4">
              <div className="bg-cyan-100 p-3 rounded-full mr-4">
                <Droplets className="h-6 w-6 text-cyan-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">水分摄入</p>
                <p className="text-2xl font-bold text-gray-900">
                  {data.quick_stats?.water_intake_ml || 0} ml
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* 快捷操作 */}
        <div className="bg-white rounded-xl shadow p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-800 mb-4">快捷操作</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <button className="flex flex-col items-center justify-center p-4 bg-blue-50 hover:bg-blue-100 text-blue-600 rounded-xl transition-colors">
              <Activity className="w-6 h-6 mb-2" />
              <span className="text-sm font-medium">记录体重</span>
            </button>
            <button className="flex flex-col items-center justify-center p-4 bg-green-50 hover:bg-green-100 text-green-600 rounded-xl transition-colors">
              <Calendar className="w-6 h-6 mb-2" />
              <span className="text-sm font-medium">完成习惯</span>
            </button>
            <button className="flex flex-col items-center justify-center p-4 bg-cyan-50 hover:bg-cyan-100 text-cyan-600 rounded-xl transition-colors">
              <Droplets className="w-6 h-6 mb-2" />
              <span className="text-sm font-medium">记录饮食</span>
            </button>
            <button className="flex flex-col items-center justify-center p-4 bg-orange-50 hover:bg-orange-100 text-orange-600 rounded-xl transition-colors">
              <Flame className="w-6 h-6 mb-2" />
              <span className="text-sm font-medium">情感签到</span>
            </button>
          </div>
        </div>

        {/* 导航到游戏化页面 */}
        <div className="bg-gradient-to-r from-green-500 to-emerald-600 rounded-xl shadow p-6 text-white">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-xl font-bold mb-2">体验全新游戏化功能</h2>
              <p className="opacity-90">解锁成就、赚取积分、挑战任务，让健康管理更有趣！</p>
            </div>
            <a 
              href="/gamification" 
              className="bg-white text-green-600 px-6 py-3 rounded-lg font-semibold hover:bg-green-50 transition-colors"
            >
              立即体验 →
            </a>
          </div>
        </div>
      </main>
    </div>
  );
}