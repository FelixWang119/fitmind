import React from 'react';
import { render } from '@testing-library/react';
import { describe, it, expect, jest } from '@jest/globals';
import Gamification from '../Gamification';

// Mock the API client
jest.mock('../../api/client', () => ({
  api: {
    getGamificationOverview: jest.fn(() => Promise.resolve({})),
    getPoints: jest.fn(() => Promise.resolve({})),
    getPointsHistory: jest.fn(() => Promise.resolve([])),
    getBadges: jest.fn(() => Promise.resolve([])),
    getAchievements: jest.fn(() => Promise.resolve([])),
    getChallenges: jest.fn(() => Promise.resolve([])),
    getStreaks: jest.fn(() => Promise.resolve({})),
    getLeaderboard: jest.fn(() => Promise.resolve([])),
    getDailyReward: jest.fn(() => Promise.resolve({})),
    claimDailyReward: jest.fn(() => Promise.resolve({})),
    getHealthScore: jest.fn(() => Promise.resolve({})),
    getScientificMetrics: jest.fn(() => Promise.resolve({})),
    getCorrelations: jest.fn(() => Promise.resolve({})),
  },
}));

// Mock lucide-react icons
jest.mock('lucide-react', () => ({
  Star: () => null,
  Target: () => null,
  TrendingUp: () => null,
  Clock: () => null,
  Flame: () => null,
  Medal: () => null,
  Crown: () => null,
  ChevronRight: () => null,
  Sparkles: () => null,
  Gift: () => null,
}));

describe('Gamification Component', () => {
  it('renders without crashing', () => {
    const { container } = render(<Gamification />);
    expect(container).toBeTruthy();
  });
});
