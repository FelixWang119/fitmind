// 类型定义
export interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  category: 'streak' | 'quantity' | 'quality' | 'milestone' | 'special';
  points: number;
  tier: 'bronze' | 'silver' | 'gold' | 'diamond';
  current: number;
  target: number;
  unlocked: boolean;
  unlockDate?: string;
}
