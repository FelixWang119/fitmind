import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, Sparkles, Cloud, Coffee, Heart } from 'lucide-react';

// 灵性语录库
const SPIRITUAL_QUOTES = [
  { text: "你不需要完美，你只需要真实。", author: "" },
  { text: "今天，允许自己有不完美的时刻。", author: "" },
  { text: "每一次呼吸，都是与自己重逢的机会。", author: "" },
  { text: "静下来，听听内心的声音。", author: "" },
  { text: "接纳自己，从接纳当下的情绪开始。", author: "" },
  { text: "你值得被温柔对待，尤其是被自己。", author: "" },
  { text: "慢下来，生活不是比赛。", author: "" },
  { text: "感恩今天发生的每一件小事。", author: "" },
];

// 场景选项
const SCENE_OPTIONS = [
  { value: 'morning', label: '晨起冥想', icon: '🌅' },
  { value: 'before-meal', label: '餐前正念', icon: '🍽️' },
  { value: 'after-meal', label: '餐后消化', icon: '🍴' },
  { value: 'work', label: '工作间隙', icon: '💼' },
  { value: 'evening', label: '睡前放松', icon: '🌙' },
  { value: 'other', label: '其他', icon: '✨' },
];

// 心情选项
const MOOD_OPTIONS = [
  { value: 'calm', label: '平静', icon: '😌', color: 'bg-green-100 text-green-700' },
  { value: 'anxious', label: '焦虑', icon: '😰', color: 'bg-yellow-100 text-yellow-700' },
  { value: 'tired', label: '疲惫', icon: '😫', color: 'bg-gray-100 text-gray-700' },
  { value: 'happy', label: '愉悦', icon: '😊', color: 'bg-pink-100 text-pink-700' },
  { value: 'sad', label: '低落', icon: '😔', color: 'bg-blue-100 text-blue-700' },
];

export default function MeditationTracker() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [completed, setCompleted] = useState(false);
  const [scene, setScene] = useState('');
  const [mood, setMood] = useState('');
  const [todayQuote] = useState(
    SPIRITUAL_QUOTES[Math.floor(Math.random() * SPIRITUAL_QUOTES.length)]
  );

  useEffect(() => {
    loadTodayMeditation();
  }, []);

  const loadTodayMeditation = async () => {
    try {
      setLoading(true);
      // TODO: 调用 API 获取今日冥想记录
      // const data = await meditationApi.getToday();
      // if (data) {
      //   setCompleted(data.completed);
      //   setScene(data.scene);
      //   setMood(data.mood);
      // }
    } catch (error) {
      console.error('加载冥想数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!completed) {
      alert('请先确认完成冥想');
      return;
    }

    try {
      // TODO: 调用 API 保存冥想记录
      // await meditationApi.save({
      //   completed: true,
      //   scene: scene || undefined,
      //   mood: mood || undefined,
      // });
      
      alert('冥想打卡成功！继续保持～ 🧘');
      navigate(-1);
    } catch (error) {
      console.error('保存冥想记录失败:', error);
      alert('保存失败，请重试');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-pink-50 via-purple-50 to-indigo-50">
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
        
        {/* 灵性语录卡片 */}
        <div className="bg-gradient-to-r from-pink-500 to-purple-600 rounded-2xl shadow-lg p-6 text-white">
          <div className="flex items-start gap-3 mb-4">
            <div className="bg-white/20 p-3 rounded-full">
              <Sparkles className="w-8 h-8" />
            </div>
            <div>
              <h1 className="text-xl font-bold mb-2">✨ 今日灵性语录</h1>
              <p className="text-lg italic leading-relaxed">"{todayQuote.text}"</p>
              {todayQuote.author && (
                <p className="text-sm text-pink-100 mt-2">— {todayQuote.author}</p>
              )}
            </div>
          </div>
        </div>

        {/* 完成确认 */}
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="bg-pink-100 p-3 rounded-xl">
              <Heart className="w-8 h-8 text-pink-600" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-800">🧘 今日冥想</h2>
              <p className="text-sm text-gray-600">与自己独处的时光</p>
            </div>
          </div>

          {/* 完成确认按钮 */}
          <div className="mb-8">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              今天冥想了吗？
            </label>
            <div className="flex gap-4">
              <button
                onClick={() => setCompleted(true)}
                className={`flex-1 py-4 rounded-xl font-semibold transition-all ${
                  completed
                    ? 'bg-pink-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                ✅ 已完成
              </button>
              <button
                onClick={() => setCompleted(false)}
                className={`flex-1 py-4 rounded-xl font-semibold transition-all ${
                  !completed
                    ? 'bg-pink-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                ❌ 未完成
              </button>
            </div>
          </div>

          {/* 场景选择 */}
          {completed && (
            <>
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  冥想场景（可选）
                </label>
                <div className="grid grid-cols-3 gap-3">
                  {SCENE_OPTIONS.map((option) => (
                    <button
                      key={option.value}
                      onClick={() => setScene(option.value)}
                      className={`p-3 rounded-xl border-2 transition-all ${
                        scene === option.value
                          ? 'border-pink-500 bg-pink-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="text-2xl mb-1">{option.icon}</div>
                      <div className="text-xs font-medium">{option.label}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* 心情选择 */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  此刻的心情（可选）
                </label>
                <div className="grid grid-cols-3 gap-3">
                  {MOOD_OPTIONS.map((option) => (
                    <button
                      key={option.value}
                      onClick={() => setMood(option.value)}
                      className={`p-3 rounded-xl border-2 transition-all ${
                        mood === option.value
                          ? `border-pink-500 ${option.color}`
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="text-2xl mb-1">{option.icon}</div>
                      <div className="text-xs font-medium">{option.label}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* 保存按钮 */}
              <button
                onClick={handleSave}
                className="w-full py-4 bg-pink-600 text-white rounded-xl font-semibold hover:bg-pink-700 transition-colors"
              >
                ✨ 完成打卡
              </button>
            </>
          )}

          {!completed && (
            <div className="text-center py-8 text-gray-500">
              <Cloud className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p>选择"已完成"后，可以继续填写场景和心情</p>
            </div>
          )}
        </div>

        {/* 冥想好处 */}
        <div className="bg-gradient-to-r from-pink-500 to-indigo-600 rounded-2xl shadow-lg p-6 text-white">
          <div className="flex items-start gap-3">
            <div className="bg-white/20 p-2 rounded-lg">
              <Sparkles className="w-6 h-6" />
            </div>
            <div>
              <h3 className="font-semibold mb-1">💡 冥想的好处</h3>
              <p className="text-sm text-pink-100">
                每天 5 分钟冥想，皮质醇降低 15%。餐前正念可以减少 20% 过量进食，帮助你分辨"饿了"vs"馋了"。
              </p>
            </div>
          </div>
        </div>

      </main>
    </div>
  );
}
