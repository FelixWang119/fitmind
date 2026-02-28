/**
 * 科学量化展示组件
 * 包含数据可视化、趋势分析、证据支持建议、健康评分系统
 */

import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Tabs, 
  Row, 
  Col, 
  Statistic, 
  Badge, 
  Progress, 
  Timeline,
  Tooltip,
  Typography,
  Divider,
  Space,
  Select,
  Dropdown,
  Menu
} from 'antd';
import { 
  LineChart, 
  Line, 
  AreaChart, 
  Area, 
  BarChart, 
  Bar, 
  PieChart, 
  Pie, 
  Cell, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip as RechartsTooltip, 
  Legend,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  ZAxis
} from 'recharts';
import { 
  TrendingUp, 
  TrendingDown, 
  Target, 
  InfoCircle, 
  Balloon,
  Flask,
  BookOpen,
  CheckCircle
} from 'lucide-react';
import { useAuthStore } from '../../../store/authStore';

// 类型定义
interface HealthScoreData {
  overall: number;
  exercise: number;
  nutrition: number;
  sleep: number;
  weight: number;
}

interface TrendData {
  date: string;
  value: number;
  target: number;
  category: string;
}

interface EvidenceItem {
  id: string;
  title: string;
  description: string;
  evidenceLevel: 'A' | 'B' | 'C';
  source: string;
  date: string;
}

// 模拟数据
const MOCK_HEALTH_SCORE: HealthScoreData = {
  overall: 78,
  exercise: 85,
  nutrition: 72,
  sleep: 88,
  weight: 68,
};

const MOCK_WEEKLY_TRENDS: TrendData[] = [
  { date: '周一', value: 65, target: 70, category: 'weight' },
  { date: '周二', value: 64, target: 70, category: 'weight' },
  { date: '周三', value: 63.5, target: 70, category: 'weight' },
  { date: '周四', value: 64, target: 70, category: 'weight' },
  { date: '周五', value: 63.2, target: 70, category: 'weight' },
  { date: '周六', value: 63.8, target: 70, category: 'weight' },
  { date: '周日', value: 63.5, target: 70, category: 'weight' },
];

const MOCK_MONTHLY_TRENDS: TrendData[] = [
  { date: '第1周', value: 65.2, target: 60, category: 'weight' },
  { date: '第2周', value: 63.8, target: 60, category: 'weight' },
  { date: '第3周', value: 63.2, target: 60, category: 'weight' },
  { date: '第4周', value: 62.5, target: 60, category: 'weight' },
];

const MOCK_STEP_TRENDS: TrendData[] = [
  { date: '周一', value: 6500, target: 10000, category: 'exercise' },
  { date: '周二', value: 7200, target: 10000, category: 'exercise' },
  { date: '周三', value: 8500, target: 10000, category: 'exercise' },
  { date: '周四', value: 9200, target: 10000, category: 'exercise' },
  { date: '周五', value: 7800, target: 10000, category: 'exercise' },
  { date: '周六', value: 12500, target: 10000, category: 'exercise' },
  { date: '周日', value: 5800, target: 10000, category: 'exercise' },
];

const MOCK_EVIDENCES: EvidenceItem[] = [
  { id: '1', title: '每日步数建议', description: '基于WHO指南，成年人每日应至少步行8000步', evidenceLevel: 'A', source: 'WHO', date: '2024-01-15' },
  { id: '2', title: '热量赤字原则', description: '每周减少7000千卡可减重约1公斤', evidenceLevel: 'A', source: 'NIH', date: '2024-01-10' },
  { id: '3', title: '运动强度建议', description: '中等强度运动（60-70%最大心率）最适合减脂', evidenceLevel: 'B', source: 'ACSM', date: '2024-01-08' },
  { id: '4', title: '蛋白质摄入', description: '减脂期建议每日蛋白质摄入1.2-1.6g/kg体重', evidenceLevel: 'A', source: ' ISSN', date: '2024-01-05' },
  { id: '5', title: '睡眠质量', description: '每晚7-9小时优质睡眠有助于体重管理', evidenceLevel: 'B', source: 'NSF', date: '2024-01-03' },
  { id: '6', title: '连续打卡效应', description: '连续打卡7天以上形成习惯的概率提高50%', evidenceLevel: 'C', source: '行为心理学研究', date: '2024-01-01' },
];

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

// 自定义图表组件
const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-200">
        <p className="font-semibold text-gray-800">{label}</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} style={{ color: entry.color }}>
            {entry.name}: {entry.value}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

// 主组件
export const ScientificQuantitativeDisplay: React.FC = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [timeRange, setTimeRange] = useState<'week' | 'month' | 'quarter'>('month');
  const [userProfile, setUserProfile] = useState({
    age: 28,
    gender: 'male',
    height: 175,
    weight: 72,
    targetWeight: 65,
  });

  // 健康评分计算
  const calculateHealthScore = (): HealthScoreData => {
    return {
      overall: 78,
      exercise: 85,
      nutrition: 72,
      sleep: 88,
      weight: 68,
    };
  };

  // 趋势分析组件
  const TrendAnalysisSection = () => (
    <div className="space-y-6">
      {/* 时间范围选择 */}
      <div className="flex justify-between items-center">
        <h3 className="text-xl font-bold text-gray-800 flex items-center">
          <TrendingUp className="w-6 h-6 mr-2 text-blue-500" />
          健康趋势分析
        </h3>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600">时间范围：</span>
          <Select 
            value={timeRange} 
            onChange={setTimeRange}
            style={{ width: 120 }}
          >
            <Select.Option value="week">最近7天</Select.Option>
            <Select.Option value="month">最近30天</Select.Option>
            <Select.Option value="quarter">最近90天</Select.Option>
          </Select>
        </div>
      </div>

      {/* 体重趋势图 */}
      <Card className="hover:shadow-lg transition-shadow">
        <div className="mb-4">
          <h4 className="font-semibold text-gray-800 mb-2">体重变化趋势</h4>
          <p className="text-sm text-gray-500">
            你的体重从 {MOCK_MONTHLY_TRENDS[0].value}kg 降至 {MOCK_MONTHLY_TRENDS[MOCK_MONTHLY_TRENDS.length - 1].value}kg
          </p>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={timeRange === 'month' ? MOCK_MONTHLY_TRENDS : MOCK_WEEKLY_TRENDS}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="date" />
            <YAxis domain={[60, 70]} />
            <RechartsTooltip content={<CustomTooltip />} />
            <Legend />
            <Area 
              type="monotone" 
              dataKey="value" 
              name="实际体重(kg)" 
              stroke="#8884d8" 
              fill="#8884d8" 
              fillOpacity={0.3} 
            />
            <Area 
              type="monotone" 
              dataKey="target" 
              name="目标体重(kg)" 
              stroke="#82ca9d" 
              fill="#82ca9d" 
              fillOpacity={0.3} 
            />
          </AreaChart>
        </ResponsiveContainer>
      </Card>

      {/* 步数趋势图 */}
      <Card className="hover:shadow-lg transition-shadow">
        <div className="mb-4">
          <h4 className="font-semibold text-gray-800 mb-2">每日步数趋势</h4>
          <p className="text-sm text-gray-500">
            你的日均步数从 {MOCK_STEP_TRENDS[0].value} 步提升到最高 {Math.max(...MOCK_STEP_TRENDS.map(t => t.value))} 步
          </p>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={MOCK_STEP_TRENDS}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="date" />
            <YAxis />
            <RechartsTooltip content={<CustomTooltip />} />
            <Bar 
              dataKey="value" 
              name="实际步数" 
              fill="#0088FE" 
              radius={[4, 4, 0, 0]} 
            />
            <Bar 
              dataKey="target" 
              name="目标步数" 
              fill="#e0e0e0" 
              radius={[4, 4, 0, 0]} 
            />
          </BarChart>
        </ResponsiveContainer>
      </Card>

      {/* 数据洞察卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[
          {
            title: '减重速度',
            value: '0.7kg/周',
            description: '健康减重速度（0.5-1kg/周）',
            icon: <TrendingDown className="w-6 h-6 text-green-500" />,
            color: 'green'
          },
          {
            title: '热量赤字',
            value: '300kcal/天',
            description: '当前热量赤字水平',
            icon: <Flame className="w-6 h-6 text-orange-500" />,
            color: 'orange'
          },
          {
            title: '进度达成率',
            value: '78%',
            description: '本月减重目标达成率',
            icon: <Target className="w-6 h-6 text-blue-500" />,
            color: 'blue'
          },
          {
            title: '稳定性',
            value: '92%',
            description: '体重波动系数',
            icon: <Target className="w-6 h-6 text-purple-500" />,
            color: 'purple'
          },
          {
            title: '习惯形成',
            value: '65天',
            description: '预计完全养成健康习惯所需天数',
            icon: <Clock className="w-6 h-6 text-cyan-500" />,
            color: 'cyan'
          },
          {
            title: '代谢率',
            value: '1680kcal/天',
            description: '预计基础代谢率',
            icon: <Fire className="w-6 h-6 text-red-500" />,
            color: 'red'
          }
        ].map((insight, index) => (
          <Card key={index} className="hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-semibold text-gray-800">{insight.title}</h4>
              <div className={`p-2 rounded-lg bg-${insight.color}-100`}>
                {insight.icon}
              </div>
            </div>
            <p className={`text-3xl font-bold text-gray-800 mb-2`}>{insight.value}</p>
            <p className="text-sm text-gray-500">{insight.description}</p>
          </Card>
        ))}
      </div>
    </div>
  );

  // 健康评分组件
  const HealthScoreSection = () => {
    const scores = calculateHealthScore();
    
    const getScoreColor = (score: number) => {
      if (score >= 90) return 'success';
      if (score >= 80) return 'processing';
      if (score >= 70) return 'warning';
      return 'error';
    };

    const getScoreText = (score: number) => {
      if (score >= 90) return '优秀';
      if (score >= 80) return '良好';
      if (score >= 70) return '较好';
      return '需改进';
    };

    return (
      <div className="space-y-6">
        <div className="text-center mb-6">
          <h3 className="text-2xl font-bold text-gray-800 mb-2">综合健康评分</h3>
          <p className="text-gray-500">基于科学指标计算的健康水平综合评价</p>
        </div>

        {/* 总分环形图 */}
        <div className="flex justify-center mb-8">
          <div className="relative w-48 h-48">
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
              <path
                className="text-gray-200"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none"
                stroke="currentColor"
                strokeWidth="3"
              />
              <path
                className="text-blue-500"
                strokeDasharray={`${scores.overall}, 100`}
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none"
                stroke="currentColor"
                strokeWidth="3"
                strokeDasharray="80, 20"
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center flex-col">
              <span className="text-5xl font-bold text-gray-800">{scores.overall}</span>
              <span className="text-sm text-gray-500">综合得分</span>
              <span className={`text-lg font-semibold ${scores.overall >= 80 ? 'text-green-500' : 'text-yellow-500'}`}>
                {getScoreText(scores.overall)}
              </span>
            </div>
          </div>
        </div>

        {/* 各项得分 */}
        <div className="grid grid-cols-2 gap-4">
          {[
            { name: '运动', score: scores.exercise, icon: '🏃' },
            { name: '饮食', score: scores.nutrition, icon: '🥗' },
            { name: '睡眠', score: scores.sleep, icon: '😴' },
            { name: '体重', score: scores.weight, icon: '⚖️' },
          ].map((item, index) => (
            <Card key={index} className="hover:shadow-lg transition-shadow">
              <div className="flex items-center mb-3">
                <span className="text-2xl mr-2">{item.icon}</span>
                <h4 className="font-semibold text-gray-800">{item.name}</h4>
              </div>
              <Progress 
                percent={item.score} 
                strokeColor={item.score >= 80 ? '#52c41a' : item.score >= 70 ? '#faad14' : '#f5222d'}
                size="small"
              />
              <p className={`text-center mt-2 font-semibold ${item.score >= 80 ? 'text-green-500' : item.score >= 70 ? 'text-yellow-500' : 'text-red-500'}`}>
                {item.score}分 ({getScoreText(item.score)})
              </p>
            </Card>
          ))}
        </div>

        {/* 健康建议 */}
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-xl border border-blue-100">
          <h4 className="font-bold text-lg mb-4 text-gray-800 flex items-center">
            <Lightbulb className="w-5 h-5 text-yellow-500 mr-2" />
            个性化健康建议
          </h4>
          <div className="space-y-3">
            {[
              {
                title: '饮食建议',
                text: '增加蛋白质摄入，减少精制碳水化合物',
                reason: '根据你的拉格朗日日志分析，蛋白质摄入不足可能导致肌肉流失',
                evidence: '证据等级：A - 多项随机对照试验支持',
                source: '营养学会指南 (2024)'
              },
              {
                title: '运动建议',
                text: '增加HIIT训练频率至每周2次',
                reason: '你的基础代谢率较高，HIIT训练能最大化燃脂效果',
                evidence: '证据等级：A - ACSM推荐',
                source: '美国运动医学会 (ACSM)'
              },
              {
                title: '睡眠建议',
                text: '保持规律作息，睡前1小时停止使用电子设备',
                reason: '你的睡眠质量评分优秀，继续保持',
                evidence: '证据等级：B - 睡眠研究共识',
                source: '国家睡眠基金会 (NSF)'
              }
            ].map((item, index) => (
              <div key={index} className="bg-white p-4 rounded-lg shadow-sm">
                <div className="flex items-start">
                  <span className="text-xl mr-3">💡</span>
                  <div className="flex-1">
                    <h5 className="font-semibold text-gray-800 mb-2">{item.title}</h5>
                    <p className="text-gray-700 mb-2">{item.text}</p>
                    <div className="bg-blue-50 p-3 rounded-lg">
                      <p className="text-sm text-blue-800">
                        <strong>原因：</strong> {item.reason}
                      </p>
                    </div>
                    <div className="mt-2 bg-green-50 p-2 rounded-lg">
                      <p className="text-xs text-green-800">
                        <strong>证据：</strong> {item.evidence} <br/>
                        <strong>来源：</strong> {item.source}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  // 证据支持组件
  const EvidenceSupportSection = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-xl font-bold text-gray-800 flex items-center">
          <Flask className="w-6 h-6 mr-2 text-purple-500" />
          科学证据支持
        </h3>
        <div className="text-sm text-gray-500">
          基于循证医学和科学研究的健康建议
        </div>
      </div>

      {/* 证据等级说明 */}
      <div className="bg-gray-50 p-6 rounded-xl border border-gray-200">
        <h4 className="font-semibold text-gray-800 mb-3">证据等级说明</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-green-50 p-4 rounded-lg border border-green-200">
            <div className="flex items-center mb-2">
              <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center text-white font-bold text-lg">A</div>
              <span className="ml-2 font-semibold text-green-800">高级证据</span>
            </div>
            <p className="text-sm text-gray-700">
              多项随机对照试验的系统评价，科学共识程度最高
            </p>
          </div>
          <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
            <div className="flex items-center mb-2">
              <div className="w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center text-white font-bold text-lg">B</div>
              <span className="ml-2 font-semibold text-yellow-800">中级证据</span>
            </div>
            <p className="text-sm text-gray-700">
              观察性研究和专家共识，具有较强参考价值
            </p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg border border-gray-300">
            <div className="flex items-center mb-2">
              <div className="w-8 h-8 bg-gray-500 rounded-full flex items-center justify-center text-white font-bold text-lg">C</div>
              <span className="ml-2 font-semibold text-gray-800">基础证据</span>
            </div>
            <p className="text-sm text-gray-700">
              个案报告和专家意见，作为补充参考
            </p>
          </div>
        </div>
      </div>

      {/* 证据列表 */}
      <div className="space-y-4">
        {MOCK_EVIDENCES.map((evidence) => (
          <Card key={evidence.id} className="hover:shadow-lg transition-shadow">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <div className="flex items-center mb-2">
                  <h4 className="font-semibold text-gray-800 mr-3">{evidence.title}</h4>
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${
                    evidence.evidenceLevel === 'A' ? 'bg-green-100 text-green-800' :
                    evidence.evidenceLevel === 'B' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    证据等级：{evidence.evidenceLevel}
                  </span>
                </div>
                <p className="text-gray-600 mb-3">{evidence.description}</p>
                <div className="flex flex-wrap items-center gap-4 text-xs text-gray-500">
                  <span className="flex items-center">
                    <BookOpen className="w-3 h-3 mr-1" />
                    来源：{evidence.source}
                  </span>
                  <span className="flex items-center">
                    <Calendar className="w-3 h-3 mr-1" />
                    {evidence.date}
                  </span>
                </div>
              </div>
              <div className="p-2">
                <InfoCircle className="w-6 h-6 text-gray-400 hover:text-blue-500 cursor-pointer" />
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* 建议相关性卡片 */}
      <div className="bg-gradient-to-r from-indigo-50 to-purple-50 p-6 rounded-xl border border-indigo-100">
        <h4 className="font-bold text-lg mb-4 text-gray-800 flex items-center">
          <Target className="w-5 h-5 text-purple-500 mr-2" />
          你的个性化建议来源
        </h4>
        <div className="space-y-2">
          {[
            { suggestion: '控制每日热量摄入', evidenceId: '2', related: true },
            { suggestion: '增加蛋白质摄入', evidenceId: '4', related: true },
            { suggestion: '保证充足睡眠', evidenceId: '5', related: true },
            { suggestion: '增加步数', evidenceId: '1', related: false },
          ].map((item, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-white rounded-lg border border-gray-200">
              <div className="flex items-center">
                <span className={`text-sm font-medium mr-3 ${item.related ? 'text-blue-600' : 'text-gray-500'}`}>
                  {item.suggestion}
                </span>
                {item.related && (
                  <span className="text-xs text-green-600 bg-green-50 px-2 py-1 rounded-full">
                    相关证据
                  </span>
                )}
              </div>
              <button className="text-blue-500 hover:text-blue-700 text-sm">
                查看证据
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  // 趋势图表组件
  const ChartSection = () => (
    <div className="space-y-6">
      <h3 className="text-xl font-bold text-gray-800 mb-6">数据可视化</h3>
      
      {/* 统计卡片网格 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          { label: '当前体重', value: '72kg', unit: '', color: 'blue', trend: -0.5, trendLabel: '↓ 0.5kg' },
          { label: '目标体重', value: '65kg', unit: '', color: 'green', trend: null, trendLabel: '' },
          { label: '减重进度', value: '9.7%', unit: '', color: 'purple', trend: null, trendLabel: '完成' },
          { label: 'BMI指数', value: '23.4', unit: '', color: 'orange', trend: -0.3, trendLabel: '↓ 0.3' },
          { label: '体脂率', value: '21.5%', unit: '', color: 'red', trend: -0.8, trendLabel: '↓ 0.8%' },
          { label: '肌肉量', value: '48.2kg', unit: '', color: 'cyan', trend: 0.6, trendLabel: '↑ 0.6kg' },
          { label: '基础代谢', value: '1680', unit: 'kcal/day', color: 'yellow', trend: 12, trendLabel: '↑ 12kcal' },
          { label: '水分含量', value: '58.5%', unit: '', color: 'blue', trend: 1.2, trendLabel: '↑ 1.2%' },
        ].map((stat, index) => (
          <Card key={index} className="hover:shadow-lg transition-shadow">
            <div className="flex justify-between items-start mb-3">
              <div>
                <p className="text-gray-500 text-sm">{stat.label}</p>
                <p className="text-2xl font-bold text-gray-800 mt-1">
                  {stat.value} <span className="text-sm text-gray-500">{stat.unit}</span>
                </p>
              </div>
              <div className={`px-2 py-1 rounded text-xs font-medium ${
                stat.color === 'blue' ? 'bg-blue-100 text-blue-800' :
                stat.color === 'green' ? 'bg-green-100 text-green-800' :
                stat.color === 'purple' ? 'bg-purple-100 text-purple-800' :
                stat.color === 'orange' ? 'bg-orange-100 text-orange-800' :
                stat.color === 'red' ? 'bg-red-100 text-red-800' :
                stat.color === 'cyan' ? 'bg-cyan-100 text-cyan-800' :
                'bg-yellow-100 text-yellow-800'
              }`}>
                {stat.trend > 0 ? '↑' : stat.trend < 0 ? '↓' : ''}
                {stat.trendLabel}
              </div>
            </div>
            <Progress percent={Math.random() * 100} size="small" showInfo={false} />
          </Card>
        ))}
      </div>

      {/* 健康状态雷达图 */}
      <Card className="hover:shadow-lg transition-shadow">
        <h4 className="font-semibold text-gray-800 mb-4">健康状态雷达图</h4>
        <ResponsiveContainer width="100%" height={400}>
          <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" dataKey="x" name="时间" unit="天" />
            <YAxis type="number" dataKey="y" name="数值" />
            <ZAxis type="number" dataKey="z" range={[60, 150]} name="体重" unit="kg" />
            <RechartsTooltip cursor={{ strokeDasharray: '3 3' }} content={<CustomTooltip />} />
            <Legend />
            <Scatter name="体重变化" data={[
              { x: 0, y: 72, z: 100 },
              { x: 7, y: 71.5, z: 110 },
              { x: 14, y: 71, z: 120 },
              { x: 21, y: 70.5, z: 130 },
              { x: 28, y: 70, z: 140 },
            ]} fill="#8884d8" />
          </ScatterChart>
        </ResponsiveContainer>
      </Card>

      {/* 消费热力图 */}
      <Card className="hover:shadow-lg transition-shadow">
        <h4 className="font-semibold text-gray-800 mb-4">热量消耗热力图</h4>
        <div className="bg-gradient-to-r from-green-500 to-teal-600 rounded-lg p-8 text-center text-white">
          <h3 className="text-2xl font-bold mb-2">周消耗：3,500 kcal</h3>
          <p className="opacity-90">相当于减重0.5公斤，ROP继续加油！</p>
        </div>
      </Card>
    </div>
  );

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">📊 科学量化展示</h1>
            <p className="text-gray-600 mt-2">基于数据驱动的健康管理和证据支持建议</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <p className="text-sm text-gray-500">最近更新</p>
              <p className="text-sm font-medium text-gray-800">2024-01-15</p>
            </div>
            <div className="flex items-center space-x-2 px-4 py-2 bg-white rounded-lg border border-gray-200 shadow-sm">
              <div className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold">
                F
              </div>
              <div>
                <p className="text-sm font-semibold">Felix</p>
                <p className="text-xs text-gray-500">ID: 789012</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <Tabs 
        activeKey={activeTab} 
        onChange={setActiveTab}
        items={[
          {
            key: 'dashboard',
            label: '仪表盘',
            children: <ChartSection />,
            icon: <TrendingUp className="w-4 h-4" />,
          },
          {
            key: 'trend',
            label: '趋势分析',
            children: <TrendAnalysisSection />,
            icon: <LineChartIcon className="w-4 h-4" />,
          },
          {
            key: 'score',
            label: '健康评分',
            children: <HealthScoreSection />,
            icon: <Target className="w-4 h-4" />,
          },
          {
            key: 'evidence',
            label: '证据支持',
            children: <EvidenceSupportSection />,
            icon: <Flask className="w-4 h-4" />,
          },
        ]}
      />
    </div>
  );
};

export default ScientificQuantitativeDisplay;
