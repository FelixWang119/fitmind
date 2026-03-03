import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, Plus, Minus, Scale, TrendingUp } from 'lucide-react';

// 体重记录
interface WeightRecord {
  id?: number;
  date: string;
  time: string;
  weight: number;
  bodyFat?: number;
  muscle?: number;
  water?: number;
  note?: string;
}

// 测量时间选项
const TIME_OPTIONS = [
  { value: 'morning', label: '晨起空腹', icon: '🌅' },
  { value: 'before-meal', label: '餐前', icon: '🍽️' },
  { value: 'after-meal', label: '餐后', icon: '🍴' },
  { value: 'evening', label: '睡前', icon: '🌙' },
];

export default function WeightTracker() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [weight, setWeight] = useState<number | ''>('');
  const [measureTime, setMeasureTime] = useState('morning');
  const [bodyFat, setBodyFat] = useState<number | ''>('');
  const [muscle, setMuscle] = useState<number | ''>('');
  const [water, setWater] = useState<number | ''>('');
  const [todayTip] = useState(
    "晨起空腹排便后称重最准确，建议固定时间"
  );

  // 模拟历史数据
  const [history] = useState([
    { date: '2026-02-26', weight: 69.2, time: 'morning' },
    { date: '2026-02-27', weight: 68.8, time: 'morning' },
    { date: '2026-02-28', weight: 68.5, time: 'morning' },
    { date: '2026-03-01', weight: 68.3, time: 'morning' },
  ]);

  useEffect(() => {
    loadTodayWeight();
  }, []);

  const loadTodayWeight = async () => {
    try {
      setLoading(true);
      // TODO: 调用 API 获取今日体重记录
      // const data = await weightApi.getToday();
      // setWeight(data.weight);
      // setMeasureTime(data.time);
      setWeight('');
      setMeasureTime('morning');
    } catch (error) {
      console.error('加载体重数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!weight || weight <= 0) {
      alert('请输入有效体重');
      return;
    }

    try {
      // TODO: 调用 API 保存记录
      // await weightApi.save({
      //   weight: Number(weight),
      //   time: measureTime,
      //   bodyFat: Number(bodyFat) || undefined,
      //   muscle: Number(muscle) || undefined,
      //   water: Number(water) || undefined,
      // });
      
      alert('体重记录成功！💪');
      navigate(-1);
    } catch (error) {
      console.error('保存体重记录失败:', error);
      alert('保存失败，请重试');
    }
  };

  // 计算趋势
  const getTrend = () => {
    if (history.length < 2) return 0;
    const lastWeight = history[history.length - 1].weight;
    const prevWeight = history[history.length - 2].weight;
    return lastWeight - prevWeight;
  };

  const trend = getTrend();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-purple-50 to-pink-100">
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
        
        {/* 体重输入卡片 */}
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="bg-purple-100 p-3 rounded-xl">
                <Scale className="w-8 h-8 text-purple-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-800">⚖️ 今日体重</h1>
                <p className="text-sm text-gray-600">记录每日体重变化</p>
              </div>
            </div>
            {trend !== 0 && (
              <div className={`flex items-center gap-1 text-sm font-medium ${
                trend > 0 ? 'text-red-600' : 'text-green-600'
              }`}>
                <TrendingUp className={`w-4 h-4 ${trend > 0 ? 'rotate-45' : '-rotate-45'}`} />
                {trend > 0 ? '+' : ''}{trend.toFixed(1)}kg
              </div>
            )}
          </div>

          {/* 体重输入 */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              体重 (kg) *
            </label>
            <div className="flex items-center gap-4">
              <input
                type="number"
                value={weight}
                onChange={(e) => setWeight(e.target.value ? Number(e.target.value) : '')}
                placeholder="68.5"
                step="0.1"
                min="20"
                max="300"
                className="flex-1 text-4xl font-bold text-center border-2 border-gray-300 rounded-xl py-4 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all"
              />
            </div>
          </div>

          {/* 测量时间选择 */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              测量时间 *
            </label>
            <div className="grid grid-cols-2 gap-3">
              {TIME_OPTIONS.map((option) => (
                <button
                  key={option.value}
                  onClick={() => setMeasureTime(option.value)}
                  className={`p-3 rounded-xl border-2 transition-all ${
                    measureTime === option.value
                      ? 'border-purple-500 bg-purple-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="text-2xl mb-1">{option.icon}</div>
                  <div className="text-sm font-medium">{option.label}</div>
                </button>
              ))}
            </div>
          </div>

          {/* 可选体脂数据 */}
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div>
              <label className="block text-sm text-gray-600 mb-1">体脂率 (%)</label>
              <input
                type="number"
                value={bodyFat}
                onChange={(e) => setBodyFat(e.target.value ? Number(e.target.value) : '')}
                placeholder="20.5"
                step="0.1"
                className="w-full border border-gray-300 rounded-lg py-2 px-3 focus:border-purple-500 focus:ring-2 focus:ring-purple-200"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">肌肉量 (kg)</label>
              <input
                type="number"
                value={muscle}
                onChange={(e) => setMuscle(e.target.value ? Number(e.target.value) : '')}
                placeholder="45.2"
                step="0.1"
                className="w-full border border-gray-300 rounded-lg py-2 px-3 focus:border-purple-500 focus:ring-2 focus:ring-purple-200"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">水分率 (%)</label>
              <input
                type="number"
                value={water}
                onChange={(e) => setWater(e.target.value ? Number(e.target.value) : '')}
                placeholder="55.0"
                step="0.1"
                className="w-full border border-gray-300 rounded-lg py-2 px-3 focus:border-purple-500 focus:ring-2 focus:ring-purple-200"
              />
            </div>
          </div>

          {/* 保存按钮 */}
          <button
            onClick={handleSave}
            disabled={!weight || weight <= 0}
            className="w-full py-4 bg-purple-600 text-white rounded-xl font-semibold hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            💾 保存记录
          </button>
        </div>

        {/* 体重趋势 */}
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">📈 体重趋势</h2>
          <div className="h-48 flex items-end justify-between gap-2">
            {history.map((record, index) => {
              const maxWeight = Math.max(...history.map(h => h.weight));
              const minWeight = Math.min(...history.map(h => h.weight));
              const range = maxWeight - minWeight || 1;
              const height = ((record.weight - minWeight) / range) * 100;
              
              return (
                <div key={index} className="flex-1 flex flex-col items-center gap-2">
                  <div 
                    className="w-full bg-purple-500 rounded-t transition-all hover:bg-purple-600"
                    style={{ height: `${Math.max(height, 20)}%` }}
                  />
                  <div className="text-xs text-gray-600">
                    {new Date(record.date).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })}
                  </div>
                  <div className="text-sm font-medium">{record.weight}</div>
                </div>
              );
            })}
          </div>
        </div>

        {/* 称重小贴士 */}
        <div className="bg-gradient-to-r from-purple-500 to-pink-600 rounded-2xl shadow-lg p-6 text-white">
          <div className="flex items-start gap-3">
            <div className="bg-white/20 p-2 rounded-lg">
              <Scale className="w-6 h-6" />
            </div>
            <div>
              <h3 className="font-semibold mb-1">💡 称重小贴士</h3>
              <p className="text-sm text-purple-100">{todayTip}</p>
            </div>
          </div>
        </div>

      </main>
    </div>
  );
}
