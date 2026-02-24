import { useEffect, useState } from 'react';
import { api } from '../api/client';
import { Flame, Target, Droplets, Info, HelpCircle } from 'lucide-react';

function MacroCard({ icon: Icon, label, value, unit, color }: any) {
  const colorClasses: Record<string, string> = {
    red: 'bg-red-50 text-red-600',
    yellow: 'bg-yellow-50 text-yellow-600',
    blue: 'bg-blue-50 text-blue-600',
  };

  return (
    <div className={`${colorClasses[color]} rounded-xl p-4 text-center`}>
      <Icon className="w-8 h-8 mx-auto mb-2" />
      <p className="text-sm opacity-80">{label}</p>
      <p className="text-2xl font-bold">
        {value} <span className="text-sm">{unit}</span>
      </p>
    </div>
  );
}

export default function Nutrition() {
  const [recommendations, setRecommendations] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showInfoModal, setShowInfoModal] = useState(false);

  useEffect(() => {
    loadNutritionData();
  }, []);

  const loadNutritionData = async () => {
    try {
      setLoading(true);
      setError(null); // Reset error when starting to fetch
      const data = await api.getNutritionRecommendations();
      setRecommendations(data);
    } catch (error: any) {
      console.error('Failed to load nutrition data:', error);
      setError(error.message || '获取营养推荐数据失败');
      setRecommendations(null);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !recommendations) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">营养管理</h1>
        <p className="text-gray-600 mt-1">科学规划饮食，实现健康目标</p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-2xl p-4">
          <div className="flex items-start gap-3">
            <svg className="w-6 h-6 text-red-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <h3 className="font-medium text-red-800">加载数据失败</h3>
              <p className="text-sm text-red-600 mt-1">{error}</p>
              <button
                onClick={loadNutritionData}
                className="mt-2 px-3 py-1 bg-red-100 text-red-700 rounded-lg text-sm hover:bg-red-200 transition-colors"
              >
                重试
              </button>
            </div>
          </div>
        </div>
      )}

      {recommendations && (
        <>
          {/* Daily Calorie Target - Simplified Design */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-2xl p-6 text-white shadow-lg">
            <div className="flex items-start justify-between mb-4">
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-xl font-semibold">今日目标热量</h2>
                  <button
                    onClick={() => setShowInfoModal(true)}
                    className="p-1 hover:bg-white/20 rounded-full transition-colors"
                    title="这个值是怎么来的？"
                  >
                    <Info className="w-5 h-5 text-blue-100" />
                  </button>
                </div>
                <p className="text-blue-100 text-sm mt-1">
                  建议每天摄入 {(recommendations.calorie_targets?.target || 0).toLocaleString()} 千卡
                </p>
              </div>
            </div>

            <div className="flex items-center justify-between mb-6">
              <div className="text-center">
                <div className="text-5xl font-bold mb-2">{(recommendations.calorie_targets?.target || 0).toLocaleString()}</div>
                <div className="text-sm text-blue-100">千卡/天</div>
              </div>
            </div>

            {/* Info Card */}
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
                  <Target className="w-4 h-4 text-blue-100" />
                </div>
                <h3 className="font-semibold text-sm">目标计算依据</h3>
              </div>
              
              <div className="text-xs text-blue-50 space-y-2">
                <p>• <strong>基础代谢率 (BMR):</strong> {recommendations.calorie_targets?.maintenance?.toLocaleString()} 千卡</p>
                <p>• <strong>活动水平:</strong> {recommendations.user_activity_level || '中等活动'}</p>
                <p>• <strong>目标:</strong> {recommendations.calorie_targets?.weight_difference && recommendations.calorie_targets?.weight_difference < 0 ? '增重' : '减重'} {Math.abs(recommendations.calorie_targets?.weight_difference || 0)}kg</p>
              </div>
            </div>
          </div>

          {/* Macro Targets */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">宏量营养素目标</h2>
            <div className="grid grid-cols-3 gap-4">
               <MacroCard
                 icon={Flame}
                 label="蛋白质"
                 value={recommendations.macronutrients?.protein_g || 0}
                 unit="g"
                 color="red"
               />
               <MacroCard
                 icon={Target}
                 label="碳水化合物"
                 value={recommendations.macronutrients?.carb_g || 0}
                 unit="g"
                 color="yellow"
               />
               <MacroCard
                 icon={Droplets}
                 label="脂肪"
                 value={recommendations.macronutrients?.fat_g || 0}
                 unit="g"
                 color="blue"
               />
            </div>
          </div>

          {/* Hydration Goal */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
                  <Droplets className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">饮水目标</h3>
                  <p className="text-sm text-gray-500">保持身体水分平衡</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold text-blue-600">{Math.round((recommendations.hydration_goal || 0) / 1000)}L</p>
                <p className="text-sm text-gray-500">≈ {Math.round((recommendations.hydration_goal || 0) / 240)}杯水</p>
              </div>
            </div>
          </div>
         </>
      )}

      {!recommendations && !loading && error && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8 text-center">
          <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
            <Info className="w-8 h-8 text-red-500" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-1">数据加载失败</h3>
          <p className="text-gray-500 mb-4">{error}</p>
          <button
            onClick={loadNutritionData}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            重试加载
          </button>
        </div>
      )}

      {/* Info Modal */}
      {showInfoModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl w-full max-w-md">
            <div className="p-6 border-b border-gray-200 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">热量目标是怎么计算的？</h2>
              <button 
                onClick={() => setShowInfoModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="p-6 space-y-4">
              <div className="bg-blue-50 rounded-xl p-4">
                <h3 className="font-semibold text-blue-900 mb-2">🎯 计算原理</h3>
                <p className="text-sm text-blue-800 mb-2">
                  我们使用国际标准的 <strong>Mifflin-St Jeor 公式</strong> 计算您的基础代谢率 (BMR)，
                  然后根据您的活动水平和体重目标计算出每日建议摄入热量。
                </p>
                <p className="text-xs text-blue-600 mt-2">
                  目标热量 = BMR × 活动系数 ± 热量赤字/盈余
                </p>
              </div>

              <div className="space-y-3">
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                    <span className="text-green-700 font-bold text-xs">1</span>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">基础代谢率 (BMR)</h4>
                    <p className="text-sm text-gray-600 mt-1">
                   您的身体在完全休息状态下每天消耗的热量。根据您的体重 {(recommendations.user_weight === undefined || recommendations.user_weight === null ? 70 : recommendations.user_weight)}kg、
                   身高 {(recommendations.user_height === undefined || recommendations.user_height === null ? 170 : recommendations.user_height)}cm、年龄 {(recommendations.user_age === undefined || recommendations.user_age === null ? 30 : recommendations.user_age)} 岁计算得出。
                </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                    <span className="text-blue-700 font-bold text-xs">2</span>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">每日总消耗 (TDEE)</h4>
                    <p className="text-sm text-gray-600 mt-1">
                      BMR × 活动水平系数。考虑了您的日常活动，得到您每天实际消耗的总热量。
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0">
                    <span className="text-purple-700 font-bold text-xs">3</span>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">调整目标热量</h4>
                    <p className="text-sm text-gray-600 mt-1">
                   当前 {(recommendations.user_current_weight === undefined || recommendations.user_current_weight === null ? 70 : recommendations.user_current_weight)}kg → 目标 {(recommendations.user_target_weight === undefined || recommendations.user_target_weight === null ? 65 : recommendations.user_target_weight)}kg
                    </p>
                    <p className="text-sm text-gray-600 mt-1">
                      • 减重：TDEE - 300~500 千卡（健康减重速度 0.5~1kg/周）
                      <br/>
                      • 增重：TDEE + 200~300 千卡
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-amber-50 rounded-xl p-4 border border-amber-200">
                <div className="flex items-center gap-2 mb-2">
                  <HelpCircle className="w-5 h-5 text-amber-500" />
                  <h4 className="font-medium text-amber-900">温馨提示</h4>
                </div>
                <p className="text-sm text-amber-800">
                  这个目标值是一个参考值。实际执行时，请根据您的身体反应灵活调整。
                  如果感觉饥饿或疲惫，可以适当增加 100~200 千卡；
                  如果体重变化过快或过慢，也可以相应调整。
                </p>
              </div>

              <div className="pt-4">
                <button
                  onClick={() => setShowInfoModal(false)}
                  className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  知道了
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
