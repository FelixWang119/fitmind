/**
 * 运动成就系统扩展组件
 * 包含新增成就、成就等级升级、成就分享功能
 */

import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Tabs, 
  Badge, 
  Button, 
  Space, 
  message, 
  Modal, 
  Progress,
  Tooltip,
  CopyOutlined,
  ShareAltOutlined,
  Trophy,
  Crown,
  Diamond,
  Star,
  Fire,
  Award
} from 'antd';
import { 
  TrophyOutlined, 
  CrownOutlined, 
  DiamondOutlined, 
  ShareAltOutlined as ShareIcon,
  CopyOutlined as CopyIcon
} from '@ant-design/icons';
import { useAuthStore } from '../../../store/authStore';

// 类型定义
interface Achievement {
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

interface SocialShareData {
  title: string;
  content: string;
  image: string;
  url: string;
}

// 模拟成就数据
const SPECIAL_ACHIEVEMENTS: Achievement[] = [
  {
    id: 'special-1',
    name: '蜕变黄金会员',
    description: '累计减重10公斤并保持3个月',
    icon: <Crown className="w-6 h-6 text-yellow-500" />,
    category: 'milestone',
    points: 2000,
    tier: 'diamond',
    current: 8.5,
    target: 10,
    unlocked: false,
  },
  {
    id: 'special-2',
    name: '运动马拉松',
    description: '累计运动100小时',
    icon: <Fire className="w-6 h-6 text-red-500" />,
    category: 'quantity',
    points: 1500,
    tier: 'gold',
    current: 78,
    target: 100,
    unlocked: false,
  },
  {
    id: 'special-3',
    name: '完美体态',
    description: 'BMI连续6个月保持在健康范围',
    icon: <Star className="w-6 h-6 text-blue-500" />,
    category: 'quality',
    points: 1800,
    tier: 'gold',
    current: 165,
    target: 180,
    unlocked: false,
  },
  {
    id: 'special-4',
    name: '健康大使',
    description: '帮助5位亲友成功减重',
    icon: <Trophy className="w-6 h-6 text-green-500" />,
    category: 'milestone',
    points: 2500,
    tier: 'diamond',
    current: 3,
    target: 5,
    unlocked: false,
  },
  {
    id: 'special-5',
    name: '超级挑战者',
    description: '完成52周运动挑战',
    icon: <Award className="w-6 h-6 text-purple-500" />,
    category: 'milestone',
    points: 3000,
    tier: 'diamond',
    current: 42,
    target: 52,
    unlocked: false,
  },
];

const MOCK_ACHIEVEMENTS: Achievement[] = [
  {
    id: '1',
    name: '连续7天打卡',
    description: '连续7天完成运动或饮食打卡',
    icon: <span className="text-xl">🔥</span>,
    category: 'streak',
    points: 200,
    tier: 'bronze',
    current: 7,
    target: 7,
    unlocked: true,
    unlockDate: '2024-01-15',
  },
  {
    id: '2',
    name: '连续30天打卡',
    description: '连续30天完成运动或饮食打卡',
    icon: <span className="text-xl">⚡</span>,
    category: 'streak',
    points: 500,
    tier: 'silver',
    current: 7,
    target: 30,
    unlocked: false,
  },
  {
    id: '3',
    name: '连续60天打卡',
    description: '连续60天完成运动或饮食打卡',
    icon: <span className="text-xl">🌟</span>,
    category: 'streak',
    points: 1000,
    tier: 'gold',
    current: 7,
    target: 60,
    unlocked: false,
  },
  {
    id: '4',
    name: '连续90天打卡',
    description: '连续90天完成运动或饮食打卡',
    icon: <span className="text-xl">🏆</span>,
    category: 'streak',
    points: 2000,
    tier: 'silver',
    current: 7,
    target: 90,
    unlocked: false,
  },
  {
    id: '5',
    name: '连续100天打卡',
    description: '连续100天完成运动或饮食打卡',
    icon: <span className="text-xl">👑</span>,
    category: 'streak',
    points: 5000,
    tier: 'gold',
    current: 7,
    target: 100,
    unlocked: false,
  },
  {
    id: '6',
    name: '累计运动50小时',
    description: '累计完成50小时运动',
    icon: <span className="text-xl">🏋️</span>,
    category: 'quantity',
    points: 500,
    tier: 'bronze',
    current: 35,
    target: 50,
    unlocked: false,
  },
  {
    id: '7',
    name: '累计运动100小时',
    description: '累计完成100小时运动',
    icon: <span className="text-xl">running-man</span>,
    category: 'quantity',
    points: 1500,
    tier: 'gold',
    current: 35,
    target: 100,
    unlocked: false,
  },
];

// 成就等级配置
const TIER_CONFIG = {
  bronze: { name: '青铜', color: 'text-orange-600', bgColor: 'bg-orange-100', border: 'border-orange-300', icon: '🥉' },
  silver: { name: '白银', color: 'text-gray-400', bgColor: 'bg-gray-100', border: 'border-gray-300', icon: '🥈' },
  gold: { name: '黄金', color: 'text-yellow-600', bgColor: 'bg-yellow-100', border: 'border-yellow-300', icon: '🥇' },
  diamond: { name: '钻石', color: 'text-blue-500', bgColor: 'bg-blue-100', border: 'border-blue-300', icon: '💎' },
};

// 主组件
export const ExerciseAchievementExtended: React.FC = () => {
  const [achievements, setAchievements] = useState<MOCK_ACHIEVEMENTS>(MOCK_ACHIEVEMENTS);
  const [specialAchievements, setSpecialAchievements] = useState<SPECIAL_ACHIEVEMENTS>(SPECIAL_ACHIEVEMENTS);
  const [activeTab, setActiveTab] = useState('list');
  const [shareModalVisible, setShareModalVisible] = useState(false);
  const [currentShareAchievement, setCurrentShareAchievement] = useState<Achievement | null>(null);

  // 计算成就进度
  const getProgress = (achievement: Achievement) => {
    if (achievement.unlocked) return 100;
    return Math.min((achievement.current / achievement.target) * 100, 100);
  };

  // 成就卡片组件
  const AchievementCard = ({ achievement, isSpecial = false }: { achievement: Achievement; isSpecial?: boolean }) => (
    <div 
      className={`relative p-6 rounded-2xl border-2 transition-all duration-300 cursor-pointer group ${
        achievement.unlocked 
          ? `bg-gradient-to-br from-${achievement.tier === 'bronze' ? 'orange' : achievement.tier === 'silver' ? 'gray' : achievement.tier === 'gold' ? 'yellow' : 'blue'}-50 to-white border-${achievement.tier === 'bronze' ? 'orange' : achievement.tier === 'silver' ? 'gray' : achievement.tier === 'gold' ? 'yellow' : 'blue'}-300` 
          : 'bg-gray-50 border-gray-200 opacity-70'
      }`}
      onClick={() => {
        if (!achievement.unlocked) {
          setCurrentShareAchievement(achievement);
          setShareModalVisible(true);
        }
      }}
    >
      {achievement.unlocked && (
        <div className="absolute top-2 right-2">
          <Badge count="已解锁" color="green" />
        </div>
      )}
      
      <div className="flex items-start space-x-4">
        <div className={`w-16 h-16 rounded-2xl flex items-center justify-center text-3xl ${
          achievement.unlocked 
            ? achievement.tier === 'bronze' ? 'bg-orange-100 text-orange-600' :
              achievement.tier === 'silver' ? 'bg-gray-200 text-gray-600' :
              achievement.tier === 'gold' ? 'bg-yellow-100 text-yellow-600' :
              'bg-blue-100 text-blue-600'
            : 'bg-gray-200 text-gray-400'
        }`}>
          {achievement.icon}
        </div>
        
        <div className="flex-1">
          <div className="flex justify-between items-start">
            <h4 className={`font-bold text-lg ${achievement.unlocked ? 'text-gray-800' : 'text-gray-600'}`}>
              {achievement.name}
            </h4>
            {achievement.unlocked && (
              <span className={`px-2 py-1 rounded-lg text-xs font-bold ${
                achievement.tier === 'bronze' ? 'bg-orange-100 text-orange-700' :
                achievement.tier === 'silver' ? 'bg-gray-200 text-gray-700' :
                achievement.tier === 'gold' ? 'bg-yellow-100 text-yellow-700' :
                'bg-blue-100 text-blue-700'
              }`}>
                {TIER_CONFIG[achievement.tier].name}级
              </span>
            )}
          </div>
          
          <p className="text-sm text-gray-500 mt-1 mb-3">{achievement.description}</p>
          
          {achievement.unlocked ? (
            <div className="flex items-center space-x-4 text-sm">
              <div className="flex items-center text-green-600">
                <span className="mr-1">🏆</span>
                {achievement.unlockDate && new Date(achievement.unlockDate).toLocaleDateString('zh-CN')}
              </div>
              <div className="flex items-center text-yellow-600">
                <span className="mr-1">⭐</span>
                {achievement.points}积分
              </div>
            </div>
          ) : (
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">进度</span>
                <span className="font-semibold text-gray-800">
                  {achievement.current} / {achievement.target}
                </span>
              </div>
              <div className="relative h-2 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  className={`absolute top-0 left-0 h-full rounded-full transition-all duration-1000 ${
                    achievement.tier === 'bronze' ? 'bg-gradient-to-r from-orange-400 to-orange-600' :
                    achievement.tier === 'silver' ? 'bg-gradient-to-r from-gray-400 to-gray-600' :
                    achievement.tier === 'gold' ? 'bg-gradient-to-r from-yellow-400 to-yellow-600' :
                    'bg-gradient-to-r from-blue-400 to-blue-600'
                  }`}
                  style={{ width: `${getProgress(achievement)}%` }}
                ></div>
              </div>
              <div className="flex justify-between text-xs text-gray-500">
                <span>{Math.round(getProgress(achievement))}%</span>
                <span>{achievement.category === 'streak' ? '天' : achievement.category === 'quantity' ? '小时' : '个'}</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  // 统计卡片
  const StatsCard = () => {
    const totalUnlocked = achievements.filter(a => a.unlocked).length;
    const totalPoints = achievements.reduce((sum, a) => sum + (a.unlocked ? a.points : 0), 0);
    const specialAchievementsUnlocked = specialAchievements.filter(a => a.unlocked).length;

    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {[
          { label: '已解锁成就', value: totalUnlocked, total: achievements.length, color: 'blue', icon: '🏆' },
          { label: '获得积分', value: totalPoints, total: 0, color: 'gold', icon: '⭐' },
          { label: '特殊成就', value: specialAchievementsUnlocked, total: specialAchievements.length, color: 'purple', icon: '💎' },
        ].map((stat, index) => (
          <Card key={index} className="hover:shadow-lg transition-shadow">
            <div className="flex items-center space-x-4">
              <div className={`p-4 rounded-xl bg-${stat.color}-100`}>
                <span className="text-3xl">{stat.icon}</span>
              </div>
              <div className="flex-1">
                <p className="text-gray-500 text-sm">{stat.label}</p>
                <div className="flex items-end space-x-2">
                  <p className="text-3xl font-bold text-gray-800">{stat.value}</p>
                  {stat.total > 0 && (
                    <p className="text-gray-500 mb-1">/ {stat.total}</p>
                  )}
                </div>
                <Progress 
                  percent={stat.total > 0 ? Math.round((stat.value / stat.total) * 100) : 100}
                  size="small"
                  strokeColor={stat.color === 'blue' ? 'blue' : stat.color === 'gold' ? 'yellow' : 'purple'}
                />
              </div>
            </div>
          </Card>
        ))}
      </div>
    );
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">🏆 运动成就系统</h1>
            <p className="text-gray-600 mt-2">解锁成就，展示你的运动旅程里程碑</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <p className="text-sm text-gray-500">当前总积分</p>
              <p className="text-2xl font-bold text-yellow-600">3,200</p>
            </div>
            <div className="px-4 py-2 bg-gradient-to-r from-yellow-400 to-orange-500 text-white rounded-xl font-bold">
              等级 6
            </div>
          </div>
        </div>
        
        <StatsCard />
      </div>

      {/* Tabs */}
      <Tabs 
        activeKey={activeTab} 
        onChange={setActiveTab}
        items={[
          {
            key: 'list',
            label: '成就列表',
            children: (
              <div className="space-y-6">
                {/* 常规成就 */}
                <div>
                  <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
                    <span className="text-2xl mr-2">🏆</span>
                    常规成就
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {achievements.map((achievement) => (
                      <AchievementCard key={achievement.id} achievement={achievement} />
                    ))}
                  </div>
                </div>

                {/* 特殊成就 */}
                <div>
                  <h3 className="text-xl font-bold text-purple-700 mb-4 flex items-center">
                    <Diamond className="w-6 h-6 mr-2" />
                    特殊成就（钻石级）
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {specialAchievements.map((achievement) => (
                      <AchievementCard key={achievement.id} achievement={achievement} isSpecial={true} />
                    ))}
                  </div>
                </div>
              </div>
            ),
            icon: <TrophyOutlined className="w-4 h-4" />,
          },
          {
            key: 'timeline',
            label: '成就时间线',
            children: (
              <div className="space-y-6">
                <div className="bg-white rounded-2xl shadow-lg p-6">
                  <h3 className="text-xl font-bold text-gray-800 mb-6">成就历程</h3>
                  <div className="relative">
                    <div className="absolute left-4 top-4 bottom-4 w-1 bg-gradient-to-b from-gray-200 to-gray-300"></div>
                    
                    {achievements.filter(a => a.unlocked).map((achievement, index) => (
                      <div key={achievement.id} className="relative pl-12 mb-8 last:mb-0">
                        <div className={`absolute left-0 top-0 w-8 h-8 rounded-full flex items-center justify-center border-4 border-white ${
                          achievement.tier === 'bronze' ? 'bg-orange-500' :
                          achievement.tier === 'silver' ? 'bg-gray-400' :
                          achievement.tier === 'gold' ? 'bg-yellow-500' :
                          'bg-blue-500'
                        }`}>
                          <span className="text-white text-lg">{achievement.icon}</span>
                        </div>
                        <div className="bg-gray-50 p-4 rounded-xl border border-gray-200 hover:shadow-md transition-shadow">
                          <div className="flex justify-between items-start">
                            <div>
                              <h4 className="font-semibold text-gray-800">{achievement.name}</h4>
                              <p className="text-sm text-gray-500 mt-1">{achievement.description}</p>
                            </div>
                            <div className="text-right">
                              <span className="px-2 py-1 bg-white rounded-lg text-xs border border-gray-200">
                                {achievement.unlockDate && new Date(achievement.unlockDate).toLocaleDateString('zh-CN')}
                              </span>
                            </div>
                          </div>
                          <div className="flex items-center mt-3 space-x-4 text-sm">
                            <span className="text-yellow-600 flex items-center">
                              <span className="mr-1">⭐</span> {achievement.points}积分
                            </span>
                            <span className="text-gray-400">|</span>
                            <span className={`text-${achievement.tier === 'bronze' ? 'orange' : achievement.tier === 'silver' ? 'gray' : achievement.tier === 'gold' ? 'yellow' : 'blue'}-600 font-semibold`}>
                              {TIER_CONFIG[achievement.tier].name}级成就
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                    
                    {achievements.filter(a => a.unlocked).length === 0 && (
                      <div className="text-center py-12 text-gray-500">
                        <span className="text-4xl mb-4 block">🏆</span>
                        <p>暂无成就记录，继续加油！</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ),
            icon: <ClockCircleOutlined className="w-4 h-4" />,
          },
          {
            key: 'share',
            label: '成就分享',
            children: (
              <div className="space-y-6">
                <div className="bg-gradient-to-r from-purple-500 to-pink-600 rounded-2xl p-8 text-white text-center">
                  <h3 className="text-2xl font-bold mb-4">分享你的成就</h3>
                  <p className="opacity-90 mb-6">展示你的运动里程碑，激励更多人加入健康生活</p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
                    {achievements.filter(a => a.unlocked).slice(0, 4).map((achievement) => (
                      <div 
                        key={achievement.id}
                        className="bg-white/10 backdrop-blur-sm p-4 rounded-xl text-center cursor-pointer hover:bg-white/20 transition-colors"
                      >
                        <div className="text-3xl mb-2">{achievement.icon}</div>
                        <h4 className="font-semibold">{achievement.name}</h4>
                        <p className="text-xs opacity-80">{achievement.unlockDate && new Date(achievement.unlockDate).toLocaleDateString('zh-CN')}</p>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {[
                    { title: '微信朋友圈', icon: <span className="text-2xl">_wechat</span>, desc: '分享到微信朋友圈' },
                    { title: 'Instagram', icon: <span className="text-2xl">📷</span>, desc: '分享到Instagram' },
                    { title: '微博', icon: <span className="text-2xl">tweets</span>, desc: '分享到微博' },
                  ].map((platform, index) => (
                    <Card key={index} className="hover:shadow-lg transition-shadow cursor-pointer">
                      <div className="text-center p-4">
                        <div className="text-3xl mb-3">{platform.icon}</div>
                        <h4 className="font-semibold text-gray-800">{platform.title}</h4>
                        <p className="text-sm text-gray-500 mt-1">{platform.desc}</p>
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            ),
            icon: <ShareIcon className="w-4 h-4" />,
          },
        ]}
      />

      {/* 分享模态框 */}
      <Modal
        title="分享成就"
        open={shareModalVisible}
        onCancel={() => setShareModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setShareModalVisible(false)}>取消</Button>,
          <Button 
            key="copy" 
            type="primary" 
            icon={<CopyIcon />}
            onClick={() => {
              message.success('成就信息已复制到剪贴板');
              setShareModalVisible(false);
            }}
          >
            复制分享内容
          </Button>,
        ]}
      >
        {currentShareAchievement && (
          <div className="space-y-4">
            <div className="bg-gradient-to-r from-yellow-400 to-orange-500 rounded-xl p-6 text-white text-center">
              <div className="text-5xl mb-4">{currentShareAchievement.icon}</div>
              <h3 className="text-xl font-bold">{currentShareAchievement.name}</h3>
              <p className="opacity-90 mt-2">{currentShareAchievement.description}</p>
              <div className="mt-4 inline-block px-4 py-2 bg-white/20 rounded-lg">
                奖励 {currentShareAchievement.points} 积分
              </div>
            </div>
            
            <div className="bg-gray-50 p-4 rounded-xl">
              <p className="text-sm text-gray-500 mb-2">分享文本：</p>
              <div className="bg-white p-3 rounded-lg text-sm text-gray-800 font-mono">
                我刚刚解锁了「{currentShareAchievement.name}」成就！🎉
                {currentShareAchievement.description}
                奖励 {currentShareAchievement.points} 积分～
              </div>
            </div>
            
            <div className="bg-gray-50 p-4 rounded-xl">
              <p className="text-sm text-gray-500 mb-2">配图建议：</p>
              <div className="flex space-x-2">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center text-white text-2xl">
                    🏆
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default ExerciseAchievementExtended;
