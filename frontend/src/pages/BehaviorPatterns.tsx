import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowLeft,
  Clock, 
  Link2,
  Lightbulb,
  BarChart3,
} from 'lucide-react';
import { api } from '../api/client';
import toast from 'react-hot-toast';

// Types
interface HabitCorrelation {
  habit_ids: number[];
  habit_names: string[];
  correlation_strength: number;
  description: string;
}

interface BehaviorPatterns {
  time_preference: string;
  checkin_time_histogram: Record<string, number>;
  weekly_pattern: Record<string, number>;
  weekend_vs_weekday: Record<string, number>;
  habit_correlations: HabitCorrelation[];
  insights: string[];
}

const TIME_LABELS: Record<string, string> = {
  morning: '早晨',
  midday: '上午',
  afternoon: '下午',
  evening: '晚间',
  night: '深夜',
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

export default function BehaviorPatterns() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [patterns, setPatterns] = useState<BehaviorPatterns | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const data = await api.getBehaviorPatterns();
      setPatterns(data);
    } catch (error) {
      console.error('Failed to load behavior patterns:', error);
      toast.error('加载行为模式失败');
    } finally {
      setLoading(false);
    }
  };

  const getTimeIcon = (time: string) => {
    switch (time) {
      case 'morning':
        return '🌅';
      case 'afternoon':
        return '☀️';
      case 'evening':
        return '🌆';
      case 'night':
        return '🌙';
      default:
        return '⏰';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <button
          onClick={() => navigate('/habits-stats')}
          className="p-2 hover:bg-gray-100 rounded-xl transition-colors"
        >
          <ArrowLeft className="w-5 h-5 text-gray-600" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">行为模式分析</h1>
          <p className="text-gray-600 mt-1">了解你的习惯养成规律</p>
        </div>
      </div>

      {(!patterns || patterns.insights.includes('添加更多习惯以解锁行为分析')) && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-12 text-center">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <BarChart3 className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">数据不足</h3>
          <p className="text-gray-500 mb-4">需要至少2个习惯才能分析行为模式</p>
          <button
            onClick={() => navigate('/habits')}
            className="px-6 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors"
          >
            去创建更多习惯
          </button>
        </div>
      )}

      {patterns && patterns.insights.length > 0 && !patterns.insights.includes('添加更多习惯以解锁行为分析') && (
        <>
          {/* Time Preference */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">时间偏好</h2>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="text-4xl">{getTimeIcon(patterns.time_preference)}</div>
                <div>
                  <p className="text-xl font-semibold text-gray-900">
                    {TIME_LABELS[patterns.time_preference] || patterns.time_preference}
                  </p>
                  <p className="text-gray-500 text-sm">
                    你最习惯在这个时间段完成习惯
                  </p>
                </div>
              </div>
              <Clock className="w-8 h-8 text-gray-300" />
            </div>
          </div>

          {/* Time Distribution */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">打卡时间分布</h2>
            <div className="grid grid-cols-5 gap-4">
              {Object.entries(patterns.checkin_time_histogram).map(([time, count]) => (
                <div key={time} className="text-center">
                  <div 
                    className="h-32 bg-blue-500 rounded-xl flex items-end justify-center p-2"
                    style={{ 
                      height: `${Math.max((count / Math.max(...Object.values(patterns.checkin_time_histogram))) * 120, 20)}px`,
                      minHeight: '20px'
                    }}
                  >
                    <span className="text-white font-bold">{count}</span>
                  </div>
                  <p className="text-sm text-gray-600 mt-2">{TIME_LABELS[time] || time}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Weekly Pattern */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">每周完成模式</h2>
            <div className="grid grid-cols-7 gap-4">
              {['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'].map((day) => {
                const rate = patterns.weekly_pattern[day] || 0;
                const isWeekend = day === 'Saturday' || day === 'Sunday';
                return (
                  <div key={day} className="text-center">
                    <div 
                      className={`h-24 rounded-xl flex items-end justify-center p-2 ${
                        isWeekend ? 'bg-purple-100' : 'bg-blue-100'
                      }`}
                      style={{ 
                        height: `${Math.max(rate, 10)}px`,
                        minHeight: '30px'
                      }}
                    >
                      <span className={`text-sm font-bold ${rate >= 80 ? 'text-green-600' : rate >= 50 ? 'text-yellow-600' : 'text-red-600'}`}>
                        {rate}%
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mt-2">{DAY_LABELS[day]}</p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Weekend vs Weekday */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">工作日 vs 周末</h2>
            <div className="grid grid-cols-2 gap-6">
              <div className="text-center">
                <div className="h-32 bg-blue-500 rounded-xl flex items-center justify-center">
                  <span className="text-3xl font-bold text-white">
                    {patterns.weekend_vs_weekday.weekday || 0}%
                  </span>
                </div>
                <p className="text-gray-600 mt-2">工作日完成率</p>
              </div>
              <div className="text-center">
                <div className="h-32 bg-purple-500 rounded-xl flex items-center justify-center">
                  <span className="text-3xl font-bold text-white">
                    {patterns.weekend_vs_weekday.weekend || 0}%
                  </span>
                </div>
                <p className="text-gray-600 mt-2">周末完成率</p>
              </div>
            </div>
          </div>

          {/* Habit Correlations */}
          {patterns.habit_correlations.length > 0 && (
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center space-x-2 mb-4">
                <Link2 className="w-5 h-5 text-blue-600" />
                <h2 className="text-lg font-semibold text-gray-900">习惯关联性</h2>
              </div>
              <div className="space-y-4">
                {patterns.habit_correlations.map((correlation, index) => (
                  <div
                    key={index}
                    className="p-4 bg-gray-50 rounded-xl"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <span className="font-medium text-gray-900">
                          {correlation.habit_names[0]}
                        </span>
                        <span className="text-gray-400">+</span>
                        <span className="font-medium text-gray-900">
                          {correlation.habit_names[1]}
                        </span>
                      </div>
                      <span className="text-sm text-gray-500">
                        关联强度: {Math.round(correlation.correlation_strength * 100)}%
                      </span>
                    </div>
                    <p className="text-sm text-gray-600">{correlation.description}</p>
                    <div className="mt-2 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-500 rounded-full h-2"
                        style={{ width: `${correlation.correlation_strength * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Insights */}
          {patterns.insights.length > 0 && (
            <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-2xl p-6 text-white">
              <div className="flex items-center space-x-2 mb-4">
                <Lightbulb className="w-5 h-5" />
                <h2 className="text-lg font-semibold">行为洞察</h2>
              </div>
              <ul className="space-y-3">
                {patterns.insights.map((insight, index) => (
                  <li key={index} className="flex items-start space-x-2">
                    <span className="text-indigo-300 mt-1">•</span>
                    <span>{insight}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </>
      )}
    </div>
  );
}
