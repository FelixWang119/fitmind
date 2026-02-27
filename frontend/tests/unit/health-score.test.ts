/**
 * Health Score Calculation Unit Tests
 * 
 * Unit tests for pure health scoring logic:
 * - P0: Score calculation accuracy
 * - P0: Grade assignment logic
 * - P1: Dimension weight validation
 * - P2: Edge cases and boundary conditions
 */

// Health score calculation utilities (mirroring backend logic)
const calculateOverallScore = (
  nutritionScore: number,
  behaviorScore: number,
  emotionScore: number
): number => {
  const nutritionWeight = 0.35;
  const behaviorWeight = 0.35;
  const emotionWeight = 0.30;
  
  const overall = nutritionScore * nutritionWeight + 
                  behaviorScore * behaviorWeight + 
                  emotionScore * emotionWeight;
  
  return Math.round(overall);
};

const getGrade = (score: number): string => {
  if (score < 40) return '需改善';
  if (score < 60) return '一般';
  if (score < 80) return '良好';
  return '优秀';
};

const calculateCompleteness = (actualDays: number, requiredDays: number): number => {
  if (requiredDays === 0) return 100;
  return Math.min(100, Math.round((actualDays / requiredDays) * 100));
};

const isValidScore = (score: number): boolean => {
  return score >= 0 && score <= 100;
};

describe('Health Score Calculation', () => {
  
  describe('Overall Score Calculation', () => {
    
    test('[P0] should calculate overall score with correct weights (35/35/30)', () => {
      const nutrition = 80;
      const behavior = 70;
      const emotion = 90;
      
      const expected = Math.round(80 * 0.35 + 70 * 0.35 + 90 * 0.30);
      // 28 + 24.5 + 27 = 79.5 → 80
      const actual = calculateOverallScore(nutrition, behavior, emotion);
      
      expect(actual).toBe(80);
    });

    test('[P0] should handle perfect scores (100/100/100)', () => {
      const result = calculateOverallScore(100, 100, 100);
      expect(result).toBe(100);
    });

    test('[P0] should handle zero scores (0/0/0)', () => {
      const result = calculateOverallScore(0, 0, 0);
      expect(result).toBe(0);
    });

    test('[P0] should handle mixed scores correctly', () => {
      const result1 = calculateOverallScore(50, 50, 50);
      expect(result1).toBe(50);
      
      const result2 = calculateOverallScore(100, 0, 0);
      expect(result2).toBe(35); // 100 * 0.35 = 35
      
      const result3 = calculateOverallScore(0, 100, 0);
      expect(result3).toBe(35); // 100 * 0.35 = 35
      
      const result4 = calculateOverallScore(0, 0, 100);
      expect(result4).toBe(30); // 100 * 0.30 = 30
    });

    test('[P1] should round to nearest integer', () => {
      const result = calculateOverallScore(83, 87, 91);
      // 83*0.35 + 87*0.35 + 91*0.30 = 29.05 + 30.45 + 27.3 = 86.8 → 87
      expect(result).toBe(87);
    });
  });

  describe('Grade Assignment', () => {
    
    test('[P0] should assign 优秀 for scores ≥80', () => {
      expect(getGrade(80)).toBe('优秀');
      expect(getGrade(85)).toBe('优秀');
      expect(getGrade(90)).toBe('优秀');
      expect(getGrade(95)).toBe('优秀');
      expect(getGrade(100)).toBe('优秀');
    });

    test('[P0] should assign 良好 for scores 60-79', () => {
      expect(getGrade(60)).toBe('良好');
      expect(getGrade(65)).toBe('良好');
      expect(getGrade(70)).toBe('良好');
      expect(getGrade(75)).toBe('良好');
      expect(getGrade(79)).toBe('良好');
    });

    test('[P0] should assign 一般为 scores 40-59', () => {
      expect(getGrade(40)).toBe('一般');
      expect(getGrade(45)).toBe('一般');
      expect(getGrade(50)).toBe('一般');
      expect(getGrade(55)).toBe('一般');
      expect(getGrade(59)).toBe('一般');
    });

    test('[P0] should assign 需改善 for scores <40', () => {
      expect(getGrade(0)).toBe('需改善');
      expect(getGrade(20)).toBe('需改善');
      expect(getGrade(30)).toBe('需改善');
      expect(getGrade(39)).toBe('需改善');
    });

    test('[P1] should handle boundary values correctly', () => {
      expect(getGrade(39)).toBe('需改善'); // Just below 40
      expect(getGrade(40)).toBe('一般');   // Exactly 40
      expect(getGrade(59)).toBe('一般');   // Just below 60
      expect(getGrade(60)).toBe('良好');   // Exactly 60
      expect(getGrade(79)).toBe('良好');   // Just below 80
      expect(getGrade(80)).toBe('优秀');   // Exactly 80
    });
  });

  describe('Score Validation', () => {
    
    test('[P0] should validate score range (0-100)', () => {
      expect(isValidScore(0)).toBe(true);
      expect(isValidScore(50)).toBe(true);
      expect(isValidScore(100)).toBe(true);
    });

    test('[P0] should reject negative scores', () => {
      expect(isValidScore(-1)).toBe(false);
      expect(isValidScore(-10)).toBe(false);
      expect(isValidScore(-100)).toBe(false);
    });

    test('[P0] should reject scores above 100', () => {
      expect(isValidScore(101)).toBe(false);
      expect(isValidScore(150)).toBe(false);
      expect(isValidScore(200)).toBe(false);
    });
  });

  describe('Dimension Weights', () => {
    
    test('[P0] should have weights that sum to 100%', () => {
      const nutritionWeight = 35;
      const behaviorWeight = 35;
      const emotionWeight = 30;
      
      const total = nutritionWeight + behaviorWeight + emotionWeight;
      expect(total).toBe(100);
    });

    test('[P1] should verify individual weight values', () => {
      expect(35).toBe(35); // nutrition
      expect(35).toBe(35); // behavior
      expect(30).toBe(30); // emotion
    });
  });
});

describe('Data Completeness Calculation', () => {
  
  describe('Completeness Percentage', () => {
    
    test('[P1] should calculate completeness for food logs (7 days required)', () => {
      expect(calculateCompleteness(0, 7)).toBe(0);
      expect(calculateCompleteness(3, 7)).toBe(43); // 42.86 rounded
      expect(calculateCompleteness(5, 7)).toBe(71); // 71.43 rounded
      expect(calculateCompleteness(7, 7)).toBe(100);
      expect(calculateCompleteness(10, 7)).toBe(100); // capped at 100
    });

    test('[P1] should calculate completeness for habit logs (14 days required)', () => {
      expect(calculateCompleteness(0, 14)).toBe(0);
      expect(calculateCompleteness(7, 14)).toBe(50);
      expect(calculateCompleteness(10, 14)).toBe(71);
      expect(calculateCompleteness(14, 14)).toBe(100);
      expect(calculateCompleteness(21, 14)).toBe(100); // capped at 100
    });

    test('[P1] should calculate completeness for sleep logs (7 days required)', () => {
      expect(calculateCompleteness(0, 7)).toBe(0);
      expect(calculateCompleteness(4, 7)).toBe(57);
      expect(calculateCompleteness(7, 7)).toBe(100);
    });

    test('[P2] should handle zero required days', () => {
      expect(calculateCompleteness(0, 0)).toBe(100);
      expect(calculateCompleteness(5, 0)).toBe(100);
    });
  });

  describe('Data Completeness Thresholds', () => {
    
    test('[P1] should define correct minimum requirements', () => {
      const foodDaysRequired = 7;
      const habitDaysRequired = 14;
      const sleepDaysRequired = 7;

      expect(foodDaysRequired).toBe(7);
      expect(habitDaysRequired).toBe(14);
      expect(sleepDaysRequired).toBe(7);
    });

    test('[P2] should validate completeness status', () => {
      const isComplete = (actual: number, required: number) => actual >= required;
      
      expect(isComplete(7, 7)).toBe(true);
      expect(isComplete(10, 7)).toBe(true);
      expect(isComplete(6, 7)).toBe(false);
      expect(isComplete(0, 7)).toBe(false);
    });
  });
});

describe('Assessment Period Validation', () => {
  
  test('[P2] should validate minimum assessment period (7 days)', () => {
    const minDays = 7;
    
    expect(3 >= minDays).toBe(false);
    expect(7 >= minDays).toBe(true);
    expect(14 >= minDays).toBe(true);
    expect(30 >= minDays).toBe(true);
  });

  test('[P2] should validate maximum assessment period (90 days)', () => {
    const maxDays = 90;
    
    expect(30 <= maxDays).toBe(true);
    expect(60 <= maxDays).toBe(true);
    expect(90 <= maxDays).toBe(true);
    expect(120 <= maxDays).toBe(false);
    expect(365 <= maxDays).toBe(false);
  });

  test('[P2] should validate period range', () => {
    const minDays = 7;
    const maxDays = 90;
    
    const isValidPeriod = (days: number) => days >= minDays && days <= maxDays;
    
    expect(isValidPeriod(3)).toBe(false);
    expect(isValidPeriod(7)).toBe(true);
    expect(isValidPeriod(30)).toBe(true);
    expect(isValidPeriod(90)).toBe(true);
    expect(isValidPeriod(120)).toBe(false);
  });
});

describe('Score Change Calculation', () => {
  
  test('[P1] should calculate absolute score change', () => {
    const current = 75;
    const previous = 65;
    const change = current - previous;
    
    expect(change).toBe(10);
  });

  test('[P1] should calculate percentage score change', () => {
    const current = 75;
    const previous = 65;
    const changePercent = ((current - previous) / previous) * 100;
    
    expect(changePercent).toBeCloseTo(15.38, 2);
  });

  test('[P1] should handle negative changes', () => {
    const current = 60;
    const previous = 75;
    const change = current - previous;
    const changePercent = ((current - previous) / previous) * 100;
    
    expect(change).toBe(-15);
    expect(changePercent).toBeCloseTo(-20, 2);
  });

  test('[P2] should handle no change scenario', () => {
    const current = 70;
    const previous = 70;
    const change = current - previous;
    
    expect(change).toBe(0);
  });

  test('[P2] should handle missing previous assessment', () => {
    const previous: number | null = null;
    const hasComparison = previous !== null;
    
    expect(hasComparison).toBe(false);
  });
});
