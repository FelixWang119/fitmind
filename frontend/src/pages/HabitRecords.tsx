import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ChevronLeft, Calendar, TrendingUp, Award } from 'lucide-react';

// 模拟月度数据
const generateMonthData = (habitId: number) => {
  const daysInMonth = 31;
  const data = [];
  for (let day = 1; day <= daysInMonth; day++) {
    const completed = Math.random() > 0.3;
    const value = completed ? Math.floor(Math.random() * 8) + 1 : 0;
    data.push({
      day,
      completed,
      value,
      date: `2026-03-${String(day).padStart(2, '0')}`,
    });
  }
  return data;
};

export default function HabitRecords() {
  const navigate = useNavigate();
  const { habitId } = useParams<{ habitId: string }>();
  const [loading, setLoading] = useState(true);
  const [habitName, setHabitName] = useState('');
  const [monthData, setMonthData] = useState<Array<{
    day: number;
    completed: boolean;
    value: number;
    date: string;
  }>>([]);

  useEffect(() => {
    loadRecords();
  }, [habitId]);

  const loadRecords = async () => {
    try {
      setLoading(true);
      // TODO: 调用 API 获取记录
      const habitNames: {[key: string]: string} = {
        '0': '每天保持热量赤字',
        '1': '每天 8 杯水',
        '2': '每天记录体重',
        '3': '每日早睡',
        '4': '每日冥想',
      };
      setHabitName(habitNames[habitId || '0'] || '习惯记录');
      setMonthData(generateMonthData(parseInt(habitId || '0')));
    } catch (error) {
      console.error('Failed to load records:', error);
    } finally {
      setLoading(false);
    }
  };

  const completedDays = monthData.filter(d => d.completed).length;
  const completionRate = Math.round((completedDays / monthData.length) * 100);
  const avgValue = Math.round(
    monthData.filter(d => d.completed).reduce((sum, d) => sum + d.value, 0) / completedDays
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
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
        
        {/* 标题 */}
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-800 mb-2">📅 {habitName}</h1>
          <p className="text-gray-600">2026 年 3 月记录</p>
        </div>

        {/* 统计卡片 */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-white rounded-xl shadow p-4 text-center">
            <p className="text-2xl font-bold text-blue-600">{completionRate}%</p>
            <p className="text-xs text-gray-600 mt-1">完成率</p>
          </div>
          <div className="bg-white rounded-xl shadow p-4 text-center">
            <p className="text-2xl font-bold text-green-600">{completedDays}天</p>
            <p className="text-xs text-gray-600 mt-1">已打卡</p>
          </div>
          <div className="bg-white rounded-xl shadow p-4 text-center">
            <p className="text-2xl font-bold text-purple-600">{avgValue}</p>
            <p className="text-xs text-gray-600 mt-1">平均/天</p>
          </div>
        </div>

        {/* 日历视图 */}
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <div className="flex items-center gap-2 mb-4">
            <Calendar className="w-5 h-5 text-blue-600" />
            <h2 className="text-lg font-semibold text-gray-800">月度日历</h2>
          </div>

          {/* 星期标题 */}
          <div className="grid grid-cols-7 gap-2 mb-2">
            {['日', '一', '二', '三', '四', '五', '六'].map(day => (
              <div key={day} className="text-center text-sm font-medium text-gray-600 py-2">
                {day}
              </div>
            ))}
          </div>

          {/* 日历网格 */}
          <div className="grid grid-cols-7 gap-2">
            {/* 空白填充（3 月 1 日是周日） */}
            <div className="aspect-square"></div>
            <div className="aspect-square"></div>
            <div className="aspect-square"></div>
            <div className="aspect-square"></div>
            <div className="aspect-square"></div>
            <div className="aspect-square"></div>
            
            {monthData.map((day) => (
              <div
                key={day.day}
                className={`aspect-square rounded-xl flex flex-col items-center justify-center transition-all ${
                  day.completed
                    ? 'bg-green-500 text-white'
                    : 'bg-gray-100 text-gray-400'
                }`}
              >
                <span className="text-sm font-medium">{day.day}</span>
                {day.completed && day.value > 0 && (
                  <span className="text-xs opacity-80">{day.value}</span>
                )}
              </div>
            ))}
          </div>

          {/* 图例 */}
          <div className="flex items-center justify-center gap-4 mt-4 pt-4 border-t">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded bg-green-500"></div>
              <span className="text-sm text-gray-600">已打卡</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded bg-gray-100"></div>
              <span className="text-sm text-gray-600">未打卡</span>
            </div>
          </div>
        </div>

        {/* 详细记录 */}
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-blue-600" />
            <h2 className="text-lg font-semibold text-gray-800">最近记录</h2>
          </div>
          <div className="space-y-3">
            {monthData.slice(0, 10).map((day) => (
              <div
                key={day.date}
                className={`flex items-center justify-between p-3 rounded-lg ${
                  day.completed ? 'bg-green-50' : 'bg-gray-50'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className={`w-2 h-2 rounded-full ${
                    day.completed ? 'bg-green-500' : 'bg-gray-300'
                  }`}></div>
                  <div>
                    <p className="font-medium text-gray-800">3 月{day.day}日</p>
                    <p className="text-xs text-gray-500">
                      {day.completed ? '已打卡' : '未打卡'}
                    </p>
                  </div>
                </div>
                {day.completed && day.value > 0 && (
                  <div className="text-right">
                    <p className="text-lg font-bold text-green-600">{day.value}</p>
                    {habitId === '1' && <p className="text-xs text-gray-500">杯</p>}
                    {habitId === '2' && <p className="text-xs text-gray-500">kg</p>}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* 成就 */}
        <div className="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-2xl shadow-lg p-6">
          <div className="flex items-center gap-3 mb-4">
            <Award className="w-6 h-6 text-yellow-600" />
            <h2 className="text-lg font-semibold text-gray-800">🏆 本月成就</h2>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white rounded-xl p-4 text-center">
              <p className="text-2xl font-bold text-yellow-600">
                {monthData.filter((d, i) => 
                  i > 0 && d.completed && monthData[i-1].completed
                ).length}天
              </p>
              <p className="text-xs text-gray-600 mt-1">连续打卡</p>
            </div>
            <div className="bg-white rounded-xl p-4 text-center">
              <p className="text-2xl font-bold text-green-600">
                {completedDays >= 20 ? '🎯' : '💪'}
              </p>
              <p className="text-xs text-gray-600 mt-1">
                {completedDays >= 20 ? '全勤奖' : '继续努力'}
              </p>
            </div>
          </div>
        </div>

      </main>
    </div>
  );
}
