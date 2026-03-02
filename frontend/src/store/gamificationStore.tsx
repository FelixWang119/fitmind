/**
 * 游戏化系统 Hooks
 * 提供状态管理和数据获取逻辑
 */

import React from 'react';
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

// 类型定义
interface GamificationState {
  // 用户积分
  userPoints: number;
  // 当前等级
  currentLevel: number;
  // 徽章列表
  badges: BadgeInfo[];
  // 挑战列表
  challenges: Challenge[];
  // 积分获取记录
  pointsHistory: PointHistoryItem[];
  // 最后加载时间
  lastLoaded: Date | null;
}

interface BadgeInfo {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  category: 'streak' | 'achievement' | 'social' | 'health';
  unlocked: boolean;
  unlockDate?: string;
  points: number;
}

interface Challenge {
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

interface PointHistoryItem {
  id: string;
  points: number;
  reason: string;
  category: 'exercise' | 'nutrition' | 'challenge' | 'social' | 'streak';
  date: Date;
}

// 初始数据
const INITIAL_BADGES: BadgeInfo[] = [
  { id: '1', name: '连续7天打卡', description: '连续7天完成运动或饮食打卡', icon: <span className="text-xl">🔥</span>, category: 'streak', unlocked: true, unlockDate: '2024-01-15', points: 200 },
  { id: '2', name: '饮食记录专家', description: '完成100次饮食记录', icon: <span className="text-xl">📋</span>, category: 'achievement', unlocked: true, unlockDate: '2024-02-01', points: 300 },
  { id: '3', name: '运动狂人', description: '累计运动50小时', icon: <span className="text-xl">🏋️</span>, category: 'achievement', unlocked: false, points: 500 },
  { id: '4', name: '健康先锋', description: '在社区分享经验5次', icon: <span className="text-xl">💬</span>, category: 'social', unlocked: false, points: 150 },
  { id: '5', name: '体重目标达成', description: '达成月度减重目标', icon: <span className="text-xl">⚖️</span>, category: 'health', unlocked: true, unlockDate: '2024-01-20', points: 400 },
];

const INITIAL_CHALLENGES: Challenge[] = [
  { id: '1', title: '本周运动3小时', description: '这周至少完成3小时运动，健康生活从运动开始', type: 'weekly', target: 180, current: 120, rewardPoints: 300, unlocked: true, deadline: '2024-01-31' },
  { id: '2', title: '本周喝水100杯', description: '每天至少8杯水，本周累计100杯', type: 'weekly', target: 100, current: 45, rewardPoints: 150, unlocked: true, deadline: '2024-01-28' },
  { id: '3', title: '月度减重2公斤', description: '本月目标减重2公斤，健康减重稳步前行', type: 'monthly', target: 2, current: 1.2, rewardPoints: 500, unlocked: true, deadline: '2024-02-29' },
];

// Zustand Store
interface GamificationStore {
  // 状态
  userPoints: number;
  currentLevel: number;
  badges: BadgeInfo[];
  challenges: Challenge[];
  pointsHistory: PointHistoryItem[];
  lastLoaded: Date | null;
  
  // Action: 获取游戏化数据
  fetchGamificationData: () => Promise<void>;
  
  // Action: 更新积分
  addPoints: (points: number, reason: string, category: PointHistoryItem['category']) => void;
  
  // Action: 解锁徽章
  unlockBadge: (badgeId: string) => void;
  
  // Action: 更新挑战进度
  updateChallengeProgress: (challengeId: string, progress: number) => void;
  
  // Helpers
  calculateLevel: (points: number) => number;
  getPointsToNextLevel: (points: number) => number;
}

export const useGamificationStore = create<GamificationStore>()(
  persist(
    (set, get) => ({
      userPoints: 3200,
      currentLevel: 6,
      badges: INITIAL_BADGES,
      challenges: INITIAL_CHALLENGES,
      pointsHistory: [],
      lastLoaded: null,
      
      fetchGamificationData: async () => {
        // 模拟 API 调用
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // 这里的数据应该从后端获取
        // const response = await fetch('/api/gamification');
        // const data = await response.json();
        
        set({
          lastLoaded: new Date(),
          // 模拟获取到的最新数据
        });
      },
      
      addPoints: (points, reason, category) => {
        const { userPoints, pointsHistory } = get();
        const newHistoryItem: PointHistoryItem = {
          id: `point-${Date.now()}`,
          points,
          reason,
          category,
          date: new Date(),
        };
        
        set(state => ({
          userPoints: userPoints + points,
          pointsHistory: [newHistoryItem, ...pointsHistory],
          // 检查等级提升
          currentLevel: calculateLevel(userPoints + points),
        }));
      },
      
      unlockBadge: (badgeId) => {
        const { badges } = get();
        const badge = badges.find(b => b.id === badgeId);
        
        if (badge && !badge.unlocked) {
          set(state => ({
            badges: state.badges.map(b => 
              b.id === badgeId 
                ? { ...b, unlocked: true, unlockDate: new Date().toISOString().split('T')[0] } 
                : b
            ),
            userPoints: state.userPoints + badge.points,
            currentLevel: calculateLevel(state.userPoints + badge.points),
          }));
        }
      },
      
      updateChallengeProgress: (challengeId, progress) => {
        const { challenges, userPoints } = get();
        const challenge = challenges.find(c => c.id === challengeId);
        
        if (challenge) {
          const newCurrent = Math.min(progress, challenge.target);
          const progressPercentage = (newCurrent / challenge.target) * 100;
          
          // 检查是否完成挑战
          if (progressPercentage >= 100 && !challenge.unlocked) {
            set(state => ({
              challenges: state.challenges.map(c => 
                c.id === challengeId 
                  ? { ...c, unlocked: true, current: newCurrent } 
                  : c
              ),
              userPoints: userPoints + challenge.rewardPoints,
              currentLevel: calculateLevel(userPoints + challenge.rewardPoints),
            }));
          } else {
            set(state => ({
              challenges: state.challenges.map(c => 
                c.id === challengeId 
                  ? { ...c, current: newCurrent } 
                  : c
              ),
            }));
          }
        }
      },
      
      // Helpers
      calculateLevel: (points) => {
        if (points >= 5000) return 10;
        if (points >= 4000) return 9;
        if (points >= 3000) return 8;
        if (points >= 2000) return 7;
        if (points >= 1500) return 6;
        if (points >= 1000) return 5;
        if (points >= 600) return 4;
        if (points >= 300) return 3;
        if (points >= 100) return 2;
        return 1;
      },
      
      getPointsToNextLevel: (points) => {
        if (points >= 5000) return 0;
        if (points >= 4000) return 5000 - points;
        if (points >= 3000) return 4000 - points;
        if (points >= 2000) return 3000 - points;
        if (points >= 1500) return 2000 - points;
        if (points >= 1000) return 1500 - points;
        if (points >= 600) return 1000 - points;
        if (points >= 300) return 600 - points;
        if (points >= 100) return 300 - points;
        return 100 - points;
      },
    }),
    {
      name: 'gamification-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        userPoints: state.userPoints,
        currentLevel: state.currentLevel,
        badges: state.badges,
        challenges: state.challenges,
        pointsHistory: state.pointsHistory.slice(0, 50), // 只保留最近50条记录
        lastLoaded: state.lastLoaded,
      }),
    }
  )
);

// 独立的等级计算函数
export const calculateLevel = (points: number): number => {
  if (points >= 5000) return 10;
  if (points >= 4000) return 9;
  if (points >= 3000) return 8;
  if (points >= 2000) return 7;
  if (points >= 1500) return 6;
  if (points >= 1000) return 5;
  if (points >= 600) return 4;
  if (points >= 300) return 3;
  if (points >= 100) return 2;
  return 1;
};

// 导出 levelIcons
export const getLevelIcon = (level: number): React.ReactNode => {
  const icons = {
    1: <span className="text-xl">👶</span>,
    2: <span className="text-xl">🔍</span>,
    3: <span className="text-xl">🏃</span>,
    4: <span className="text-xl">🥗</span>,
    5: <span className="text-xl">金牌</span>,
    6: <span className="text-xl">银牌</span>,
    7: <span className="text-xl">铜牌</span>,
    8: <span className="text-xl">📢</span>,
    9: <span className="text-xl">🔥</span>,
    10: <span className="text-xl">👑</span>,
  };
  return icons[level as keyof typeof icons] || icons[1];
};

// 导出 levelColors
export const getLevelColor = (level: number): string => {
  const colors = {
    1: 'bg-gray-100 text-gray-600',
    2: 'bg-blue-100 text-blue-600',
    3: 'bg-purple-100 text-purple-600',
    4: 'bg-green-100 text-green-600',
    5: 'bg-yellow-100 text-yellow-600',
    6: 'bg-gray-200 text-gray-600',
    7: 'bg-orange-100 text-orange-600',
    8: 'bg-red-100 text-red-600',
    9: 'bg-indigo-100 text-indigo-600',
    10: 'bg-gradient-to-r from-yellow-400 via-red-500 to-pink-500 text-white',
  };
  return colors[level as keyof typeof colors] || colors[1];
};

// 导出 levelNames
export const getLevelName = (level: number): string => {
  const names = {
    1: '新手入门',
    2: '健康探索者',
    3: '运动达人',
    4: '营养专家',
    5: '金牌选手',
    6: '银牌选手',
    7: '铜牌选手',
    8: '健康大使',
    9: '健身传奇',
    10: '蜕变大师',
  };
  return names[level as keyof typeof names] || names[1];
};
