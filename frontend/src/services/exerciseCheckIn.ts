import api from '@/api/client';

export interface ExerciseCheckIn {
  id: number;
  user_id: number;
  exercise_type: string;
  category: string;
  duration_minutes: number;
  intensity: 'low' | 'medium' | 'high';
  distance_km?: number;
  heart_rate_avg?: number;
  notes?: string;
  rating?: number;
  calories_burned: number;
  is_estimated: boolean;
  estimation_details?: {
    met_value: number;
    weight_kg: number;
    duration_hours: number;
    intensity_factor: number;
    formula: string;
  };
  started_at: string;
  created_at: string;
  updated_at?: string;
}

export interface ExerciseType {
  type: string;
  met_value: number;
  category: string;
}

export interface ExerciseDailySummary {
  date: string;
  total_duration_minutes: number;
  total_calories_burned: number;
  sessions_count: number;
  exercise_types: string[];
  average_heart_rate?: number;
  goal_duration?: number;
  goal_calories?: number;
  progress_percentage?: number;
}

export interface CreateExerciseCheckIn {
  exercise_type: string;
  category?: string;
  duration_minutes: number;
  intensity: 'low' | 'medium' | 'high';
  distance_km?: number;
  heart_rate_avg?: number;
  notes?: string;
  rating?: number;
  started_at?: string;
}

export interface ExerciseCheckInListParams {
  page?: number;
  limit?: number;
  start_date?: string;
  end_date?: string;
  exercise_type?: string;
}

export const exerciseCheckInApi = {
  /**
   * 创建运动打卡
   */
  async create(data: CreateExerciseCheckIn): Promise<ExerciseCheckIn> {
    return await api.createExerciseCheckIn(data);
  },

  /**
   * 获取打卡列表
   */
  async getList(params?: ExerciseCheckInListParams): Promise<ExerciseCheckIn[]> {
    return await api.getExerciseCheckIns(params);
  },

  /**
   * 获取单条记录
   */
  async getById(id: number): Promise<ExerciseCheckIn> {
    return await api.getExerciseCheckInById(id);
  },

  /**
   * 更新打卡记录
   */
  async update(id: number, data: Partial<CreateExerciseCheckIn>): Promise<ExerciseCheckIn> {
    return await api.updateExerciseCheckIn(id, data);
  },

  /**
   * 删除打卡记录
   */
  async delete(id: number): Promise<void> {
    await api.deleteExerciseCheckIn(id);
  },

  /**
   * 获取当日摘要
   */
  async getDailySummary(date?: string): Promise<ExerciseDailySummary> {
    return await api.getExerciseDailySummary(date);
  },

  /**
   * 获取运动类型列表
   */
  async getExerciseTypes(): Promise<ExerciseType[]> {
    return await api.getExerciseTypes();
  },

  /**
   * Dashboard 运动摘要
   */
  async getDashboardSummary(date?: string): Promise<ExerciseDailySummary> {
    return await api.getDashboardExerciseSummary(date);
  },
};
