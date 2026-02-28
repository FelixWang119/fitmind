import React, { useState, useEffect } from 'react';
import { 
  Star, 
  Target, 
  TrendingUp, 
  Clock,
  Flame,
  Medal,
  Crown,
  ChevronRight,
  Sparkles,
  Gift,
} from 'lucide-react';
import { api } from '../api/client';
import { 
  GamificationOverview, 
  PointsTransaction,
} from '../types';

const Gamification: React.FC = () => {
  const [overview, setOverview] = useState<GamificationOverview | null>(null);
  const [pointsHistory, setPointsHistory] = useState<PointsTransaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [dailyReward, setDailyReward] = useState<{ day: number; points: number; bonus?: string; claimed: boolean } | null>(null);
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [nutritionAchievements, setNutritionAchievements] = useState<any[]>([]);
  const [exerciseAchievements, setExerciseAchievements] = useState<any[]>([]);

  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
    try {
      setLoading(true);
      
      // Load available data
      const [
        overviewData,
        historyData,
        rewardData,
        nutritionData
      ] = await Promise.all([
        api.getGamificationOverview(),
        api.getPointsHistory(20),
        api.getDailyReward(),
        api.getNutritionAchievements() // Story 4.1
      ]);

      setOverview(overviewData);
      setPointsHistory(historyData);
      setDailyReward(rewardData);
      setNutritionAchievements(nutritionData);
      
      // 加载运动成就 (Story 4.2)
      try {
        const exerciseData = await api.getExerciseAchievements();
        setExerciseAchievements(exerciseData);
      } catch (error) {
        console.error('Failed to load exercise achievements:', error);
      }
    } catch (error) {
      console.error('Failed to load gamification data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClaimDailyReward = async () => {
    try {
      const result = await api.claimDailyReward();
      alert(`成功领取${result.points}积分！`);
      loadAllData(); // 重新加载数据
    } catch (error) {
      console.error('Failed to claim daily reward:', error);
    }
  };

  const handleCheckBadges = async () => {
    try {
      const badges = await api.checkAndAwardBadges();
      if (badges.length > 0) {
        alert(`恭喜！您获得了${badges.length}个新徽章！`);
        loadAllData();
      } else {
        alert('暂时没有新的徽章可以解锁。');
      }
    } catch (error) {
      console.error('Failed to check badges:', error);
    }
  };

  const getBadgeColor = (level: string) => {
    switch (level) {
      case 'bronze': return 'bg-amber-700 text-white';
      case 'silver': return 'bg-gray-300 text-gray-800';
      case 'gold': return 'bg-yellow-500 text-white';
      case 'platinum': return 'bg-blue-300 text-blue-900';
      case 'diamond': return 'bg-purple-300 text-purple-900';
      default: return 'bg-gray-200 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* 头部 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">游戏化激励系统</h1>
        <p className="text-gray-600">通过积分、徽章、成就和挑战保持动力，实现健康目标</p>
      </div>

      {/* 每日奖励卡片 */}
      {dailyReward && (
        <div className="mb-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center mb-2">
                <Gift className="w-6 h-6 mr-2" />
                <h2 className="text-xl font-bold">每日登录奖励</h2>
              </div>
              <p className="mb-4">连续登录第{dailyReward.day}天</p>
              <div className="flex items-center space-x-4">
                <div className="bg-white/20 backdrop-blur-sm rounded-lg p-3">
                  <div className="text-2xl font-bold">{dailyReward.points} 积分</div>
                  <div className="text-sm opacity-90">今日奖励</div>
                </div>
                {dailyReward.bonus && (
                  <div className="bg-yellow-500/20 backdrop-blur-sm rounded-lg p-3">
                    <div className="text-lg font-bold">{dailyReward.bonus}</div>
                    <div className="text-sm opacity-90">特别奖励</div>
                  </div>
                )}
              </div>
            </div>
            <button
              onClick={handleClaimDailyReward}
              disabled={dailyReward.claimed}
              className={`px-6 py-3 rounded-lg font-bold text-lg transition-all ${
                dailyReward.claimed 
                  ? 'bg-gray-400 cursor-not-allowed' 
                  : 'bg-white text-purple-600 hover:bg-purple-50 hover:scale-105'
              }`}
            >
              {dailyReward.claimed ? '已领取' : '立即领取'}
            </button>
          </div>
        </div>
      )}

      {/* 主要内容区域 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* 左侧栏 - 积分与等级 */}
        <div className="lg:col-span-2 space-y-8">
          {/* 积分与等级卡片 */}
          {overview && (
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900">积分与等级</h2>
                <button
                  onClick={handleCheckBadges}
                  className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <Sparkles className="w-4 h-4 mr-2" />
                  检查新徽章
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                {/* 积分卡片 */}
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-5">
                  <div className="flex items-center mb-4">
                    <Star className="w-6 h-6 text-blue-600 mr-2" />
                    <h3 className="text-lg font-semibold text-gray-900">积分总览</h3>
                  </div>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600">当前积分</span>
                      <span className="text-2xl font-bold text-blue-700">
                        {overview.user_points.current_points.toLocaleString()}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600">历史总积分</span>
                      <span className="text-lg font-semibold text-gray-800">
                        {overview.user_points.lifetime_points.toLocaleString()}
                      </span>
                    </div>
                    <div className="pt-3 border-t border-blue-200">
                      <div className="text-sm text-gray-600 mb-2">积分分布</div>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm">习惯积分</span>
                          <span className="font-medium">{overview.user_points.breakdown.habit_points}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm">营养积分</span>
                          <span className="font-medium">{overview.user_points.breakdown.nutrition_points}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm">情感积分</span>
                          <span className="font-medium">{overview.user_points.breakdown.emotional_points}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* 等级卡片 */}
                <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-5">
                  <div className="flex items-center mb-4">
                    <Crown className="w-6 h-6 text-purple-600 mr-2" />
                    <h3 className="text-lg font-semibold text-gray-900">等级进度</h3>
                  </div>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-gray-600">当前等级</span>
                        <span className="text-2xl font-bold text-purple-700">
                          Lv.{overview.user_level.current_level}
                        </span>
                      </div>
                      <div className="text-sm text-gray-500 mb-2">
                        {overview.user_level.current_title}
                      </div>
                    </div>
                    
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>进度</span>
                        <span>{overview.user_level.progress_percentage.toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2.5">
                        <div 
                          className="bg-purple-600 h-2.5 rounded-full transition-all duration-500"
                          style={{ width: `${Math.min(overview.user_level.progress_percentage, 100)}%` }}
                        ></div>
                      </div>
                    </div>

                    <div className="text-sm text-gray-600">
                      距离下一等级还需 {overview.user_level.points_to_next_level.toLocaleString()} 积分
                      {overview.user_level.next_level_title && (
                        <div className="mt-1 text-purple-700 font-medium">
                          下一等级: {overview.user_level.next_level_title}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 徽章展示 */}
          {overview && overview.recent_badges.length > 0 && (
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900">最近获得的徽章</h2>
                <button 
                  onClick={() => setActiveTab('badges')}
                  className="flex items-center text-blue-600 hover:text-blue-800 transition-colors"
                >
                  查看全部 <ChevronRight className="w-4 h-4 ml-1" />
                </button>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4">
                {overview.recent_badges.map((badge) => (
                  <div 
                    key={badge.id} 
                    className={`rounded-lg p-4 text-center transition-transform hover:scale-105 ${
                      getBadgeColor(badge.badge_level)
                    }`}
                  >
                    <div className="text-2xl mb-2">{badge.badge_icon}</div>
                    <div className="font-semibold text-sm mb-1">{badge.badge_name}</div>
                    <div className="text-xs opacity-90">{badge.badge_level.toUpperCase()}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 活跃挑战 */}
          {overview && overview.active_challenges.length > 0 && (
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900">进行中的挑战</h2>
                <button 
                  onClick={() => setActiveTab('challenges')}
                  className="flex items-center text-blue-600 hover:text-blue-800 transition-colors"
                >
                  查看全部 <ChevronRight className="w-4 h-4 ml-1" />
                </button>
              </div>
              <div className="space-y-4">
                {overview.active_challenges.map((challenge) => (
                  <div key={challenge.id} className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center">
                        <Target className="w-5 h-5 text-blue-600 mr-2" />
                        <h3 className="font-semibold text-gray-900">{challenge.challenge_name}</h3>
                      </div>
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded">
                        {challenge.points_reward} 积分
                      </span>
                    </div>
                    <p className="text-gray-600 text-sm mb-3">{challenge.challenge_description}</p>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>进度</span>
                        <span>{challenge.current_value} / {challenge.target_value}</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-green-600 h-2 rounded-full transition-all duration-500"
                          style={{ width: `${(challenge.current_value / challenge.target_value) * 100}%` }}
                        ></div>
                      </div>
                      <div className="flex justify-between text-xs text-gray-500">
                        <span>开始: {new Date(challenge.start_date).toLocaleDateString()}</span>
                        <span>结束: {new Date(challenge.end_date).toLocaleDateString()}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* 右侧栏 */}
        <div className="space-y-8">
          {/* 连续记录 */}
          {overview && overview.streaks.length > 0 && (
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center mb-6">
                <Flame className="w-6 h-6 text-orange-600 mr-2" />
                <h2 className="text-xl font-bold text-gray-900">连续记录</h2>
              </div>
              <div className="space-y-4">
                {overview.streaks.map((streak) => (
                  <div key={streak.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-gray-900">{streak.streak_name}</span>
                      <span className="text-lg font-bold text-orange-600">{streak.current_streak} 天</span>
                    </div>
                    <div className="text-sm text-gray-600">
                      最长记录: {streak.longest_streak} 天
                    </div>
                    {streak.milestones_reached.length > 0 && (
                      <div className="mt-2 text-xs text-gray-500">
                        里程碑: {streak.milestones_reached.join(', ')} 天
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 活跃成就 */}
          {overview && overview.active_achievements.length > 0 && (
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900">进行中的成就</h2>
                <button 
                  onClick={() => setActiveTab('achievements')}
                  className="flex items-center text-blue-600 hover:text-blue-800 transition-colors"
                >
                  查看全部 <ChevronRight className="w-4 h-4 ml-1" />
                </button>
              </div>
              <div className="space-y-4">
                {overview.active_achievements.map((achievement) => (
                  <div key={achievement.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center">
                        <Medal className="w-5 h-5 text-yellow-600 mr-2" />
                        <h3 className="font-semibold text-gray-900">{achievement.achievement_name}</h3>
                      </div>
                      <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs font-medium rounded">
                        {achievement.points_reward} 积分
                      </span>
                    </div>
                    <p className="text-gray-600 text-sm mb-3">{achievement.achievement_description}</p>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>进度</span>
                        <span>{achievement.current_value} / {achievement.target_value}</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-yellow-500 h-2 rounded-full transition-all duration-500"
                          style={{ width: `${achievement.progress_percentage}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Story 4.1: 营养成就 */}
          {nutritionAchievements.length > 0 && (
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900">🍎 营养成就</h2>
                <span className="text-sm text-gray-500">
                  {nutritionAchievements.filter((a: any) => a.is_completed).length} / {nutritionAchievements.length} 已完成
                </span>
              </div>
              <div className="space-y-4">
                {nutritionAchievements.map((achievement: any) => (
                  <div 
                    key={achievement.id} 
                    className={`border rounded-lg p-4 ${
                      achievement.is_completed 
                        ? 'border-green-300 bg-green-50' 
                        : 'border-gray-200'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center">
                        {achievement.is_completed ? (
                          <span className="text-2xl mr-2">🏆</span>
                        ) : (
                          <span className="text-2xl mr-2">🎯</span>
                        )}
                        <h3 className="font-semibold text-gray-900">{achievement.achievement_name}</h3>
                      </div>
                      <span className={`px-2 py-1 text-xs font-medium rounded ${
                        achievement.is_completed 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-orange-100 text-orange-800'
                      }`}>
                        {achievement.points_reward} 积分
                      </span>
                    </div>
                    <p className="text-gray-600 text-sm mb-3">{achievement.achievement_description}</p>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>进度</span>
                        <span>{achievement.current_value} / {achievement.target_value}</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full transition-all duration-500 ${
                            achievement.is_completed ? 'bg-green-500' : 'bg-orange-500'
                          }`}
                          style={{ width: `${achievement.progress_percentage}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Story 4.2: 运动成就 */}
          {exerciseAchievements.length > 0 && (
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900">🏃 运动成就</h2>
                <span className="text-sm text-gray-500">
                  {exerciseAchievements.filter((a: any) => a.is_completed).length} / {exerciseAchievements.length} 已完成
                </span>
              </div>
              <div className="space-y-4">
                {exerciseAchievements.map((achievement: any) => (
                  <div 
                    key={achievement.id} 
                    className={`border rounded-lg p-4 ${
                      achievement.is_completed 
                        ? 'border-blue-300 bg-blue-50' 
                        : 'border-gray-200'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center">
                        {achievement.is_completed ? (
                          <span className="text-2xl mr-2">🏆</span>
                        ) : (
                          <span className="text-2xl mr-2">🎯</span>
                        )}
                        <h3 className="font-semibold text-gray-900">{achievement.achievement_name}</h3>
                      </div>
                      <span className={`px-2 py-1 text-xs font-medium rounded ${
                        achievement.is_completed 
                          ? 'bg-blue-100 text-blue-800' 
                          : 'bg-green-100 text-green-800'
                      }`}>
                        {achievement.points_reward} 积分
                      </span>
                    </div>
                    <p className="text-gray-600 text-sm mb-3">{achievement.achievement_description}</p>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>进度</span>
                        <span>
                          {/* 对于距离类成就，显示公里 */}
                          {achievement.target_value >= 1000 && achievement.achievement_id.includes('km') 
                            ? `${(achievement.current_value / 1000).toFixed(1)} / ${(achievement.target_value / 1000).toFixed(0)} km`
                            : `${achievement.current_value} / ${achievement.target_value}`
                          }
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full transition-all duration-500 ${
                            achievement.is_completed ? 'bg-blue-500' : 'bg-green-500'
                          }`}
                          style={{ width: `${Math.min(100, achievement.progress_percentage)}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 积分历史 */}
          {pointsHistory.length > 0 && (
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center mb-6">
                <Clock className="w-6 h-6 text-gray-600 mr-2" />
                <h2 className="text-xl font-bold text-gray-900">最近积分记录</h2>
              </div>
              <div className="space-y-3">
                {pointsHistory.slice(0, 5).map((transaction) => (
                  <div key={transaction.id} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                    <div>
                      <div className="font-medium text-gray-900">{transaction.description}</div>
                      <div className="text-sm text-gray-500">
                        {new Date(transaction.created_at).toLocaleDateString()}
                      </div>
                    </div>
                    <div className={`font-bold ${transaction.points_amount > 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {transaction.points_amount > 0 ? '+' : ''}{transaction.points_amount}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 快速操作 */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">快速操作</h3>
            <div className="space-y-3">
              <button 
                onClick={handleCheckBadges}
                className="w-full flex items-center justify-between p-3 bg-white rounded-lg hover:bg-blue-50 transition-colors"
              >
                <div className="flex items-center">
                  <Sparkles className="w-5 h-5 text-blue-600 mr-3" />
                  <span className="font-medium">检查新徽章</span>
                </div>
                <ChevronRight className="w-4 h-4 text-gray-400" />
              </button>
              <button 
                onClick={handleClaimDailyReward}
                className="w-full flex items-center justify-between p-3 bg-white rounded-lg hover:bg-blue-50 transition-colors"
              >
                <div className="flex items-center">
                  <Gift className="w-5 h-5 text-green-600 mr-3" />
                  <span className="font-medium">领取每日奖励</span>
                </div>
                <ChevronRight className="w-4 h-4 text-gray-400" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Gamification;