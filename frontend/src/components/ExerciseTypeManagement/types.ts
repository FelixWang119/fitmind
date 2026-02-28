// 类型定义
export interface ExerciseType {
  id: string;
  name: string;
  description: string;
  category: 'cardio' | 'strength' | 'flexibility' | 'balance' | 'mindfulness';
  metValue: number;
  isPublic: boolean;
  icon: string;
  createdAt: string;
  usageCount: number;
}

export interface MovementStatistics {
  totalMinutes: number;
  totalCalories: number;
  sessionCount: number;
  averageDuration: number;
}
