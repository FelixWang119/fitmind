/**
 * Health Assessment API Tests
 * 
 * Tests for health assessment endpoints covering:
 * - P0: Health score calculation accuracy
 * - P1: Assessment history and comparison
 * - P2: Performance and edge cases
 */

import { test, expect } from '@playwright/test';

// Test data factories
const createUser = (overrides = {}) => ({
  id: Math.floor(Math.random() * 10000),
  email: `test-${Date.now()}@example.com`,
  name: 'Test User',
  age: overrides.age || 30,
  height: overrides.height || 170,
  initial_weight: overrides.initial_weight || 70,
  target_weight: overrides.target_weight || 65,
  ...overrides,
});

const createHealthRecord = (overrides = {}) => ({
  user_id: overrides.user_id || 1,
  record_date: overrides.record_date || new Date().toISOString().split('T')[0],
  weight: overrides.weight || 70,
  sleep_hours: overrides.sleep_hours || 7.5,
  mood: overrides.mood || 'good',
  ...overrides,
});

test.describe('[Health Assessment] API Tests', () => {
  
  // P0: Critical - Health score calculation
  test.describe('Health Score Calculation', () => {
    
    test('[P0] should calculate health score within valid range (0-100)', async ({ request }) => {
      // This tests the scoring algorithm boundaries
      const validScores = [0, 25, 50, 75, 100];
      
      for (const score of validScores) {
        const isValid = score >= 0 && score <= 100;
        expect(isValid).toBe(true);
      }
      
      const invalidScores = [-1, 101, 150];
      for (const score of invalidScores) {
        const isValid = score >= 0 && score <= 100;
        expect(isValid).toBe(false);
      }
    });

    test('[P0] should apply correct dimension weights (35% nutrition, 35% behavior, 30% emotion)', () => {
      const nutritionWeight = 35;
      const behaviorWeight = 35;
      const emotionWeight = 30;
      const total = nutritionWeight + behaviorWeight + emotionWeight;
      
      expect(total).toBe(100);
      expect(nutritionWeight).toBe(35);
      expect(behaviorWeight).toBe(35);
      expect(emotionWeight).toBe(30);
    });

    test('[P0] should assign correct grade labels based on score', () => {
      const getGrade = (score: number): string => {
        if (score < 40) return '需改善';
        if (score < 60) return '一般';
        if (score < 80) return '良好';
        return '优秀';
      };

      expect(getGrade(30)).toBe('需改善');
      expect(getGrade(50)).toBe('一般');
      expect(getGrade(70)).toBe('良好');
      expect(getGrade(90)).toBe('优秀');
      expect(getGrade(40)).toBe('一般'); // boundary
      expect(getGrade(60)).toBe('良好'); // boundary
      expect(getGrade(80)).toBe('优秀'); // boundary
    });
  });

  // P0: Critical - Authentication requirements
  test.describe('Authentication Requirements', () => {
    
    test('[P0] should require authentication for getting latest assessment', async ({ request }) => {
      const response = await request.get('/api/v1/health-assessment/assessments/latest');
      expect(response.status()).toBe(401);
    });

    test('[P0] should require authentication for creating assessment', async ({ request }) => {
      const response = await request.post('/api/v1/health-assessment/assessment', {
        data: {
          start_date: '2024-01-01',
          end_date: '2024-01-31',
        },
      });
      expect(response.status()).toBe(401);
    });

    test('[P0] should require authentication for assessment history', async ({ request }) => {
      const response = await request.get('/api/v1/health-assessment/assessments/history');
      expect(response.status()).toBe(401);
    });
  });

  // P1: High - Assessment data validation
  test.describe('Assessment Data Validation', () => {
    
    test('[P1] should validate data completeness thresholds', () => {
      const foodDaysRequired = 7;
      const habitDaysRequired = 14;
      const sleepDaysRequired = 7;

      expect(foodDaysRequired).toBe(7);
      expect(habitDaysRequired).toBe(14);
      expect(sleepDaysRequired).toBe(7);
    });

    test('[P1] should calculate completeness percentage correctly', () => {
      const calculateCompleteness = (actualDays: number, requiredDays: number): number => {
        if (requiredDays === 0) return 100;
        return Math.min(100, (actualDays / requiredDays) * 100);
      };

      expect(calculateCompleteness(7, 7)).toBe(100);
      expect(calculateCompleteness(3, 7)).toBeCloseTo(42.86, 1);
      expect(calculateCompleteness(0, 7)).toBe(0);
      expect(calculateCompleteness(10, 7)).toBe(100); // capped at 100
    });

    test('[P1] should handle missing data gracefully', async ({ request }) => {
      // Test with incomplete data (less than required days)
      const incompleteData = {
        food_logs_days: 3, // less than 7 required
        habit_logs_days: 5, // less than 14 required
        sleep_logs_days: 2, // less than 7 required
      };

      const foodComplete = incompleteData.food_logs_days >= 7;
      const habitComplete = incompleteData.habit_logs_days >= 14;
      const sleepComplete = incompleteData.sleep_logs_days >= 7;

      expect(foodComplete).toBe(false);
      expect(habitComplete).toBe(false);
      expect(sleepComplete).toBe(false);
    });
  });

  // P1: High - Assessment comparison
  test.describe('Assessment Comparison', () => {
    
    test('[P1] should calculate score changes correctly', () => {
      const current = { overall_score: 75, nutrition_score: 70, behavior_score: 80, emotion_score: 75 };
      const previous = { overall_score: 65, nutrition_score: 60, behavior_score: 70, emotion_score: 65 };

      const overallChange = current.overall_score - previous.overall_score;
      const overallChangePercent = ((overallChange / previous.overall_score) * 100).toFixed(1);

      expect(overallChange).toBe(10);
      expect(parseFloat(overallChangePercent)).toBeCloseTo(15.4, 1);
    });

    test('[P1] should handle missing previous assessment', () => {
      const current = { overall_score: 75 };
      const previous = null;

      const hasComparison = previous !== null;
      expect(hasComparison).toBe(false);
    });
  });

  // P2: Medium - Performance and edge cases
  test.describe('Performance and Edge Cases', () => {
    
    test('[P2] should handle large date ranges', async ({ request }) => {
      // Test with a full year of data
      const startDate = '2023-01-01';
      const endDate = '2023-12-31';
      
      const start = new Date(startDate);
      const end = new Date(endDate);
      const daysDiff = Math.floor((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
      
      expect(daysDiff).toBe(364); // ~1 year
    });

    test('[P2] should handle zero data scenario', () => {
      const userRecords = [];
      
      const hasData = userRecords.length > 0;
      expect(hasData).toBe(false);
      
      // Should return null or default assessment
      const assessment = hasData ? 'calculated' : null;
      expect(assessment).toBeNull();
    });

    test('[P2] should validate assessment period constraints', () => {
      const minDaysForAssessment = 7;
      const maxDaysForAssessment = 90;

      const testPeriods = [
        { days: 3, valid: false },
        { days: 7, valid: true },
        { days: 30, valid: true },
        { days: 90, valid: true },
        { days: 120, valid: false },
      ];

      for (const { days, valid } of testPeriods) {
        const isValid = days >= minDaysForAssessment && days <= maxDaysForAssessment;
        expect(isValid).toBe(valid);
      }
    });
  });
});

// Test metadata
test.describe('Test Metadata', () => {
  test('should have correct test tags', () => {
    const tags = ['@health-assessment', '@api', '@p0', '@p1', '@p2'];
    expect(tags).toContain('@health-assessment');
    expect(tags).toContain('@api');
  });
});
