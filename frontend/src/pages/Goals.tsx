/**
 * Goals Page
 * Story 2.2: 目标创建与追踪
 * 显示和管理用户的健康目标
 */

import { useEffect, useState } from 'react';
import { 
  Plus, Target, TrendingUp, TrendingDown, Pause, Play, 
  Check, X, Calendar, Clock, ChevronRight, RefreshCw 
} from 'lucide-react';
import toast from 'react-hot-toast';
import { 
  goalService, 
  Goal, 
  GoalType, 
  GoalStatus,
  getGoalTypeLabel,
  getGoalTypeIcon,
  getGoalStatusLabel,
  getStatusColor,
  formatGoalValue,
  calculateProgress
} from '../services/goalService';

// 目标类型配置
const GOAL_TYPES: { value: GoalType; label: string; icon: string; color: string }[] = [
  { value: 'weight', label: '体重管理', icon: '⚖️', color: '#4CAF50' },
  { value: 'exercise', label: '运动健身', icon: '🏃', color: '#2196F3' },
  { value: 'diet', label: '饮食控制', icon: '🍽️', color: '#FF9800' },
  { value: 'habit', label: '习惯养成', icon: '💪', color: '#9' },
];

//C27B0 状态筛选
const STATUS_FILTERS: { value: GoalStatus | 'all'; label: string }[] = [
  { value: 'all', label: '全部' },
  { value: 'active', label: '进行中' },
  { value: 'completed', label: '已完成' },
  { value: 'paused', label: '已暂停' },
];

export default function Goals() {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [recommendations, setRecommendations] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<GoalStatus | 'all'>('all');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showProgressModal, setShowProgressModal] = useState(false);
  const [selectedGoal, setSelectedGoal] = useState<Goal | null>(null);
  
  // Form state
  const [formData, setFormData] = useState({
    goal_type: 'weight' as GoalType,
    current_value: '',
    target_value: '',
    unit: 'kg',
    target_date: '',
  });
  
  // Progress form
  const [progressValue, setProgressValue] = useState('');
  const [dailyTargetMet, setDailyTargetMet] = useState(false);

  // 加载数据
  const loadData = async () => {
    setLoading(true);
    try {
      const [goalsData, recsData] = await Promise.all([
        goalService.getGoals(statusFilter === 'all' ? undefined : statusFilter),
        goalService.getRecommendations().catch(() => null),
      ]);
      setGoals(goalsData);
      setRecommendations(recsData);
    } catch (error) {
      console.error('加载目标失败:', error);
      toast.error('加载目标失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [statusFilter]);

  // 创建目标
  const handleCreateGoal = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await goalService.createGoal({
        goal_type: formData.goal_type,
        current_value: formData.current_value ? parseFloat(formData.current_value) : undefined,
        target_value: parseFloat(formData.target_value),
        unit: formData.unit,
        target_date: formData.target_date || undefined,
      });
      toast.success('目标创建成功！');
      setShowCreateModal(false);
      resetForm();
      loadData();
    } catch (error: any) {
      console.error('创建目标失败:', error);
      toast.error(error.response?.data?.detail || '创建目标失败');
    }
  };

  // 更新目标状态
  const handleUpdateStatus = async (goalId: number, newStatus: GoalStatus) => {
    try {
      await goalService.updateGoalStatus(goalId, newStatus);
      toast.success(`目标已${newStatus === 'active' ? '恢复' : newStatus === 'paused' ? '暂停' : '取消'}`);
      loadData();
    } catch (error) {
      console.error('更新状态失败:', error);
      toast.error('更新状态失败');
    }
  };

  // 记录进度
  const handleRecordProgress = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedGoal) return;
    
    try {
      await goalService.recordProgress(selectedGoal.goal_id, {
        value: parseFloat(progressValue),
        daily_target_met: dailyTargetMet,
      });
      toast.success('进度记录成功！');
      setShowProgressModal(false);
      setProgressValue('');
      setDailyTargetMet(false);
      loadData();
    } catch (error) {
      console.error('记录进度失败:', error);
      toast.error('记录进度失败');
    }
  };

  // 删除目标
  const handleDeleteGoal = async (goalId: number) => {
    if (!confirm('确定要删除这个目标吗？')) return;
    
    try {
      await goalService.deleteGoal(goalId);
      toast.success('目标已删除');
      loadData();
    } catch (error) {
      console.error('删除目标失败:', error);
      toast.error('删除目标失败');
    }
  };

  // 重置表单
  const resetForm = () => {
    setFormData({
      goal_type: 'weight',
      current_value: '',
      target_value: '',
      unit: 'kg',
      target_date: '',
    });
  };

  // 选择目标类型时更新单位
  const handleGoalTypeChange = (type: GoalType) => {
    setFormData(prev => ({ ...prev, goal_type: type }));
    
    // 根据类型设置默认单位
    const defaultUnits: Record<GoalType, string> = {
      weight: 'kg',
      exercise: '步',
      diet: 'kcal',
      habit: 'ml',
    };
    setFormData(prev => ({ ...prev, unit: defaultUnits[type] }));
  };

  // 打开进度记录弹窗
  const openProgressModal = (goal: Goal) => {
    setSelectedGoal(goal);
    setProgressValue(goal.current_value?.toString() || '');
    setShowProgressModal(true);
  };

  // 打开详情弹窗
  const openDetailModal = (goal: Goal) => {
    setSelectedGoal(goal);
    setShowDetailModal(true);
  };

  // 渲染进度条
  const renderProgressBar = (progress: number, color: string) => (
    <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
      <div 
        className="h-full rounded-full transition-all duration-500"
        style={{ 
          width: `${Math.min(100, progress)}%`,
          backgroundColor: color 
        }}
      />
    </div>
  );

  // 渲染目标卡片
  const renderGoalCard = (goal: Goal) => {
    const typeConfig = GOAL_TYPES.find(t => t.value === goal.goal_type) || GOAL_TYPES[0];
    const progress = calculateProgress(goal.current_value, goal.target_value, goal.goal_type);
    
    return (
      <div 
        key={goal.goal_id}
        className="bg-white rounded-xl shadow-sm border border-gray-100 p-5 hover:shadow-md transition-shadow cursor-pointer"
        onClick={() => openDetailModal(goal)}
      >
        {/* 头部 */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div 
              className="w-10 h-10 rounded-lg flex items-center justify-center text-xl"
              style={{ backgroundColor: typeConfig.color + '20' }}
            >
              {typeConfig.icon}
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">{getGoalTypeLabel(goal.goal_type)}</h3>
              <span 
                className="text-xs px-2 py-0.5 rounded-full"
                style={{ 
                  backgroundColor: getStatusColor(goal.status) + '20',
                  color: getStatusColor(goal.status)
                }}
              >
                {getGoalStatusLabel(goal.status)}
              </span>
            </div>
          </div>
          <button 
            className="p-2 hover:bg-gray-100 rounded-lg"
            onClick={(e) => {
              e.stopPropagation();
              openProgressModal(goal);
            }}
          >
            <Plus className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* 进度 */}
        <div className="mb-3">
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-600">
              当前: {formatGoalValue(goal.current_value, goal.unit)}
            </span>
            <span className="font-medium" style={{ color: typeConfig.color }}>
              {progress.toFixed(0)}%
            </span>
          </div>
          {renderProgressBar(progress, typeConfig.color)}
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>目标: {formatGoalValue(goal.target_value, goal.unit)}</span>
            {goal.predicted_date && (
              <span>预计: {new Date(goal.predicted_date).toLocaleDateString()}</span>
            )}
          </div>
        </div>

        {/* 操作按钮 */}
        <div className="flex gap-2 pt-3 border-t border-gray-100">
          {goal.status === 'active' && (
            <button
              className="flex-1 flex items-center justify-center gap-1 py-2 text-sm text-orange-600 hover:bg-orange-50 rounded-lg"
              onClick={(e) => {
                e.stopPropagation();
                handleUpdateStatus(goal.goal_id, 'paused');
              }}
            >
              <Pause className="w-4 h-4" />
              暂停
            </button>
          )}
          {goal.status === 'paused' && (
            <button
              className="flex-1 flex items-center justify-center gap-1 py-2 text-sm text-green-600 hover:bg-green-50 rounded-lg"
              onClick={(e) => {
                e.stopPropagation();
                handleUpdateStatus(goal.goal_id, 'active');
              }}
            >
              <Play className="w-4 h-4" />
              恢复
            </button>
          )}
          <button
            className="flex-1 flex items-center justify-center gap-1 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg"
            onClick={(e) => {
              e.stopPropagation();
              handleDeleteGoal(goal.goal_id);
            }}
          >
            <X className="w-4 h-4" />
            删除
          </button>
        </div>
      </div>
    );
  };

  // 加载中
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 text-blue-500 animate-spin mx-auto mb-2" />
          <p className="text-gray-500">加载中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold flex items-center gap-2">
                <Target className="w-7 h-7" />
                我的目标
              </h1>
              <p className="text-blue-100 mt-1">追踪你的健康目标，保持动力！</p>
            </div>
            <button
              onClick={() => setShowCreateModal(true)}
              className="bg-white text-blue-600 px-4 py-2 rounded-lg font-medium flex items-center gap-2 hover:bg-blue-50 transition-colors"
            >
              <Plus className="w-5 h-5" />
              新建目标
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto p-6">
        {/* AI 推荐 */}
        {recommendations && (
          <div className="mb-6 bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl p-5 border border-purple-100">
            <h2 className="font-semibold text-purple-900 mb-3 flex items-center gap-2">
              <span>🤖</span> AI 智能推荐
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {Object.entries(recommendations).map(([type, data]: [string, any]) => (
                <div key={type} className="bg-white rounded-lg p-3 shadow-sm">
                  <div className="text-lg mb-1">{getGoalTypeIcon(type as GoalType)}</div>
                  <div className="text-sm font-medium text-gray-700">{getGoalTypeLabel(type as GoalType)}</div>
                  {data?.recommended_target_g && (
                    <div className="text-xs text-gray-500">
                      推荐: {(data.recommended_target_g / 1000).toFixed(1)} kg
                    </div>
                  )}
                  {data?.recommended_range?.min_kg && (
                    <div className="text-xs text-gray-500">
                      范围: {data.recommended_range.min_kg.toFixed(1)}-{data.recommended_range.max_kg.toFixed(1)} kg
                    </div>
                  )}
                  {data?.daily_steps && (
                    <div className="text-xs text-gray-500">
                      每日: {data.daily_steps.toLocaleString()} 步
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 筛选 */}
        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          {STATUS_FILTERS.map(filter => (
            <button
              key={filter.value}
              onClick={() => setStatusFilter(filter.value as GoalStatus | 'all')}
              className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${
                statusFilter === filter.value
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'
              }`}
            >
              {filter.label}
            </button>
          ))}
        </div>

        {/* 目标列表 */}
        {goals.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Target className="w-10 h-10 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">还没有目标</h3>
            <p className="text-gray-500 mb-4">创建你的第一个健康目标吧！</p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <Plus className="w-5 h-5" />
              创建目标
            </button>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {goals.map(renderGoalCard)}
          </div>
        )}
      </div>

      {/* 创建目标弹窗 */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl w-full max-w-md max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-100">
              <h2 className="text-xl font-bold">创建新目标</h2>
            </div>
            <form onSubmit={handleCreateGoal} className="p-6 space-y-4">
              {/* 目标类型选择 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">目标类型</label>
                <div className="grid grid-cols-4 gap-2">
                  {GOAL_TYPES.map(type => (
                    <button
                      key={type.value}
                      type="button"
                      onClick={() => handleGoalTypeChange(type.value)}
                      className={`p-3 rounded-lg border-2 text-center transition-all ${
                        formData.goal_type === type.value
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="text-2xl mb-1">{type.icon}</div>
                      <div className="text-xs font-medium">{type.label}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* 当前值 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  当前值 <span className="text-gray-400">(可选)</span>
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={formData.current_value}
                  onChange={(e) => setFormData({ ...formData, current_value: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="当前进度"
                />
              </div>

              {/* 目标值 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">目标值 *</label>
                <div className="flex gap-2">
                  <input
                    type="number"
                    step="0.1"
                    required
                    value={formData.target_value}
                    onChange={(e) => setFormData({ ...formData, target_value: e.target.value })}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="目标值"
                  />
                  <select
                    value={formData.unit}
                    onChange={(e) => setFormData({ ...formData, unit: e.target.value })}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="kg">kg</option>
                    <option value="g">g</option>
                    <option value="步">步</option>
                    <option value="kcal">kcal</option>
                    <option value="ml">ml</option>
                    <option value="小时">小时</option>
                  </select>
                </div>
              </div>

              {/* 目标日期 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  目标日期 <span className="text-gray-400">(可选)</span>
                </label>
                <input
                  type="date"
                  value={formData.target_date}
                  onChange={(e) => setFormData({ ...formData, target_date: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* 按钮 */}
              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowCreateModal(false);
                    resetForm();
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                >
                  取消
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  创建
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 记录进度弹窗 */}
      {showProgressModal && selectedGoal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl w-full max-w-md">
            <div className="p-6 border-b border-gray-100">
              <h2 className="text-xl font-bold">记录进度</h2>
              <p className="text-gray-500 text-sm mt-1">
                {getGoalTypeLabel(selectedGoal.goal_type)} - 目标: {formatGoalValue(selectedGoal.target_value, selectedGoal.unit)}
              </p>
            </div>
            <form onSubmit={handleRecordProgress} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">当前数值 *</label>
                <input
                  type="number"
                  step="0.1"
                  required
                  value={progressValue}
                  onChange={(e) => setProgressValue(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="请输入当前数值"
                />
              </div>

              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={dailyTargetMet}
                  onChange={(e) => setDailyTargetMet(e.target.checked)}
                  className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
                />
                <span className="text-gray-700">今日目标已达成</span>
              </label>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowProgressModal(false);
                    setProgressValue('');
                    setDailyTargetMet(false);
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                >
                  取消
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  记录
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 目标详情弹窗 */}
      {showDetailModal && selectedGoal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl w-full max-w-md max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-100">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold">{getGoalTypeLabel(selectedGoal.goal_type)}</h2>
                <button
                  onClick={() => setShowDetailModal(false)}
                  className="p-2 hover:bg-gray-100 rounded-lg"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>
            <div className="p-6 space-y-4">
              {/* 进度 */}
              <div className="bg-gray-50 rounded-xl p-4">
                <div className="flex justify-between mb-2">
                  <span className="text-gray-600">完成进度</span>
                  <span className="font-bold text-blue-600">
                    {calculateProgress(selectedGoal.current_value, selectedGoal.target_value, selectedGoal.goal_type).toFixed(0)}%
                  </span>
                </div>
                {renderProgressBar(
                  calculateProgress(selectedGoal.current_value, selectedGoal.target_value, selectedGoal.goal_type),
                  GOAL_TYPES.find(t => t.value === selectedGoal.goal_type)?.color || '#4CAF50'
                )}
              </div>

              {/* 详情 */}
              <div className="space-y-3">
                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-gray-600">当前值</span>
                  <span className="font-medium">{formatGoalValue(selectedGoal.current_value, selectedGoal.unit)}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-gray-600">目标值</span>
                  <span className="font-medium">{formatGoalValue(selectedGoal.target_value, selectedGoal.unit)}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-gray-600">状态</span>
                  <span 
                    className="font-medium"
                    style={{ color: getStatusColor(selectedGoal.status) }}
                  >
                    {getGoalStatusLabel(selectedGoal.status)}
                  </span>
                </div>
                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-gray-600">开始日期</span>
                  <span className="font-medium">{new Date(selectedGoal.start_date).toLocaleDateString()}</span>
                </div>
                {selectedGoal.target_date && (
                  <div className="flex justify-between py-2 border-b border-gray-100">
                    <span className="text-gray-600">目标日期</span>
                    <span className="font-medium">{new Date(selectedGoal.target_date).toLocaleDateString()}</span>
                  </div>
                )}
                {selectedGoal.predicted_date && (
                  <div className="flex justify-between py-2">
                    <span className="text-gray-600">预计完成</span>
                    <span className="font-medium text-purple-600">
                      {new Date(selectedGoal.predicted_date).toLocaleDateString()}
                    </span>
                  </div>
                )}
              </div>

              {/* 操作 */}
              <div className="flex gap-3 pt-4">
                <button
                  onClick={() => {
                    setShowDetailModal(false);
                    openProgressModal(selectedGoal);
                  }}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center justify-center gap-2"
                >
                  <Plus className="w-4 h-4" />
                  记录进度
                </button>
                <button
                  onClick={() => {
                    setShowDetailModal(false);
                    setShowCreateModal(true);
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                >
                  新建目标
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
