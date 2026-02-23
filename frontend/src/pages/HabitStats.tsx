import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  TrendingUp, 
  TrendingDown, 
  Target, 
  Award, 
  Calendar,
  BarChart3,
  Activity,
  Clock,
  ChevronRight
} from 'lucide-react';
import { api } from '../api/client';
import toast from 'react-hot-toast';

// Types
interface HabitStatsOverview {
  total_habits: number;
  active_habits: number;
  completion_rate: number;
  total_checkins: number;
  current_longest_streak: number;
  best_streak_ever: number;
  weekly_checkins: number;
  monthly_checkins: number;
  by_category: Record<string, number>;
}

interface CompletionRateStats {
  period: string;
  completion_rate: number;
  total_required: number;
  total_completed: number;
  trend: number[];
}

interface Habit {
  id: number;
  name: string;
  category: string;
  frequency: string;
  streak_days: number;
  total_completions: number;
}

const CATEGORY_COLORS: Record<string, string> = {
  diet: 'bg-green-500',
  exercise: 'bg-blue-500',
  sleep: 'bg-purple-500',
  mental_health: 'bg-pink-500',
  hydration: 'bg-cyan-500',
  other: 'bg-gray-500',
};

const CATEGORY_LABELS: Record<string, string> = {
  diet: '饮食',
  exercise: '运动',
  sleep: '睡眠',
  mental_health: '心理',
  hydration: '饮水',
  other: '其他',
};

const PERIODS = [
  { value: 'weekly', label: '本周' },
  { value: 'monthly', label: '本月' },
  { value: 'quarterly', label: '本季度' },
];

export default function HabitStats() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<HabitStatsOverview | null>(null);
  const [completionStats, setCompletionStats] = useState<CompletionRateStats | null>(null);
  const [habits, setHabits] = useState<Habit[]>([]);
  const [selectedPeriod, setSelectedPeriod] = useState('weekly');

  useEffect(() => {
    loadData();
  }, [selectedPeriod]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [statsData, completionData, habitsData] = await Promise.all([
        api.getHabitStatsOverview(selectedPeriod),
        api.getCompletionRateStats(selectedPeriod),
        api.getHabits(),
      ]);
      setStats(statsData);
      setCompletionStats(completionData);
      setHabits(habitsData);
    } catch (error) {
      console.error('Failed to load stats:', error);
      toast.error('加载统计数据失败');
    } finally {
      setLoading(false);
    }
  };

  const getCompletionColor = (rate: number) => {
    if (rate >= 80) return 'text-green-600 bg-green-50';
    if (rate >= 50) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const getCategoryRate = (category: string) => {
    if (!stats?.by_category) return 0;
    return stats.by_category[category] || 0;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">习惯分析</h1>
          <p className="text-gray-600 mt-1">追踪你的习惯养成进度</p>
        </div>
        
        {/* Period Selector */}
        <div className="flex bg-gray-100 rounded-xl p-1">
          {PERIODS.map((period) => (
            <button
              key={period.value}
              onClick={() => setSelectedPeriod(period.value)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedPeriod === period.value
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {period.label}
            </button>
          ))}
        </div>
      </div>

      {/* No Data State */}
      {(!stats || stats.total_habits === 0) && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-12 text-center">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <BarChart3 className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">暂无数据</h3>
          <p className="text-gray-500 mb-4">请先创建习惯开始打卡</p>
          <button
            onClick={() => navigate('/habits')}
            className="px-6 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors"
          >
            去创建习惯
          </button>
        </div>
      )}

      {stats && stats.total_habits > 0 && (
        <>
          {/* Main Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Completion Rate */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="p-2 bg-blue-50 rounded-xl">
                  <Target className="w-5 h-5 text-blue-600" />
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getCompletionColor(stats.completion_rate)}`}>
                  {stats.completion_rate >= 80 ? '优秀' : stats.completion_rate >= 50 ? '良好' : '需努力'}
                </span>
              </div>
              <p className="text-3xl font-bold text-gray-900">{stats.completion_rate}%</p>
              <p className="text-sm text-gray-500 mt-1">完成率</p>
              <div className="mt-4 bg-gray-100 rounded-full h-2">
                <div
                  className={`rounded-full h-2 transition-all ${
                    stats.completion_rate >= 80 ? 'bg-green-500' : stats.completion_rate >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${Math.min(stats.completion_rate, 100)}%` }}
                />
              </div>
            </div>

            {/* Total Check-ins */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="p-2 bg-green-50 rounded-xl">
                  <Activity className="w-5 h-5 text-green-600" />
                </div>
              </div>
              <p className="text-3xl font-bold text-gray-900">{stats.total_checkins}</p>
              <p className="text-sm text-gray-500 mt-1">总打卡次数</p>
              <p className="text-xs text-gray-400 mt-2">
                本周 {stats.weekly_checkins} 次 · 本月 {stats.monthly_checkins} 次
              </p>
            </div>

            {/* Current Streak */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="p-2 bg-orange-50 rounded-xl">
                  <Award className="w-5 h-5 text-orange-600" />
                </div>
              </div>
              <p className="text-3xl font-bold text-gray-900">{stats.current_longest_streak}</p>
              <p className="text-sm text-gray-500 mt-1">当前最长连续</p>
              <p className="text-xs text-gray-400 mt-2">
                历史最长: {stats.best_streak_ever} 天
              </p>
            </div>

            {/* Active Habits */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="p-2 bg-purple-50 rounded-xl">
                  <Calendar className="w-5 h-5 text-purple-600" />
                </div>
              </div>
              <p className="text-3xl font-bold text-gray-900">{stats.active_habits}</p>
              <p className="text-sm text-gray-500 mt-1">活跃习惯</p>
              <p className="text-xs text-gray-400 mt-2">
                共 {stats.total_habits} 个习惯
              </p>
            </div>
          </div>

          {/* Category Stats */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">分类完成率</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {Object.entries(CATEGORY_LABELS).map(([key, label]) => {
                const rate = getCategoryRate(key);
                return (
                  <div
                    key={key}
                    className="p-4 bg-gray-50 rounded-xl"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-gray-600">{label}</span>
                      <span className={`text-sm font-medium ${
                        rate >= 80 ? 'text-green-600' : rate >= 50 ? 'text-yellow-600' : 'text-red-600'
                      }`}>
                        {rate}%
                      </span>
                    </div>
                    <div className="bg-gray-200 rounded-full h-2">
                      <div
                        className={`rounded-full h-2 ${
                          rate >= 80 ? 'bg-green-500' : rate >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${Math.min(rate, 100)}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Completion Trend */}
          {completionStats && completionStats.trend.length > 0 && (
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">完成率趋势</h2>
              <div className="h-48 flex items-end justify-between gap-2">
                {completionStats.trend.map((value, index) => (
                  <div key={index} className="flex-1 flex flex-col items-center">
                    <div
                      className="w-full bg-blue-500 rounded-t transition-all hover:bg-blue-600"
                      style={{ height: `${Math.max(value, 5)}%` }}
                      title={`${value}%`}
                    />
                    <span className="text-xs text-gray-500 mt-2">
                      {index + 1}日
                    </span>
                  </div>
                ))}
              </div>
              <div className="flex justify-between mt-4 text-sm text-gray-500">
                <span>应完成: {completionStats.total_required} 次</span>
                <span>实际完成: {completionStats.total_completed} 次</span>
              </div>
            </div>
          )}

          {/* Habit List */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">习惯列表</h2>
              <button
                onClick={() => navigate('/habits')}
                className="text-blue-600 hover:text-blue-700 text-sm font-medium flex items-center"
              >
                查看全部 <ChevronRight className="w-4 h-4" />
              </button>
            </div>
            <div className="space-y-3">
              {habits.slice(0, 5).map((habit) => (
                <div
                  key={habit.id}
                  onClick={() => navigate(`/habits/${habit.id}/detail`)}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors cursor-pointer"
                >
                  <div className="flex items-center space-x-4">
                    <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center">
                      <span className="text-lg">
                        {CATEGORY_LABELS[habit.category]?.[0] || '📌'}
                      </span>
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{habit.name}</p>
                      <p className="text-sm text-gray-500">
                        {CATEGORY_LABELS[habit.category] || '其他'}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <p className="font-medium text-gray-900">{habit.total_completions} 次</p>
                      <p className="text-sm text-gray-500">总打卡</p>
                    </div>
                    <div className="flex items-center space-x-1 bg-orange-50 px-3 py-1 rounded-full">
                      <Award className="w-4 h-4 text-orange-500" />
                      <span className="text-sm font-medium text-orange-600">{habit.streak_days}天</span>
                    </div>
                    <ChevronRight className="w-5 h-5 text-gray-400" />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button
              onClick={() => navigate('/habits/patterns')}
              className="flex items-center justify-between p-6 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-2xl text-white hover:from-indigo-600 hover:to-purple-700 transition-colors"
            >
              <div>
                <h3 className="font-semibold text-lg">行为模式分析</h3>
                <p className="text-indigo-100 text-sm mt-1">了解你的习惯养成规律</p>
              </div>
              <BarChart3 className="w-8 h-8 text-white" />
            </button>
            
            <button
              onClick={() => navigate('/habits')}
              className="flex items-center justify-between p-6 bg-gradient-to-r from-blue-500 to-cyan-600 rounded-2xl text-white hover:from-blue-600 hover:to-cyan-700 transition-colors"
            >
              <div>
                <h3 className="font-semibold text-lg">设置目标</h3>
                <p className="text-blue-100 text-sm mt-1">为习惯设定目标并追踪</p>
              </div>
              <Target className="w-8 h-8 text-white" />
            </button>
          </div>
        </>
      )}
    </div>
  );
}
