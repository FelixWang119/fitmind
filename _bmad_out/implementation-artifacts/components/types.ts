export interface WeightData {
  current: number;
  target: number;
  change: number;
  unit: string;
  progress: number;
  predictedDays: number;
}

export interface运动Data {
  current: {
    minutes: number;
    calories: number;
    workoutCount: number;
  };
  target: {
    minutes: number;
    calories: number;
    workoutCount: number;
  };
  unit: string;
  progress: number;
  trend: 'up' | 'down' | 'neutral';
}

export interface饮食Data {
  current: {
    calories: number;
    protein: number;
    carbs: number;
    fat: number;
  };
  target: {
    calories: number;
    protein: number;
    carbs: number;
    fat: number;
  };
  unit: string;
  progress: number;
  caloricBalance: number;
  balanceStatus: 'good' | 'warning' | 'danger';
}

export interface AIFeedbackData {
  type: 'positive' | 'improvement' | 'maintenance';
  icon: string;
  title: string;
  text: string;
}

export interface GoalTrackingData {
  weight: WeightData;
 运动:运动Data;
 饮食:饮食Data;
}
