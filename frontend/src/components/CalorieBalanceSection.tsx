import React, { useEffect, useState, useCallback } from 'react';
import { Utensils, Dumbbell, ChevronDown, ChevronUp, AlertCircle, Zap, RefreshCw } from 'lucide-react';
import { getCalorieBalance, getCalorieBalanceHistory, CalorieBalanceData as ApiCalorieBalanceData } from '../services/calorieBalanceService';

// 支持两种数据格式 - 旧的兼容格式和新的API格式
interface CalorieBalanceData {
  // 新API格式
  date?: string;
  intake?: number;
  bmr?: number;
  burn?: number;
  surplus?: number;
  net?: number;
  progress?: number;
  target?: number;
  // 旧兼容格式
  intake_calories?: number;
  basal_metabolism?: number;
  exercise_calories_burned?: number;
}

// 热量栏组件
const CalorieColumn: React.FC<{
  title: string;
  value: number;
  color: string;
  backgroundColor: string;
  icon: React.ReactNode;
  description: string;
  dataSource: string;
  highlight?: boolean;
}> = ({ title, value, color, backgroundColor, icon, description, dataSource, highlight = false }) => {
  const [expanded, setExpanded] = React.useState(false);
  const [showTooltip, setShowTooltip] = React.useState(false);

  return (
    <div className="relative">
      <div 
        className={`
          rounded-xl p-4 transition-all hover:shadow-lg
          ${highlight ? 'ring-2 ring-blue-500 ring-offset-2' : ''}
        `}
        style={{ backgroundColor }}
      >
        <div className="flex items-start justify-between mb-3">
          <div className={`${color} p-2 rounded-lg bg-opacity-20`}>
            {icon}
          </div>
          <div className="relative">
            <button
              onClick={() => setShowTooltip(!showTooltip)}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </button>
            {showTooltip && (
              <div className="absolute right-0 top-full mt-2 w-48 p-3 bg-white border border-gray-200 rounded-lg shadow-xl z-50 animate-fade-in">
                <p className="text-xs font-semibold text-gray-700 mb-1">数据来源</p>
                <p className="text-xs text-gray-600">{dataSource}</p>
              </div>
            )}
          </div>
        </div>
        
        <div className="mb-2">
          <p className="text-sm font-medium text-gray-700">{title}</p>
          <p className="text-xl font-bold text-gray-900">{value} <span className="text-sm font-normal text-gray-500">kcal</span></p>
        </div>
        
        {/* 进度条 */}
        <div className="mt-3">
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div className={`h-full rounded-full`} style={{ width: `${Math.min(100, (value / 2500) * 100)}%`, backgroundColor }} />
          </div>
        </div>
        
        {/* 描述点击展开 */}
        <div className="mt-3">
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-xs text-gray-500 hover:text-blue-600 flex items-center"
          >
            {expanded ? (
              <>
                <ChevronUp className="w-3 h-3 mr-1" />
                收起说明
              </>
            ) : (
              <>
                <ChevronDown className="w-3 h-3 mr-1" />
                查看说明
              </>
            )}
          </button>
          
          {expanded && (
            <div className="mt-2 text-xs text-gray-600 bg-gray-50 p-2 rounded-lg animate-fade-in">
              {description}
            </div>
          )}
        </div>
      </div>
      
      {/* 装饰性光晕 */}
      {highlight && (
        <div className="absolute -inset-1 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl blur opacity-20 animate-pulse" />
      )}
    </div>
  );
};

// 热量平衡汇总卡片
const BalanceSummaryCard: React.FC<{
  intake: number;
  basal: number;
  exercise: number;
}> = ({ intake, basal, exercise }) => {
  const balance = intake - basal - exercise;
  const isDeficit = balance < 0;
  const isSurplus = balance > 0;
  const isNeutral = balance === 0;
  
  return (
    <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl p-6 text-white shadow-xl mt-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">今日热量平衡</h3>
        <div className={`px-3 py-1 rounded-full text-xs font-semibold ${
          isDeficit 
            ? 'bg-green-500 text-green-100' 
            : isSurplus 
              ? 'bg-red-500 text-red-100' 
              : 'bg-blue-500 text-blue-100'
        }`}>
          {isDeficit ? '热量缺口' : isSurplus ? '热量盈余' : '收支平衡'}
        </div>
      </div>
      
      <div className="flex items-center justify-between mb-4">
        <div>
          <p className="text-gray-400 text-sm mb-1">净热量变化</p>
          <p className={`text-4xl font-bold ${isDeficit ? 'text-green-400' : isSurplus ? 'text-red-500' : 'text-white'}`}>
            {Math.abs(balance)}
          </p>
          <p className="text-sm text-gray-400 mt-1">
            {isDeficit ? '向下箭头表示热量缺口，促进减脂' : 
             isSurplus ? '向上箭头表示热量盈余，增加体重' : 
             '水平线表示热量平衡'}
          </p>
        </div>
        
        <div className="text-right">
          <div className={`flex items-center justify-center w-20 h-20 rounded-full ${
            isDeficit ? 'bg-green-500/20' : isSurplus ? 'bg-red-500/20' : 'bg-blue-500/20'
          }`}>
            <div className={`text-2xl font-bold ${isDeficit ? 'text-green-500' : isSurplus ? 'text-red-500' : 'text-blue-500'}`}>
              {isDeficit ? '↓' : isSurplus ? '↑' : '-'}
            </div>
          </div>
        </div>
      </div>
      
      <div className="flex items-center justify-center">
        <div className="relative w-48 h-24">
          <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 50">
            <path d="M10 25 Q50 45 90 25" fill="none" stroke="#e5e7eb" strokeWidth="8" strokeLinecap="round" />
            <path 
              d="M10 25 Q50 45 90 25" 
              fill="none" 
              stroke={isDeficit ? '#22c55e' : isSurplus ? '#ef4444' : '#3b82f6'} 
              strokeWidth="8" 
              strokeLinecap="round"
              strokeDasharray="157"
              strokeDashoffset={Math.min(157, Math.max(0, 157 * (isDeficit ? -0.5 : isSurplus ? 0.5 : 0)))}
              className="transition-all duration-1000 ease-out"
            />
          </svg>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center">
            <p className="text-2xl font-bold">{Math.abs(balance)}</p>
            <p className="text-xs text-gray-400 mt-1">kcal 差异</p>
          </div>
        </div>
      </div>
    </div>
  );
};

// 响应式提示
const ResponsiveHint: React.FC = () => {
  return (
    <div className="bg-yellow-50 border border-yellow-100 rounded-lg p-3 text-sm text-yellow-800 flex items-center">
      <AlertCircle className="w-4 h-4 mr-2 flex-shrink-0" />
      <p>
        💡 <strong>提示：</strong>在手机上会自动转换为垂直滚动布局，方便单手操作。
      </p>
    </div>
  );
};

// 计算公式说明
const FormulaExplanation: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  intakes: number;
  basals: number;
  exercises: number;
}> = ({ isOpen, onClose, intakes, basals, exercises }) => {
  if (!isOpen) return null;
  
  const result = intakes - basals - exercises;
  const isDeficit = result < 0;
  const isSurplus = result > 0;
  
  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-5 animate-fade-in">
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-lg font-semibold text-gray-800 flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 text-blue-500 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          热量计算公式详解
        </h4>
        <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
          <ChevronUp className="w-5 h-5" />
        </button>
      </div>
      
      <div className="space-y-3">
        <div className="bg-blue-50 p-3 rounded-lg border border-blue-100">
          <p className="text-sm text-gray-600">
            <span className="font-semibold text-blue-700">热量盈余 = 摄入热量 - 基础代谢 - 运动消耗</span>
          </p>
        </div>
        
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-gray-50 p-2 rounded-lg">
            <p className="text-xs text-gray-500">摄入热量</p>
            <p className="text-lg font-semibold text-gray-800">{intakes} kcal</p>
            <p className="text-xs text-gray-500">来自饮食记录</p>
          </div>
          
          <div className="bg-gray-50 p-2 rounded-lg">
            <p className="text-xs text-gray-500">基础代谢</p>
            <p className="text-lg font-semibold text-gray-800">{basals} kcal</p>
            <p className="text-xs text-gray-500">身体维持消耗</p>
          </div>
          
          <div className="bg-gray-50 p-2 rounded-lg">
            <p className="text-xs text-gray-500">运动消耗</p>
            <p className="text-lg font-semibold text-gray-800">{exercises} kcal</p>
            <p className="text-xs text-gray-500">来自运动记录</p>
          </div>
          
          <div className="bg-gray-50 p-2 rounded-lg">
            <p className="text-xs text-gray-500">热量盈余</p>
            <p className={`text-lg font-bold ${isDeficit ? 'text-green-600' : isSurplus ? 'text-red-600' : 'text-blue-600'}`}>
              {result} kcal
            </p>
            <p className="text-xs text-gray-500">{isDeficit ? '（热量缺口，促进减脂）' : isSurplus ? '（热量盈余，增加体重）' : '（收支平衡）'}</p>
          </div>
        </div>
        
        <div className="pt-2 border-t border-gray-200">
          <p className="text-xs text-gray-500">
            💡 <strong>健康减重建议：</strong>每天维持 500-1000 kcal 的热量缺口，可实现每周减重 0.5-1 kg
          </p>
        </div>
      </div>
    </div>
  );
};

// 主组件 - 支持手动传入数据或自动获取API数据
export const CalorieBalanceSection: React.FC<{ data?: CalorieBalanceData; autoRefresh?: boolean }> = ({ 
  data: initialData, 
  autoRefresh = true 
}) => {
  const [showFormula, setShowFormula] = useState(false);
  const [data, setData] = useState<CalorieBalanceData>(initialData || {});
  const [loading, setLoading] = useState(!initialData);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // 从API获取热量平衡数据
  const fetchData = useCallback(async (showLoading = true) => {
    try {
      if (showLoading) setIsRefreshing(true);
      const apiData = await getCalorieBalance();
      
      // 转换为组件期望的格式
      const formattedData: CalorieBalanceData = {
        intake_calories: apiData.intake,
        basal_metabolism: apiData.bmr,
        exercise_calories_burned: apiData.burn,
        // 新API字段
        date: apiData.date,
        intake: apiData.intake,
        bmr: apiData.bmr,
        burn: apiData.burn,
        surplus: apiData.surplus,
        net: apiData.net,
        progress: apiData.progress,
        target: apiData.target,
      };
      
      setData(formattedData);
      setLastUpdated(new Date());
    } catch (error) {
      console.error('获取热量平衡数据失败:', error);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  // 初始加载或数据变化时
  useEffect(() => {
    if (initialData) {
      setData(initialData);
      setLoading(false);
    } else if (autoRefresh) {
      fetchData();
    }
  }, [initialData, autoRefresh, fetchData]);

  // 自动刷新 - 每60秒刷新一次 (Story 3.2)
  useEffect(() => {
    if (!autoRefresh || loading) return;
    
    const interval = setInterval(() => {
      fetchData(false);
    }, 60000); // 60秒
    
    return () => clearInterval(interval);
  }, [autoRefresh, loading, fetchData]);

  // 手动刷新函数 (暴露给父组件)
  const handleRefresh = () => {
    fetchData();
  };

  // 获取用于显示的数值
  const intakeValue = data.intake ?? data.intake_calories ?? 0;
  const bmrValue = data.bmr ?? data.basal_metabolism ?? 0;
  const burnValue = data.burn ?? data.exercise_calories_burned ?? 0;
  
  return (
    <div className="space-y-6">
      {/* 刷新按钮和时间显示 */}
      {autoRefresh && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-500">
            {lastUpdated && (
              <span>最后更新: {lastUpdated.toLocaleTimeString()}</span>
            )}
          </div>
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="flex items-center px-3 py-1.5 text-sm bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 mr-1 ${isRefreshing ? 'animate-spin' : ''}`} />
            刷新
          </button>
        </div>
      )}
      
      {loading && (
        <div className="flex items-center justify-center py-8">
          <RefreshCw className="w-6 h-6 animate-spin text-blue-500" />
          <span className="ml-2 text-gray-500">加载中...</span>
        </div>
      )}
      
      {!loading && (
        <>
          {/* 响应式提示 */}
          <ResponsiveHint />
          
          {/* 三栏布局 */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* 摄入栏 */}
            <CalorieColumn
              title="摄入热量"
              value={intakeValue}
              color="bg-orange-500"
              backgroundColor="#fff7ed"
              icon={<Utensils className="w-6 h-6 text-orange-600" />}
              description="来自您记录的三餐及零食，包含蛋白质、碳水化合物和脂肪的热量贡献"
              dataSource="饮食记录 + AI 食物识别"
              highlight
            />
            
            {/* 基础代谢栏 */}
            <CalorieColumn
              title="基础代谢"
              value={bmrValue}
              color="bg-purple-500"
              backgroundColor="#f5f3ff"
              icon={<svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>}
              description="您的身体在静息状态下维持生命所需的最低热量，包括呼吸、血液循环、细胞修复等"
              dataSource="基于您的身体数据计算 (Mifflin-St Jeor 公式)"
            />
            
            {/* 运动消耗栏 */}
            <CalorieColumn
              title="运动消耗"
              value={burnValue}
              color="bg-blue-500"
              backgroundColor="#eff6ff"
              icon={<Dumbbell className="w-6 h-6 text-blue-600" />}
              description="您今天运动所消耗的额外热量，包括有氧运动、力量训练和其他日常活动"
              dataSource="运动记录 + MET 值计算"
            />
          </div>
      
      {/* 计算公式展开 */}
      <div className="relative">
        <button
          onClick={() => setShowFormula(!showFormula)}
          className="w-full text-left px-4 py-3 rounded-xl bg-blue-50 hover:bg-blue-100 border border-blue-200 transition-all flex items-center justify-between"
        >
          <div className="flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 text-blue-500 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="font-medium text-blue-800">查看热量计算公式详解</span>
          </div>
          {showFormula ? <ChevronUp className="w-5 h-5 text-blue-500" /> : <ChevronDown className="w-5 h-5 text-blue-500" />}
        </button>
        
        {showFormula && (
          <FormulaExplanation 
            isOpen={showFormula}
            onClose={() => setShowFormula(false)}
            intakes={intakeValue}
            basals={bmrValue}
            exercises={burnValue}
          />
        )}
      </div>
      
      {/* 热量平衡汇总卡片 */}
      <BalanceSummaryCard 
        intake={intakeValue}
        basal={bmrValue}
        exercise={burnValue}
      />
      
      {/* 数据可视化说明 */}
      <div className="bg-gray-50 rounded-xl p-6 border border-gray-200">
        <h4 className="font-semibold text-gray-800 mb-4">📊 数据可视化说明</h4>
        
        <div className="space-y-3">
          <div className="flex items-center">
            <div className="w-12 h-3 bg-orange-500 rounded-full mr-3"></div>
            <div>
              <p className="text-sm text-gray-700"><strong>摄入热量</strong></p>
              <p className="text-xs text-gray-500">黄色渐变，表示您今天的饮食摄入</p>
            </div>
          </div>
          
          <div className="flex items-center">
            <div className="w-12 h-3 bg-purple-500 rounded-full mr-3"></div>
            <div>
              <p className="text-sm text-gray-700"><strong>基础代谢</strong></p>
              <p className="text-xs text-gray-500">紫色渐变，表示身体维持生命所需</p>
            </div>
          </div>
          
          <div className="flex items-center">
            <div className="w-12 h-3 bg-blue-500 rounded-full mr-3"></div>
            <div>
              <p className="text-sm text-gray-700"><strong>运动消耗</strong></p>
              <p className="text-xs text-gray-500">蓝色渐变，表示运动额外消耗</p>
            </div>
          </div>
          
          <div className="flex items-center">
            <div className="w-12 h-3 bg-gray-200 rounded-full mr-3 relative overflow-hidden">
              <div className="absolute inset-y-0 left-0 w-full bg-blue-600 -skew-x-12 opacity-30"></div>
            </div>
            <div>
              <p className="text-sm text-gray-700"><strong>热量平衡</strong></p>
              <p className="text-xs text-gray-500">左侧绿色表示热量缺口，右侧红色表示热量盈余</p>
            </div>
          </div>
        </div>
      </div>
      
      {/* 实时更新动画说明 */}
      <div className="bg-green-50 rounded-xl p-6 border border-green-200">
        <div className="flex items-start">
          <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6 text-green-600 mr-3 flex-shrink-0 mt-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          <div>
            <h4 className="font-semibold text-green-800 mb-2">⚡ 实时更新警告</h4>
            <p className="text-sm text-green-700">
              您的热量数据实时更新。每当你完成一次饮食记录或运动打卡，右侧的三栏数据会自动刷新。
            </p>
          </div>
        </div>
      </div>
      </>
      )}
    </div>
  );
};