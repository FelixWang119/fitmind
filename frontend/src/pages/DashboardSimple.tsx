import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, Target, Flame, Droplets, TrendingDown, Calendar, ChevronRight, Heart, TrendingUp, MessageCircle, Brain, HeartHandshake, Dumbbell, Timer, CheckCircle } from 'lucide-react';
import api from '@/api/client';
import { exerciseCheckInApi, ExerciseDailySummary } from '@/services/exerciseCheckIn';

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
          <div className="bg-white rounded-xl shadow p-6">
             <div className="flex items-center mb-4">
               <div className="bg-green-100 p-3 rounded-full mr-4">
                 <TrendingUp className="h-6 w-6 text-green-600" />
               </div>
               <div className="flex items-start">
                 <div>
                   <p className="text-sm text-gray-500">今日热量</p>
                   <p className="text-2xl font-bold text-gray-900">
                     {data.quick_stats?.today_calories || 0} 卡
                   </p>
                 </div>
                 {/* 提示按钮 */}
                 <div className="relative ml-2 group">
                   <button className="text-gray-400 hover:text-gray-600 focus:outline-none">
                     <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                       <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                     </svg>
                   </button>
                   {/* 浮窗 - 现在显示具体数值 */}
                   <div className="absolute left-0 top-full mt-2 w-72 p-4 bg-white border border-gray-200 rounded-lg shadow-lg z-10 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300">
                     <p className="text-xs text-gray-600">
                       <strong>热量盈余计算：</strong><br/>
                       热量盈余 = 摄入热量 - 基础代谢 - 运动消耗<br/><br/>
                       <span className="font-medium">摄入热量：</span>{data.quick_stats?.intake_calories || 0} kcal（来自饮食记录）<br/>
                       <span className="font-medium">基础代谢：</span>{data.quick_stats?.basal_metabolism || 2000} kcal（目标值）<br/>
                       <span className="font-medium">运动消耗：</span>{data.quick_stats?.exercise_calories_burned || 0} kcal（来自运动记录）<br/><br/>
                       <span className="font-medium">计算过程：</span> {data.quick_stats?.intake_calories || 0} - {data.quick_stats?.basal_metabolism || 2000} - {data.quick_stats?.exercise_calories_burned || 0} = {data.quick_stats?.today_calories || 0}
                     </p>
                   </div>
                 </div>
               </div>
             </div>
          </div>

           <div className="bg-white rounded-xl shadow p-6">
             <div className="flex items-center mb-4">
               <div className="bg-blue-100 p-3 rounded-full mr-4">
                 <Activity className="h-6 w-6 text-blue-600" />
               </div>
               <div className="flex items-start">
                 <div>
                   <p className="text-sm text-gray-500">今日步数</p>
                   <p className="text-2xl font-bold text-gray-900">
                     {data.quick_stats?.daily_step_count?.toLocaleString() || 0} 步
                   </p>
                 </div>
                 {/* 步数提示按钮 */}
                 <div className="relative ml-2 group">
                   <button className="text-gray-400 hover:text-gray-600 focus:outline-none">
                     <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                       <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                     </svg>
                   </button>
                   {/* 步数浮窗 */}
                   <div className="absolute left-0 top-full mt-2 w-64 p-4 bg-white border border-gray-200 rounded-lg shadow-lg z-10 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300">
                     <p className="text-xs text-gray-600">
                       <strong>步数来源：</strong><br/>
                       步数数据来自您设备上的计步器<br/>
                       或手动输入的步数数据
                     </p>
                   </div>
                 </div>
               </div>
             </div>
           </div>

           <div className="bg-white rounded-xl shadow p-6">
             <div className="flex items-center mb-4">
               <div className="bg-purple-100 p-3 rounded-full mr-4">
                 <Heart className="h-6 w-6 text-purple-600" />
               </div>
               <div className="flex items-start">
                 <div>
                   <p className="text-sm text-gray-500">睡眠时长</p>
                   <p className="text-2xl font-bold text-gray-900">
                     {data.quick_stats?.sleep_hours || 0} 小时
                   </p>
                 </div>
                 {/* 睡眠提示按钮 */}
                 <div className="relative ml-2 group">
                   <button className="text-gray-400 hover:text-gray-600 focus:outline-none">
                     <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                       <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                     </svg>
                   </button>
                   {/* 睡眠浮窗 */}
                   <div className="absolute left-0 top-full mt-2 w-64 p-4 bg-white border border-gray-200 rounded-lg shadow-lg z-10 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300">
                     <p className="text-xs text-gray-600">
                       <strong>睡眠时长来源：</strong><br/>
                       睡眠数据来自您的设备或<br/>
                       手动输入的睡眠记录
                     </p>
                   </div>
                 </div>
               </div>
             </div>
           </div>

           <div className="bg-white rounded-xl shadow p-6">
             <div className="flex items-center mb-4">
               <div className="bg-cyan-100 p-3 rounded-full mr-4">
                 <Droplets className="h-6 w-6 text-cyan-600" />
               </div>
               <div className="flex items-start">
                 <div>
                   <p className="text-sm text-gray-500">水分摄入</p>
                   <p className="text-2xl font-bold text-gray-900">
                     {data.quick_stats?.water_intake_ml || 0} ml
                   </p>
                 </div>
                 {/* 水分提示按钮 */}
                 <div className="relative ml-2 group">
                   <button className="text-gray-400 hover:text-gray-600 focus:outline-none">
                     <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                       <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                     </svg>
                   </button>
                   {/* 水分浮窗 */}
                   <div className="absolute left-0 top-full mt-2 w-64 p-4 bg-white border border-gray-200 rounded-lg shadow-lg z-10 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300">
                     <p className="text-xs text-gray-600">
                       <strong>水分摄入来源：</strong><br/>
                       水分记录来自您手动记录<br/>
                       的饮水活动
                     </p>
                   </div>
                 </div>
               </div>
             </div>
           </div>
        </div>

        {/* 运动数据显示 */}
        {exerciseData && (
          <div className="bg-white rounded-xl shadow p-6 mb-8">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <Dumbbell className="w-6 h-6 text-orange-500 mr-3" />
                <h3 className="font-bold text-gray-800">今日运动</h3>
              </div>
              <button
                onClick={() => navigate('/exercise-checkin')}
                className="text-orange-600 hover:text-orange-700 text-sm font-medium flex items-center"
              >
                详情 <ChevronRight className="w-4 h-4 ml-1" />
              </button>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center relative">
                <div className="flex items-center justify-center mb-1">
                  <Timer className="w-4 h-4 text-orange-500 mr-1" />
                </div>
                <div className="text-lg font-bold text-orange-600">
                  {exerciseData.total_duration_minutes}
                </div>
                <div className="text-xs text-gray-500">分钟</div>
                
                {/* 时间提示按钮 */}
                <div className="absolute top-0 right-0 transform translate-x-1/2 -translate-y-1/2 group">
                  <button className="text-gray-300 hover:text-gray-500 focus:outline-none">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </button>
                  <div className="absolute right-0 top-full mt-2 w-48 p-3 bg-white border border-gray-200 rounded-lg shadow-lg z-10 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300">
                    <p className="text-xs text-gray-600">
                      <strong>运动时长来源：</strong><br/>
                      所有运动打卡的时长总和
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="text-center relative">
                <div className="flex items-center justify-center mb-1">
                  <Timer className="w-4 h-4 text-red-500 mr-1" />
                </div>
                <div className="text-lg font-bold text-red-600">
                  {exerciseData.total_calories_burned}
                </div>
                <div className="text-xs text-gray-500">kcal</div>
                
                {/* 卡路里提示按钮 */}
                <div className="absolute top-0 right-0 transform translate-x-1/2 -translate-y-1/2 group">
                  <button className="text-gray-300 hover:text-gray-500 focus:outline-none">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </button>
                  <div className="absolute right-0 top-full mt-2 w-48 p-3 bg-white border border-gray-200 rounded-lg shadow-lg z-10 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300">
                    <p className="text-xs text-gray-600">
                      <strong>运动消耗来源：</strong><br/>
                      所有运动打卡计算的卡路里总和
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="text-center relative">
                <div className="flex items-center justify-center mb-1">
                  <CheckCircle className="w-4 h-4 text-blue-500 mr-1" />
                </div>
                <div className="text-lg font-bold text-blue-600">
                  {exerciseData.sessions_count}
                </div>
                <div className="text-xs text-gray-500">次</div>
                
                {/* 次数提示按钮 */}
                <div className="absolute top-0 right-0 transform translate-x-1/2 -translate-y-1/2 group">
                  <button className="text-gray-300 hover:text-gray-500 focus:outline-none">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </button>
                  <div className="absolute right-0 top-full mt-2 w-48 p-3 bg-white border border-gray-200 rounded-lg shadow-lg z-10 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300">
                    <p className="text-xs text-gray-600">
                      <strong>运动次数来源：</strong><br/>
                      今日完成的运动打卡总次数
                    </p>
                  </div>
                </div>
              </div>
            </div>
            
            {exerciseData.progress_percentage !== undefined && (
              <div className="mt-4">
                <div className="flex justify-between text-xs text-gray-600 mb-1">
                  <span>今日目标进度</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-full bg-gray-200 rounded-full h-2 flex-1">
                    <div 
                      className="bg-gradient-to-r from-orange-500 to-red-500 h-2 rounded-full transition-all"
                      style={{ width: `${Math.min(exerciseData.progress_percentage, 100)}%` }}
                    ></div>
                  </div>
                  
                  {/* 进度提示按钮 */}
                  <div className="relative group ml-1">
                    <button className="text-gray-300 hover:text-gray-500 focus:outline-none">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </button>
                    <div className="absolute right-0 top-full mt-2 w-48 p-3 bg-white border border-gray-200 rounded-lg shadow-lg z-10 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300">
                      <p className="text-xs text-gray-600">
                        <strong>目标进度来源：</strong><br/>
                        当前运动量与今日运动目标的比例
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
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