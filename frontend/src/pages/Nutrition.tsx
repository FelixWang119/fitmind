import { useEffect, useState } from 'react';
import { api } from '../api/client';
import { Flame, Droplets, Wheat, Target } from 'lucide-react';

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

  useEffect(() => {
    loadNutritionData();
  }, []);

  const loadNutritionData = async () => {
    try {
      setLoading(true);
      const data = await api.getNutritionRecommendations();
      setRecommendations(data);
    } catch (error) {
      console.error('Failed to load nutrition data:', error);
    } finally {
      setLoading(false);
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
      <div>
        <h1 className="text-2xl font-bold text-gray-900">营养管理</h1>
        <p className="text-gray-600 mt-1">科学规划饮食，实现健康目标</p>
      </div>

      {recommendations && (
        <>
          {/* Calorie Targets */}
          <div className="bg-gradient-to-r from-green-600 to-green-700 rounded-2xl p-6 text-white">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
               <div className="text-center">
                 <Flame className="w-8 h-8 mx-auto mb-2" />
                 <p className="text-green-100 text-sm">目标卡路里</p>
                 <p className="text-2xl font-bold">{recommendations.calorie_targets?.target}</p>
               </div>
              <div className="text-center">
                <Target className="w-8 h-8 mx-auto mb-2" />
                <p className="text-green-100 text-sm">维持体重</p>
                <p className="text-2xl font-bold">{recommendations.calorie_targets?.maintenance}</p>
              </div>
               <div className="text-center">
                 <Flame className="w-8 h-8 mx-auto mb-2" />
                 <p className="text-green-100 text-sm">减重</p>
                 <p className="text-2xl font-bold">{recommendations.calorie_targets?.weight_loss}</p>
               </div>
              <div className="text-center">
                <Droplets className="w-8 h-8 mx-auto mb-2" />
                <p className="text-green-100 text-sm">饮水目标</p>
                <p className="text-2xl font-bold">{Math.round(recommendations.hydration_goal / 1000)}L</p>
              </div>
            </div>
          </div>

          {/* Macros */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">宏量营养素目标</h2>
            <div className="grid grid-cols-3 gap-4">
               <MacroCard
                icon={Flame}
                label="蛋白质"
                value={recommendations.macronutrients?.protein_g}
                unit="g"
                color="red"
              />
              <MacroCard
                icon={Wheat}
                label="碳水化合物"
                value={recommendations.macronutrients?.carb_g}
                unit="g"
                color="yellow"
              />
              <MacroCard
                icon={Droplets}
                label="脂肪"
                value={recommendations.macronutrients?.fat_g}
                unit="g"
                color="blue"
              />
            </div>
          </div>
        </>
      )}
    </div>
  );
}