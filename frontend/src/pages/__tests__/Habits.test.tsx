import React from 'react';
import { render } from '@testing-library/react';
import { describe, it, expect, jest } from '@jest/globals';
import Habits from '../Habits';

// Mock the API client
jest.mock('../../api/client', () => ({
  api: {
    getHabits: jest.fn(() => Promise.resolve([])),
    createHabit: jest.fn(() => Promise.resolve({})),
    updateHabit: jest.fn(() => Promise.resolve({})),
    deleteHabit: jest.fn(() => Promise.resolve({})),
    completeHabit: jest.fn(() => Promise.resolve({})),
    getHabitTemplates: jest.fn(() => Promise.resolve([])),
    getHabitStats: jest.fn(() => Promise.resolve({})),
    getHabitStreakInfo: jest.fn(() => Promise.resolve({})),
  },
}));

// Mock lucide-react icons - provide simple null fallbacks
jest.mock('lucide-react', () => ({
  Plus: () => null,
  Check: () => null,
  Trash2: () => null,
  Edit: () => null,
  Flame: () => null,
  Target: () => null,
  Clock: () => null,
  X: () => null,
  Coffee: () => null,
  Dumbbell: () => null,
  Moon: () => null,
  Heart: () => null,
  Apple: () => null,
  Footprints: () => null,
  Calendar: () => null,
  Award: () => null,
  ChevronLeft: () => null,
  ChevronRight: () => null,
}));

// Mock react-hot-toast
jest.mock('react-hot-toast', () => ({
  __esModule: true,
  default: {
    success: jest.fn(),
    error: jest.fn(),
  },
  success: jest.fn(),
  error: jest.fn(),
}));

describe('Habits Component', () => {
  it('renders without crashing', () => {
    // Simple smoke test - just verify component can render
    const { container } = render(<Habits />);
    expect(container).toBeTruthy();
  });
});
