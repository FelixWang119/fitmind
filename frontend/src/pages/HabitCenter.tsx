import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Plus, Edit2, Pause, Play, TrendingUp, Trophy, AlertCircle, 
  Flame, ChevronRight, Target, Award, Activity, BarChart3, X, Calendar
} from 'lucide-react';
import habitApi, { Habit, HabitStats, HabitCompletion } from '@/services/habitService';

interface HabitWithCompletion extends Habit {
  completed: boolean;
  weeklyProgress: boolean[];
  icon: string;
  color: string;
  id: number | null;  // 允许 ID 为 null（演示模式）
}

const HABIT_ICONS: Record<string, { icon: string; color: string }> = {
  'hydration': { icon: '💧', color: 'bg-blue-500' },
  'diet': { icon: '🥗', color: 'bg-green-500' },
  'exercise': { icon: '🏃', color: 'bg-primary-500' },
  'sleep': { icon: '🌙', color: 'bg-indigo-500' },
  'mental_health': { icon: '🧘', color: 'bg-secondary-500' },
  'calorie-deficit': { icon: '🔥', color: 'bg-red-500' },
};

export default function HabitCenter() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [showIntro, setShowIntro] = useState(false);
  const [showManage, setShowManage] = useState(false);
  const [showRecords, setShowRecords] = useState(false);
  const [selectedHabitId, setSelectedHabitId] = useState<number | null>(null);
  
  const [stats, setStats] = useState<HabitStats | null>(null);
  const [habits, setHabits] = useState<HabitWithCompletion[]>([]);
  const [monthData, setMonthData] = useState<HabitCompletion[]>([]);

  useEffect(() => {
    loadData();
  }, []);

  // 习惯图标和颜色映射
  const getHabitStyle = (name: string, category: string) => {
    const iconMap: Record<string, string> = {
      '每天保持热量赤字': '🔥',
      '每天 8 杯水': '💧',
      '每天记录体重': '⚖️',
      '每日早睡': '🌙',
      '每日冥想': '🧘',
    };
    const colorMap: Record<string, string> = {
      'DIET': 'bg-red-500',
      'HYDRATION': 'bg-blue-500',
      'OTHER': 'bg-purple-500',
      'SLEEP': 'bg-indigo-500',
      'MENTAL_HEALTH': 'bg-secondary-500',
      'EXERCISE': 'bg-primary-500',
    };
    return {
      icon: iconMap[name] || '📌',
      color: colorMap[category] || 'bg-gray-500',
    };
  };

  const loadData = async () => {
    try {
      setLoading(true);
      const habitsData = await habitApi.getHabits();
      console.log('API返回的习惯:', habitsData);
      
      // 直接使用后端返回的数据，添加图标和颜色
      const habitsWithCompletion = habitsData.map((habit: any) => {
        const style = getHabitStyle(habit.name, habit.category);
        return {
          ...habit,
          icon: style.icon,
          color: style.color,
          completed: habit.total_completions > 0,
          weeklyProgress: Array(7).fill(false).map((_, i) => i < (habit.streak_days || 0) % 7),
        };
      });
      
      console.log('处理后的习惯:', habitsWithCompletion);
      setHabits(habitsWithCompletion);
      
      // 统计数据
      const activeCount = habitsWithCompletion.filter((h: any) => h.is_active).length;
      setStats({
        total_habits: habitsData.length,
        active_habits: activeCount,
        completion_rate: 75,
        total_completions: habitsData.reduce((sum: number, h: any) => sum + (h.total_completions || 0), 0),
        current_streak: Math.max(...habitsData.map((h: any) => h.streak_days || 0), 0),
        category_stats: {},
        weekly_completions: [3, 4, 2, 5, 3, 4, 2],
      });
      
      // 如果没有开启的习惯，显示引导页
      setShowIntro(activeCount === 0);
    } catch (error) {
      console.error('Failed to load habit data:', error);
      // 使用模拟数据回退
      setStats({
        total_habits: 5,
        active_habits: 0,
        completion_rate: 75,
        total_completions: 0,
        current_streak: 0,
        category_stats: {},
        weekly_completions: [3, 4, 2, 5, 3, 4, 2],
      });
      setShowIntro(true);
    } finally {
      setLoading(false);
    }
  };

  const toggleHabit = async (habitId: number) => {
    console.log('toggleHabit called, habitId:', habitId);
    if (!habitId) {
      console.error('Invalid habitId');
      return;
    }
    
    try {
      const habit = habits.find(h => h.id === habitId);
      if (!habit) {
        console.error('Habit not found');
        return;
      }
      
      console.log('当前习惯状态:', habit.is_active);
      
      // 先更新本地状态（保证用户体验）
      setHabits(prevHabits => prevHabits.map(h => 
        h.id === habitId ? { ...h, is_active: !h.is_active } : h
      ));
      
      // 调用 API 更新状态
      try {
        await habitApi.updateHabit(habitId, { is_active: !habit.is_active });
        console.log('API更新成功');
      } catch (apiError: any) {
        console.error('API Error:', apiError.response?.data);
        console.log('使用本地状态（演示模式）');
      }
    } catch (error) {
      console.error('Failed to toggle habit:', error);
    }
  };

  const pauseHabit = async (habitId: number | null) => {
    if (habitId === null) {
      // 对于 null ID，只更新本地状态
      setHabits(habits.map(h => 
        h.id === habitId ? { ...h, is_active: false } : h
      ));
      return;
    }
    try {
      await habitApi.updateHabit(habitId, { is_active: false });
      setHabits(habits.map(h => 
        h.id === habitId ? { ...h, is_active: false } : h
      ));
    } catch (error) {
      console.error('Failed to pause habit:', error);
    }
  };

  const loadMonthData = async (habitId: number | null) => {
    if (habitId === null) {
      // 对于 null ID，返回空数据
      setMonthData([]);
      return;
    }
    try {
      const completions = await habitApi.getCompletions(habitId);
      setMonthData(completions);
    } catch (error) {
      console.error('Failed to load month data:', error);
      setMonthData([]);
    }
  };

  const toggleRecords = async (habitId: number | null) => {
    setSelectedHabitId(habitId);
    await loadMonthData(habitId);
    setShowRecords(true);
  };

  const activeHabits = habits.filter(h => h.is_active);
  const pausedHabits = habits.filter(h => !h.is_active && h.total_completions > 0);
  const inactiveHabits = habits.filter(h => !h.is_active && h.total_completions === 0);

  const getBestHabit = () => {
    if (activeHabits.length === 0) return habits[0] || { icon: '📌', name: '暂无习惯', streak_days: 0 };
    return activeHabits.reduce((best, current) => 
      current.streak_days > best.streak_days ? current : best
    );
  };

  const getNeedImprovement = () => {
    if (activeHabits.length === 0) return habits[0] || { icon: '📌', name: '暂无习惯', streak_days: 0 };
    return activeHabits.reduce((worst, current) => 
      current.streak_days < worst.streak_days ? current : worst
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (showIntro) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 p-6">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-800 mb-2">🎯 开启你的习惯之旅</h1>
            <p className="text-gray-600">选择你想开始的习惯，每天花 1 分钟打卡</p>
          </div>
          <div className="space-y-4 mb-8">
            {habits.map((habit) => (
              <div key={habit.id} className="bg-white rounded-2xl shadow-lg p-6">
                <div className="flex items-start gap-4 mb-4">
                  <div className={`${habit.color} p-4 rounded-xl text-3xl`}>{habit.icon}</div>
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-gray-800 mb-2">{habit.name}</h3>
                    <ul className="space-y-1">
                      <li className="text-sm text-gray-600 flex items-start gap-2">
                        <span className="text-green-500 mt-1">✓</span>
                        <span>科学验证的减重习惯</span>
                      </li>
                      <li className="text-sm text-gray-600 flex items-start gap-2">
                        <span className="text-green-500 mt-1">✓</span>
                        <span>每天只需 1 分钟</span>
                      </li>
                    </ul>
                  </div>
                </div>
                <button
                  onClick={() => {
                    if (habit.id) {
                      toggleHabit(habit.id);
                      setShowIntro(false);
                    }
                  }}
                  className="w-full py-3 bg-primary-600 text-white rounded-xl font-semibold hover:bg-primary-700 transition-colors"
                >
                  开启这个习惯
                </button>
              </div>
            ))}
          </div>
          <button
            onClick={() => setShowIntro(false)}
            className="w-full py-4 bg-gray-100 text-gray-700 rounded-xl font-semibold hover:bg-gray-200 transition-colors"
          >
            稍后再说
          </button>
        </div>
      </div>
    );
  }

  const activeHabit = selectedHabitId !== null ? habits.find(h => h.id === selectedHabitId) : null;
  const completedDays = monthData.length;
  const completionRate = stats?.completion_rate ?? 75;
  const avgValue = monthData.length > 0 ? Math.round(monthData.reduce((sum, d) => sum + (d.actual_value || 0), 0) / monthData.length) : 0;

  const bestHabit = getBestHabit();
  const needImprovement = getNeedImprovement();

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-5xl mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-800">习惯管理中心</h1>
              <p className="text-sm text-gray-600">追踪习惯 + 统计分析</p>
            </div>
            <button
              onClick={() => setShowManage(true)}
              className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-xl hover:bg-primary-700 transition-colors"
            >
              <Plus className="w-5 h-5" />
              管理
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-6 space-y-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-xl shadow p-4">
            <div className="flex items-center gap-2 mb-2">
              <Target className="w-5 h-5 text-primary-600" />
              <span className="text-sm text-gray-600">完成率</span>
            </div>
            <p className="text-2xl font-bold text-gray-900">{stats?.completion_rate ?? 75}%</p>
            <div className="mt-2 bg-gray-100 rounded-full h-2">
              <div className="bg-primary-500 h-2 rounded-full transition-all" style={{ width: `${stats?.completion_rate ?? 75}%` }} />
            </div>
          </div>
          <div className="bg-white rounded-xl shadow p-4">
            <div className="flex items-center gap-2 mb-2">
              <Award className="w-5 h-5 text-yellow-600" />
              <span className="text-sm text-gray-600">总打卡</span>
            </div>
            <p className="text-2xl font-bold text-gray-900">{stats?.total_completions ?? 128}</p>
          </div>
          <div className="bg-white rounded-xl shadow p-4">
            <div className="flex items-center gap-2 mb-2">
              <Flame className="w-5 h-5 text-red-600" />
              <span className="text-sm text-gray-600">最佳连续</span>
            </div>
            <p className="text-2xl font-bold text-gray-900">{stats?.current_streak ?? 7}天</p>
          </div>
          <div className="bg-white rounded-xl shadow p-4">
            <div className="flex items-center gap-2 mb-2">
              <Activity className="w-5 h-5 text-green-600" />
              <span className="text-sm text-gray-600">本周</span>
            </div>
            <p className="text-2xl font-bold text-gray-900">{stats?.weekly_completions?.reduce((a, b) => a + b, 0) ?? 23}次</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-gradient-to-br from-yellow-50 to-orange-50 rounded-2xl shadow-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <Trophy className="w-6 h-6 text-yellow-600" />
              <h2 className="text-lg font-semibold">🏆 最佳习惯</h2>
            </div>
            <div className="text-center py-4">
              <p className="text-3xl mb-2">{bestHabit?.icon}</p>
              <p className="text-xl font-bold">{bestHabit?.name}</p>
              <p className="text-sm text-gray-600 mt-2">连续 {bestHabit?.streak_days}天</p>
            </div>
          </div>
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl shadow-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <AlertCircle className="w-6 h-6 text-blue-600" />
              <h2 className="text-lg font-semibold">💪 需要加油</h2>
            </div>
            <div className="text-center py-4">
              <p className="text-3xl mb-2">{needImprovement?.icon}</p>
              <p className="text-xl font-bold">{needImprovement?.name}</p>
              <p className="text-sm text-gray-600 mt-2">连续 {needImprovement?.streak_days}天</p>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-r from-primary-500 to-secondary-600 rounded-2xl shadow-lg p-6 text-white">
          <div className="flex items-start gap-3">
            <TrendingUp className="w-6 h-6" />
            <div>
              <h3 className="font-semibold mb-1">💡 智能建议</h3>
              <p className="text-sm text-primary-100">可以把冥想放在早餐后，和喝水一起完成，更容易坚持哦～</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-lg p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-lg font-semibold text-gray-800">我的习惯 ({activeHabits.length}个)</h2>
          </div>
          <div className="space-y-4">
            {activeHabits.map((habit) => (
              <div key={habit.id} className={`border-2 rounded-xl p-4 ${habit.completed ? 'border-green-200 bg-green-50' : 'border-gray-200'}`}>
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className={`${habit.color} p-3 rounded-xl text-2xl`}>{habit.icon}</div>
                    <div>
                      <h3 className="font-semibold">{habit.name}</h3>
                      <p className={`text-sm ${habit.completed ? 'text-green-600' : 'text-orange-600'}`}>
                        {habit.completed ? '今日已完成 ✓' : '今日未完成'}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold">🔥 {habit.streak_days}天</p>
                    <p className="text-xs text-gray-600">总计 {habit.total_completions}次</p>
                  </div>
                </div>
                <div className="flex justify-between mb-3">
                  {habit.weeklyProgress.map((completed, index) => (
                    <div key={index} className={`w-8 h-8 rounded-full flex items-center justify-center text-xs ${completed ? 'bg-green-500 text-white' : 'bg-gray-200 text-gray-400'}`}>
                      {['一','二','三','四','五','六','日'][index]}
                    </div>
                  ))}
                </div>
                <div className="flex gap-2 pt-3 border-t">
                  <button onClick={() => toggleRecords(habit.id)} className="flex-1 flex items-center justify-center gap-2 py-2 text-sm text-primary-600 hover:bg-primary-50 rounded-lg transition-colors">
                    <BarChart3 className="w-4 h-4" />
                    查看记录
                  </button>
                  <button className="flex-1 flex items-center justify-center gap-2 py-2 text-sm text-gray-600 hover:bg-gray-50 rounded-lg transition-colors">
                    <Edit2 className="w-4 h-4" />
                    提醒设置
                  </button>
                  <button onClick={() => pauseHabit(habit.id)} className="flex-1 flex items-center justify-center gap-2 py-2 text-sm text-orange-600 hover:bg-orange-50 rounded-lg transition-colors">
                    <Pause className="w-4 h-4" />
                    暂停
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {pausedHabits.length > 0 && (
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">💤 已暂停的习惯</h2>
            <div className="space-y-3">
              {pausedHabits.map((habit) => (
                <div key={habit.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="text-2xl grayscale opacity-50">{habit.icon}</div>
                    <div>
                      <p className="font-medium text-gray-600">{habit.name}</p>
                      <p className="text-xs text-gray-500">已暂停 • 总计{habit.total_completions}次</p>
                    </div>
                  </div>
                  <button onClick={() => toggleHabit(habit.id)} className="px-4 py-2 bg-green-100 text-green-700 rounded-lg font-semibold hover:bg-green-200 text-sm flex items-center gap-2">
                    <Play className="w-4 h-4" />
                    恢复
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {inactiveHabits.length > 0 && (
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">➕ 未开启的习惯</h2>
            <div className="space-y-3">
              {inactiveHabits.map((habit) => (
                <div key={habit.id} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="text-2xl">{habit.icon}</div>
                    <div>
                      <p className="font-medium">{habit.name}</p>
                      <p className="text-xs text-gray-500">点击开启开始追踪</p>
                    </div>
                  </div>
                  <button onClick={() => toggleHabit(habit.id)} className="px-4 py-2 bg-primary-100 text-primary-700 rounded-lg font-semibold hover:bg-primary-200 text-sm">
                    开启
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* 管理习惯弹窗 */}
      {showManage && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={() => setShowManage(false)}>
          <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="sticky top-0 bg-white border-b p-4 flex justify-between items-center">
              <h2 className="text-xl font-bold">管理习惯</h2>
              <button onClick={() => setShowManage(false)} className="p-2 hover:bg-gray-100 rounded-full">
                <X className="w-6 h-6" />
              </button>
            </div>
            <div className="p-6 space-y-6">
              {/* 已开启的习惯 */}
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-3">已开启的习惯 ({habits.filter(h => h.is_active).length})</h3>
                <div className="space-y-3">
                  {habits.filter(h => h.is_active).map((habit) => (
                    <div key={habit.id} className="flex items-center justify-between p-4 bg-green-50 border border-green-200 rounded-xl">
                      <div className="flex items-center gap-3">
                        <div className={`${habit.color} w-12 h-12 rounded-full flex items-center justify-center text-2xl`}>{habit.icon}</div>
                        <div>
                          <p className="font-semibold">{habit.name}</p>
                          <p className="text-sm text-green-700">✓ 已开启</p>
                        </div>
                      </div>
                      <button onClick={() => toggleHabit(habit.id)} className="px-4 py-2 bg-orange-100 text-orange-700 rounded-lg font-semibold hover:bg-orange-200 transition-colors">
                        暂停
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              {/* 已暂停的习惯 */}
              {habits.filter(h => !h.is_active && h.total_completions > 0).length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">已暂停的习惯 ({habits.filter(h => !h.is_active && h.total_completions > 0).length})</h3>
                  <div className="space-y-3">
                    {habits.filter(h => !h.is_active && h.total_completions > 0).map((habit) => (
                      <div key={habit.id} className="flex items-center justify-between p-4 bg-gray-50 border border-gray-200 rounded-xl">
                        <div className="flex items-center gap-3">
                          <div className="w-12 h-12 rounded-full flex items-center justify-center text-2xl grayscale opacity-50">{habit.icon}</div>
                          <div>
                            <p className="font-semibold">{habit.name}</p>
                            <p className="text-sm text-gray-500">已暂停 • 总计{habit.total_completions}次</p>
                          </div>
                        </div>
                        <button onClick={() => toggleHabit(habit.id)} className="px-4 py-2 bg-green-100 text-green-700 rounded-lg font-semibold hover:bg-green-200 transition-colors">
                          恢复
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* 未开启的习惯 */}
              {habits.filter(h => !h.is_active && h.total_completions === 0).length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">未开启的习惯 ({habits.filter(h => !h.is_active && h.total_completions === 0).length})</h3>
                  <div className="space-y-3">
                    {habits.filter(h => !h.is_active && h.total_completions === 0).map((habit) => (
                      <div key={habit.id} className="flex items-center justify-between p-4 bg-blue-50 border border-blue-200 rounded-xl">
                        <div className="flex items-center gap-3">
                          <div className={`${habit.color} w-12 h-12 rounded-full flex items-center justify-center text-2xl`}>{habit.icon}</div>
                          <div>
                            <p className="font-semibold">{habit.name}</p>
                            <p className="text-sm text-blue-700">点击开启开始追踪</p>
                          </div>
                        </div>
                        <button onClick={() => toggleHabit(habit.id)} className="px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors">
                          开启
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="bg-primary-50 rounded-xl p-4 mt-4">
                <p className="text-sm text-primary-800">💡 <strong>提示：</strong>关闭习惯不会删除历史数据，只是暂时停止追踪。</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 查看记录弹窗 */}
      {showRecords && activeHabit && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={() => setShowRecords(false)}>
          <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="sticky top-0 bg-white border-b p-4 flex justify-between items-center">
              <div className="flex items-center gap-3">
                <div className={`${activeHabit.color} w-10 h-10 rounded-full flex items-center justify-center text-xl`}>{activeHabit.icon}</div>
                <div>
                  <h2 className="text-xl font-bold">{activeHabit.name}</h2>
                  <p className="text-sm text-gray-600">月度记录</p>
                </div>
              </div>
              <button onClick={() => setShowRecords(false)} className="p-2 hover:bg-gray-100 rounded-full">
                <X className="w-6 h-6" />
              </button>
            </div>
            <div className="p-6 space-y-6">
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-primary-50 rounded-xl p-4 text-center">
                  <p className="text-2xl font-bold text-primary-600">{completionRate}%</p>
                  <p className="text-xs text-gray-600 mt-1">完成率</p>
                </div>
                <div className="bg-green-50 rounded-xl p-4 text-center">
                  <p className="text-2xl font-bold text-green-600">{completedDays}天</p>
                  <p className="text-xs text-gray-600 mt-1">已打卡</p>
                </div>
                <div className="bg-secondary-50 rounded-xl p-4 text-center">
                  <p className="text-2xl font-bold text-secondary-600">{avgValue}</p>
                  <p className="text-xs text-gray-600 mt-1">平均/天</p>
                </div>
              </div>

              <div>
                <div className="flex items-center gap-2 mb-4">
                  <Calendar className="w-5 h-5 text-primary-600" />
                  <h3 className="text-lg font-semibold">月度日历</h3>
                </div>
                <div className="grid grid-cols-7 gap-2 mb-2">
                  {['日','一','二','三','四','五','六'].map(day => (
                    <div key={day} className="text-center text-sm font-medium text-gray-600 py-2">{day}</div>
                  ))}
                </div>
                <div className="grid grid-cols-7 gap-2">
                  {/* 空白填充（3 月 1 日是周六）*/}
                  <div className="aspect-square"></div>
                  {Array.from({ length: 31 }).map((_, i) => {
                    const day = i + 1;
                    const dayStr = `2026-03-${String(day).padStart(2, "0")}`;
                    const completion = monthData.find(c => c.completion_date.startsWith(dayStr));
                    const isCompleted = !!completion;
                    
                    return (
                      <div
                        key={day}
                        className={`aspect-square rounded-xl flex flex-col items-center justify-center transition-all ${
                          isCompleted ? "bg-green-500 text-white" : "bg-gray-100 text-gray-400"
                        }`}
                      >
                        <span className="text-sm font-medium">{day}</span>
                        {isCompleted && completion.actual_value && (
                          <span className="text-xs opacity-80">{completion.actual_value}</span>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

              <div>
                <div className="flex items-center gap-2 mb-4">
                  <TrendingUp className="w-5 h-5 text-primary-600" />
                  <h3 className="text-lg font-semibold">最近记录</h3>
                </div>
                <div className="space-y-2">
                  {monthData.slice(0, 7).map((day, index) => (
                    <div key={index} className="flex items-center justify-between p-3 rounded-lg bg-green-50">
                      <div className="flex items-center gap-3">
                        <div className="w-2 h-2 rounded-full bg-green-500"></div>
                        <div>
                          <p className="font-medium text-gray-800">{day.completion_date}</p>
                          <p className="text-xs text-gray-500">已打卡</p>
                        </div>
                      </div>
                      {day.actual_value && (
                        <div className="text-right">
                          <p className="text-lg font-bold text-green-600">{day.actual_value}</p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
