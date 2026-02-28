// 类型定义文件
// Gamification System TYPES

export interface Level {
  level: number;
  name: string;
  minPoints: number;
  maxPoints: number;
  color: string;
  icon: React.ReactNode;
}

export interface BadgeInfo {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  category: 'streak' | 'achievement' | 'social' | 'health';
  unlocked: boolean;
  unlockDate?: string;
  points: number;
}

export interface Challenge {
  id: string;
  title: string;
  description: string;
  type: 'daily' | 'weekly' | 'monthly' | 'special';
  target: number;
  current: number;
  rewardPoints: number;
  unlocked: boolean;
  deadline?: string;
}

export interface Role {
  id: string;
  name: string;
  icon: React.ReactNode;
  description: string;
  activeTab: string;
}
