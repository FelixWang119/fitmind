/**
 * Goal API Service
 * Story 2.2: 目标创建与追踪
 */

import api from '@/api/client';

// Goal Types
export type GoalType = 'weight' | 'exercise' | 'diet' | 'habit';
export type GoalStatus = 'active' | 'paused' | 'completed' | 'cancelled';

export interface Goal {
  goal_id: number;
  user_id: number;
  goal_type: GoalType;
  current_value: number | null;
  target_value: number;
  unit: string;
  start_date: string;
  target_date: string | null;
  predicted_date: string | null;
  status: GoalStatus;
  created_at: string;
  updated_at: string;
  progress_percentage?: number;
}

export interface GoalCreate {
  goal_type: GoalType;
  current_value?: number;
  target_value: number;
  unit: string;
  target_date?: string;
}

export interface GoalUpdate {
  target_value?: number;
  target_date?: string;
  current_value?: number;
  status?: GoalStatus;
}

export interface GoalProgress {
  progress_id: number;
  goal_id: number;
  recorded_date: string;
  value: number;
  daily_target_met: boolean;
  streak_count: number;
}

export interface GoalProgressCreate {
  value: number;
  daily_target_met: boolean;
  recorded_date?: string;
}

export interface GoalRecommendation {
  goal_type: GoalType;
  recommendation: any;
  prediction?: any;
}

// API Functions
export const goalService = {
  /**
   * 获取所有目标推荐
   */
  getRecommendations: async (): Promise<any> => {
    const response = await api.client.get('/goals/recommendations');
    return response.data;
  },

  /**
   * 获取指定类型的目标推荐
   */
  getRecommendationByType: async (goalType: GoalType): Promise<GoalRecommendation> => {
    const response = await api.client.get(`/goals/recommendations/${goalType}`);
    return response.data;
  },

  /**
   * 创建目标
   */
  createGoal: async (goal: GoalCreate): Promise<Goal> => {
    const response = await api.client.post('/goals', goal);
    return response.data;
  },

  /**
   * 获取目标列表
   */
  getGoals: async (status?: GoalStatus, goalType?: GoalType): Promise<Goal[]> => {
    const params: Record<string, string> = {};
    if (status) params.status = status;
    if (goalType) params.goal_type = goalType;
    
    const response = await api.client.get('/goals', { params });
    return response.data;
  },

  /**
   * 获取目标详情
   */
  getGoal: async (goalId: number): Promise<Goal> => {
    const response = await api.client.get(`/goals/${goalId}`);
    return response.data;
  },

  /**
   * 更新目标
   */
  updateGoal: async (goalId: number, goal: GoalUpdate): Promise<Goal> => {
    const response = await api.client.patch(`/goals/${goalId}`, goal);
    return response.data;
  },

  /**
   * 删除目标
   */
  deleteGoal: async (goalId: number): Promise<void> => {
    await api.client.delete(`/goals/${goalId}`);
  },

  /**
   * 记录进度
   */
  recordProgress: async (goalId: number, progress: GoalProgressCreate): Promise<GoalProgress> => {
    const response = await api.client.post(`/goals/${goalId}/progress`, progress);
    return response.data;
  },

  /**
   * 获取目标进度历史
   */
  getGoalProgress: async (goalId: number, days: number = 30): Promise<GoalProgress[]> => {
    const response = await api.client.get(`/goals/${goalId}/progress`, { params: { days } });
    return response.data;
  },

  /**
   * 更新目标状态
   */
  updateGoalStatus: async (goalId: number, status: GoalStatus): Promise<Goal> => {
    const response = await api.client.patch(`/goals/${goalId}/status?new_status=${status}`, {});
    return response.data;
  },

  /**
   * 获取目标历史
   */
  getGoalHistory: async (goalId: number): Promise<any[]> => {
    const response = await api.client.get(`/goals/${goalId}/history`);
    return response.data;
  },
};

// Utility Functions
export const getGoalTypeLabel = (type: GoalType): string => {
  const labels: Record<GoalType, string> = {
    weight: '体重',
    exercise: '运动',
    diet: '饮食',
    habit: '习惯',
  };
  return labels[type] || type;
};

export const getGoalTypeIcon = (type: GoalType): string => {
  const icons: Record<GoalType, string> = {
    weight: '⚖️',
    exercise: '🏃',
    diet: '🍽️',
    habit: '💪',
  };
  return icons[type] || '🎯';
};

export const getGoalStatusLabel = (status: GoalStatus): string => {
  const labels: Record<GoalStatus, string> = {
    active: '进行中',
    paused: '已暂停',
    completed: '已完成',
    cancelled: '已取消',
  };
  return labels[status] || status;
};

export const getStatusColor = (status: GoalStatus): string => {
  const colors: Record<GoalStatus, string> = {
    active: '#4CAF50',
    paused: '#FF9800',
    completed: '#2196F3',
    cancelled: '#9E9E9E',
  };
  return colors[status] || '#9E9E9E';
};

export const formatGoalValue = (value: number | null, unit: string): string => {
  if (value === null) return '--';
  
  switch (unit) {
    case 'kg':
      return `${(value / 1000).toFixed(1)} kg`;
    case 'g':
      return `${value} g`;
    case '步':
      return `${value.toLocaleString()} 步`;
    case 'kcal':
      return `${value} kcal`;
    case 'ml':
      return `${value} ml`;
    case '小时':
      return `${value} 小时`;
    default:
      return `${value} ${unit}`;
  }
};

export const calculateProgress = (
  currentValue: number | null,
  targetValue: number,
  goalType: GoalType
): number => {
  if (currentValue === null) return 0;
  
  if (goalType === 'weight' || goalType === 'diet') {
    // For weight/diet (decreasing), progress is inverse
    // This is simplified - should track start value for accurate calculation
    return Math.min(100, Math.max(0, (1 - (currentValue / targetValue)) * 100));
  } else {
    // For exercise/habit (increasing)
    return Math.min(100, (currentValue / targetValue) * 100);
  }
};
