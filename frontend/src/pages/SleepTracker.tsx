import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, Moon, MoonStar, Star, Coffee } from 'lucide-react';

// 情绪鸡汤库
const SLEEP_QUOTES = [
  { text: "今天辛苦了，你值得一次优质的睡眠。放下一切，好好照顾自己。", emoji: "🌙" },
  { text: "好梦是明天的能量，早点休息吧～", emoji: "💤" },
  { text: "放下手机，让大脑休息一下吧。", emoji: "📱❌" },
  { text: "皮质醇需要休息了，晚安好梦！", emoji: "😴" },
  { text: "睡眠是免费的保健品，好好珍惜哦～", emoji: "💊" },
];

// 睡前准备 checklist
const PRE_SLEEP_CHECKLIST = [
  { id: 'phone', label: '放下手机', icon: '📱' },
  { id: 'light', label: '调暗灯光', icon: '💡' },
  { id: 'wash', label: '洗漱', icon: '🛁' },
  { id: 'read', label: '冥想/阅读', icon: '📖' },
];

export default function SleepTracker() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [sleepTime, setSleepTime] = useState('22:30');
  const [wakeTime, setWakeTime] = useState('06:30');
  const [sleepQuality, setSleepQuality] = useState(0);
  const [checklist, setChecklist] = useState<string[]>([]);
  const [todayQuote] = useState(
    SLEEP_QUOTES[Math.floor(Math.random() * SLEEP_QUOTES.length)]
  );

  useEffect(() => {
    loadTodaySleep();
  }, []);

  const loadTodaySleep = async () => {
    try {
      setLoading(true);
      // TODO: 调用 API 获取今日睡眠记录
      // const data = await sleepApi.getToday();
      // if (data) {
      //   setSleepTime(data.sleep_time);
      //   setWakeTime(data.wake_time);
      //   setSleepQuality(data.quality);
      // }
    } catch (error) {
      console.error('加载睡眠数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      // TODO: 调用 API 保存睡眠记录
      // await sleepApi.save({
      //   sleep_time: sleepTime,
      //   wake_time: wakeTime,
      //   quality: sleepQuality,
      //   checklist: checklist,
      // });
      
      alert('早睡打卡成功！晚安好梦～ 🌙');
      navigate(-1);
    } catch (error) {
      console.error('保存睡眠记录失败:', error);
      alert('保存失败，请重试');
    }
  };

  const toggleChecklist = (id: string) => {
    if (checklist.includes(id)) {
      setChecklist(checklist.filter(item => item !== id));
    } else {
      setChecklist([...checklist, id]);
    }
  };

  // 计算睡眠时长
  const calculateDuration = () => {
    const sleep = new Date(`2000-01-01 ${sleepTime}`);
    const wake = new Date(`2000-01-02 ${wakeTime}`);
    const diff = wake.getTime() - sleep.getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    return `${hours}小时${minutes > 0 ? minutes + '分钟' : ''}`;
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-indigo-900 via-purple-900 to-pink-900">
      {/* 头部 */}
      <header className="bg-white/10 backdrop-blur-sm shadow-sm">
        <div className="max-w-3xl mx-auto px-4 py-4">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center text-white hover:text-white/80"
          >
            <ChevronLeft className="w-5 h-5 mr-1" />
            返回
          </button>
        </div>
      </header>

      {/* 主内容区 */}
      <main className="max-w-3xl mx-auto px-4 py-6 space-y-6">
        
        {/* 情绪卡片 */}
        <div className="bg-white/10 backdrop-blur-sm rounded-2xl shadow-lg p-6 text-white">
          <div className="flex items-center gap-3 mb-4">
            <div className="text-4xl">{todayQuote.emoji}</div>
            <div>
              <h1 className="text-xl font-bold">{todayQuote.text}</h1>
            </div>
          </div>
        </div>

        {/* 入睡时间卡片 */}
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="bg-indigo-100 p-3 rounded-xl">
              <Moon className="w-8 h-8 text-indigo-600" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-800">🌙 昨晚睡得好吗？</h2>
              <p className="text-sm text-gray-600">记录你的睡眠情况</p>
            </div>
          </div>

          {/* 入睡时间 */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              昨晚几点入睡的？*
            </label>
            <div className="flex items-center gap-4">
              <input
                type="time"
                value={sleepTime}
                onChange={(e) => setSleepTime(e.target.value)}
                className="flex-1 text-3xl font-bold text-center border-2 border-gray-300 rounded-xl py-4 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all"
              />
            </div>
          </div>

          {/* 起床时间 */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              今早几点起床的？
            </label>
            <div className="flex items-center gap-4">
              <input
                type="time"
                value={wakeTime}
                onChange={(e) => setWakeTime(e.target.value)}
                className="flex-1 text-3xl font-bold text-center border-2 border-gray-300 rounded-xl py-4 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all"
              />
            </div>
            {sleepTime && wakeTime && (
              <p className="text-center text-sm text-gray-600 mt-2">
                睡眠时长：{calculateDuration()}
              </p>
            )}
          </div>

          {/* 睡眠质量评分 */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              睡眠质量评分
            </label>
            <div className="flex justify-between gap-2">
              {[1, 2, 3, 4, 5].map((rating) => (
                <button
                  key={rating}
                  onClick={() => setSleepQuality(rating)}
                  className={`flex-1 py-4 rounded-xl transition-all ${
                    sleepQuality >= rating
                      ? 'bg-yellow-400 text-white'
                      : 'bg-gray-100 text-gray-400'
                  }`}
                >
                  <div className="text-2xl mb-1">
                    <Star className={`w-8 h-8 ${sleepQuality >= rating ? 'fill-current' : ''}`} />
                  </div>
                  <div className="text-sm font-medium">{rating}星</div>
                </button>
              ))}
            </div>
          </div>

          {/* 睡前准备 */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              睡前准备（可选）
            </label>
            <div className="grid grid-cols-2 gap-3">
              {PRE_SLEEP_CHECKLIST.map((item) => (
                <button
                  key={item.id}
                  onClick={() => toggleChecklist(item.id)}
                  className={`flex items-center gap-3 p-3 rounded-xl border-2 transition-all ${
                    checklist.includes(item.id)
                      ? 'border-indigo-500 bg-indigo-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="text-2xl">{item.icon}</div>
                  <div className="text-sm font-medium">{item.label}</div>
                  {checklist.includes(item.id) && (
                    <div className="ml-auto">✅</div>
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* 保存按钮 */}
          <button
            onClick={handleSave}
            className="w-full py-4 bg-indigo-600 text-white rounded-xl font-semibold hover:bg-indigo-700 transition-colors"
          >
            🌙 完成打卡
          </button>
        </div>

        {/* 科学小贴士 */}
        <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-2xl shadow-lg p-6 text-white">
          <div className="flex items-start gap-3">
            <div className="bg-white/20 p-2 rounded-lg">
              <MoonStar className="w-6 h-6" />
            </div>
            <div>
              <h3 className="font-semibold mb-1">💡 睡眠小知识</h3>
              <p className="text-sm text-indigo-100">
                睡眠不足 7 小时，第二天食欲增加 23%。皮质醇过高会让脂肪更容易堆积在腹部。
              </p>
            </div>
          </div>
        </div>

      </main>
    </div>
  );
}
