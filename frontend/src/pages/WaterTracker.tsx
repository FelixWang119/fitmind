import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, Plus, Minus, GlassWater, Droplets } from 'lucide-react';

// 喝水小贴士库
const WATER_TIPS = [
  "小口慢饮比大口灌水更容易被身体吸收",
  "晨起第一杯水可以帮助唤醒新陈代谢",
  "饭前喝水可以增加饱腹感，帮助控制饮食",
  "运动后要及时补充水分，但不要一次性喝太多",
  "睡前 2 小时减少饮水，避免影响睡眠",
  "每天喝水量 = 体重 (kg) × 30ml",
  "尿液呈淡黄色说明水分充足",
  "不要等到口渴才喝水，那时已经轻度脱水了",
];

interface WaterIntake {
  id?: number;
  date: string;
  cup_count: number;
  total_ml: number;
  timestamps?: string[];
}

interface Reminder {
  time: string;
  label: string;
  completed: boolean;
}

export default function WaterTracker() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [cupCount, setCupCount] = useState(0);
  const [targetCups] = useState(8);
  const [cupSize] = useState(250); // ml
  const [todayTip] = useState(() => 
    WATER_TIPS[Math.floor(Math.random() * WATER_TIPS.length)]
  );

  // 提醒时间配置
  const [reminders] = useState<Reminder[]>([
    { time: '09:00', label: '晨起第一杯水', completed: false },
    { time: '11:00', label: '上午补水', completed: false },
    { time: '14:00', label: '下午补水', completed: false },
    { time: '17:00', label: '傍晚补水', completed: false },
    { time: '20:00', label: '睡前少喝', completed: false },
  ]);

  useEffect(() => {
    loadTodayWater();
  }, []);

  const loadTodayWater = async () => {
    try {
      setLoading(true);
      // TODO: 调用 API 获取今日饮水记录
      // const data = await waterApi.getToday();
      // setCupCount(data.cup_count);
      
      // 临时使用模拟数据
      setCupCount(0);
    } catch (error) {
      console.error('加载饮水数据失败:', error);
      setCupCount(0);
    } finally {
      setLoading(false);
    }
  };

  const handleAddCup = async () => {
    if (cupCount >= targetCups) {
      alert('今天已经喝够 8 杯水了！真棒！🎉');
      return;
    }
    
    try {
      // TODO: 调用 API 记录饮水
      // await waterApi.addCup();
      setCupCount(prev => prev + 1);
    } catch (error) {
      console.error('添加饮水记录失败:', error);
      alert('记录失败，请重试');
    }
  };

  const handleRemoveCup = async () => {
    if (cupCount <= 0) return;
    
    try {
      // TODO: 调用 API 删除最后一条记录
      // await waterApi.removeCup();
      setCupCount(prev => prev - 1);
    } catch (error) {
      console.error('删除饮水记录失败:', error);
    }
  };

  const totalMl = cupCount * cupSize;
  const targetMl = targetCups * cupSize;
  const progress = (cupCount / targetCups) * 100;

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-indigo-100">
      {/* 头部 */}
      <header className="bg-white shadow-sm">
        <div className="max-w-3xl mx-auto px-4 py-4">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center text-gray-600 hover:text-gray-900"
          >
            <ChevronLeft className="w-5 h-5 mr-1" />
            返回
          </button>
        </div>
      </header>

      {/* 主内容区 */}
      <main className="max-w-3xl mx-auto px-4 py-6 space-y-6">
        
        {/* 进度卡片 */}
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="bg-blue-100 p-3 rounded-xl">
                <Droplets className="w-8 h-8 text-blue-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-800">💧 今日饮水</h1>
                <p className="text-sm text-gray-600">保持身体水分平衡</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-3xl font-bold text-blue-600">
                {cupCount}/{targetCups}
              </p>
              <p className="text-xs text-gray-600">杯</p>
            </div>
          </div>

          {/* 进度条 */}
          <div className="mb-4">
            <div className="flex justify-between text-sm mb-2">
              <span className="text-gray-600">已喝 {totalMl}ml</span>
              <span className="text-gray-600">目标 {targetMl}ml</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-4">
              <div
                className="bg-gradient-to-r from-blue-500 to-indigo-600 h-4 rounded-full transition-all duration-500"
                style={{ width: `${progress}%` }}
              />
            </div>
            <p className="text-center text-sm text-gray-600 mt-2">
              进度 {Math.round(progress)}%
            </p>
          </div>

          {/* 操作按钮 */}
          <div className="flex gap-4">
            <button
              onClick={handleRemoveCup}
              disabled={cupCount <= 0}
              className="flex-1 flex items-center justify-center gap-2 py-3 px-4 border-2 border-gray-300 rounded-xl hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Minus className="w-5 h-5" />
              <span className="font-medium">少喝一杯</span>
            </button>
            <button
              onClick={handleAddCup}
              disabled={cupCount >= targetCups}
              className="flex-1 flex items-center justify-center gap-2 py-3 px-4 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Plus className="w-5 h-5" />
              <span className="font-medium">喝一杯</span>
            </button>
          </div>
        </div>

        {/* 水杯展示区 */}
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">今日水杯</h2>
          <div className="grid grid-cols-4 gap-4">
            {Array.from({ length: targetCups }).map((_, index) => (
              <button
                key={index}
                onClick={() => {
                  if (index < cupCount) {
                    // 减少到点击的位置
                    setCupCount(index);
                  } else {
                    // 增加到点击的位置
                    setCupCount(index + 1);
                  }
                }}
                className="aspect-square flex items-center justify-center transition-all hover:scale-105"
              >
                <GlassWater
                  className={`w-12 h-12 transition-colors ${
                    index < cupCount
                      ? 'text-blue-600 fill-blue-600'
                      : 'text-gray-300'
                  }`}
                />
              </button>
            ))}
          </div>
        </div>

        {/* 喝水提醒 */}
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">⏰ 喝水提醒</h2>
          <div className="space-y-3">
            {reminders.map((reminder, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <div className={`w-2 h-2 rounded-full ${
                    reminder.completed ? 'bg-green-500' : 'bg-orange-400'
                  }`} />
                  <div>
                    <p className="font-medium text-gray-800">{reminder.time}</p>
                    <p className="text-sm text-gray-600">{reminder.label}</p>
                  </div>
                </div>
                <span className={`text-sm ${
                  reminder.completed ? 'text-green-600' : 'text-orange-600'
                }`}>
                  {reminder.completed ? '✅' : '⏳'}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* 喝水小贴士 */}
        <div className="bg-gradient-to-r from-blue-500 to-indigo-600 rounded-2xl shadow-lg p-6 text-white">
          <div className="flex items-start gap-3">
            <div className="bg-white/20 p-2 rounded-lg">
              <GlassWater className="w-6 h-6" />
            </div>
            <div>
              <h3 className="font-semibold mb-1">💡 喝水小贴士</h3>
              <p className="text-sm text-blue-100">{todayTip}</p>
            </div>
          </div>
        </div>

      </main>
    </div>
  );
}
