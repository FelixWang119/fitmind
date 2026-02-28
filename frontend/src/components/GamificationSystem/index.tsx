/**
 * 游戏化系统主组件
 * 包含积分系统、等级系统、徽章系统、挑战系统
 */

import React, { useState, useEffect } from 'react';
import { Tabs, Card, Progress, Badge, Skeleton, Empty } from 'antd';
import { 
  Trophy, 
  Star, 
  Award, 
  Challenge, 
  UserSwitch, 
  Coin, 
  Fire,
  Tooltip
} from 'lucide-react';
import { useAuthStore } from '../../../store/authStore';
import { GamificationStore, useGamificationStore } from '../../../store/gamificationStore';
import { formatDate } from '../../../utils/dateUtils';

// 类型定义
interface Level {
  level: number;
  name: string;
  minPoints: number;
  maxPoints: number;
  color: string;
  icon: React.ReactNode;
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

// 模拟数据
const MOCK_LEVELS: Level[] = [
  { level: 1, name: '新手入门', minPoints: 0, maxPoints: 99, color: 'bg-gray-100 text-gray-600', icon: <span className="text-xl">👶</span> },
  { level: 2, name: '健康探索者', minPoints: 100, maxPoints: 299, color: 'bg-blue-100 text-blue-600', icon: <span className="text-xl">🔍</span> },
  { level: 3, name: '运动达人', minPoints: 300, maxPoints: 599, color: 'bg-purple-100 text-purple-600', icon: <span className="text-xl">🏃</span> },
  { level: 4, name: '营养专家', minPoints: 600, maxPoints: 999, color: 'bg-green-100 text-green-600', icon: <span className="text-xl">🥗</span> },
  { level: 5, name: '金牌选手', minPoints: 1000, maxPoints: 1499, color: 'bg-yellow-100 text-yellow-600', icon: <span className="text-xl">金牌</span> },
  { level: 6, name: '银牌选手', minPoints: 1500, maxPoints: 1999, color: 'bg-gray-200 text-gray-600', icon: <span className="text-xl">银牌</span> },
  { level: 7, name: '铜牌选手', minPoints: 2000, maxPoints: 2999, color: 'bg-orange-100 text-orange-600', icon: <span className="text-xl">铜牌</span> },
  { level: 8, name: '健康大使', minPoints: 3000, maxPoints: 3999, color: 'bg-red-100 text-red-600', icon: <span className="text-xl">📢</span> },
  { level: 9, name: '健身传奇', minPoints: 4000, maxPoints: 4999, color: 'bg-indigo-100 text-indigo-600', icon: <span className="text-xl">🔥</span> },
  { level: 10, name: '蜕变大师', minPoints: 5000, maxPoints: Infinity, color: 'bg-gradient-to-r from-yellow-400 via-red-500 to-pink-500 text-white', icon: <span className="text-xl">👑</span> },
];

const MOCK_BADGES: BadgeInfo[] = [
  { id: '1', name: '连续7天打卡', description: '连续7天完成运动或饮食打卡', icon: <Fire className="w-5 h-5 text-orange-500" />, category: 'streak', unlocked: true, unlockDate: '2024-01-15', points: 200 },
  { id: '2', name: '饮食记录专家', description: '完成100次饮食记录', icon: <span className="text-xl">📋</span>, category: 'achievement', unlocked: true, unlockDate: '2024-02-01', points: 300 },
  { id: '3', name: '运动狂人', description: '累计运动50小时', icon: <span className="text-xl">🏋️</span>, category: 'achievement', unlocked: false, points: 500 },
  { id: '4', name: '健康先锋', description: '在社区分享经验5次', icon: <span className="text-xl">💬</span>, category: 'social', unlocked: false, points: 150 },
  { id: '5', name: '体重目标达成', description: '达成月度减重目标', icon: <span className="text-xl">⚖️</span>, category: 'health', unlocked: true, unlockDate: '2024-01-20', points: 400 },
  { id: '6', name: '早起鸟', description: '连续7天早起运动', icon: <span className="text-xl">🌞</span>, category: 'streak', unlocked: false, points: 250 },
];

const MOCK_CHALLENGES: Challenge[] = [
  { id: '1', title: '本周运动3小时', description: '这周至少完成3小时运动，健康生活从运动开始', type: 'weekly', target: 180, current: 120, rewardPoints: 300, unlocked: true, deadline: '2024-01-31' },
  { id: '2', title: '本周喝水100杯', description: '每天至少8杯水，本周累计100杯', type: 'weekly', target: 100, current: 45, rewardPoints: 150, unlocked: true, deadline: '2024-01-28' },
  { id: '3', title: '月度减重2公斤', description: '本月目标减重2公斤，健康减重稳步前行', type: 'monthly', target: 2, current: 1.2, rewardPoints: 500, unlocked: true, deadline: '2024-02-29' },
  { id: '4', title: '挑战10000积分', description: '本周积累10000积分，解锁新徽章', type: 'special', target: 10000, current: 7500, rewardPoints: 1000, unlocked: true, deadline: '2024-02-14' },
];

// 自定义组件
const LevelBadge = ({ level }: { level: number }) => {
  const currentLevel = MOCK_LEVELS.find(l => l.level === level) || MOCK_LEVELS[0];
  
  return (
    <div className={`flex items-center justify-center w-12 h-12 rounded-full ${currentLevel.color} shadow-md transition-all duration-300 hover:scale-110`}>
      {currentLevel.icon}
    </div>
  );
};

const BadgeCard = ({ badge, onClick }: { badge: BadgeInfo; onClick: () => void }) => {
  return (
    <div 
      onClick={onClick}
      className={`group relative p-4 rounded-xl border-2 transition-all duration-300 cursor-pointer ${
        badge.unlocked 
          ? 'border-green-200 bg-green-50 hover:border-green-300 hover:bg-green-100' 
          : 'border-gray-200 bg-gray-50 opacity-70 hover:opacity-100'
      }`}
    >
      <div className="flex flex-col items-center space-y-2">
        <div className={`w-16 h-16 rounded-full flex items-center justify-center transition-all duration-300 ${
          badge.unlocked 
            ? 'bg-white shadow-lg group-hover:shadow-xl' 
            : 'bg-gray-200'
        }`}>
          {badge.icon}
        </div>
        <div className="text-center">
          <h4 className={`font-bold ${badge.unlocked ? 'text-gray-800' : 'text-gray-500'}`}>
            {badge.name}
          </h4>
          <p className="text-xs text-gray-500 mt-1 line-clamp-1">{badge.description}</p>
        </div>
        {badge.unlocked && (
          <div className="mt-2">
            <Badge count={badge.points} showZero color="green" offset={[-5, -5]} size="small" />
          </div>
        )}
      </div>
    </div>
  );
};

const ChallengeCard = ({ challenge }: { challenge: Challenge }) => {
  const progressPercentage = Math.min((challenge.current / challenge.target) * 100, 100);
  const isSpecial = challenge.type === 'special';
  
  return (
    <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 transition-all duration-300 hover:shadow-xl hover:border-blue-200">
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center space-x-2">
          {isSpecial && (
            <div className="px-2 py-1 bg-gradient-to-r from-yellow-400 to-orange-500 text-white text-xs font-bold rounded-full">
             Special
            </div>
          )}
          <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs font-semibold rounded-full capitalize">
            {challenge.type === 'daily' ? '每日' : challenge.type === 'weekly' ? '每周' : '每月'}
          </span>
        </div>
        <div className="flex items-center text-yellow-600 font-bold">
          <Coin className="w-4 h-4 mr-1" />
          {challenge.rewardPoints}
        </div>
      </div>
      
      <h3 className="font-bold text-gray-800 mb-2">{challenge.title}</h3>
      <p className="text-gray-600 text-sm mb-4 line-clamp-2">{challenge.description}</p>
      
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">当前进度</span>
          <span className="font-semibold text-gray-800">
            {challenge.current} / {challenge.target} {challenge.type === 'special' ? '' : challenge.type === 'weekly' ? '分钟' : '公斤'}
          </span>
        </div>
        <div className="relative h-3 bg-gray-100 rounded-full overflow-hidden">
          <div 
            className={`absolute top-0 left-0 h-full rounded-full transition-all duration-1000 ${
              progressPercentage > 80 ? 'bg-gradient-to-r from-green-400 to-emerald-600' :
              progressPercentage > 50 ? 'bg-gradient-to-r from-blue-400 to-indigo-600' :
              'bg-gradient-to-r from-orange-400 to-red-500'
            }`}
            style={{ width: `${progressPercentage}%` }}
          ></div>
        </div>
        <div className="flex justify-between text-xs text-gray-500">
          <span>{Math.round(progressPercentage)}%</span>
          <span>{challenge.deadline && new Date(challenge.deadline).toLocaleDateString('zh-CN')}</span>
        </div>
      </div>
    </div>
  );
};

const calculateLevel = (points: number) => {
  const level = MOCK_LEVELS.find(l => points >= l.minPoints && points <= l.maxPoints);
  return level || MOCK_LEVELS[0];
};

// 主组件
export const GamificationSystem: React.FC = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isLoaded, setIsLoaded] = useState(false);
  
  // 使用状态管理
  const { user } = useAuthStore();
  const { 
    userPoints, 
    currentLevel, 
    badges, 
    challenges, 
    fetchGamificationData,
    unlockBadge 
  } = useGamificationStore();
  
  useEffect(() => {
    // 模拟数据获取
    const loadData = async () => {
      await fetchGamificationData();
      setIsLoaded(true);
    };
    loadData();
  }, [fetchGamificationData]);
  
  const currentLevelData = calculateLevel(userPoints);
  const nextLevel = MOCK_LEVELS.find(l => l.level === currentLevel + 1);
  const pointsToNextLevel = nextLevel ? nextLevel.minPoints - userPoints : 0;
  const levelProgress = nextLevel 
    ? ((userPoints - currentLevelData.minPoints) / (nextLevel.minPoints - currentLevelData.minPoints)) * 100
    : 100;
  
  if (!isLoaded) {
    return (
      <div className="p-8">
        <Skeleton active />
      </div>
    );
  }
  
  const DashboardTab = () => (
    <div className="space-y-8 animate-fade-in">
      {/* 等级展示 */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-700 rounded-3xl p-8 text-white shadow-2xl">
        <div className="flex flex-col md:flex-row items-center space-y-6 md:space-y-0 md:space-x-8">
          <div className="flex-shrink-0">
            <div className="w-24 h-24 rounded-full bg-white/10 backdrop-blur-sm flex items-center justify-center border-4 border-white/20 shadow-inner">
              <LevelBadge level={currentLevel} />
            </div>
          </div>
          <div className="flex-1 text-center md:text-left">
            <h2 className="text-3xl font-bold mb-2">等级 {currentLevel}</h2>
            <p className="text-xl opacity-90 mb-4">{currentLevelData.name}</p>
            
            <div className="space-y-2">
              <div className="flex justify-between text-sm opacity-80">
                <span>当前积分</span>
                <span className="font-bold text-yellow-300">{userPoints.toLocaleString()} 分</span>
              </div>
              <div className="relative h-4 bg-gray-600/50 rounded-full overflow-hidden">
                <div 
                  className="absolute top-0 left-0 h-full bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full transition-all duration-1000"
                  style={{ width: `${levelProgress}%` }}
                ></div>
              </div>
              <div className="flex justify-between text-xs opacity-60">
                <span>{currentLevelData.name}</span>
                <span>{nextLevel ? `${nextLevel.name} (${pointsToNextLevel}分)` : '已达到最高等级'}</span>
              </div>
            </div>
          </div>
          <div className="text-center space-y-4">
            <div className="px-6 py-3 bg-white/10 backdrop-blur-sm rounded-xl border border-white/20">
              <p className="text-sm opacity-70 mb-1">总积分排行</p>
              <p className="text-3xl font-bold">Top 15%</p>
            </div>
          </div>
        </div>
      </div>
      
      {/* 积分概览 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          { title: '本周积分', value: '850', icon: <Fire className="w-6 h-6 text-red-500" />, color: 'bg-red-50' },
          { title: '本月积分', value: '3,200', icon: <Calendar className="w-6 h-6 text-blue-500" />, color: 'bg-blue-50' },
          { title: '总积分', value: userPoints.toLocaleString(), icon: <Coin className="w-6 h-6 text-yellow-500" />, color: 'bg-yellow-50' },
        ].map((stat, index) => (
          <Card key={index} className="hover:shadow-lg transition-shadow duration-300">
            <div className="flex items-center space-x-4">
              <div className={`p-3 rounded-xl ${stat.color}`}>
                {stat.icon}
              </div>
              <div>
                <p className="text-gray-500 text-sm">{stat.title}</p>
                <p className="text-2xl font-bold text-gray-800">{stat.value}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>
      
      {/* 快速操作 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { title: '运动打卡', icon: <span className="text-2xl">🏃</span>, action: () => {} },
          { title: '饮食记录', icon: <span className="text-2xl">🥗</span>, action: () => {} },
          { title: '社区分享', icon: <span className="text-2xl">💬</span>, action: () => {} },
          { title: '完成挑战', icon: <span className="text-2xl">🏆</span>, action: () => {} },
        ].map((item, index) => (
          <Card 
            key={index} 
            onClick={item.action}
            className="cursor-pointer hover:border-blue-400 hover:shadow-md transition-all duration-300 group"
          >
            <div className="text-center">
              <div className="mb-3 transition-transform duration-300 group-hover:scale-125 group-hover:rotate-3">
                {item.icon}
              </div>
              <p className="font-medium text-gray-700">{item.title}</p>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
  
  const BadgesTab = () => (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-green-500 to-emerald-600 rounded-2xl p-6 text-white">
        <h3 className="text-xl font-bold mb-2">徽章成就墙</h3>
        <p className="opacity-90">解锁徽章，展示你的健康旅程成就</p>
        <div className="mt-4 flex items-center space-x-2">
          <div className="px-4 py-2 bg-white/20 rounded-lg backdrop-blur-sm">
            <span className="font-bold">{badges.filter(b => b.unlocked).length}</span>
            <span className="mx-2">/</span>
            <span>{badges.length}</span>
            <span className="ml-2 text-sm opacity-80">已解锁</span>
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {badges.map((badge) => (
          <BadgeCard key={badge.id} badge={badge} onClick={() => {}} />
        ))}
      </div>
    </div>
  );
  
  const ChallengesTab = () => (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-purple-500 to-indigo-600 rounded-2xl p-6 text-white">
        <h3 className="text-xl font-bold mb-2">挑战任务</h3>
        <p className="opacity-90">完成挑战获得额外积分和奖励</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {challenges.map((challenge) => (
          <ChallengeCard key={challenge.id} challenge={challenge} />
        ))}
      </div>
    </div>
  );
  
  const RoleSwitchTab = () => (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-teal-500 to-cyan-600 rounded-2xl p-6 text-white">
        <h3 className="text-xl font-bold mb-2">专业角色系统</h3>
        <p className="opacity-90">切换不同专业角度，获取个性化建议</p>
      </div>
      
      {[
        { 
          id: 'fitness', 
          name: '健身教练', 
          icon: <span className="text-3xl">💪</span>,
          description: '专注于运动计划和训练强度建议',
          activeTab: '运动计划'
        },
        { 
          id: 'nutrition', 
          name: '营养师', 
          icon: <span className="text-3xl">🥗</span>,
          description: '提供饮食计划和营养搭配建议',
          activeTab: '饮食计划'
        },
        { 
          id: 'psychology', 
          name: '心理顾问', 
          icon: <span className="text-3xl">🧠</span>,
          description: '关注心理健康和情绪管理建议',
          activeTab: '情绪日记'
        },
        { 
          id: 'medical', 
          name: '健康顾问', 
          icon: <span className="text-3xl">🏥</span>,
          description: '提供综合健康管理建议',
          activeTab: '健康报告'
        }
      ].map((role, index) => (
        <Card key={index} className="hover:shadow-lg transition-all duration-300 group">
          <div className="flex items-start space-x-4 p-4 group-hover:bg-gray-50 rounded-xl transition-colors">
            <div className="flex-shrink-0">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white shadow-lg">
                {role.icon}
              </div>
            </div>
            <div className="flex-1">
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="font-bold text-lg text-gray-800">{role.name}</h4>
                  <p className="text-sm text-gray-500 mt-1">{role.description}</p>
                </div>
                <div className="px-3 py-1 bg-green-100 text-green-700 text-xs font-bold rounded-full">
                  推荐角色
                </div>
              </div>
              <div className="mt-3 flex items-center text-sm">
                <span className="text-gray-500 mr-2">当前活跃:</span>
                <span className="font-semibold text-blue-600">{role.activeTab}</span>
              </div>
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
  
  return (
    <div className="p-4 md:p-8 max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800">🏆 游戏化中心</h1>
        <p className="text-gray-600 mt-2">探索你的健康旅程，解锁成就与奖励</p>
      </div>
      
      <div className="bg-white rounded-3xl shadow-xl overflow-hidden">
        <Tabs 
          activeKey={activeTab}
          onChange={setActiveTab}
          items={[
            {
              key: 'dashboard',
              label: '仪表盘',
              children: <DashboardTab />,
              icon: <Trophy className="w-4 h-4" />
            },
            {
              key: 'badges',
              label: '成就墙',
              children: <BadgesTab />,
              icon: <Award className="w-4 h-4" />
            },
            {
              key: 'challenges',
              label: '挑战任务',
              children: <ChallengesTab />,
              icon: <Challenge className="w-4 h-4" />
            },
            {
              key: 'roles',
              label: '专业角色',
              children: <RoleSwitchTab />,
              icon: <UserSwitch className="w-4 h-4" />
            }
          ]}
        />
      </div>
      
      {/* 积分获取指南 */}
      <div className="mt-8 bg-blue-50 rounded-2xl p-6">
        <h3 className="font-bold text-lg text-gray-800 mb-4">💡 积分获取指南</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { action: '每日打卡', points: '50', description: '完成运动或饮食打卡' },
            { action: '额外挑战', points: '100-500', description: '完成每周/每月挑战' },
            { action: '社区分享', points: '200', description: '分享健康经验或建议' },
            { action: '连续打卡', points: '100-500', description: '连续打卡天数奖励' },
          ].map((item, index) => (
            <div key={index} className="bg-white p-4 rounded-xl shadow-sm">
              <div className="flex justify-between items-center mb-2">
                <span className="font-semibold text-gray-700">{item.action}</span>
                <span className="text-yellow-600 font-bold">{item.points}</span>
              </div>
              <p className="text-sm text-gray-500">{item.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default GamificationSystem;
