import React, { useState, useEffect } from 'react';
import { 
  Trophy, 
  Star, 
  Award, 
  Lock, 
  Unlock, 
  Zap, 
  Heart, 
  Smile, 
  Calendar,
  CheckCircle,
  Clap,
  Flame
} from 'lucide-react';
import { Card, Button, Badge } from '@/components/ui';

/**
 * 成就墙卡片 - 单个成就组件
 * 包含已解锁和未解锁两种状态
 */
interface AchievementCardProps {
  achievement: {
    id: string;
    title: string;
    description: string;
    icon: React.ReactNode;
    tier: 'bronze' | 'silver' | 'gold' | 'diamond';
    condition?: string;
    unlocked?: boolean;
    unlockedAt?: string;
    points?: number;
  };
  onClick?: (achievement: any) => void;
}

export function AchievementCard({ achievement, onClick }: AchievementCardProps) {
  const [isHovered, setIsHovered] = useState(false);
  const [showAnimation, setShowAnimation] = useState(false);

  // 解锁动画触发
  useEffect(() => {
    if (achievement.unlocked) {
      setTimeout(() => {
        setShowAnimation(true);
        const timer = setTimeout(() => setShowAnimation(false), 2000);
        return () => clearTimeout(timer);
      }, 100);
    }
  }, [achievement.unlocked]);

  const getTierColors = (tier: string) => {
    switch (tier) {
      case 'bronze':
        return { bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-800', badge: 'bg-amber-100 text-amber-800' };
      case 'silver':
        return { bg: 'bg-gray-50', border: 'border-gray-200', text: 'text-gray-800', badge: 'bg-gray-100 text-gray-800' };
      case 'gold':
        return { bg: 'bg-yellow-50', border: 'border-yellow-200', text: 'text-yellow-800', badge: 'bg-yellow-100 text-yellow-800' };
      case 'diamond':
        return { bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-800', badge: 'bg-blue-100 text-blue-800' };
      default:
        return { bg: 'bg-gray-50', border: 'border-gray-200', text: 'text-gray-800', badge: 'bg-gray-100 text-gray-800' };
    }
  };

  const tierColors = achievement.unlocked ? getTierColors(achievement.tier) : { bg: 'bg-gray-50', border: 'border-gray-200', text: 'text-gray-500', badge: 'bg-gray-200 text-gray-500' };

  return (
    <div
      className={`
        relative overflow-hidden rounded-2xl border-2 p-3 transition-all duration-300
        ${achievement.unlocked 
          ? `bg-gradient-to-br ${tierColors.bg} hover:scale-105 hover:shadow-lg cursor-pointer` 
          : 'bg-gray-50 border-gray-200 opacity-80'}
        ${showAnimation ? 'animate-pulse' : ''}
      `}
      onClick={() => achievement.unlocked && onClick && onClick(achievement)}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* 成就等级标识 */}
      <div className="absolute top-2 right-2">
        {achievement.tier === 'bronze' && <span className="text-amber-600">🥉</span>}
        {achievement.tier === 'silver' && <span className="text-gray-500">🥈</span>}
        {achievement.tier === 'gold' && <span className="text-yellow-600">🏆</span>}
        {achievement.tier === 'diamond' && <span className="text-blue-600">💎</span>}
      </div>

      {/* 解锁动画粒子 */}
      {showAnimation && achievement.unlocked && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-10">
          <div className="w-full h-full bg-yellow-200 opacity-20 animate-ping" />
        </div>
      )}

      <div className="flex items-start space-x-3">
        {/* 图标区域 */}
        <div className={`
          flex-shrink-0 w-12 h-12 rounded-xl flex items-center justify-center text-2xl
          ${achievement.unlocked ? `bg-white shadow-sm border border-gray-200 ${tierColors.text}` : 'bg-gray-200 text-gray-400'}
        `}>
          {achievement.icon}
        </div>

        {/* 成就信息 */}
        <div className="flex-1 min-w-0">
          <div className="flex justify-between items-start mb-1">
            <h4 className={`
              text-sm font-bold truncate w-3/4
              ${achievement.unlocked ? 'text-gray-900' : 'text-gray-500'}
            `}>
              {achievement.title}
            </h4>
            {achievement.unlocked && achievement.points && (
              <span className={`
                px-1.5 py-0.5 rounded-full text-xs font-medium
                ${tierColors.badge}
              `}>
                +{achievement.points}分
              </span>
            )}
          </div>
          
          <p className={`
            text-xs line-clamp-2 mb-2
            ${achievement.unlocked ? 'text-gray-600' : 'text-gray-400 italic'}
          `}>
            {achievement.description}
          </p>

          {achievement.unlocked && achievement.unlockedAt && (
            <div className="flex items-center text-[10px] text-gray-500 mt-1">
              <CheckCircle className="w-3 h-3 mr-1 text-green-600" />
              {achievement.unlockedAt}
            </div>
          )}
        </div>
      </div>

      {/* 满分进度条（仅未解锁时显示） */}
      {!achievement.unlocked && achievement.condition && (
        <div className="mt-3 border-t border-gray-200 pt-2">
          <div className="flex justify-between text-[10px] text-gray-500 mb-1">
            <span>{achievement.condition}</span>
            <span>进度: 0/1</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-1.5">
            <div className="bg-gray-400 rounded-full h-1.5" style={{ width: '0%' }} />
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * 成就解锁弹窗 - 解锁成就时的动画弹窗
 */
export function AchievementUnlockModal({ 
  achievement, 
  onClose 
}: { 
  achievement: any; 
  onClose: () => void 
}) {
  const [show, setShow] = useState(false);

  useEffect(() => {
    setShow(true);
    const timer = setTimeout(() => {
      setShow(false);
      setTimeout(onClose, 500);
    }, 3000);
    return () => clearTimeout(timer);
  }, [onClose]);

  const getTierColors = (tier: string) => {
    switch (tier) {
      case 'bronze': return 'bg-gradient-to-br from-amber-100 to-amber-200 border-amber-300 shadow-amber-200';
      case 'silver': return 'bg-gradient-to-br from-gray-100 to-gray-200 border-gray-300 shadow-gray-200';
      case 'gold': return 'bg-gradient-to-br from-yellow-100 to-yellow-200 border-yellow-300 shadow-yellow-200';
      case 'diamond': return 'bg-gradient-to-br from-blue-100 to-blue-200 border-blue-300 shadow-blue-200';
      default: return 'bg-gradient-to-br from-gray-100 to-gray-200';
    }
  };

  if (!show) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/20 backdrop-blur-sm transition-opacity" />
      
      <div className={`
        relative w-full max-w-sm rounded-2xl border-4 p-6 text-center animate-bounce-in
        ${getTierColors(achievement.tier)}
        shadow-2xl
      `}>
        {/* 爆炸特效装饰 */}
        <div className="absolute -top-4 -right-4 text-4xl animate-bounce">🎉</div>
        <div className="absolute -bottom-2 -left-4 text-3xl animate-bounce">✨</div>
        <div className="absolute top-1/2 -left-2 text-2xl animate-pulse">⭐</div>

        {/* 解锁图标 */}
        <div className="relative w-20 h-20 mx-auto mb-4">
          <div className="w-full h-full bg-white rounded-full flex items-center justify-center shadow-lg">
            {achievement.tier === 'bronze' && <span className="text-5xl">🥉</span>}
            {achievement.tier === 'silver' && <span className="text-5xl">🥈</span>}
            {achievement.tier === 'gold' && <span className="text-5xl">🏆</span>}
            {achievement.tier === 'diamond' && <span className="text-5xl">💎</span>}
          </div>
          {/* 光环效果 */}
          <div className="absolute inset-0 rounded-full border-4 border-white opacity-30 animate-ping" />
        </div>

        {/* 成就名称 */}
        <h3 className="text-xl font-bold text-gray-900 mb-2">
          {achievement.title}
        </h3>

        {/* 成就描述 */}
        <p className="text-gray-700 mb-4">
          {achievement.description}
        </p>

        {/* 成就徽章 */}
        <div className="flex justify-center space-x-2">
          <div className="px-3 py-1 bg-white/80 rounded-full text-sm font-medium shadow-sm">
            +{achievement.points}积分
          </div>
          {achievement.tier === 'gold' && (
            <div className="px-3 py-1 bg-yellow-100 rounded-full text-sm font-medium">
              金色成就
            </div>
          )}
        </div>

        {/* 按钮 */}
        <button
          onClick={onClose}
          className="mt-6 w-full bg-white/90 hover:bg-white text-gray-800 font-semibold py-2.5 rounded-xl transition-colors"
        >
          收藏成就
        </button>
      </div>
    </div>
  );
}

/**
 * 成就墙 - 主要组件
 * 以网格布局展示所有成就
 */
export function AchievementWall() {
  const [unlockedAchievements, setUnlockedAchievements] = useState<any[]>([]);
  const [lockedAchievements, setLockedAchievements] = useState<any[]>([]);
  const [selectedAchievement, setSelectedAchievement] = useState<any>(null);
  const [showUnlockModal, setShowUnlockModal] = useState(false);
  const [achievementToUnlock, setAchievementToUnlock] = useState<any>(null);

  // 模拟成就数据
  const mockAchievements = [
    {
      id: 'daily-streak-3',
      title: '坚持是种力量',
      description: '连续3天完成饮食记录',
      icon: <Flame className="w-6 h-6" />,
      tier: 'bronze',
      points: 50,
      unlocked: true,
      unlockedAt: '3月5日',
      condition: '连续3天记录'
    },
    {
      id: 'weekly-consistency',
      title: '一周全勤',
      description: '连续7天完成饮食记录',
      icon: <Calendar className="w-6 h-6" />,
      tier: 'silver',
      points: 100,
      unlocked: true,
      unlockedAt: '3月12日',
      condition: '连续7天记录'
    },
    {
      id: 'macro-master',
      title: '营养大师',
      description: '连续3天蛋白质、碳水、脂肪均达标',
      icon: <Trophy className="w-6 h-6" />,
      tier: 'gold',
      points: 150,
      unlocked: false,
      condition: '连续3天三大营养素达标'
    },
    {
      id: 'calorie-quantum',
      title: '热量守门员',
      description: '连续7天热量控制在目标±10%内',
      icon: <Star className="w-6 h-6" />,
      tier: 'gold',
      points: 200,
      unlocked: false,
      condition: '连续7天热量精准'
    },
    {
      id: 'vegetable-lover',
      title: '蔬菜爱好者',
      description: '单日蔬菜摄入≥300g',
      icon: <Heart className="w-6 h-6" />,
      tier: 'silver',
      points: 75,
      unlocked: true,
      unlockedAt: '3月8日',
      condition: '单日蔬菜摄入≥300g'
    },
    {
      id: 'breakfast-lover',
      title: '早餐不缺席',
      description: '连续7天记录早餐',
      icon: <Smile className="w-6 h-6" />,
      tier: 'silver',
      points: 80,
      unlocked: false,
      condition: '连续7天记录早餐'
    },
    {
      id: 'weight-milestone-5kg',
      title: '里程碑-减重5kg',
      description: '累计减重达到5kg',
      icon: <Trophy className="w-6 h-6" />,
      tier: 'diamond',
      points: 500,
      unlocked: true,
      unlockedAt: '3月1日',
      condition: '累计减重≥5kg'
    },
    {
      id: 'weight-milestone-10kg',
      title: '里程碑-减重10kg',
      description: '累计减重达到10kg',
      icon: <Zap className="w-6 h-6" />,
      tier: 'diamond',
      points: 800,
      unlocked: false,
      condition: '累计减重≥10kg'
    }
  ];

  useEffect(() => {
    const [unlocked, locked] = mockAchievements.reduce((acc, achievement) => {
      if (achievement.unlocked) {
        acc[0].push(achievement);
      } else {
        acc[1].push(achievement);
      }
      return acc;
    }, [[], []] as [any[], any[]]);

    // 排序：钻石 > 金牌 > 银牌 > 铜牌
    const sortOrder = { diamond: 0, gold: 1, silver: 2, bronze: 3 };
    setUnlockedAchievements(unlocked.sort((a, b) => sortOrder[a.tier] - sortOrder[b.tier]));
    setLockedAchievements(locked.sort((a, b) => sortOrder[a.tier] - sortOrder[b.tier]));
  }, []);

  const handleAchievementClick = (achievement: any) => {
    setSelectedAchievement(achievement);
  };

  const handleUnlockAchievement = (achievement: any) => {
    setAchievementToUnlock(achievement);
    setShowUnlockModal(true);
    
    // 模拟解锁动画后处理
    setTimeout(() => {
      setUnlockedAchievements(prev => [achievement, ...prev]);
      setLockedAchievements(prev => prev.filter(a => a.id !== achievement.id));
    }, 3000);
  };

  return (
    <div className="space-y-6 pb-4 animate-fade-in">
      {/* 头部概览 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <Card className="p-4 text-center border-t-4 border-t-amber-400">
          <div className="text-3xl font-bold text-amber-600">{unlockedAchievements.length}</div>
          <div className="text-xs text-gray-500">已解锁</div>
        </Card>
        <Card className="p-4 text-center border-t-4 border-t-gray-400">
          <div className="text-3xl font-bold text-gray-600">{lockedAchievements.length}</div>
          <div className="text-xs text-gray-500">待解锁</div>
        </Card>
        <Card className="p-4 text-center border-t-4 border-t-blue-400">
          <div className="text-3xl font-bold text-blue-600">
            {unlockedAchievements.reduce((sum, a) => sum + (a.points || 0), 0)}
          </div>
          <div className="text-xs text-gray-500">成就积分</div>
        </Card>
        <Card className="p-4 text-center border-t-4 border-t-purple-400">
          <div className="text-3xl font-bold text-purple-600">
            {Math.round((unlockedAchievements.length / mockAchievements.length) * 100)}%
          </div>
          <div className="text-xs text-gray-500">成就完成率</div>
        </Card>
      </div>

      {/* 已解锁成就 */}
      {unlockedAchievements.length > 0 && (
        <div>
          <div className="flex items-center mb-4">
            <Badge variant="primary" className="mr-2">🏆 已解锁</Badge>
            <span className="text-sm text-gray-500">你已经实现了这些目标</span>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {unlockedAchievements.map((achievement) => (
              <AchievementCard
                key={achievement.id}
                achievement={achievement}
                onClick={handleAchievementClick}
              />
            ))}
          </div>
        </div>
      )}

      {/* 未解锁成就 */}
      {lockedAchievements.length > 0 && (
        <div>
          <div className="flex items-center mb-4">
            <Badge variant="secondary" className="mr-2">🔒 待解锁</Badge>
            <span className="text-sm text-gray-500">继续努力，这些等着你</span>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {lockedAchievements.map((achievement) => (
              <AchievementCard
                key={achievement.id}
                achievement={achievement}
              />
            ))}
          </div>
        </div>
      )}

      {/* 成就详情模态 */}
      {selectedAchievement && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/20 backdrop-blur-sm" onClick={() => setSelectedAchievement(null)} />
          <div className="relative bg-white rounded-2xl p-6 max-w-sm w-full shadow-2xl">
            <button
              onClick={() => setSelectedAchievement(null)}
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
            >
              ✖
            </button>

            <div className="flex items-center space-x-4 mb-6">
              <div className={`
                w-24 h-24 rounded-2xl flex items-center justify-center text-4xl
                ${selectedAchievement.tier === 'bronze' ? 'bg-amber-100 text-amber-600' : 
                  selectedAchievement.tier === 'silver' ? 'bg-gray-100 text-gray-600' :
                  selectedAchievement.tier === 'gold' ? 'bg-yellow-100 text-yellow-600' : 
                  'bg-blue-100 text-blue-600'}
              `}>
                {selectedAchievement.icon}
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-1">
                  {selectedAchievement.title}
                </h3>
                <p className="text-gray-600 text-sm">{selectedAchievement.description}</p>
                {selectedAchievement.unlocked && selectedAchievement.unlockedAt && (
                  <div className="flex items-center text-xs text-green-600 mt-2">
                    <CheckCircle className="w-3 h-3 mr-1" />
                    {selectedAchievement.unlockedAt}解锁
                  </div>
                )}
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                <span className="text-gray-600">成就等级</span>
                <span className={`
                  font-medium
                  ${selectedAchievement.tier === 'bronze' ? 'text-amber-600' : 
                    selectedAchievement.tier === 'silver' ? 'text-gray-600' :
                    selectedAchievement.tier === 'gold' ? 'text-yellow-600' : 
                    'text-blue-600'}
                `}>
                  {selectedAchievement.tier === 'bronze' ? '铜牌 🥉' : 
                   selectedAchievement.tier === 'silver' ? '银牌 🥈' :
                   selectedAchievement.tier === 'gold' ? '金牌 🏆' : '钻石💎'}
                </span>
              </div>
              
              {selectedAchievement.condition && (
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <span className="text-gray-600">达成条件</span>
                  <span className="text-gray-900 font-medium text-right">
                    {selectedAchievement.condition}
                  </span>
                </div>
              )}

              {selectedAchievement.points && (
                <div className="flex justify-between items-center p-3 bg-yellow-50 rounded-lg">
                  <span className="text-yellow-600">成就奖励</span>
                  <span className="text-yellow-700 font-bold">+{selectedAchievement.points}积分</span>
                </div>
              )}
            </div>

            <div className="mt-6 space-y-3">
              {selectedAchievement.unlocked ? (
                <Button className="w-full" variant="primary">
                  分享成就 🎉
                </Button>
              ) : (
                <Button className="w-full" variant="secondary" disabled>
                  获取成就
                </Button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 解锁弹窗 */}
      {showUnlockModal && achievementToUnlock && (
        <AchievementUnlockModal
          achievement={achievementToUnlock}
          onClose={() => {
            setShowUnlockModal(false);
            setAchievementToUnlock(null);
          }}
        />
      )}
    </div>
  );
}

/**
 * 成就记录页浮层 - 在打卡后弹出
 */
export function AchievementRewardOverlay({ 
  onContinue, 
  onViewAchievements 
}: { 
  onContinue: () => void;
  onViewAchievements: () => void;
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" />
      
      <div className="relative bg-gradient-to-br from-green-50 to-emerald-50 rounded-3xl p-8 max-w-md w-full shadow-2xl text-center animate-bounce-in">
        {/* 爆花特效 */}
        <div className="flex justify-center space-x-2 mb-4">
          <span className="text-3xl animate-pulse">🎉</span>
          <span className="text-3xl animate-pulse animation-delay-100">✨</span>
          <span className="text-3xl animate-pulse animation-delay-200">🌟</span>
        </div>

        <h2 className="text-2xl font-bold text-green-800 mb-2">
          恭喜解锁新成就！
        </h2>
        
        <div className="bg-white rounded-xl p-4 mb-6 shadow-sm">
          <div className="flex items-center justify-center space-x-4 mb-3">
            <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center text-4xl">
              🥉
            </div>
            <div className="text-left">
              <h3 className="font-bold text-gray-900 text-lg">坚持是种力量</h3>
              <p className="text-sm text-gray-600">连续3天完成饮食记录</p>
              <div className="flex items-center mt-1 text-xs text-green-600">
                <CheckCircle className="w-4 h-4 mr-1" />
                +50积分
              </div>
            </div>
          </div>
        </div>

        <div className="flex flex-col space-y-3">
          <button 
            onClick={onContinue}
            className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3.5 rounded-xl shadow-lg shadow-green-200 transition-all active:scale-98"
          >
            继续记录 📝
          </button>
          
          <button 
            onClick={onViewAchievements}
            className="w-full bg-white hover:bg-gray-50 text-green-700 font-semibold py-3.5 rounded-xl shadow-lg shadow-green-100 transition-all active:scale-98"
          >
            查看成就墙 🏆
          </button>
        </div>

        {/* 进度条（可选） */}
        <div className="mt-6 pt-6 border-t border-green-200">
          <div className="flex justify-between text-xs text-gray-500 mb-2">
            <span>成就进度</span>
            <span>3/3完成</span>
          </div>
          <div className="w-full bg-green-200 rounded-full h-2">
            <div className="bg-green-600 rounded-full h-2" style={{ width: '100%' }} />
          </div>
        </div>
      </div>
    </div>
  );
}

export { AchievementCard, AchievementUnlockModal, AchievementWall, AchievementRewardOverlay };
