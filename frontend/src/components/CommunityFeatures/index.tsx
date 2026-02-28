/**
 * 社区功能组件
 * 包含用户排行榜、成就分享、互助社区、专家问答
 */

import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Tabs, 
  List, 
  Badge, 
  Avatar, 
  Button, 
  Space, 
  Typography,
  Input,
  Comment,
  Form,
  Divider
} from 'antd';
import { 
  TrophyOutlined, 
  StarOutlined, 
  FireOutlined, 
  QuestionCircleOutlined,
  ExclamationCircleOutlined,
  ShareAltOutlined
} from '@ant-design/icons';

const { Title, Text, Paragraph } = Typography;

// 模拟数据
const LEADERBOARD_DATA = [
  { rank: 1, name: 'Felix', avatar: 'lee', points: 12500, level: 10, trend: 'up', trendValue: '↑5' },
  { rank: 2, name: 'Sarah', avatar: 'sara', points: 11800, level: 9, trend: 'up', trendValue: '↑3' },
  { rank: 3, name: 'Mike', avatar: 'mike', points: 11200, level: 9, trend: 'down', trendValue: '↓2' },
  { rank: 4, name: 'Emma', avatar: 'emma', points: 10500, level: 9, trend: 'up', trendValue: '↑1' },
  { rank: 5, name: 'David', avatar: 'david', points: 9800, level: 8, trend: 'stable', trendValue: '-' },
  { rank: 6, name: 'Lisa', avatar: 'lisa', points: 9200, level: 8, trend: 'up', trendValue: '↑4' },
  { rank: 7, name: 'John', avatar: 'john', points: 8700, level: 8, trend: 'down', trendValue: '↓1' },
  { rank: 8, name: 'Amy', avatar: 'amy', points: 8100, level: 7, trend: 'stable', trendValue: '-' },
  { rank: 9, name: 'Tom', avatar: 'tom', points: 7600, level: 7, trend: 'up', trendValue: '↑2' },
  { rank: 10, name: 'Lucy', avatar: 'lucy', points: 7200, level: 7, trend: 'down', trendValue: '↓3' },
];

const TRENDS = { up: { icon: '↑', color: 'text-green-500' }, down: { icon: '↓', color: 'text-red-500' }, stable: { icon: '→', color: 'text-gray-500' } };

const COMMUNITY_POSTS = [
  { id: 1, author: 'Felix', avatar: 'lee', content: '坚持打卡第30天！分享我的减重经验：每天记录饮食和运动，坚持就是胜利！', likes: 125, comments: 34, timestamp: '2小时前' },
  { id: 2, author: 'Sarah', avatar: 'sara', content: '刚刚达成月度目标！减重2.5公斤，感谢社区伙伴们的鼓励！', likes: 98, comments: 56, timestamp: '4小时前' },
  { id: 3, author: 'Mike', avatar: 'mike', content: '新手提问：HIIT训练应该如何安排？一周几次比较合适？', likes: 24, comments: 12, timestamp: '6小时前' },
  { id: 4, author: 'Emma', avatar: 'emma', content: '分享我的运动歌单，跑步时听特别带感！🎵', likes: 67, comments: 21, timestamp: '8小时前' },
  { id: 5, author: 'David', avatar: 'david', content: '体重平台期怎么破？求大神支招！', likes: 45, comments: 78, timestamp: '1天前' },
];

const EXPERT问答 = [
  { id: 1, question: '如何制定科学的减脂计划？', expert: '李医生', status: '已回答', likes: 234, timestamp: '2天前' },
  { id: 2, question: '蛋白质摄入量如何计算？', expert: '张营养师', status: '已回答', likes: 189, timestamp: '3天前' },
  { id: 3, question: '运动后肌肉酸痛怎么办？', expert: '王教练', status: '已回答', likes: 312, timestamp: '4天前' },
  { id: 4, question: '深夜饥饿感怎么控制？', expert: '陈心理师', status: '已回答', likes: 167, timestamp: '5天前' },
  { id: 5, question: '女性月经期如何调整运动？', expert: '刘健身师', status: '已回答', likes: 289, timestamp: '6天前' },
];

// 社区功能组件
export const CommunityFeatures: React.FC = () => {
  const [activeTab, setActiveTab] = useState('leaderboard');

  return (
    <div className="p-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">👥 互助社区</h1>
            <p className="text-gray-600 mt-2">与其他用户交流经验，获取专业指导</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="px-4 py-2 bg-blue-100 rounded-lg">
              <span className="text-blue-700 font-semibold">社区成员：12,500+</span>
            </div>
            <Button type="primary" icon={<QuestionCircleOutlined />}>
              提问专家
            </Button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <Tabs 
        activeKey={activeTab} 
        onChange={setActiveTab}
        items={[
          {
            key: 'leaderboard',
            label: '用户排行榜',
            children: <LeaderboardSection />,
            icon: <TrophyOutlined className="w-4 h-4" />,
          },
          {
            key: 'posts',
            label: '社区动态',
            children: <CommunityPostsSection />,
            icon: <ShareAltOutlined className="w-4 h-4" />,
          },
          {
            key: 'expert',
            label: '专家问答',
            children: <ExpertQASection />,
            icon: <ExclamationCircleOutlined className="w-4 h-4" />,
          },
        ]}
      />
    </div>
  );
};

// 排行榜组件
const LeaderboardSection = () => (
  <div className="space-y-6">
    {/* 本周之星 */}
    <div className="flex items-center justify-between mb-6">
      <Title level={3} className="mb-0">🏆 周排行榜</Title>
      <div className="flex items-center space-x-2">
        <span className="text-gray-500 text-sm">时间范围：</span>
        <select className="px-4 py-2 border border-gray-300 rounded-lg text-sm">
          <option>本周</option>
          <option>本月</option>
          <option>本季</option>
          <option>全年</option>
        </select>
      </div>
    </div>

    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* 前三名特写 */}
      <div className="lg:grid lg:grid-cols-3 lg:gap-6">
        <div className="lg:col-span-3 mb-6">
          <div className="bg-gradient-to-r from-yellow-400 to-orange-500 rounded-2xl p-8 text-white text-center">
            <h2 className="text-2xl font-bold mb-4">🏆 这周的赢家</h2>
            <div className="flex items-center justify-center space-x-8">
              <div className="flex flex-col items-center">
                <div className="w-24 h-24 rounded-full bg-white text-yellow-600 flex items-center justify-center text-3xl mb-2">
                  1
                </div>
                <div className="text-2xl font-bold">Felix</div>
                <div className="text-yellow-100 text-sm">12,500 积分</div>
              </div>
              <div className="flex flex-col items-center">
                <div className="w-20 h-20 rounded-full bg-gray-200 text-gray-600 flex items-center justify-center text-2xl mb-2">
                  2
                </div>
                <div className="text-xl font-bold">Sarah</div>
                <div className="text-yellow-100 text-sm">11,800 积分</div>
              </div>
              <div className="flex flex-col items-center">
                <div className="w-16 h-16 rounded-full bg-yellow-200 text-yellow-800 flex items-center justify-center text-xl mb-2">
                  3
                </div>
                <div className="text-lg font-bold">Mike</div>
                <div className="text-yellow-100 text-sm">11,200 积分</div>
              </div>
            </div>
          </div>
        </div>

        {/* 排行榜列表 */}
        <div className="lg:col-span-3 overflow-hidden rounded-xl shadow-lg">
          <table className="w-full bg-white">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">排名</th>
                <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">用户</th>
                <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">积分</th>
                <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">等级</th>
                <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">趋势</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {LEADERBOARD_DATA.map((user) => (
                <tr key={user.rank} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className={`flex items-center justify-center w-8 h-8 rounded-lg ${
                      user.rank === 1 ? 'bg-yellow-100 text-yellow-600' :
                      user.rank === 2 ? 'bg-gray-100 text-gray-600' :
                      user.rank === 3 ? 'bg-yellow-100 text-yellow-800' :
                      user.rank === 4 ? 'bg-cyan-100 text-cyan-600' :
                      user.rank === 5 ? 'bg-blue-100 text-blue-600' :
                      'text-gray-500'
                    }`}>
                      {user.rank}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10">
                        <div className="h-10 w-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold">
                          {user.avatar.charAt(0).toUpperCase()}
                        </div>
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">{user.name}</div>
                        <div className="text-xs text-gray-500">ID: {900000 + user.rank}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-bold text-gray-900">{user.points.toLocaleString()}</div>
                    <div className="text-xs text-gray-500">+{user.trendValue === '↑' ? user.trendValue + '100' : user.trendValue}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <span className={`px-2 py-1 rounded-lg text-xs font-semibold ${
                        user.level === 10 ? 'bg-gradient-to-r from-yellow-400 to-orange-500 text-white' :
                        user.level >= 8 ? 'bg-gradient-to-r from-blue-400 to-purple-500 text-white' :
                        user.level >= 6 ? 'bg-gradient-to-r from-green-400 to-teal-500 text-white' :
                        'bg-gray-100 text-gray-600'
                      }`}>
                        等级 {user.level}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`text-sm font-medium flex items-center ${TRENDS[user.trend]?.color}`}>
                      {TRENDS[user.trend]?.icon} {user.trendValue}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 用户成就统计 */}
      <div className="lg:col-span-1">
        <div className="bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl p-6 text-white">
          <h3 className="text-lg font-bold mb-4">🎯 你的成就</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-3 bg-white/10 rounded-lg">
              <div className="flex items-center">
                <span className="text-2xl mr-3">🔥</span>
                <div>
                  <p className="font-medium">连续打卡</p>
                  <p className="text-xs opacity-80">7天</p>
                </div>
              </div>
              <span className="text-2xl font-bold">7/30</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-white/10 rounded-lg">
              <div className="flex items-center">
                <span className="text-2xl mr-3">🏆</span>
                <div>
                  <p className="font-medium">周积分</p>
                  <p className="text-xs opacity-80">Top 15%</p>
                </div>
              </div>
              <span className="text-2xl font-bold">850</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-white/10 rounded-lg">
              <div className="flex items-center">
                <span className="text-2xl mr-3">⭐</span>
                <div>
                  <p className="font-medium">徽章解锁</p>
                  <p className="text-xs opacity-80">12/20</p>
                </div>
              </div>
              <span className="text-2xl font-bold">60%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
);

// 社区动态组件
const CommunityPostsSection = () => (
  <div className="space-y-6">
    <Card>
      <div className="flex items-center space-x-3 mb-4">
        <div className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center text-white">
          F
        </div>
        <Input placeholder="分享你的经验或提问..." size="large" />
        <Button type="primary">发布</Button>
      </div>
    </Card>

    <div className="space-y-4">
      {COMMUNITY_POSTS.map((post) => (
        <Card key={post.id} className="hover:shadow-lg transition-shadow">
          <List.Item>
            <List.Item.Meta
              avatar={<Avatar size="large" src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${post.author}`} />}
              title={
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-gray-800">{post.author}</span>
                  <span className="text-xs text-gray-500">{post.timestamp}</span>
                </div>
              }
              description={
                <div>
                  <p className="text-gray-600 mb-2">{post.content}</p>
                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    <button className="flex items-center hover:text-red-500">
                      <StarOutlined className="mr-1" />
                      {post.likes} 赞
                    </button>
                    <button className="flex items-center hover:text-blue-500">
                      <ShareAltOutlined className="mr-1" />
                      {post.comments} 评论
                    </button>
                  </div>
                </div>
              }
            />
          </List.Item>
        </Card>
      ))}
    </div>
  </div>
);

// 专家问答组件
const ExpertQASession = () => (
  <div className="space-y-6">
    <div className="bg-gradient-to-r from-blue-500 to-cyan-600 rounded-2xl p-8 text-white">
      <h3 className="text-2xl font-bold mb-2">Ask the Experts</h3>
      <p className="opacity-90 mb-4">专业医生、营养师、健身教练为你解答疑问</p>
      <div className="flex items-center space-x-4">
        {[
          { icon: '👨‍⚕️', name: '李医生', specialty: '营养学' },
          { icon: '👩‍🍳', name: '张营养师', specialty: '饮食计划' },
          { icon: '健身教练', name: '王教练', specialty: '运动训练' },
        ].map((expert, index) => (
          <div key={index} className="bg-white/20 backdrop-blur-sm p-3 rounded-lg text-center">
            <div className="text-2xl mb-1">{expert.icon}</div>
            <div className="text-sm font-semibold">{expert.name}</div>
            <div className="text-xs opacity-80">{expert.specialty}</div>
          </div>
        ))}
      </div>
    </div>

    <div className="space-y-4">
      {EXPERT问答.map((qa) => (
        <Card key={qa.id} className="hover:shadow-lg transition-shadow">
          <div className="flex justify-between items-start">
            <div className="flex items-start space-x-4">
              <div className="w-12 h-12 rounded-full bg-gradient-to-r from-green-500 to-teal-600 flex items-center justify-center text-white text-xl">
                👨‍⚕️
              </div>
              <div>
                <h4 className="font-semibold text-lg text-gray-800 mb-2">{qa.question}</h4>
                <div className="flex items-center space-x-4 text-sm text-gray-500">
                  <span className="text-green-600 font-medium">{qa.expert}</span>
                  <span className="px-2 py-1 bg-green-100 text-green-700 rounded-lg text-xs">已回答</span>
                </div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-yellow-500 mb-1">{qa.likes}</div>
              <span className="text-xs text-gray-500">赞同</span>
            </div>
          </div>
          <div className="mt-4 p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-gray-700">
              <strong>{qa.expert}：</strong>
              {' '}
              建议根据个人情况制定饮食计划，包括蛋白质、碳水化合物和脂肪的合理搭配...
            </p>
          </div>
          <div className="mt-4 text-right">
            <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">查看完整回答</button>
          </div>
        </Card>
      ))}
    </div>
  </div>
);

export default CommunityFeatures;
