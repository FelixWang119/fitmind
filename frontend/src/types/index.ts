// User Types
export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  age?: number;
  gender?: string;
  height?: number;
  initial_weight?: number;
  target_weight?: number;
  activity_level?: string;
  dietary_preferences?: string;
  created_at: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

// Health Types
export interface HealthRecord {
  id: number;
  user_id: number;
  record_date: string;
  weight?: number;
  body_fat?: number;
  bmi?: number;
  daily_calories?: number;
  steps?: number;
  water_ml?: number;
  notes?: string;
}

// Habit Types
export interface Habit {
  id: number;
  user_id: number;
  name: string;
  description?: string;
  category: string;
  frequency: 'daily' | 'weekly' | 'monthly';
  target_value?: number;
  target_unit?: string;
  streak_days: number;
  total_completions: number;
  is_active: boolean;
}

export interface HabitCompletion {
  id: number;
  habit_id: number;
  completion_date: string;
  actual_value?: number;
  notes?: string;
}

// Nutrition Types
export interface NutritionRecommendation {
  calorie_targets: {
    maintenance: number;
    target: number;
    weight_loss: number;
    weight_gain: number;
  };
  macronutrients: {
    protein_g: number;
    fat_g: number;
    carb_g: number;
  };
  hydration_goal: number;
}

// Emotional Support Types
export interface EmotionalState {
  id: number;
  emotion_type: string;
  intensity: number;
  description?: string;
  recorded_at: string;
}

export interface StressLevel {
  id: number;
  stress_level: number;
  recorded_at: string;
}

// Gamification Types
export interface PointsBreakdown {
  nutrition_points: number;
  habit_points: number;
  emotional_points: number;
  login_points: number;
  achievement_points: number;
}

export interface UserPoints {
  id: number;
  user_id: number;
  total_points: number;
  current_points: number;
  lifetime_points: number;
  breakdown: PointsBreakdown;
  last_updated?: string;
  created_at: string;
}

export interface LevelProgress {
  current_level: number;
  current_title: string;
  experience_points: number;
  points_to_next_level: number;
  progress_percentage: number;
  next_level_title?: string;
}

export interface Badge {
  id: number;
  user_id: number;
  badge_id: string;
  badge_name: string;
  badge_description: string;
  badge_category: string;
  badge_level: string;
  badge_icon: string;
  earned_at: string;
  earned_criteria?: string;
  progress_data?: Record<string, any>;
  is_showcased: boolean;
  showcase_order: number;
  created_at: string;
}

export interface Achievement {
  id: number;
  user_id: number;
  achievement_id: string;
  achievement_name: string;
  achievement_description?: string;
  achievement_category?: string;
  target_value: number;
  current_value: number;
  progress_percentage: number;
  is_completed: boolean;
  completed_at?: string;
  points_reward: number;
  badge_reward?: string;
  created_at: string;
  updated_at?: string;
}

export interface Challenge {
  id: number;
  user_id: number;
  challenge_id: string;
  challenge_name: string;
  challenge_description?: string;
  challenge_type?: string;
  start_date: string;
  end_date: string;
  duration_days: number;
  target_metric: string;
  target_value: number;
  current_value: number;
  status: string;
  completed_at?: string;
  points_reward: number;
  badge_reward?: string;
  created_at: string;
  updated_at?: string;
}

export interface StreakRecord {
  id: number;
  user_id: number;
  streak_type: string;
  streak_name: string;
  current_streak: number;
  longest_streak: number;
  streak_start_date?: string;
  last_activity_date?: string;
  milestones_reached: number[];
  created_at: string;
  updated_at?: string;
}

export interface GamificationStats {
  total_badges: number;
  total_points: number;
  current_level: number;
  completed_achievements: number;
  active_challenges: number;
  longest_streak: number;
}

export interface GamificationOverview {
  user_points: UserPoints;
  user_level: LevelProgress;
  recent_badges: Badge[];
  active_achievements: Achievement[];
  active_challenges: Challenge[];
  streaks: StreakRecord[];
  gamification_stats: GamificationStats;
}

export interface PointsEarned {
  points: number;
  reason: string;
  new_total: number;
  level_up: boolean;
  new_level?: number;
}

export interface BadgeUnlocked {
  badge: Badge;
  points_reward: number;
  message: string;
}

export interface PointsTransaction {
  id: number;
  user_id: number;
  points_amount: number;
  transaction_type: string;
  description?: string;
  reference_id?: string;
  reference_type?: string;
  created_at: string;
}

export interface DailyReward {
  day: number;
  points: number;
  base_points: number;
  streak_bonus: number;
  bonus?: string;
  claimed: boolean;
}

// Health Score Types
export interface HealthScore {
  overall_score: number;
  weight_score: number;
  nutrition_score: number;
  exercise_score: number;
  habit_score: number;
  emotional_score: number;
  trend: string;
  insights: string[];
  recommendations: string[];
}

// Scientific Quantification Types
export interface ScientificMetric {
  name: string;
  value: number;
  unit: string;
  normal_range?: { min: number; max: number };
  trend: string;
  percentile?: number;
  z_score?: number;
}

export interface CorrelationAnalysis {
  metric1: string;
  metric2: string;
  correlation_coefficient: number;
  p_value: number;
  significance: string;
  interpretation: string;
}

// Dashboard Types
export interface DashboardOverview {
  user_info: {
    name: string;
    weight_progress: any;
  };
  today_todos: {
    completed_count: number;
    total_count: number;
    completion_percentage: number;
    todos: any[];
  };
  motivational_message: {
    message: string;
    type: string;
  };
  health_trends: any;
  habit_stats: any;
  nutrition_overview: any;
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}
