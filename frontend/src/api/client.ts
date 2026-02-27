import axios, { AxiosError, AxiosInstance, AxiosResponse } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Handle unauthorized
          localStorage.removeItem('token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth
  async login(email: string, password: string) {
    const params = new URLSearchParams();
    params.append('username', email);
    params.append('password', password);
    const response = await this.client.post('/auth/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  }

  async register(userData: any) {
    const response = await this.client.post('/auth/register', userData);
    return response.data;
  }

  async getCurrentUser() {
    const response = await this.client.get('/users/profile');
    return response.data;
  }

  async updateUserProfile(profileData: any) {
    const response = await this.client.put('/users/profile', profileData);
    return response.data;
  }

  // Dashboard
  async getDashboardOverview() {
    const response = await this.client.get('/dashboard/overview');
    return response.data;
  }

  async getQuickStats() {
    const response = await this.client.get('/dashboard/quick-stats');
    return response.data;
  }

  async getAiSuggestions() {
    const response = await this.client.get('/dashboard/ai-suggestions');
    return response.data;
  }

  async getTrends() {
    const response = await this.client.get('/dashboard/trends');
    return response.data;
  }

  // Health
  async getHealthRecords(startDate?: string, endDate?: string) {
    const params = startDate && endDate ? { start_date: startDate, end_date: endDate } : {};
    const response = await this.client.get('/health/records', { params });
    return response.data;
  }

  async createHealthRecord(data: any) {
    const response = await this.client.post('/health/records', data);
    return response.data;
  }

  // Habits
  async getHabits(activeOnly: boolean = true) {
    const response = await this.client.get('/habits/', { params: { active_only: activeOnly } });
    return response.data;
  }

  async createHabit(data: any) {
    const response = await this.client.post('/habits/', data);
    return response.data;
  }

  async getDailyChecklist(targetDate?: string) {
    const params = targetDate ? { target_date: targetDate } : {};
    const response = await this.client.get('/habits/daily-checklist', { params });
    return response.data;
  }

  async completeHabit(habitId: number, data: any) {
    const response = await this.client.post(`/habits/${habitId}/completions`, data);
    return response.data;
  }

  async updateHabit(habitId: number, data: any) {
    const response = await this.client.put(`/habits/${habitId}`, data);
    return response.data;
  }

  async deleteHabit(habitId: number) {
    const response = await this.client.delete(`/habits/${habitId}`);
    return response.data;
  }

  async getHabitStreakInfo(habitId: number) {
    const response = await this.client.get(`/habits/${habitId}/streak-info`);
    return response.data;
  }

  async getHabitCompletions(habitId: number, startDate?: string, endDate?: string) {
    const params: any = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    const response = await this.client.get(`/habits/${habitId}/completions`, { params });
    return response.data;
  }

  async getHabitStats() {
    const response = await this.client.get('/habits/statistics');
    return response.data;
  }

  async getHabitRecommendations() {
    const response = await this.client.get('/habits/templates');
    return response.data;
  }

  // Habit Stats (Story 4.2)
  async getHabitStatsOverview(period: string = 'weekly') {
    const response = await this.client.get('/habits/stats/overview', { params: { period } });
    return response.data;
  }

  async getCompletionRateStats(period: string = 'weekly') {
    const response = await this.client.get('/habits/stats/completion', { params: { period } });
    return response.data;
  }

  async getHabitDetailedStats(habitId: number) {
    const response = await this.client.get(`/habits/${habitId}/detailed-stats`);
    return response.data;
  }

  async getBehaviorPatterns() {
    const response = await this.client.get('/habits/stats/patterns');
    return response.data;
  }

  // Habit Goals
  async getHabitGoals(habitId?: number, activeOnly: boolean = false) {
    const params: any = { active_only: activeOnly };
    if (habitId) params.habit_id = habitId;
    const response = await this.client.get('/habits/goals', { params });
    return response.data;
  }

  async getHabitGoal(goalId: number) {
    const response = await this.client.get(`/habits/goals/${goalId}`);
    return response.data;
  }

  async createHabitGoal(data: any) {
    const response = await this.client.post('/habits/goals', data);
    return response.data;
  }

  async updateHabitGoal(goalId: number, data: any) {
    const response = await this.client.put(`/habits/goals/${goalId}`, data);
    return response.data;
  }

  async deleteHabitGoal(goalId: number) {
    const response = await this.client.delete(`/habits/goals/${goalId}`);
    return response.data;
  }

  // Nutrition
  async getNutritionRecommendations() {
    const response = await this.client.get('/nutrition/recommendations');
    return response.data;
  }

  async getCalorieTarget() {
    const response = await this.client.get('/nutrition/calorie-target');
    return response.data;
  }

  // Meals
  async getDailyMeals(date?: string) {
    const params = date ? { target_date: date } : {};
    const response = await this.client.get('/meals/daily-nutrition-summary', { params });
    return response.data;
  }

  // Meal Check-in (拍照识别打卡)
  async uploadMealPhoto(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await this.client.post('/meal-checkin/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async recalculateNutrition(items: any[]) {
    const response = await this.client.post('/meal-checkin/recalculate', { items });
    return response.data;
  }

  async confirmMealCheckin(data: any) {
    const response = await this.client.post('/meal-checkin/confirm', data);
    return response.data;
  }

  // Calorie Goal API
  async getCalorieGoal(date?: string) {
    const params = date ? { target_date: date } : {};
    const response = await this.client.get('/meal-checkin/calorie-goal', { params });
    return response.data;
  }

  async setCalorieGoal(data: any, date?: string) {
    const params = date ? { target_date: date } : {};
    const response = await this.client.post('/meal-checkin/calorie-goal', data, { params });
    return response.data;
  }

  async getDailyBalance(date?: string) {
    const params = date ? { target_date: date } : {};
    const response = await this.client.get('/meal-checkin/daily-balance', { params });
    return response.data;
  }

  async getFoodItems(skip: number = 0, limit: number = 100, category?: string, isCustom?: boolean) {
    const params: any = { skip, limit };
    if (category) params.category = category;
    if (isCustom !== undefined) params.is_custom = isCustom;
    const response = await this.client.get('/meals/food-items', { params });
    return response.data;
  }

  async createMeal(mealData: any) {
    const response = await this.client.post('/meals', mealData);
    return response.data;
  }

  async updateMeal(mealId: number, mealData: any) {
    const response = await this.client.put(`/meals/${mealId}`, mealData);
    return response.data;
  }

  async deleteMeal(mealId: number) {
    const response = await this.client.delete(`/meals/${mealId}`);
    return response.data;
  }

  async createFoodItem(foodData: any) {
    const response = await this.client.post('/meals/food-items', foodData);
    return response.data;
  }

  // Emotional Support
  async getEmotionalCheckIn() {
    const response = await this.client.get('/emotional-support/check-in');
    return response.data;
  }

  async recordEmotionalState(data: any) {
    const response = await this.client.post('/emotional-support/emotional-states', data);
    return response.data;
  }

  async getStressTrend(days: number = 7) {
    const response = await this.client.get('/emotional-support/stress-trend', { params: { days } });
    return response.data;
  }

  // Gamification
  async getGamificationOverview() {
    const response = await this.client.get('/gamification/overview');
    return response.data;
  }

  async getUserPoints() {
    const response = await this.client.get('/gamification/points');
    return response.data;
  }

  async getPointsHistory(limit: number = 50) {
    const response = await this.client.get('/gamification/points-history', {
      params: { limit },
    });
    return response.data;
  }

  async getLevelProgress() {
    const response = await this.client.get('/gamification/level');
    return response.data;
  }

  async getUserBadges(category?: string, limit: number = 50) {
    const params: any = { limit };
    if (category) params.category = category;
    const response = await this.client.get('/gamification/badges', { params });
    return response.data;
  }

  async checkAndAwardBadges() {
    const response = await this.client.post('/gamification/check-badges');
    return response.data;
  }

  async showcaseBadge(badgeId: string, order: number = 0) {
    const response = await this.client.post(`/gamification/badges/${badgeId}/showcase`, null, {
      params: { order },
    });
    return response.data;
  }

  async getUserAchievements(completedOnly: boolean = false) {
    const response = await this.client.get('/gamification/achievements', {
      params: { completed_only: completedOnly },
    });
    return response.data;
  }

  async getUserChallenges(status?: string) {
    const params: any = {};
    if (status) params.status = status;
    const response = await this.client.get('/gamification/challenges', { params });
    return response.data;
  }

  async createChallenge(challengeData: any) {
    const response = await this.client.post('/gamification/challenges', challengeData);
    return response.data;
  }

  async getUserStreaks() {
    const response = await this.client.get('/gamification/streaks');
    return response.data;
  }

  async getDailyReward() {
    const response = await this.client.get('/gamification/daily-reward');
    return response.data;
  }

  async claimDailyReward() {
    const response = await this.client.post('/gamification/claim-daily-reward');
    return response.data;
  }

  async getLeaderboard(type: string = 'points', period: string = 'weekly', limit: number = 20) {
    const response = await this.client.get('/gamification/leaderboard', {
      params: { type, period, limit },
    });
    return response.data;
  }

  async getGamificationStats() {
    const response = await this.client.get('/gamification/stats');
    return response.data;
  }

  // Health Score
  async getHealthScore() {
    const response = await this.client.get('/health-score/score');
    return response.data;
  }

  // Health Assessment (Story 6.1)
  async createHealthAssessment(startDate?: string, endDate?: string) {
    const params: any = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    const response = await this.client.post('/health-assessment/assessments', {}, { params });
    return response.data;
  }

  async getLatestAssessment() {
    const response = await this.client.get('/health-assessment/assessments/latest');
    return response.data;
  }

  async getAssessmentHistory(limit: number = 10) {
    const response = await this.client.get('/health-assessment/assessments/history', {
      params: { limit },
    });
    return response.data;
  }

  async getAssessmentById(id: number) {
    const response = await this.client.get(`/health-assessment/assessments/${id}`);
    return response.data;
  }

  async getAssessmentComparison(id: number) {
    const response = await this.client.get(`/health-assessment/assessments/${id}/comparison`);
    return response.data;
  }

  // Scientific Visualization
  async getScientificMetrics() {
    const response = await this.client.get('/scientific-visualization/metrics');
    return response.data;
  }

  async getCorrelationAnalysis() {
    const response = await this.client.get('/scientific-visualization/correlations');
    return response.data;
  }

  // Scientific Persona
  async getScientificReport(days: number = 30) {
    const response = await this.client.get('/scientific-persona/scientific-report', {
      params: { days },
    });
    return response.data;
  }

  async calculateBMI() {
    const response = await this.client.get('/scientific-persona/bmi');
    return response.data;
  }

  // User Experience
  async getHomeScreenData() {
    const response = await this.client.get('/ux/home-screen-data');
    return response.data;
  }

  // AI Chat
  async sendMessage(message: string, conversationId?: number) {
    const payload = {
      message,
      conversation_id: conversationId
    };
    const response = await this.client.post('/ai/chat', payload);
    return response.data;
  }

  // Role-based chat
  async sendRoleMessage(message: string, role: string = "general") {
    const payload = {
      message,
      context: { role }
    };
    // Add role as a query parameter
    const response = await this.client.post(`/ai/role-chat?ai_role=${role}`, payload);
    return response.data;
  }

  // Chat with role switching support
  async sendChatMessage(message: string, conversationId?: number, role?: string) {
    const payload: any = {
      message,
      conversation_id: conversationId
    };
    if (role) {
      payload.role = role;
    }
    const response = await this.client.post('/ai/chat', payload);
    return response.data;
  }

  // Switch role manually
  async switchRole(conversationId: number, targetRole: string) {
    const response = await this.client.post(`/ai/conversations/${conversationId}/switch-role`, {
      target_role: targetRole
    });
    return response.data;
  }

  // Get role history
  async getRoleHistory(conversationId: number) {
    const response = await this.client.get(`/ai/conversations/${conversationId}/role-history`);
    return response.data;
  }

  // Get conversation list (from /chat/conversations)
  async getConversations() {
    const response = await this.client.get('/chat/conversations');
    return response.data;
  }

  // Get messages from a conversation
  async getMessages(conversationId: number) {
    const response = await this.client.get(`/chat/conversations/${conversationId}/messages`);
    return response.data;
  }

  // Create new conversation
  async createConversation(title?: string) {
    const response = await this.client.post('/chat/conversations', { title });
    return response.data;
  }

  // Delete a conversation
  async deleteConversation(conversationId: number) {
    const response = await this.client.delete(`/chat/conversations/${conversationId}`);
    return response.data;
  }

  async getDailyTip() {
    const response = await this.client.get('/ux/daily-tip');
    return response.data;
  }

  async getRecommendedNextSteps() {
    const response = await this.client.get('/ux/recommended-next-steps');
    return response.data;
  }

  // Exercise Check-in
  async getExerciseCheckIns(params?: {
    page?: number;
    limit?: number;
    start_date?: string;
    end_date?: string;
    exercise_type?: string;
  }) {
    const response = await this.client.get('/exercise-checkin/', { params });
    return response.data;
  }

  async getExerciseCheckInById(id: number) {
    const response = await this.client.get(`/exercise-checkin/${id}`);
    return response.data;
  }

  async createExerciseCheckIn(data: any) {
    const response = await this.client.post('/exercise-checkin/', data);
    return response.data;
  }

  async updateExerciseCheckIn(id: number, data: any) {
    const response = await this.client.put(`/exercise-checkin/${id}`, data);
    return response.data;
  }

  async deleteExerciseCheckIn(id: number) {
    const response = await this.client.delete(`/exercise-checkin/${id}`);
    return response.data;
  }

  async getExerciseDailySummary(date?: string) {
    const params = date ? { date } : {};
    const response = await this.client.get('/exercise-checkin/daily-summary', { params });
    return response.data;
  }

  async getExerciseTypes() {
    const response = await this.client.get('/exercise-checkin/exercise-types');
    return response.data;
  }

  async getDashboardExerciseSummary(date?: string) {
    const params = date ? { date } : {};
    const response = await this.client.get('/dashboard/exercise-summary', { params });
    return response.data;
  }
}

export const api = new ApiClient();
export const apiClient = api;
export default api;