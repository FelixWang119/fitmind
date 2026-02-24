import React from 'react';
import { ActivityCard } from './ActivityCard';
import { Dumbbell, Droplets, Flame, Calendar, Timer, CheckCircle } from 'lucide-react';

interface ExerciseData {
  total_duration_minutes: number;
  total_calories_burned: number;
  sessions_count: number;
  progress_percentage?: number;
  exercise_types?: string[];
}

interface NutritionData {
  total_calories: number;
  calories_consumed: number;
  calories_burned?: number;
  meals_count: number;
  remaining_calories?: number;
  progress_percentage?: number;
}

interface ActivitySectionProps {
  exerciseData?: ExerciseData;
  nutritionData?: NutritionData;
  onExerciseClick: () => void;
  onNutritionClick: () => void;
}

export const ActivitySection: React.FC<ActivitySectionProps> = ({
  exerciseData,
  nutritionData,
  onExerciseClick,
  onNutritionClick
}) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
      {/* 运动打卡卡片 */}
      <ActivityCard
        icon={<Dumbbell className="w-6 h-6 text-orange-600" />}
        title="运动打卡"
        stats={[
          { value: exerciseData?.total_duration_minutes || 0, unit: "分钟", label: "时长", color: "bg-orange-100" },
          { value: exerciseData?.total_calories_burned || 0, unit: "卡", label: "消耗", color: "bg-red-100" },
          { value: exerciseData?.sessions_count || 0, unit: "次", label: "打卡", color: "bg-blue-100" }
        ]}
        progress={exerciseData?.progress_percentage}
        progressLabel="目标进度"
        onClick={onExerciseClick}
        infoText="运动时长来源于您的运动打卡累计时长，消耗的卡路里为根据运动类型和时长估算得出"
      />

      {/* 饮食打卡卡片 */}
      <ActivityCard
        icon={<Droplets className="w-6 h-6 text-green-600" />}
        title="饮食打卡"
        stats={[
          { value: nutritionData?.calories_consumed || 0, unit: "卡", label: "已吃", color: "bg-green-100" },
          { value: nutritionData?.remaining_calories || 0, unit: "卡", label: "剩余", color: "bg-yellow-100" },
          { value: nutritionData?.meals_count || 0, unit: "餐", label: "记录", color: "bg-blue-100" }
        ]}
        progress={nutritionData?.progress_percentage}
        progressLabel="热量进度"
        onClick={onNutritionClick}
        infoText="摄入热量来源于您记录的每餐食物，剩余热量为您的热量目标与已摄入热量的差额"
      />
    </div>
  );
};
