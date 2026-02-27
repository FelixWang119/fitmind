/**
 * Data Factories for Health Assessment Tests
 * 
 * Factory functions for generating test data using faker.
 * All factories support overrides for specific scenarios.
 */

import { faker } from '@faker-js/faker';

// User data factory
export const createUserData = (overrides = {}) => ({
  id: faker.number.int({ min: 1000, max: 9999 }),
  email: faker.internet.email(),
  name: faker.person.fullName(),
  age: faker.number.int({ min: 18, max: 80 }),
  height: faker.number.float({ min: 150, max: 200, fractionDigits: 1 }),
  initial_weight: faker.number.float({ min: 50, max: 120, fractionDigits: 1 }),
  target_weight: faker.number.float({ min: 45, max: 100, fractionDigits: 1 }),
  gender: faker.helpers.arrayElement(['male', 'female', 'other']),
  ...overrides,
});

// Health record factory
export const createHealthRecord = (overrides = {}) => ({
  user_id: overrides.user_id || faker.number.int({ min: 1000, max: 9999 }),
  record_date: faker.date.recent({ days: 30 }).toISOString().split('T')[0],
  weight: faker.number.float({ min: 50, max: 120, fractionDigits: 1 }),
  sleep_hours: faker.number.float({ min: 4, max: 10, fractionDigits: 1 }),
  mood: faker.helpers.arrayElement(['excellent', 'good', 'average', 'poor', 'terrible']),
  energy_level: faker.number.int({ min: 1, max: 10 }),
  stress_level: faker.number.int({ min: 1, max: 10 }),
  ...overrides,
});

// Nutrition log factory
export const createNutritionLog = (overrides = {}) => ({
  user_id: overrides.user_id || faker.number.int({ min: 1000, max: 9999 }),
  date: faker.date.recent({ days: 30 }).toISOString().split('T')[0],
  calories: faker.number.int({ min: 1000, max: 3500 }),
  protein: faker.number.int({ min: 50, max: 200 }),
  carbs: faker.number.int({ min: 100, max: 400 }),
  fat: faker.number.int({ min: 30, max: 150 }),
  fiber: faker.number.int({ min: 10, max: 50 }),
  ...overrides,
});

// Habit factory
export const createHabit = (overrides = {}) => ({
  user_id: overrides.user_id || faker.number.int({ min: 1000, max: 9999 }),
  name: faker.helpers.arrayElement([
    '晨跑',
    '健康饮食',
    '充足睡眠',
    '冥想',
    '阅读',
    '喝水',
  ]),
  category: faker.helpers.arrayElement(['exercise', 'nutrition', 'sleep', 'mindfulness', 'other']),
  frequency: faker.helpers.arrayElement(['daily', 'weekly', 'monthly']),
  target_value: faker.number.int({ min: 1, max: 10 }),
  is_active: faker.datatype.boolean({ probability: 0.8 }),
  ...overrides,
});

// Habit completion factory
export const createHabitCompletion = (overrides = {}) => ({
  habit_id: overrides.habit_id || faker.number.int({ min: 1000, max: 9999 }),
  completion_date: faker.date.recent({ days: 14 }).toISOString().split('T')[0],
  completed: faker.datatype.boolean({ probability: 0.7 }),
  notes: faker.lorem.sentence(),
  ...overrides,
});

// Emotion log factory
export const createEmotionLog = (overrides = {}) => ({
  user_id: overrides.user_id || faker.number.int({ min: 1000, max: 9999 }),
  timestamp: faker.date.recent({ days: 7 }).toISOString(),
  emotion: faker.helpers.arrayElement(['happy', 'sad', 'anxious', 'calm', 'excited', 'tired']),
  intensity: faker.number.int({ min: 1, max: 10 }),
  trigger: faker.lorem.word(),
  notes: faker.lorem.sentence(),
  ...overrides,
});

// Health assessment factory
export const createHealthAssessment = (overrides = {}) => ({
  user_id: overrides.user_id || faker.number.int({ min: 1000, max: 9999 }),
  assessment_date: faker.date.recent({ days: 30 }).toISOString().split('T')[0],
  overall_score: faker.number.int({ min: 30, max: 95 }),
  nutrition_score: faker.number.int({ min: 30, max: 95 }),
  behavior_score: faker.number.int({ min: 30, max: 95 }),
  emotion_score: faker.number.int({ min: 30, max: 95 }),
  overall_grade: faker.helpers.arrayElement(['优秀', '良好', '一般', '需改善']),
  ...overrides,
});

// Assessment suggestion factory
export const createAssessmentSuggestion = (overrides = {}) => ({
  category: faker.helpers.arrayElement(['nutrition', 'behavior', 'emotion', 'general']),
  content: faker.lorem.paragraph(),
  priority: faker.helpers.arrayElement(['high', 'medium', 'low']),
  ...overrides,
});

// Helper: Generate multiple records
export const createMultiple = <T>(factory: (overrides?: any) => T, count: number, baseOverrides = {}): T[] => {
  return Array.from({ length: count }, () => factory(baseOverrides));
};

// Helper: Generate date range of records
export const createDateRange = <T>(
  factory: (overrides?: any) => T,
  startDate: Date,
  endDate: Date,
  baseOverrides = {}
): T[] => {
  const records: T[] = [];
  const currentDate = new Date(startDate);

  while (currentDate <= endDate) {
    records.push(factory({
      date: currentDate.toISOString().split('T')[0],
      record_date: currentDate.toISOString().split('T')[0],
      ...baseOverrides,
    }));
    currentDate.setDate(currentDate.getDate() + 1);
  }

  return records;
};
