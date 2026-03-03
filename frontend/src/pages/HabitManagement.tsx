import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Edit2, Trash2, Pause, Play, TrendingUp, Trophy, AlertCircle, GlassWater, Scale, Moon, Sparkles, ChevronRight } from 'lucide-react';

// 习惯数据
interface Habit {
  id: number;
  name: string;
  icon: string;
  color: string;
  completed: boolean;
  streakDays: number;
  weeklyProgress: boolean[];
  status: 'completed' | 'pending' | 'missed';
}

// 习惯开通引导数据
const HABIT_INTRODUCTIONS = [
  {
    id: 'calorie-deficit',
    name: '每天保持热量赤字',
    icon: '🔥',
    color: 'bg-red-500',
    benefits: [
      '热量赤字是减重的第一性原理',
      '摄入 < 消耗 = 必然瘦',
      '自动计算，无需手动打卡',
    ],
  },
  {
    id: 'water',
    name: '每天 8 杯水',
    icon: '💧',
    color: 'bg-blue-500',
    benefits: [
      '提升代谢 5-10%，燃烧更多热量',
      '减少虚假饥饿感，避免过量进食',
      '帮助身体排出代谢废物',
    ],
  },
  {
    id: 'weight',
    name: '每天记录体重',
    icon: '⚖️',
    color: 'bg-purple-500',
    benefits: [
      '及时反馈，调整饮食和运动策略',
      '发现体重规律，找到最适合你的节奏',
      '长期坚持者平均多减重 2.3kg',
    ],
  },
  {
    id: 'sleep',
    name: '每日早睡（23 点前）',
    icon: '🌙',
    color: 'bg-indigo-500',
    benefits: [
      '降低皮质醇，减少腹部脂肪堆积',
      '睡眠 7-8 小时者减重效果提升 55%',
      '提升瘦素分泌，抑制食欲',
    ],
  },
  {
    id: 'meditation',
    name: '每日正念冥想',
    icon: '🧘',
    color: 'bg-pink-500',
    benefits: [
      '减少情绪化进食，提升饮食自控力',
      '餐前正念可减少 20% 过量进食',
      '降低压力激素，改善睡眠质量',
    ],
  },
];

export default function HabitManagement() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [showIntro, setShowIntro] = useState(false);
  const [enabledHabits, setEnabledHabits] = useState<string[]>([]);
  
  // 模拟习惯数据
  const [habits] = useState<Habit[]>([
    {
      id: 0,
      name: '每天保持热量赤字',
      icon: '🔥',
      color: 'bg-red-500',
      completed: true,
      streakDays: 3,
      weeklyProgress: [true, true, true, false, false, false, false],
      status: 'completed',
    },
    {
      id: 1,
      name: '每天 8 杯水',
      icon: '💧',
      color: 'bg-blue-500',
      completed: true,
      streakDays: 5,
      weeklyProgress: [true, true, true, true, true, false, false],
      status: 'completed',
    },
    {
      id: 2,
      name: '每天记录体重',
      icon: '⚖️',
      color: 'bg-purple-500',
      completed: false,
      streakDays: 3,
      weeklyProgress: [true, true, true, false, false, false, false],
      status: 'pending',
    },
    {
      id: 3,
      name: '每日早睡',
      icon: '🌙',
      color: 'bg-indigo-500',
      completed: true,
      streakDays: 7,
      weeklyProgress: [true, true, true, true, true, true, true],
      status: 'completed',
    },
    {
      id: 4,
      name: '每日冥想',
      icon: '🧘',
      color: 'bg-pink-500',
      completed: false,
      streakDays: 0,
      weeklyProgress: [false, false, true, false, false, false, false],
      status: 'missed',
    },
  ]);

  useEffect(() => {
    loadHabits();
  }, []);

  const loadHabits = async () => {
    try {
      setLoading(true);
      // TODO: 调用 API 获取习惯列表
      // const data = await habitApi.getList();
      // setEnabledHabits(data.map(h => h.id));
      setShowIntro(enabledHabits.length === 0);
    } catch (error) {
      console.error('加载习惯数据失败:', error);
      setShowIntro(true);
    } finally {
      setLoading(false);
    }
  };

  const handleEnableHabit = (habitId: string) => {
    setEnabledHabits([...enabledHabits, habitId]);
    if (enabledHabits.length + 1 === HABIT_INTRODUCTIONS.length) {
      setShowIntro(false);
    }
  };

  const handleEnableAll = () => {
    setEnabledHabits(HABIT_INTRODUCTIONS.map(h => h.id));
    setShowIntro(false);
  };

  const getStatusColor = (status: Habit['status']) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-50';
      case 'pending': return 'text-orange-600 bg-orange-50';
      case 'missed': return 'text-gray-600 bg-gray-50';
    }
  };

  const getStatusText = (status: Habit['status']) => {
    switch (status) {
      case 'completed': return '今日已完成';
      case 'pending': return '今日未完成';
      case 'missed': return '今日未打卡';
    }
  };

  const getBestHabit = () => {
    return habits.reduce((best, current) => 
      current.streakDays > best.streakDays ? current : best
    );
  };

  const getNeedImprovementHabit = () => {
    return habits.reduce((worst, current) => 
      current.streakDays < worst.streakDays ? current : worst
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // 显示开通引导
  if (showIntro) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-100 p-6">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-800 mb-2">
              🎯 开启你的习惯之旅
            </h1>
            <p className="text-gray-600">
              我们为你精选了 4 个科学验证的减重习惯<br/>
              选择你想开始的习惯，每天花 1 分钟打卡
            </p>
          </div>

          <div className="space-y-4 mb-8">
            {HABIT_INTRODUCTIONS.map((habit) => (
              <div
                key={habit.id}
                className="bg-white rounded-2xl shadow-lg p-6 hover:shadow-xl transition-shadow"
              >
                <div className="flex items-start gap-4 mb-4">
                  <div className={`${habit.color} p-4 rounded-xl text-3xl`}>
                    {habit.icon}
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-gray-800 mb-2">
                      {habit.name}
                    </h3>
                    <ul className="space-y-1">
                      {habit.benefits.map((benefit, index) => (
                        <li key={index} className="text-sm text-gray-600 flex items-start gap-2">
                          <span className="text-green-500 mt-1">✓</span>
                          <span>{benefit}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
                <button
                  onClick={() => handleEnableHabit(habit.id)}
                  disabled={enabledHabits.includes(habit.id)}
                  className={`w-full py-3 rounded-xl font-semibold transition-colors ${
                    enabledHabits.includes(habit.id)
                      ? 'bg-green-100 text-green-700 cursor-default'
                      : 'bg-blue-600 text-white hover:bg-blue-700'
                  }`}
                >
                  {enabledHabits.includes(habit.id) ? '✅ 已开启' : '开启这个习惯'}
                </button>
              </div>
            ))}
          </div>

          <div className="flex gap-4">
            <button
              onClick={handleEnableAll}
              className="flex-1 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-semibold hover:from-blue-700 hover:to-purple-700 transition-all"
            >
              全部开启
            </button>
            <button
              onClick={() => enabledHabits.length > 0 && setShowIntro(false)}
              className="flex-1 py-4 bg-gray-100 text-gray-700 rounded-xl font-semibold hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={enabledHabits.length === 0}
            >
              先开{enabledHabits.length}个试试
            </button>
          </div>
        </div>
      </div>
    );
  }

  const bestHabit = getBestHabit();
  const needImprovement = getNeedImprovementHabit();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 头部 */}
      <header className="bg-white shadow-sm">
        <div className="max-w-5xl mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-800">习惯管理</h1>
              <p className="text-sm text-gray-600 mt-1">追踪你的习惯养成进度</p>
            </div>
            <button
              onClick={() => setShowIntro(true)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors"
            >
              <Plus className="w-5 h-5" />
              <span>管理习惯</span>
            </button>
          </div>
        </div>
      </header>

      {/* 主内容区 */}
      <main className="max-w-5xl mx-auto px-4 py-6 space-y-6">
        
        {/* 习惯分析 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* 最佳习惯 */}
          <div className="bg-gradient-to-br from-yellow-50 to-orange-50 rounded-2xl shadow-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="bg-yellow-100 p-3 rounded-xl">
                <Trophy className="w-6 h-6 text-yellow-600" />
              </div>
              <h2 className="text-lg font-semibold text-gray-800">🏆 最佳习惯</h2>
            </div>
            <div className="text-center py-4">
              <p className="text-3xl mb-2">{bestHabit.icon}</p>
              <p className="text-xl font-bold text-gray-800">{bestHabit.name}</p>
              <p className="text-sm text-gray-600 mt-2">
                连续 {bestHabit.streakDays} 天
              </p>
            </div>
          </div>

          {/* 需要加油 */}
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl shadow-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="bg-blue-100 p-3 rounded-xl">
                <AlertCircle className="w-6 h-6 text-blue-600" />
              </div>
              <h2 className="text-lg font-semibold text-gray-800">💪 需要加油</h2>
            </div>
            <div className="text-center py-4">
              <p className="text-3xl mb-2">{needImprovement.icon}</p>
              <p className="text-xl font-bold text-gray-800">{needImprovement.name}</p>
              <p className="text-sm text-gray-600 mt-2">
                本周仅{needImprovement.weeklyProgress.filter(Boolean).length}次
              </p>
            </div>
          </div>
        </div>

        {/* 智能建议 */}
        <div className="bg-gradient-to-r from-purple-500 to-indigo-600 rounded-2xl shadow-lg p-6 text-white">
          <div className="flex items-start gap-3">
            <div className="bg-white/20 p-2 rounded-lg">
              <TrendingUp className="w-6 h-6" />
            </div>
            <div>
              <h3 className="font-semibold mb-1">💡 智能建议</h3>
              <p className="text-sm text-purple-100">
                可以把冥想放在早餐后，和喝水一起完成，更容易坚持哦～
              </p>
            </div>
          </div>
        </div>

        {/* 已开启的习惯列表 */}
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-6">已开启的习惯</h2>
          <div className="space-y-4">
            {habits.map((habit) => (
              <div
                key={habit.id}
                className={`border-2 rounded-xl p-4 transition-all ${
                  habit.completed
                    ? 'border-green-200 bg-green-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className={`${habit.color} p-3 rounded-xl text-2xl`}>
                      {habit.icon}
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-800">{habit.name}</h3>
                      <p className={`text-sm ${getStatusColor(habit.status)}`}>
                        {getStatusText(habit.status)}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-gray-800">
                      🔥 {habit.streakDays}天
                    </p>
                    <p className="text-xs text-gray-600">连续打卡</p>
                  </div>
                </div>

                {/* 周进度 */}
                <div className="flex justify-between mb-3">
                  {habit.weeklyProgress.map((completed, index) => (
                    <div
                      key={index}
                      className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium ${
                        completed
                          ? 'bg-green-500 text-white'
                          : 'bg-gray-200 text-gray-400'
                      }`}
                    >
                      {['一', '二', '三', '四', '五', '六', '日'][index]}
                    </div>
                  ))}
                </div>

                {/* 操作按钮 */}
                <div className="flex gap-2 pt-3 border-t border-gray-200">
                  <button
                    onClick={() => {
                      // TODO: 跳转到习惯详情页
                    }}
                    className="flex-1 flex items-center justify-center gap-2 py-2 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                  >
                    <TrendingUp className="w-4 h-4" />
                    查看记录
                  </button>
                  <button
                    onClick={() => {
                      // TODO: 编辑习惯设置
                    }}
                    className="flex-1 flex items-center justify-center gap-2 py-2 text-sm text-gray-600 hover:bg-gray-50 rounded-lg transition-colors"
                  >
                    <Edit2 className="w-4 h-4" />
                    提醒设置
                  </button>
                  <button
                    onClick={() => {
                      // TODO: 暂停习惯
                    }}
                    className="flex-1 flex items-center justify-center gap-2 py-2 text-sm text-orange-600 hover:bg-orange-50 rounded-lg transition-colors"
                  >
                    <Pause className="w-4 h-4" />
                    暂停
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 更多习惯 */}
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">更多习惯</h2>
          <button
            onClick={() => navigate('/habits-library')}
            className="w-full py-4 border-2 border-dashed border-gray-300 rounded-xl text-gray-600 hover:border-blue-500 hover:text-blue-600 transition-colors flex items-center justify-center gap-2"
          >
            <Plus className="w-5 h-5" />
            浏览习惯库（未来扩展）
          </button>
        </div>

      </main>
    </div>
  );
}
