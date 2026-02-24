import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, Target, Flame, Droplets, TrendingDown, Calendar, ChevronRight, Heart, TrendingUp, MessageCircle, Brain, HeartHandshake, Dumbbell, Timer, CheckCircle } from 'lucide-react';
import api from '@/api/client';
import { exerciseCheckInApi, ExerciseDailySummary } from '@/services/exerciseCheckIn';
import { 
  CalorieCard,
  StepCountCard,
  SleepCard,
  WaterIntakeCard 
} from '../components/Dashboard/Cards';
import { ActivitySection } from '../components/Dashboard/ActivitySection';

interface NutritionData {
  calories_consumed: number;
  remaining_calories: number;
  meals_count: number;
  progress_percentage?: number;
}

interface DashboardData {
  greeting?: string;
  quick_stats?: {
    today_calories?: number;
    daily_step_count?: number;
    sleep_hours?: number;
    water_intake_ml?: number;
    // 热量构成明细 (配合后端增强)
    intake_calories?: number;
    basal_metabolism?: number;
    exercise_calories_burned?: number;
  };
}

export default function DashboardSimple() {
  const [data, setData] = useState<DashboardData>({});
  const [loading, setLoading] = useState(true);
  const [exerciseData, setExerciseData] = useState<ExerciseDailySummary | null>(null);
  const [nutritionData, setNutritionData] = useState<NutritionData | null>(null);
  const navigate = useNavigate();

  const handleQuickAction = (action: string) => {
    switch (action) {
      case 'weight':
        navigate('/health');
        break;
      case 'habit':
        navigate('/habits');
        break;
      case 'diet':
        navigate('/diet-tracking');
        break;
      case 'emotion':
        navigate('/emotional');
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
      
      // 加载营养数据（从已有API获取）
      // 暂时使用模拟数据，实际应用中从diet tracking API获取
      setNutritionData({
        calories_consumed: data.quick_stats?.intake_calories || 0,
        remaining_calories: 2000 - (data.quick_stats?.intake_calories || 0), // 假设目标为2000
        meals_count: Math.floor(Math.random() * 6), // 模拟餐数
        progress_percentage: 60
      });
      
      setData({
        ...dashboardData,
        quick_stats: quickStatsData,
      });
    } catch (err) {
      console.error('加载数据失败:', err);
      // 使用模拟数据
      setData({
        greeting: '欢迎回来，测试用户！',
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
      // 运动数据模拟
      setExerciseData({
        date: new Date().toISOString().split('T')[0],
        total_duration_minutes: 45,
        total_calories_burned: 320,
        sessions_count: 2,
        exercise_types: ['跑步', '游泳'],
        progress_percentage: 50
      });
      
      // 营养数据模拟
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
          <CalorieCard 
            today_calories={data.quick_stats?.today_calories}
            intake_calories={data.quick_stats?.intake_calories}
            basal_metabolism={data.quick_stats?.basal_metabolism}
            exercise_calories_burned={data.quick_stats?.exercise_calories_burned}
          />
          
          <StepCountCard 
            daily_step_count={data.quick_stats?.daily_step_count}
          />

          <WaterIntakeCard 
            water_intake_ml={data.quick_stats?.water_intake_ml}
          />

          <SleepCard 
            sleep_hours={data.quick_stats?.sleep_hours}
          />
        </div>

        {/* 运动打卡与饮食打卡对称入口 */}
        <ActivitySection 
          exerciseData={exerciseData || undefined}
          nutritionData={nutritionData || undefined}
          onExerciseClick={() => navigate('/exercise-checkin')}
          onNutritionClick={() => navigate('/diet-tracking')}
        />

        {/* 快捷操作 */}
        <div className="bg-white rounded-xl shadow p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-800 mb-4">快捷操作</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <button 
              onClick={() => handleQuickAction('weight')}
              className="flex flex-col items-center justify-center p-4 bg-blue-50 hover:bg-blue-100 text-blue-600 rounded-xl transition-colors"
            >
              <Activity className="w-6 h-6 mb-2" />
              <span className="text-sm font-medium">记录体重</span>
            </button>
            <button 
              onClick={() => handleQuickAction('habit')}
              className="flex flex-col items-center justify-center p-4 bg-green-50 hover:bg-green-100 text-green-600 rounded-xl transition-colors"
            >
              <Calendar className="w-6 h-6 mb-2" />
              <span className="text-sm font-medium">完成习惯</span>
            </button>
             <button 
               onClick={() => handleQuickAction('diet')}
               className="flex flex-col items-center justify-center p-4 bg-cyan-50 hover:bg-cyan-100 text-cyan-600 rounded-xl transition-colors"
            >
              <Droplets className="w-6 h-6 mb-2" />
              <span className="text-sm font-medium">记录饮食</span>
            </button>
            <button 
              onClick={() => handleQuickAction('emotion')}
              className="flex flex-col items-center justify-center p-4 bg-orange-50 hover:bg-orange-100 text-orange-600 rounded-xl transition-colors"
            >
              <Flame className="w-6 h-6 mb-2" />
              <span className="text-sm font-medium">情感签到</span>
            </button>
          </div>
        </div>

        {/* AI 咨询入口 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <button 
            onClick={() => navigate('/chat')}
            className="bg-gradient-to-r from-purple-500 to-indigo-600 rounded-xl shadow p-6 text-white hover:from-purple-600 hover:to-indigo-700 transition-all"
          >
            <div className="flex items-center">
              <div className="bg-white/20 p-3 rounded-full mr-4">
                <Brain className="h-8 w-8" />
              </div>
              <div className="text-left">
                <h3 className="text-lg font-bold mb-1">AI 側康顾问</h3>
                <p className="text-sm opacity-90">智能分析您的健康数据，提供个性化建议</p>
              </div>
            </div>
          </button>
          
          <button 
            onClick={() => navigate('/emotional')}
            className="bg-gradient-to-r from-pink-500 to-rose-500 rounded-xl shadow p-6 text-white hover:from-pink-600 hover:to-rose-600 transition-all"
          >
            <div className="flex items-center">
              <div className="bg-white/20 p-3 rounded-full mr-4">
                <HeartHandshake className="h-8 w-8" />
              </div>
              <div className="text-left">
                <h3 className="text-lg font-bold mb-1">情感支持</h3>
                <p className="text-sm opacity-90">AI 倾听您的情绪，提供心理支持和建议</p>
              </div>
            </div>
          </button>
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

export default function DashboardSimple() {
  const [data, setData] = useState<DashboardData>({});
  const [loading, setLoading] = useState(true);
  const [exerciseData, setExerciseData] = useState<ExerciseDailySummary | null>(null);
  const navigate = useNavigate();

  const handleQuickAction = (action: string) => {
    switch (action) {
      case 'weight':
        navigate('/health');
        break;
      case 'habit':
        navigate('/habits');
        break;
      case 'diet':
        navigate('/diet-tracking');
        break;
      case 'emotion':
        navigate('/emotional');
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
      
      setData({
        ...dashboardData,
        quick_stats: quickStatsData,
      });
    } catch (err) {
      console.error('加载数据失败:', err);
      // 使用模拟数据
      setData({
        greeting: '欢迎回来，测试用户！',
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
      // 运动数据模拟
      setExerciseData({
        date: new Date().toISOString().split('T')[0],
        total_duration_minutes: 45,
        total_calories_burned: 320,
        sessions_count: 2,
        exercise_types: ['跑步', '游泳'],
        progress_percentage: 50
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
          <CalorieCard 
            today_calories={data.quick_stats?.today_calories}
            intake_calories={data.quick_stats?.intake_calories}
            basal_metabolism={data.quick_stats?.basal_metabolism}
            exercise_calories_burned={data.quick_stats?.exercise_calories_burned}
          />
          
          <StepCountCard 
            daily_step_count={data.quick_stats?.daily_step_count}
          />

          <SleepCard 
            sleep_hours={data.quick_stats?.sleep_hours}
          />

          <WaterIntakeCard 
            water_intake_ml={data.quick_stats?.water_intake_ml}
          />
        </div>

        {/* 运动数据显示 */}
        {exerciseData && (
          <ExerciseSection 
            exerciseData={exerciseData}
            navigate={navigate}
          />
        )}

        {/* 快捷操作 */}
        <div className="bg-white rounded-xl shadow p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-800 mb-4">快捷操作</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <button 
              onClick={() => handleQuickAction('weight')}
              className="flex flex-col items-center justify-center p-4 bg-blue-50 hover:bg-blue-100 text-blue-600 rounded-xl transition-colors"
            >
              <Activity className="w-6 h-6 mb-2" />
              <span className="text-sm font-medium">记录体重</span>
            </button>
            <button 
              onClick={() => handleQuickAction('habit')}
              className="flex flex-col items-center justify-center p-4 bg-green-50 hover:bg-green-100 text-green-600 rounded-xl transition-colors"
            >
              <Calendar className="w-6 h-6 mb-2" />
              <span className="text-sm font-medium">完成习惯</span>
            </button>
             <button 
               onClick={() => handleQuickAction('diet')}
               className="flex flex-col items-center justify-center p-4 bg-cyan-50 hover:bg-cyan-100 text-cyan-600 rounded-xl transition-colors"
            >
              <Droplets className="w-6 h-6 mb-2" />
              <span className="text-sm font-medium">记录饮食</span>
            </button>
            <button 
              onClick={() => handleQuickAction('emotion')}
              className="flex flex-col items-center justify-center p-4 bg-orange-50 hover:bg-orange-100 text-orange-600 rounded-xl transition-colors"
            >
              <Flame className="w-6 h-6 mb-2" />
              <span className="text-sm font-medium">情感签到</span>
            </button>
          </div>
        </div>

        {/* AI 咨询入口 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <button 
            onClick={() => navigate('/chat')}
            className="bg-gradient-to-r from-purple-500 to-indigo-600 rounded-xl shadow p-6 text-white hover:from-purple-600 hover:to-indigo-700 transition-all"
          >
            <div className="flex items-center">
              <div className="bg-white/20 p-3 rounded-full mr-4">
                <Brain className="h-8 w-8" />
              </div>
              <div className="text-left">
                <h3 className="text-lg font-bold mb-1">AI 健康顾问</h3>
                <p className="text-sm opacity-90">智能分析您的健康数据，提供个性化建议</p>
              </div>
            </div>
          </button>
          
          <button 
            onClick={() => navigate('/emotional')}
            className="bg-gradient-to-r from-pink-500 to-rose-500 rounded-xl shadow p-6 text-white hover:from-pink-600 hover:to-rose-600 transition-all"
          >
            <div className="flex items-center">
              <div className="bg-white/20 p-3 rounded-full mr-4">
                <HeartHandshake className="h-8 w-8" />
              </div>
              <div className="text-left">
                <h3 className="text-lg font-bold mb-1">情感支持</h3>
                <p className="text-sm opacity-90">AI 倾听您的情绪，提供心理支持和建议</p>
              </div>
            </div>
          </button>
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