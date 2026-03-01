import api from '@/api/client';

export interface Habit {
  id: number;
  user_id: number;
  name: string;
  category: string;
  frequency: 'daily' | 'weekly' | 'monthly';
  target_value?: number;
  target_unit?: string;
  streak_days: number;
  total_completions: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface HabitCompletion {
  id: number;
  habit_id: number;
  completion_date: string;
  actual_value?: number;
  notes?: string;
  mood_rating?: number;
  difficulty_rating?: number;
  created_at: string;
}

export interface HabitStats {
  total_habits: number;
  active_habits: number;
  completion_rate: number;
  total_completions: number;
  current_streak: number;
  category_stats: Record<string, number>;
  weekly_completions: number[];
}

export interface CreateHabit {
  name: string;
  category: string;
  frequency: 'daily' | 'weekly' | 'monthly';
  target_value?: number;
  target_unit?: string;
  is_active?: boolean;
}

const habitApi = {
  // 获取习惯列表
  async getHabits(): Promise<Habit[]> {
    const response = await api.client.get('/habits/');
    return response.data;
  },

  // 获取习惯统计
  async getStats(): Promise<HabitStats> {
    const response = await api.client.get('/habits/statistics');
    return response.data;
  },

  // 获取习惯完成记录
  async getCompletions(habitId: number, startDate?: string, endDate?: string): Promise<HabitCompletion[]> {
    const params: any = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    const response = await api.client.get(`/habits/${habitId}/completions`, { params });
    return response.data;
  },

  // 创建习惯
  async createHabit(habit: CreateHabit): Promise<Habit> {
    const response = await api.client.post('/habits/', habit);
    return response.data;
  },

  // 更新习惯
  async updateHabit(habitId: number, updates: Partial<CreateHabit>): Promise<Habit> {
    const response = await api.client.put(`/habits/${habitId}`, updates);
    return response.data;
  },

  // 删除习惯
  async deleteHabit(habitId: number): Promise<void> {
    await api.client.delete(`/habits/${habitId}`);
  },

  // 打卡习惯
  async completeHabit(habitId: number, data: { completion_date: string; actual_value?: number }): Promise<HabitCompletion> {
    const response = await api.client.post(`/habits/${habitId}/complete`, data);
    return response.data;
  },
};

export default habitApi;
