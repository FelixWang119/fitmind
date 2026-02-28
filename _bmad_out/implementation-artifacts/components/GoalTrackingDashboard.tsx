import React, { useState, useEffect } from 'react';
import { 
  TrendingDown, 
  TrendingUp, 
  Target, 
  Clock, 
  Activity, 
  Utensils, 
  Brain,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { Progress, Card, Badge, Button } from '@/components/ui';

/**
 * 目标追踪仪表盘 - P1-4 模块
 * 显示用户在体重、运动、饮食三个维度的目标完成进度
 */
export function GoalTrackingDashboard() {
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('7d');
  const [showDetails, setShowDetails] = useState(false);

  // 模拟数据 - 实际应该从 store 或 API 获取
  const mockData = {
    weight: {
      current: 92.5,
      target: 75.0,
      change: -0.3,
      unit: 'kg',
      progress: 87,
      predictedDays: 45
    },
   运动: {
      current: {
        minutes: 30,
        calories: 2450,
        workoutCount: 3
      },
      target: {
        minutes: 45,
        calories: 3000,
        workoutCount: 5
      },
      unit: '分钟',
      progress: 67,
      trend: 'up'
    },
   饮食: {
      current: {
        calories: 1850,
        protein: 120,
        carbs: 220,
        fat: 65
      },
      target: {
        calories: 2000,
        protein: 140,
        carbs: 250,
        fat: 70
      },
      unit: 'kcal',
      progress: 93,
      caloricBalance: 150, // 余额
      balanceStatus: 'good' // good (充足), warning (接近), danger (超限)
    }
  };

  const trendData = {
    体重: [93.2, 92.8, 93.5, 92.5, 92.3, 92.0, 92.5], // 最近7天
    运动: [25, 30, 28, 35, 40, 30, 30],
    饮食摄入: [2100, 1950, 2050, 1850, 1900, 1850, 1850],
    运动消耗: [2200, 2350, 2400, 2550, 2600, 2450, 2450]
  };

  // 计算趋势（用于图表）
  const calculateTrend = (data: number[]) => {
    if (data.length < 2) return 'neutral';
    const lastTwo = data.slice(-2);
    const diff = lastTwo[1] - lastTwo[0];
    if (Math.abs(diff) < 0.5) return 'neutral';
    return diff > 0 ? 'up' : 'down';
  };

  const formatNumber = (num: number, decimals = 1) => 
    num.toFixed(decimals);

  const getBalanceColor = (status: string) => {
    switch (status) {
      case 'good': return 'text-green-600 bg-green-50';
      case 'warning': return 'text-orange-600 bg-orange-50';
      case 'danger': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <div className="space-y-6 pb-4">
      {/* 时间范围切换 */}
      <div className="flex justify-center space-x-2">
        {(['7d', '30d', '90d'] as const).map((range) => (
          <button
            key={range}
            onClick={() => setTimeRange(range)}
            className={`
              px-4 py-1.5 rounded-full text-sm font-medium transition-all
              ${timeRange === range 
                ? 'bg-primary-600 text-white shadow-md' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}
            `}
          >
            {range === '7d' ? '7天' : range === '30d' ? '30天' : '90天'}
          </button>
        ))}
      </div>

      {/* 1. 体重追踪卡片 */}
      <Card className="p-4 border-t-4 border-t-primary-500 shadow-sm">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center space-x-2 mb-2">
              <TrendingDown className="w-5 h-5 text-primary-600" />
              <h3 className="text-base font-semibold text-gray-900">体重目标追踪</h3>
            </div>
            <div className="space-y-1">
              <div className="flex justify-between items-end">
                <span className="text-sm text-gray-500">当前体重</span>
                <span className="text-2xl font-bold text-gray-900">
                  {formatNumber(mockData.weight.current)}<span className="text-sm text-gray-500 ml-1">{mockData.weight.unit}</span>
                </span>
              </div>
              <div className="flex items-center space-x-3 text-sm text-gray-600">
                <span className={mockData.weight.change < 0 ? 'text-green-600 flex items-center' : 'text-red-600 flex items-center'}>
                  {mockData.weight.change < 0 ? <TrendingDown className="w-3 h-3 mr-1" /> : <TrendingUp className="w-3 h-3 mr-1" />}
                  {Math.abs(mockData.weight.change)}kg
                </span>
                <span>•</span>
                <span className="text-primary-600 font-medium">目标: {formatNumber(mockData.weight.target)}kg</span>
              </div>
            </div>
          </div>
          <div className="text-right">
            <div className="flex items-center justify-end space-x-1 mb-2">
              <Target className="w-4 h-4 text-primary-500" />
              <span className="text-xs font-medium text-gray-500">完成度</span>
            </div>
            <div className="text-3xl font-bold text-primary-600">{mockData.weight.progress}%</div>
            <p className="text-xs text-gray-500 mt-1 flex items-center justify-end">
              <Clock className="w-3 h-3 mr-1" />
              预计{mockData.weight.predictedDays}天达成
            </p>
          </div>
        </div>
        
        {/* 进度条 - 移动端优先显示线性 */}
        <div className="mt-4">
          <div className="flex justify-between text-xs text-gray-500 mb-1">
            <span>0kg</span>
            <span>目标达成</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <div 
              className={`h-3 rounded-full transition-all duration-500 ${
                mockData.weight.progress >= 100 ? 'bg-green-600' : 
                mockData.weight.progress >= 90 ? 'bg-orange-500' : 'bg-primary-600'
              }`}
              style={{ width: `${mockData.weight.progress}%` }}
            />
          </div>
        </div>
        
        {/* 详情展开区域 */}
        {showDetails && (
          <div className="mt-3 pt-3 border-t border-gray-100 animate-fade-in">
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <span className="text-gray-500 block text-xs mb-1">本周变化</span>
                <span className={calculateTrend(trendData.体重) === 'down' ? 'text-green-600 font-medium' : 'text-red-600 font-medium'}>
                  {calculateTrend(trendData.体重) === 'down' ? '✔️ ' : '⚠️ '}{Math.abs(trendData.体重[6] - trendData.体重[0]).toFixed(1)}kg
                </span>
              </div>
              <div>
                <span className="text-gray-500 block text-xs mb-1">平台期</span>
                <span className={trendData.体重.filter(x => Math.abs(x - trendData.体重[6]) < 0.3).length > 2 ? 'text-orange-600 font-medium' : 'text-green-600 font-medium'}>
                  {trendData.体重.filter(x => Math.abs(x - trendData.体重[6]) < 0.3).length > 2 ? '2天' : '无'}
                </span>
              </div>
            </div>
          </div>
        )}
        
        {/* 展开/收起按钮 */}
        <button 
          onClick={() => setShowDetails(!showDetails)}
          className="mt-3 flex items-center text-xs text-primary-600 hover:text-primary-700"
        >
          {showDetails ? <ChevronUp className="w-4 h-4 mr-1" /> : <ChevronDown className="w-4 h-4 mr-1" />}
          {showDetails ? '收起详情' : '查看详细分析'}
        </button>
      </Card>

      {/* 2. 运动追踪卡片 */}
      <Card className="p-4 border-t-4 border-t-green-500 shadow-sm">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center space-x-2 mb-2">
              <Activity className="w-5 h-5 text-green-600" />
              <h3 className="text-base font-semibold text-gray-900">运动目标追踪</h3>
            </div>
            <div className="space-y-1">
              <div className="flex justify-between items-end">
                <span className="text-sm text-gray-500">今日运动</span>
                <span className="text-2xl font-bold text-gray-900">
                  {mockData运动.current.minutes}<span className="text-sm text-gray-500 ml-1">{mockData运动.unit}</span>
                </span>
              </div>
              <div className="flex items-center space-x-3 text-sm text-gray-600">
                <span className="text-green-600 flex items-center">
                  <Target className="w-3 h-3 mr-1" />
                  <span className="text-xs">目标: {mockData运动.target.minutes}分钟</span>
                </span>
                <span>•</span>
                <span className="flex items-center text-gray-500">
                  <Activity className="w-3 h-3 mr-1" />
                  {mockData运动.current.calories}kcal消耗
                </span>
              </div>
            </div>
          </div>
          <div className="text-right">
            <div className="flex items-center justify-end space-x-1 mb-2">
              <Target className="w-4 h-4 text-green-500" />
              <span className="text-xs font-medium text-gray-500">完成度</span>
            </div>
            <div className="text-3xl font-bold text-green-600">{mockData运动.progress}%</div>
            <p className="text-xs text-gray-500 mt-1 flex items-center justify-end">
              {mockData运动.current.workoutCount}次/ {mockData运动.target.workoutCount}次目标
            </p>
          </div>
        </div>
        
        {/* 进度条 - 环形 + 线性组合 */}
        <div className="mt-4 flex items-center justify-between">
          {/* 环形进度 */}
          <div className="relative w-16 h-16 flex-shrink-0">
            <svg className="w-full h-full transform -rotate-90">
              <circle
                className="text-gray-200"
                strokeWidth="8"
                stroke="currentColor"
                fill="transparent"
                r="24"
                cx="32"
                cy="32"
              />
              <circle
                className={`transition-all duration-500 ${
                  mockData运动.progress >= 100 ? 'text-green-600' : 
                  mockData运动.progress >= 80 ? 'text-green-500' : 'text-green-400'
                }`}
                strokeWidth="8"
                strokeDasharray={150}
                strokeDashoffset={150 - (150 * mockData运动.progress / 100)}
                strokeLinecap="round"
                stroke="currentColor"
                fill="transparent"
                r="24"
                cx="32"
                cy="32"
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center text-xs font-semibold">
              {mockData运动.progress}%
            </div>
          </div>
          
          {/* 线性进度 */}
          <div className="flex-1 ml-4 mr-8">
            <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
              <div 
                className={`h-2 rounded-full transition-all duration-500 ${
                  mockData运动.progress >= 100 ? 'bg-green-600' : 
                  mockData运动.progress >= 80 ? 'bg-green-500' : 'bg-green-400'
                }`}
                style={{ width: `${mockData运动.progress}%` }}
              />
            </div>
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>{mockData运动.current.minutes}分钟</span>
              <span>{mockData运动.target.minutes}分钟目标</span>
            </div>
          </div>
        </div>
      </Card>

      {/* 3. 饮食追踪卡片 */}
      <Card className="p-4 border-t-4 border-t-orange-500 shadow-sm">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center space-x-2 mb-2">
              <Utensils className="w-5 h-5 text-orange-600" />
              <h3 className="text-base font-semibold text-gray-900">饮食热量追踪</h3>
            </div>
            <div className="space-y-1">
              <div className="flex justify-between items-end">
                <span className="text-sm text-gray-500">今日摄入</span>
                <span className="text-2xl font-bold text-gray-900">
                  {mockData.饮食.current.calories}<span className="text-sm text-gray-500 ml-1">kcal</span>
                </span>
              </div>
              <div className="flex items-center space-x-3 text-sm text-gray-600">
                <span className={mockData.饮食.current.calories > mockData.饮食.target.calories ? 'text-red-600 flex items-center' : 'text-green-600 flex items-center'}>
                  <Target className="w-3 h-3 mr-1" />
                  <span className="text-xs">目标: {mockData.饮食.target.calories}kcal</span>
                </span>
                <span>•</span>
                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getBalanceColor(mockData.饮食.balanceStatus)}`}>
                  热量余额: {mockData.饮食.caloricBalance}kcal
                </span>
              </div>
            </div>
          </div>
          <div className="text-right">
            <div className="flex items-center justify-end space-x-1 mb-2">
              <Target className="w-4 h-4 text-orange-500" />
              <span className="text-xs font-medium text-gray-500">完成度</span>
            </div>
            <div className={`text-3xl font-bold ${
              mockData.饮食.current.calories > mockData.饮食.target.calories ? 'text-orange-600' : 
              mockData.饮食.progress >= 100 ? 'text-orange-500' : 'text-green-600'
            }`}>
              {mockData.饮食.progress}%
            </div>
            <p className="text-xs text-gray-500 mt-1 flex items-center justify-end">
              蛋白质: {mockData.饮食.current.protein}/{mockData.饮食.target.protein}g
            </p>
          </div>
        </div>
        
        {/* 营养素分布环 */}
        <div className="mt-4 flex justify-center space-x-4">
          {[
            { label: '蛋白质', value: mockData.饮食.current.protein, target: mockData.饮食.target.protein, color: 'bg-blue-500' },
            { label: '碳水', value: mockData.饮食.current.carbs, target: mockData.饮食.target.carbs, color: 'bg-yellow-500' },
            { label: '脂肪', value: mockData.饮食.current.fat, target: mockData.饮食.target.fat, color: 'bg-red-500' }
          ].map((nutrient, i) => {
            const progress = Math.min(100, Math.round((nutrient.value / nutrient.target) * 100));
            return (
              <div key={i} className="flex flex-col items-center">
                <div className="relative w-12 h-12 mb-1">
                  <svg className="w-full h-full transform -rotate-90">
                    <circle
                      className="text-gray-200"
                      strokeWidth="6"
                      stroke="currentColor"
                      fill="transparent"
                      r="18"
                      cx="24"
                      cy="24"
                    />
                    <circle
                      className={`${nutrient.color} transition-all duration-500`}
                      strokeWidth="6"
                      strokeDasharray={113}
                      strokeDashoffset={113 - (113 * progress / 100)}
                      strokeLinecap="round"
                      stroke="currentColor"
                      fill="transparent"
                      r="18"
                      cx="24"
                      cy="24"
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center text-[10px] font-bold">
                    {progress}%
                  </div>
                </div>
                <span className="text-xs text-gray-600">{nutrient.label}</span>
              </div>
            );
          })}
        </div>
      </Card>

      {/* 4. 趋势图表组件 */}
      <Card className="p-4 shadow-sm">
        <div className="flex justify-between items-center mb-4">
          <div className="flex items-center space-x-2">
            <TrendingUp className="w-5 h-5 text-primary-600" />
            <h3 className="text-base font-semibold text-gray-900">趋势分析 ({timeRange})</h3>
          </div>
          <div className="flex space-x-2">
            {timeRange === '7d' && <span className="px-2 py-1 bg-primary-100 text-primary-800 text-xs rounded-md">7天</span>}
            {timeRange === '30d' && <span className="px-2 py-1 bg-primary-100 text-primary-800 text-xs rounded-md">30天</span>}
            {timeRange === '90d' && <span className="px-2 py-1 bg-primary-100 text-primary-800 text-xs rounded-md">90天</span>}
          </div>
        </div>
        
        {/* 模拟图表 - 实际应该用 Chart.js */}
        <div className="space-y-3">
          {/* 体重趋势 */}
          <div>
            <div className="flex justify-between text-xs text-gray-500 mb-1">
              <span>体重 (kg)</span>
              <span>当前: {mockData.weight.current}kg</span>
            </div>
            <div className="h-24 flex items-end space-x-1">
              {trendData.体重.map((value, i) => {
                const isLast = i === trendData.体重.length - 1;
                const height = Math.min(100, Math.max(20, (value - 85) / 10 * 100));
                return (
                  <div key={i} className="flex-1 flex flex-col items-center group">
                    <div className="relative w-full flex items-end">
                      <div 
                        className={`w-full rounded-t-sm transition-all duration-500 ${
                          isLast && value < mockData.weight.current 
                            ? 'bg-green-500' 
                            : value < 92 ? 'bg-primary-500' : 'bg-primary-300'
                        }`}
                        style={{ height: `${height}%` }}
                      />
                      {/* 气泡 */}
                      <div 
                        className={`absolute -top-3 w-3 h-3 rounded-full border-2 border-white shadow-sm transition-all duration-300 ${
                          isLast && value < mockData.weight.current ? 'bg-green-500' : 'bg-primary-600'
                        }`}
                        style={{ left: '50%', transform: 'translateX(-50%)' }}
                      />
                    </div>
                    <span className="text-[10px] text-gray-500 mt-1">
                      {['一', '二', '三', '四', '五', '六', '日'][i]}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
          
          {/* 热量平衡趋势 */}
          <div>
            <div className="flex justify-between text-xs text-gray-500 mb-1">
              <span>热量平衡 (kcal)</span>
              <span>摄入(绿) vs 消耗(橙)</span>
            </div>
            <div className="h-24 flex items-center space-x-1">
              <div className="flex-1 flex justify-between items-end space-x-1">
                {trendData.饮食摄入.map((value, i) => {
                  const height = Math.min(100, Math.max(10, (value - 1500) / 1000 * 100));
                  return (
                    <div key={`in-${i}`} className="flex-1 flex flex-col items-center">
                      <div 
                        className="w-full bg-green-400 rounded-t-sm transition-all duration-300"
                        style={{ height: `${height}%` }}
                      />
                    </div>
                  );
                })}
              </div>
              <div className="flex-1 flex justify-between items-start space-x-1 -mt-2">
                {trendData.运动消耗.map((value, i) => {
                  const height = Math.min(100, Math.max(10, (value - 1500) / 1000 * 100));
                  return (
                    <div key={`out-${i}`} className="flex-1 flex flex-col items-center">
                      <div 
                        className="w-full bg-orange-400 rounded-t-sm transition-all duration-300"
                        style={{ height: `${height}%` }}
                      />
                    </div>
                  );
                })}
              </div>
            </div>
            <div className="flex justify-center space-x-6 text-xs text-gray-500 mt-1">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-green-400 rounded-sm mr-1" />
                <span>摄入</span>
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 bg-orange-400 rounded-sm mr-1" />
                <span>消耗</span>
              </div>
            </div>
          </div>
        </div>
      </Card>
      
      {/* 5. AI 反馈卡片 */}
      <AIFeedbackCard />
    </div>
  );
}

/**
 * AI 反馈卡片组件
 * 显示针对用户当前数据的个性化建议
 */
function AIFeedbackCard() {
  const [feedback, setFeedback] = useState<'helpful' | 'unhelpful' | null>(null);
  const [isCollapsed, setIsCollapsed] = useState(false);

  const suggestions = [
    {
      type: 'positive',
      icon: '🌟',
      title: '优秀进展',
      text: '体重持续下降趋势很好！已连续7天 Negative，继续保持～'
    },
    {
      type: 'improvement',
      icon: '🎯',
      title: '优化建议',
      text: '运动量可以再增加10分钟/次会更好。当前平均30分钟，目标是45分钟。'
    },
    {
      type: 'maintenance',
      icon: '🛡️',
      title: '保持现状',
      text: '饮食热量控制非常精准，蛋白质摄入也达标了！这种节奏很可持续。'
    }
  ];

  const getBadgeColor = (type: string) => {
    switch (type) {
      case 'positive': return 'bg-green-100 text-green-800';
      case 'improvement': return 'bg-blue-100 text-blue-800';
      case 'maintenance': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (isCollapsed) {
    return (
      <div className="bg-primary-50 rounded-xl p-3 cursor-pointer hover:bg-primary-100 transition-colors" onClick={() => setIsCollapsed(false)}>
        <p className="text-sm font-medium text-primary-900 flex items-center">
          <Brain className="w-4 h-4 mr-1" />
          AI 看到您的最新数据...
          <ChevronDown className="w-3 h-3 ml-auto" />
        </p>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-br from-primary-50 to-blue-50 rounded-xl p-5 shadow-sm border border-primary-100 animate-fade-in">
      <div className="flex items-start space-x-3 mb-3">
        <div className="bg-primary-600 text-white rounded-full p-1.5 flex-shrink-0">
          <Brain className="w-5 h-5" />
        </div>
        <div className="flex-1">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="font-semibold text-gray-900 flex items-center">
                <span className="text-xl mr-1.5">AI 说...</span>
                <Badge variant="primary" className="ml-2 py-0.5 px-2 text-xs">个性化建议</Badge>
              </h3>
            </div>
            <button 
              onClick={() => setIsCollapsed(true)}
              className="text-primary-600 hover:text-primary-800 ml-2"
            >
              <ChevronDown className="w-5 h-5" />
            </button>
          </div>
          
          <div className="space-y-2 mt-3">
            {suggestions.map((item, index) => (
              <div key={index} className="bg-white rounded-lg p-3 shadow-sm border border-primary-100">
                <div className="flex items-start">
                  <div className={`w-2 h-2 mt-1.5 rounded-full mr-2 flex-shrink-0`} 
                       style={{ backgroundColor: item.type === 'positive' ? '#10B981' : item.type === 'improvement' ? '#3B82F6' : '#F59E0B' }} 
                  />
                  <div>
                    <span className={`inline-block px-2 py-0.5 rounded text-[10px] font-medium mb-1 ${getBadgeColor(item.type)}`}>
                      {item.type === 'positive' ? '✅' : item.type === 'improvement' ? '💡' : '🛡️'} {item.title}
                    </span>
                    <p className="text-sm text-gray-700 leading-relaxed">{item.text}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          {/* 反馈按钮 */}
          <div className="mt-4 pt-3 border-t border-primary-200 flex justify-center space-x-3">
            <button 
              onClick={() => setFeedback('helpful')}
              className={`flex items-center px-4 py-1.5 rounded-full text-sm ${
                feedback === 'helpful' 
                  ? 'bg-primary-600 text-white' 
                  : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300'
              }`}
            >
              <span className="mr-1">👍</span> 有用
            </button>
            <button 
              onClick={() => setFeedback('unhelpful')}
              className={`flex items-center px-4 py-1.5 rounded-full text-sm ${
                feedback === 'unhelpful' 
                  ? 'bg-primary-600 text-white' 
                  : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300'
              }`}
            >
              <span className="mr-1">👎</span> 一般
            </button>
            <button className="px-3 py-1.5 text-sm text-gray-500 hover:text-gray-700 ml-2">
              隐藏
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// 导出所有组件
export { AIFeedbackCard };
