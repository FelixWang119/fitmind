import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Activity, Target, Flame, Droplets, TrendingDown, Calendar, ChevronRight, 
  Heart, TrendingUp, MessageCircle, Brain, HeartHandshake, Dumbbell, Timer, 
  CheckCircle, Moon, MoonStar, CloudRain, Coffee, GlassWater, Scale, Bed, Sparkles 
} from 'lucide-react';
import api from '@/api/client';
import { exerciseCheckInApi, ExerciseDailySummary } from '@/services/exerciseCheckIn';
import { numberWithCommas, roundToDecimal } from '../utils/numUtils';

interface NutritionData {
  calories_consumed: number;
  remaining_calories: number;
  meals_count: number;
  progress_percentage?: number;
}

interface HabitStatus {
  water: { completed: number; target: number };
  weight: { recorded: boolean; value?: number };
  sleep: { completed: boolean };
  meditation: { completed: boolean };
}

interface DashboardData {
  greeting?: string;
  userName?: string;
  currentWeight?: number;
  streakDays?: number;
  quick_stats?: {
    today_calories?: number;
    daily_step_count?: number;
    sleep_hours?: number;
    water_intake_ml?: number;
    intake_calories?: number;
    basal_metabolism?: number;
    exercise_calories_burned?: number;
  };
}

export default function DashboardV2() {
  const [data, setData] = useState<DashboardData>({});
  const [loading, setLoading] = useState(true);
  const [exerciseData, setExerciseData] = useState<ExerciseDailySummary | null>(null);
  const [nutritionData, setNutritionData] = useState<NutritionData | null>(null);
  const [habitStatus, setHabitStatus] = useState<HabitStatus>({
    water: { completed: 0, target: 8 },
    weight: { recorded: false },
    sleep: { completed: false },
    meditation: { completed: false }
  });
  const navigate = useNavigate();

  const handleQuickAction = (action: string) => {
    switch (action) {
      case 'water':
        navigate('/water-tracker');
        break;
      case 'weight':
        navigate('/weight-tracker');
        break;
      case 'sleep':
        navigate('/sleep-tracker');
        break;
      case 'meditation':
        navigate('/meditation-tracker');
        break;
      case 'exercise':
        navigate('/exercise-checkin');
        break;
      case 'diet':
        navigate('/diet-tracking');
        break;
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const dashboardData = await api.getDashboardOverview();
      const quickStatsData = await api.getQuickStats();
      
      // 加载运动数据
      let exerciseSummary = null;
      try {
        exerciseSummary = await exerciseCheckInApi.getDailySummary();
        if (exerciseSummary) {
          setExerciseData(exerciseSummary);
        }
      } catch (err) {
        console.error('加载运动数据失败:', err);
      }
      
      // 加载营养数据
      try {
        const dailyMeals = await api.getDailyMeals();
        const nutritionGoals = await api.getCalorieGoal();
        
        const targetCalories = nutritionGoals?.target_calories || 2000;
        const intakeCalories = dailyMeals?.total_calories || quickStatsData.intake_calories || 0;
        const caloriesRemaining = targetCalories - intakeCalories;
        
        setNutritionData({
          calories_consumed: intakeCalories,
          remaining_calories: Math.max(0, caloriesRemaining),
          meals_count: dailyMeals?.meals?.length || 0,
          progress_percentage: Math.min(100, Math.round((intakeCalories / targetCalories) * 100))
        });
      } catch (err) {
        console.log('加载营养数据失败，使用默认值:', err);
        const defaultTarget = 2000;
        const intakeCalories = quickStatsData.intake_calories || 0;
        setNutritionData({
          calories_consumed: intakeCalories,
          remaining_calories: defaultTarget - intakeCalories,
          meals_count: 0,
          progress_percentage: Math.min(100, Math.round((intakeCalories / defaultTarget) * 100))
        });
      }
      
      setData({
        ...dashboardData,
        quick_stats: quickStatsData,
      });
    } catch (err) {
      console.error('加载数据失败:', err);
      // 使用模拟数据
      setData({
        greeting: '欢迎回来，测试用户！',
        userName: '测试用户',
        currentWeight: 68.5,
        streakDays: 12,
        quick_stats: {
          today_calories: 1200,
          daily_step_count: 8542,
          sleep_hours: 7.2,
          water_intake_ml: 1800,
          intake_calories: 3500,
          basal_metabolism: 2000,
          exercise_calories_burned: 300
        },
      });
      setExerciseData({
        date: new Date().toISOString().split('T')[0],
        total_duration_minutes: 45,
        total_calories_burned: 320,
        sessions_count: 2,
        exercise_types: ['跑步', '游泳'],
        progress_percentage: 50
      });
      setNutritionData({
        calories_consumed: 1800,
        remaining_calories: 200,
        meals_count: 5,
        progress_percentage: 90
      });
    } finally {
      setLoading(false);
    }
  };

  // 获取问候语
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 6) return '晚安';
    if (hour < 12) return '早上好';
    if (hour < 18) return '下午好';
    return '晚上好';
  };

  // 获取习惯状态显示
  const getHabitStatusDisplay = (habit: keyof HabitStatus) => {
    const status = habitStatus[habit];
    if ('completed' in status && typeof status.completed === 'number') {
      return `${status.completed}/${status.target}`;
    }
    if ('recorded' in status) {
      return status.recorded ? '✅' : '⏳';
    }
    if ('completed' in status && typeof status.completed === 'boolean') {
      return status.completed ? '✅' : '❌';
    }
    return '';
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // 计算热量净变化
  const calorieNet = (data.quick_stats?.intake_calories || 0) - 
                     (data.quick_stats?.basal_metabolism || 2000) - 
                     (data.quick_stats?.exercise_calories_burned || 0);
  const isCalorieSurplus = calorieNet > 0;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 第 0 行：欢迎 Banner */}
      <header className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 shadow-md">
        <div className="max-w-7xl mx-auto">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold">
                👋 {getGreeting()}，{data.userName || '测试用户'}！新的一天，继续照顾好自己 💪
              </h1>
              <p className="text-blue-100 mt-1">
                {data.currentWeight ? `今日体重 ${data.currentWeight}kg` : ''} | 
                已坚持 {data.streakDays || 0} 天
              </p>
            </div>
            <div className="text-right">
              <p className="font-semibold">{new Date().toLocaleDateString('zh-CN', { weekday: 'long' })}</p>
              <p className="text-sm opacity-80">{new Date().toLocaleDateString('zh-CN')}</p>
            </div>
          </div>
        </div>
      </header>

      {/* 主内容区 */}
      <main className="max-w-7xl mx-auto p-6 space-y-6">
        
        {/* 第 1 行：热量净变化 Card */}
        <div className="bg-white rounded-xl shadow p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-blue-100 p-3 rounded-lg">
                <TrendingUp className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-gray-800">🔥 今日热量净变化</h2>
                <p className={`text-3xl font-bold ${isCalorieSurplus ? 'text-red-600' : 'text-green-600'}`}>
                  {calorieNet > 0 ? '+' : ''}{numberWithCommas(roundToDecimal(calorieNet))} 大卡
                  {isCalorieSurplus ? '（盈余）' : '（赤字）'}
                </p>
                <p className="text-sm text-gray-600 mt-1">
                  摄入 {numberWithCommas(data.quick_stats?.intake_calories || 0)} - 
                  消耗 {numberWithCommas((data.quick_stats?.basal_metabolism || 2000) + (data.quick_stats?.exercise_calories_burned || 0))} = 
                  {isCalorieSurplus ? '盈余' : '赤字'} {Math.abs(roundToDecimal(calorieNet))}
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-600">💡 建议</p>
              <p className="text-sm font-medium">
                {isCalorieSurplus ? '今晚散步 20 分钟 或 晚餐减少 100g 米饭' : '继续保持！热量控制得很好'}
              </p>
            </div>
          </div>
        </div>

        {/* 第 2 行：运动打卡 + 饮食打卡 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* 运动打卡 */}
          <div className="bg-white rounded-xl shadow p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-800">🏃 运动打卡</h3>
              <button 
                onClick={() => handleQuickAction('exercise')}
                className="text-blue-600 hover:text-blue-700 text-sm font-medium"
              >
                [+ 记录运动]
              </button>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">今日运动</span>
                <span className="font-medium">
                  {exerciseData?.total_duration_minutes || 0} 分钟
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">🔥 消耗</span>
                <span className="font-medium">
                  {exerciseData?.total_calories_burned || 0} 大卡
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">次数</span>
                <span className="font-medium">{exerciseData?.sessions_count || 0} 次</span>
              </div>
              {exerciseData?.exercise_types && exerciseData.exercise_types.length > 0 && (
                <div className="flex gap-2 mt-2">
                  {exerciseData.exercise_types.map((type, index) => (
                    <span key={index} className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                      {type}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* 饮食打卡 */}
          <div className="bg-white rounded-xl shadow p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-800">🍽️ 饮食打卡</h3>
              <button 
                onClick={() => handleQuickAction('diet')}
                className="text-blue-600 hover:text-blue-700 text-sm font-medium"
              >
                [+ 记录饮食]
              </button>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">今日摄入</span>
                <span className="font-medium">{nutritionData?.calories_consumed || 0} 大卡</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">剩余</span>
                <span className="font-medium text-green-600">{nutritionData?.remaining_calories || 0} 大卡</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">餐数</span>
                <span className="font-medium">{nutritionData?.meals_count || 0} 餐</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                <div 
                  className="bg-green-600 h-2 rounded-full transition-all"
                  style={{ width: `${nutritionData?.progress_percentage || 0}%` }}
                />
              </div>
              <p className="text-xs text-gray-600 text-right">
                进度 {nutritionData?.progress_percentage || 0}%
              </p>
            </div>
          </div>
        </div>

        {/* 第 3 行：快捷操作（4 个习惯） */}
        <div className="bg-white rounded-xl shadow p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">⚡ 习惯快捷打卡</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {/* 饮水 */}
            <button 
              onClick={() => handleQuickAction('water')}
              className="flex flex-col items-center p-4 bg-blue-50 hover:bg-blue-100 rounded-xl transition-colors"
            >
              <GlassWater className="w-8 h-8 text-blue-600 mb-2" />
              <span className="text-sm font-medium">💧 8 杯水</span>
              <span className="text-xs text-blue-700 mt-1">
                {habitStatus.water.completed}/{habitStatus.water.target} 杯
              </span>
            </button>

            {/* 体重 */}
            <button 
              onClick={() => handleQuickAction('weight')}
              className="flex flex-col items-center p-4 bg-purple-50 hover:bg-purple-100 rounded-xl transition-colors"
            >
              <Scale className="w-8 h-8 text-purple-600 mb-2" />
              <span className="text-sm font-medium">⚖️ 体重</span>
              <span className="text-xs text-purple-700 mt-1">
                {getHabitStatusDisplay('weight')}
              </span>
            </button>

            {/* 早睡 */}
            <button 
              onClick={() => handleQuickAction('sleep')}
              className="flex flex-col items-center p-4 bg-indigo-50 hover:bg-indigo-100 rounded-xl transition-colors"
            >
              <Moon className="w-8 h-8 text-indigo-600 mb-2" />
              <span className="text-sm font-medium">🌙 早睡</span>
              <span className="text-xs text-indigo-700 mt-1">
                {getHabitStatusDisplay('sleep')}
              </span>
            </button>

            {/* 冥想 */}
            <button 
              onClick={() => handleQuickAction('meditation')}
              className="flex flex-col items-center p-4 bg-pink-50 hover:bg-pink-100 rounded-xl transition-colors"
            >
              <Sparkles className="w-8 h-8 text-pink-600 mb-2" />
              <span className="text-sm font-medium">🧘 冥想</span>
              <span className="text-xs text-pink-700 mt-1">
                {getHabitStatusDisplay('meditation')}
              </span>
            </button>
          </div>
        </div>

        {/* 第 4 行：AI 健康顾问 */}
        <div className="bg-gradient-to-r from-purple-500 to-indigo-600 rounded-xl shadow p-6 text-white">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="bg-white/20 p-3 rounded-full">
                <Brain className="h-8 w-8" />
              </div>
              <div>
                <h3 className="text-xl font-bold">🤖 AI 健康顾问</h3>
                <p className="text-sm text-purple-100">智能分析您的健康数据，提供个性化建议</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white/10 rounded-lg p-4 mb-4">
            <h4 className="font-semibold mb-2">💡 今日观察</h4>
            <ul className="space-y-2 text-sm">
              <li className="flex items-start gap-2">
                <span>•</span>
                <span>
                  {isCalorieSurplus 
                    ? `你今天的热量盈余主要来自晚餐，建议减少主食摄入或增加运动` 
                    : `今天热量控制得很好，继续保持！`}
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span>•</span>
                <span>
                  💧 喝水提醒：今天还没喝够 8 杯水哦～
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span>•</span>
                <span>
                  🌙 昨晚睡得很好，继续保持 23 点前入睡！
                </span>
              </li>
            </ul>
          </div>

          <div className="flex gap-3">
            <button 
              onClick={() => navigate('/chat')}
              className="bg-white text-purple-600 px-4 py-2 rounded-lg font-semibold hover:bg-purple-50 transition-colors flex items-center gap-2"
            >
              💬 和 AI 聊聊
            </button>
            <button 
              onClick={() => navigate('/analytics')}
              className="bg-white/20 text-white px-4 py-2 rounded-lg font-semibold hover:bg-white/30 transition-colors"
            >
              📊 查看详细分析
            </button>
          </div>
        </div>

      </main>
    </div>
  );
}
