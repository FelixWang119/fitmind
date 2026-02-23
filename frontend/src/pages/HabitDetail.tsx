import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  Award, 
  Target, 
  Calendar,
  Clock,
  TrendingUp,
  Plus,
  X,
  Check
} from 'lucide-react';
import { api } from '../api/client';
import toast from 'react-hot-toast';

// Types
interface DailyStats {
  date: string;
  completed: boolean;
  actual_value: number | null;
}

interface HabitDetailedStats {
  habit_id: number;
  habit_name: string;
  total_checkins: number;
  current_streak: number;
  best_streak: number;
  completion_rate: number;
  last_30_days_trend: DailyStats[];
  checkin_time_distribution: Record<string, number>;
  weekly_pattern: Record<string, number>;
  monthly_pattern: Record<string, number>;
}

interface HabitGoal {
  id: number;
  habit_id: number;
  goal_type: string;
  target_value: number;
  period: string;
  start_date: string;
  end_date: string;
  is_active: boolean;
  is_achieved: boolean;
  current_progress: number;
}

const TIME_LABELS: Record<string, string> = {
  morning: '早晨 (6-10点)',
  midday: '上午 (10-14点)',
  afternoon: '下午 (14-18点)',
  evening: '晚间 (18-22点)',
  night: '深夜 (22-6点)',
};

const DAY_LABELS: Record<string, string> = {
  Monday: '周一',
  Tuesday: '周二',
  Wednesday: '周三',
  Thursday: '周四',
  Friday: '周五',
  Saturday: '周六',
  Sunday: '周日',
};

const GOAL_TYPES = [
  { value: 'completion_rate', label: '完成率目标' },
  { value: 'streak', label: '连续天数目标' },
  { value: 'total_count', label: '总次数目标' },
];

const PERIODS = [
  { value: 'weekly', label: '每周' },
  { value: 'monthly', label: '每月' },
];

export default function HabitDetail() {
  const { habitId } = useParams<{ habitId: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<HabitDetailedStats | null>(null);
  const [goals, setGoals] = useState<HabitGoal[]>([]);
  const [showGoalModal, setShowGoalModal] = useState(false);
  
  // Form state
  const [goalForm, setGoalForm] = useState({
    goal_type: 'completion_rate',
    target_value: '80',
    period: 'weekly',
  });

  useEffect(() => {
    if (habitId) {
      loadData(parseInt(habitId));
    }
  }, [habitId]);

  const loadData = async (id: number) => {
    try {
      setLoading(true);
      const [statsData, goalsData] = await Promise.all([
        api.getHabitDetailedStats(id),
        api.getHabitGoals(id),
      ]);
      setStats(statsData);
      setGoals(goalsData);
    } catch (error) {
      console.error('Failed to load habit details:', error);
      toast.error('加载习惯详情失败');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateGoal = async () => {
    if (!habitId) return;
    
    try {
      const today = new Date();
      const endDate = goalForm.period === 'weekly' 
        ? new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000)
        : new Date(today.getTime() + 30 * 24 * 60 * 60 * 1000);

      await api.createHabitGoal({
        habit_id: parseInt(habitId),
        goal_type: goalForm.goal_type,
        target_value: parseInt(goalForm.target_value),
        period: goalForm.period,
        start_date: today.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0],
      });
      
      toast.success('目标创建成功！');
      setShowGoalModal(false);
      loadData(parseInt(habitId));
    } catch (error) {
      console.error('Failed to create goal:', error);
      toast.error('创建目标失败');
    }
  };

  const handleDeleteGoal = async (goalId: number) => {
    try {
      await api.deleteHabitGoal(goalId);
      toast.success('目标已删除');
      if (habitId) {
        loadData(parseInt(habitId));
      }
    } catch (error) {
      console.error('Failed to delete goal:', error);
      toast.error('删除目标失败');
    }
  };

  const getCompletionColor = (rate: number) => {
    if (rate >= 80) return 'text-green-600 bg-green-50';
    if (rate >= 50) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">习惯不存在</p>
        <button
          onClick={() => navigate('/habits')}
          className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-xl"
        >
          返回习惯列表
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/habits')}
            className="p-2 hover:bg-gray-100 rounded-xl transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-gray-600" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{stats.habit_name}</h1>
            <p className="text-gray-600 mt-1">习惯详细分析</p>
          </div>
        </div>
        <button
          onClick={() => setShowGoalModal(true)}
          className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-xl hover:bg-blue-700 transition-colors"
        >
          <Target className="w-5 h-5" />
          <span>设置目标</span>
        </button>
      </div>

      {/* Main Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Check-ins */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-blue-50 rounded-xl">
              <Calendar className="w-5 h-5 text-blue-600" />
            </div>
          </div>
          <p className="text-3xl font-bold text-gray-900">{stats.total_checkins}</p>
          <p className="text-sm text-gray-500 mt-1">总打卡次数</p>
        </div>

        {/* Current Streak */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-orange-50 rounded-xl">
              <Award className="w-5 h-5 text-orange-600" />
            </div>
          </div>
          <p className="text-3xl font-bold text-gray-900">{stats.current_streak}</p>
          <p className="text-sm text-gray-500 mt-1">当前连续天数</p>
          <p className="text-xs text-gray-400 mt-1">历史最长: {stats.best_streak} 天</p>
        </div>

        {/* Completion Rate */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-green-50 rounded-xl">
              <TrendingUp className="w-5 h-5 text-green-600" />
            </div>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getCompletionColor(stats.completion_rate)}`}>
              {stats.completion_rate >= 80 ? '优秀' : stats.completion_rate >= 50 ? '良好' : '需努力'}
            </span>
          </div>
          <p className="text-3xl font-bold text-gray-900">{stats.completion_rate}%</p>
          <p className="text-sm text-gray-500 mt-1">完成率</p>
        </div>

        {/* Best Time */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-purple-50 rounded-xl">
              <Clock className="w-5 h-5 text-purple-600" />
            </div>
          </div>
          <p className="text-xl font-bold text-gray-900">
            {stats.checkin_time_distribution && Object.keys(stats.checkin_time_distribution).length > 0
              ? TIME_LABELS[Object.entries(stats.checkin_time_distribution).sort((a, b) => b[1] - a[1])[0][0]] || '暂无数据'
              : '暂无数据'}
          </p>
          <p className="text-sm text-gray-500 mt-1">最活跃时间段</p>
        </div>
      </div>

      {/* 30 Days Trend */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">30天完成趋势</h2>
        <div className="flex flex-wrap gap-1">
          {stats.last_30_days_trend.map((day, index) => (
            <div
              key={index}
              className={`w-8 h-8 rounded flex items-center justify-center text-xs font-medium ${
                day.completed 
                  ? 'bg-green-500 text-white' 
                  : 'bg-gray-100 text-gray-500'
              }`}
              title={`${day.date}: ${day.completed ? '已打卡' : '未打卡'}`}
            >
              {day.date.slice(-2)}
            </div>
          ))}
        </div>
        <div className="flex items-center space-x-4 mt-4 text-sm text-gray-500">
          <div className="flex items-center">
            <div className="w-4 h-4 bg-green-500 rounded mr-2"></div>
            <span>已打卡</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-gray-100 rounded mr-2"></div>
            <span>未打卡</span>
          </div>
        </div>
      </div>

      {/* Time Distribution & Weekly Pattern */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Time Distribution */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">打卡时间分布</h2>
          <div className="space-y-3">
            {Object.entries(stats.checkin_time_distribution || {}).length > 0 ? (
              Object.entries(stats.checkin_time_distribution).map(([time, count]) => (
                <div key={time} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">{TIME_LABELS[time] || time}</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-32 bg-gray-100 rounded-full h-2">
                      <div
                        className="bg-blue-500 rounded-full h-2"
                        style={{ 
                          width: `${(count / Math.max(...Object.values(stats.checkin_time_distribution))) * 100}%` 
                        }}
                      />
                    </div>
                    <span className="text-sm font-medium text-gray-900 w-8">{count}次</span>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-sm">暂无打卡数据</p>
            )}
          </div>
        </div>

        {/* Weekly Pattern */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">每周完成模式</h2>
          <div className="space-y-3">
            {Object.entries(stats.weekly_pattern || {}).length > 0 ? (
              Object.entries(stats.weekly_pattern).map(([day, rate]) => (
                <div key={day} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">{DAY_LABELS[day] || day}</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-32 bg-gray-100 rounded-full h-2">
                      <div
                        className={`rounded-full h-2 ${
                          rate >= 80 ? 'bg-green-500' : rate >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${Math.min(rate, 100)}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium text-gray-900 w-12">{rate}%</span>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-sm">暂无数据，数据积累中...</p>
            )}
          </div>
        </div>
      </div>

      {/* Goals */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">目标追踪</h2>
        {goals.length > 0 ? (
          <div className="space-y-4">
            {goals.map((goal) => (
              <div
                key={goal.id}
                className="p-4 bg-gray-50 rounded-xl"
              >
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <p className="font-medium text-gray-900">
                      {GOAL_TYPES.find(g => g.value === goal.goal_type)?.label || goal.goal_type}
                    </p>
                    <p className="text-sm text-gray-500">
                      {goal.period === 'weekly' ? '每周' : '每月'} {goal.target_value}
                      {goal.goal_type === 'completion_rate' ? '%' : '天'}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleDeleteGoal(goal.id)}
                      className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                <div className="mt-2">
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">进度</span>
                    <span className="font-medium text-gray-900">
                      {goal.current_progress} / {goal.target_value}
                      {goal.goal_type === 'completion_rate' ? '%' : ''}
                    </span>
                  </div>
                  <div className="bg-gray-200 rounded-full h-2">
                    <div
                      className={`rounded-full h-2 ${
                        goal.is_achieved ? 'bg-green-500' : 'bg-blue-500'
                      }`}
                      style={{ 
                        width: `${Math.min((goal.current_progress / goal.target_value) * 100, 100)}%` 
                      }}
                    />
                  </div>
                </div>
                {goal.is_achieved && (
                  <div className="mt-2 flex items-center text-green-600 text-sm">
                    <Award className="w-4 h-4 mr-1" />
                    目标已达成！
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <Target className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500">还没有设置目标</p>
            <button
              onClick={() => setShowGoalModal(true)}
              className="mt-3 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              设置目标
            </button>
          </div>
        )}
      </div>

      {/* Goal Modal */}
      {showGoalModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl w-full max-w-md">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-gray-900">设置目标</h2>
                <button onClick={() => setShowGoalModal(false)} className="text-gray-400 hover:text-gray-600">
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>
            
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">目标类型</label>
                <select
                  value={goalForm.goal_type}
                  onChange={(e) => setGoalForm({ ...goalForm, goal_type: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  {GOAL_TYPES.map((type) => (
                    <option key={type.value} value={type.value}>{type.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  目标值 {goalForm.goal_type === 'completion_rate' ? '(%)' : ''}
                </label>
                <input
                  type="number"
                  value={goalForm.target_value}
                  onChange={(e) => setGoalForm({ ...goalForm, target_value: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  min="1"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">周期</label>
                <select
                  value={goalForm.period}
                  onChange={(e) => setGoalForm({ ...goalForm, period: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  {PERIODS.map((period) => (
                    <option key={period.value} value={period.value}>{period.label}</option>
                  ))}
                </select>
              </div>

              <div className="flex space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowGoalModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  取消
                </button>
                <button
                  onClick={handleCreateGoal}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  创建目标
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
