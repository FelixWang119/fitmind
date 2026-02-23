import { useState, useEffect } from 'react';
import { apiClient } from '../api/client';

// Types
interface NutritionDetail {
  calorie_balance: number;
  macro_balance: number;
  diet_regularity: number;
  nutrition_diversity: number;
  healthy_habits: number;
  avg_daily_calories: number;
  target_calories?: number;
  protein_ratio: number;
  carbs_ratio: number;
  fat_ratio: number;
  meal_regularity_score: number;
}

interface BehaviorDetail {
  habit_completion_rate: number;
  exercise_frequency: number;
  sleep_quality: number;
  routine_regularity: number;
  total_active_habits: number;
  completed_habits: number;
  avg_daily_exercise_minutes: number;
  weekly_exercise_days: number;
  avg_daily_steps: number;
  avg_sleep_hours: number;
  sleep_quality_score: number;
}

interface EmotionDetail {
  emotional_stability: number;
  positive_emotion_ratio: number;
  stress_level: number;
  psychological_resilience: number;
  emotional_check_ins: number;
  primary_emotion: string;
  positive_ratio: number;
  emotional_variety: number;
  stress_indicators: string[];
}

interface DataCompleteness {
  food_logs_complete: boolean;
  food_logs_days: number;
  habit_logs_complete: boolean;
  habit_logs_days: number;
  sleep_logs_complete: boolean;
  sleep_logs_days: number;
  overall_completeness: number;
}

interface AssessmentSuggestion {
  category: string;
  content: string;
  priority: string;
}

interface HealthAssessmentRecord {
  id: number;
  user_id: number;
  assessment_date: string;
  overall_score: number;
  overall_grade: string;
  nutrition_score: number;
  nutrition_details: NutritionDetail;
  nutrition_suggestions: AssessmentSuggestion[];
  behavior_score: number;
  behavior_details: BehaviorDetail;
  behavior_suggestions: AssessmentSuggestion[];
  emotion_score: number;
  emotion_details: EmotionDetail;
  emotion_suggestions: AssessmentSuggestion[];
  overall_suggestions: AssessmentSuggestion[];
  data_completeness: DataCompleteness;
  assessment_period_start?: string;
  assessment_period_end?: string;
  created_at: string;
}

interface HealthAssessmentHistoryItem {
  id: number;
  assessment_date: string;
  overall_score: number;
  overall_grade: string;
  nutrition_score: number;
  behavior_score: number;
  emotion_score: number;
}

interface HealthAssessmentComparison {
  current: HealthAssessmentRecord;
  previous?: HealthAssessmentRecord;
  overall_change?: number;
  overall_change_percent?: number;
  nutrition_change?: number;
  behavior_change?: number;
  emotion_change?: number;
  trends: {
    nutrition: string;
    behavior: string;
    emotion: string;
  };
}

type TabType = 'overview' | 'nutrition' | 'behavior' | 'emotion' | 'history';

// Helper function to get grade color
const getGradeColor = (grade: string): string => {
  switch (grade) {
    case '优秀':
      return 'text-green-600';
    case '良好':
      return 'text-blue-600';
    case '一般':
      return 'text-yellow-600';
    case '需改善':
      return 'text-red-600';
    default:
      return 'text-gray-600';
  }
};

// Helper function to get trend icon
const getTrendIcon = (trend: string): string => {
  switch (trend) {
    case 'improving':
      return '↑';
    case 'declining':
      return '↓';
    default:
      return '→';
  }
};

// Helper function to get trend color
const getTrendColor = (trend: string): string => {
  switch (trend) {
    case 'improving':
      return 'text-green-600';
    case 'declining':
      return 'text-red-600';
    default:
      return 'text-gray-600';
  }
};

// Score Circle Component
const ScoreCircle = ({ score, grade, size = 'large' }: { score: number; grade: string; size?: 'large' | 'medium' | 'small' }) => {
  const sizeClasses = {
    large: 'w-40 h-40 text-4xl',
    medium: 'w-28 h-28 text-2xl',
    small: 'w-20 h-20 text-xl',
  };
  
  const circumference = 2 * Math.PI * 45;
  const progress = (score / 100) * circumference;
  
  return (
    <div className={`relative ${sizeClasses[size]} rounded-full flex items-center justify-center`}>
      <svg className="transform -rotate-90 w-full h-full">
        <circle
          cx="50"
          cy="50"
          r="45"
          stroke="#e5e7eb"
          strokeWidth="8"
          fill="none"
        />
        <circle
          cx="50"
          cy="50"
          r="45"
          stroke={score >= 80 ? '#10b981' : score >= 60 ? '#3b82f6' : score >= 40 ? '#f59e0b' : '#ef4444'}
          strokeWidth="8"
          fill="none"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={circumference - progress}
          className="transition-all duration-1000"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={`font-bold ${getGradeColor(grade)}`}>{score}</span>
        <span className="text-xs text-gray-500">{grade}</span>
      </div>
    </div>
  );
};

// Score Bar Component
const ScoreBar = ({ label, score, trend }: { label: string; score: number; trend?: string }) => {
  const progress = Math.min(score, 100);
  const colorClass = score >= 80 ? 'bg-green-500' : score >= 60 ? 'bg-blue-500' : score >= 40 ? 'bg-yellow-500' : 'bg-red-500';
  
  return (
    <div className="mb-3">
      <div className="flex justify-between items-center mb-1">
        <span className="text-sm font-medium text-gray-700">{label}</span>
        <div className="flex items-center">
          <span className="text-sm font-bold text-gray-800 mr-2">{score}</span>
          {trend && (
            <span className={`text-lg ${getTrendColor(trend)}`}>{getTrendIcon(trend)}</span>
          )}
        </div>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2.5">
        <div
          className={`h-2.5 rounded-full ${colorClass} transition-all duration-1000`}
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
};

// Main Component
export default function HealthAssessment() {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [currentAssessment, setCurrentAssessment] = useState<HealthAssessmentRecord | null>(null);
  const [history, setHistory] = useState<HealthAssessmentHistoryItem[]>([]);
  const [comparison, setComparison] = useState<HealthAssessmentComparison | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  // Fetch latest assessment on mount
  useEffect(() => {
    fetchLatestAssessment();
    fetchHistory();
  }, []);
  
  const fetchLatestAssessment = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getLatestAssessment();
      setCurrentAssessment(data);
      if (data.id) {
        fetchComparison(data.id);
      }
    } catch (err: any) {
      if (err.response?.status !== 404) {
        console.error('Failed to fetch latest assessment:', err);
      }
    } finally {
      setLoading(false);
    }
  };
  
  const fetchHistory = async () => {
    try {
      const data = await apiClient.getAssessmentHistory(5);
      setHistory(data.assessments || []);
    } catch (err) {
      console.error('Failed to fetch history:', err);
    }
  };
  
  const fetchComparison = async (id: number) => {
    try {
      const data = await apiClient.getAssessmentComparison(id);
      setComparison(data);
    } catch (err) {
      console.error('Failed to fetch comparison:', err);
    }
  };
  
  const handleCreateAssessment = async () => {
    try {
      setCreating(true);
      setError(null);
      const response = await apiClient.createHealthAssessment();
      
      if (response.success && response.assessment) {
        setCurrentAssessment(response.assessment);
        if (response.assessment.id) {
          fetchComparison(response.assessment.id);
        }
        fetchHistory();
      } else {
        setError(response.message || '评估创建失败');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || '创建评估时出错');
    } finally {
      setCreating(false);
    }
  };
  
  const renderOverview = () => (
    <div className="space-y-6">
      {/* Main Score Display */}
      {currentAssessment ? (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">综合健康评分</h2>
          <div className="flex flex-col md:flex-row items-center justify-center gap-8">
            <ScoreCircle score={currentAssessment.overall_score} grade={currentAssessment.overall_grade} />
            <div className="flex-1 w-full">
              <h3 className="text-lg font-semibold mb-3">三维度评分</h3>
              <ScoreBar 
                label="营养维度" 
                score={currentAssessment.nutrition_score} 
                trend={comparison?.trends?.nutrition}
              />
              <ScoreBar 
                label="行为维度" 
                score={currentAssessment.behavior_score} 
                trend={comparison?.trends?.behavior}
              />
              <ScoreBar 
                label="情感维度" 
                score={currentAssessment.emotion_score} 
                trend={comparison?.trends?.emotion}
              />
              
              {/* Comparison with previous */}
              {comparison?.previous && (
                <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600">
                    相比上次评估
                    <span className={`font-bold ml-2 ${comparison.overall_change && comparison.overall_change > 0 ? 'text-green-600' : comparison.overall_change && comparison.overall_change < 0 ? 'text-red-600' : 'text-gray-600'}`}>
                      {comparison.overall_change && comparison.overall_change > 0 ? '+' : ''}{comparison.overall_change}分
                      ({comparison.overall_change_percent && comparison.overall_change_percent > 0 ? '+' : ''}{comparison.overall_change_percent}%)
                    </span>
                  </p>
                </div>
              )}
            </div>
          </div>
          
          {/* Data Completeness */}
          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <h4 className="font-semibold text-blue-800 mb-2">数据完整性</h4>
            <div className="flex gap-4 text-sm">
              <span className={currentAssessment.data_completeness.food_logs_complete ? 'text-green-600' : 'text-yellow-600'}>
                饮食记录: {currentAssessment.data_completeness.food_logs_days}天
              </span>
              <span className={currentAssessment.data_completeness.habit_logs_complete ? 'text-green-600' : 'text-yellow-600'}>
                习惯记录: {currentAssessment.data_completeness.habit_logs_days}天
              </span>
              <span className={currentAssessment.data_completeness.sleep_logs_complete ? 'text-green-600' : 'text-yellow-600'}>
                睡眠记录: {currentAssessment.data_completeness.sleep_logs_days}天
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              整体完整度: {currentAssessment.data_completeness.overall_completeness}%
            </p>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <p className="text-gray-500 mb-4">暂无健康评估数据</p>
          <button
            onClick={handleCreateAssessment}
            disabled={creating}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
          >
            {creating ? '生成中...' : '开始健康评估'}
          </button>
        </div>
      )}
      
      {/* Overall Suggestions */}
      {currentAssessment && currentAssessment.overall_suggestions && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-bold mb-3">综合建议</h3>
          <div className="space-y-2">
            {currentAssessment.overall_suggestions.map((suggestion, index) => (
              <div 
                key={index} 
                className={`p-3 rounded-lg ${
                  suggestion.priority === 'high' ? 'bg-red-50 border-l-4 border-red-500' :
                  suggestion.priority === 'medium' ? 'bg-yellow-50 border-l-4 border-yellow-500' :
                  'bg-green-50 border-l-4 border-green-500'
                }`}
              >
                <p className="text-gray-700">{suggestion.content}</p>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Quick Actions */}
      <div className="flex justify-center gap-4">
        <button
          onClick={handleCreateAssessment}
          disabled={creating || !currentAssessment}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
        >
          {creating ? '生成中...' : '重新评估'}
        </button>
        <button
          onClick={() => setActiveTab('history')}
          className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
        >
          查看历史
        </button>
      </div>
    </div>
  );
  
  const renderNutritionDetail = () => {
    if (!currentAssessment) return null;
    
    const details = currentAssessment.nutrition_details;
    const suggestions = currentAssessment.nutrition_suggestions;
    
    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold">营养维度详情</h2>
            <ScoreCircle score={currentAssessment.nutrition_score} grade={currentAssessment.nutrition_score >= 80 ? '优秀' : currentAssessment.nutrition_score >= 60 ? '良好' : currentAssessment.nutrition_score >= 40 ? '一般' : '需改善'} size="medium" />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold mb-3">热量摄入</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">平均每日摄入</span>
                  <span className="font-medium">{details.avg_daily_calories} 千卡</span>
                </div>
                {details.target_calories && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">目标热量</span>
                    <span className="font-medium">{details.target_calories} 千卡</span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span className="text-gray-600">热量均衡得分</span>
                  <span className="font-medium">{details.calorie_balance}/30</span>
                </div>
              </div>
            </div>
            
            <div>
              <h3 className="font-semibold mb-3">宏量营养素</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">蛋白质</span>
                  <span className="font-medium">{details.protein_ratio}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">碳水化合物</span>
                  <span className="font-medium">{details.carbs_ratio}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">脂肪</span>
                  <span className="font-medium">{details.fat_ratio}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">营养平衡得分</span>
                  <span className="font-medium">{details.macro_balance}/25</span>
                </div>
              </div>
            </div>
          </div>
          
          <div className="mt-6">
            <h3 className="font-semibold mb-3">饮食规律性</h3>
            <div className="flex justify-between">
              <span className="text-gray-600">规律性得分</span>
              <span className="font-medium">{details.diet_regularity}/20</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">营养多样性</span>
              <span className="font-medium">{details.nutrition_diversity}/15</span>
            </div>
          </div>
        </div>
        
        {/* Suggestions */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-bold mb-3">营养建议</h3>
          <div className="space-y-2">
            {suggestions.map((suggestion, index) => (
              <div 
                key={index} 
                className={`p-3 rounded-lg ${
                  suggestion.priority === 'high' ? 'bg-red-50' :
                  suggestion.priority === 'medium' ? 'bg-yellow-50' :
                  'bg-green-50'
                }`}
              >
                <p className="text-gray-700">{suggestion.content}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };
  
  const renderBehaviorDetail = () => {
    if (!currentAssessment) return null;
    
    const details = currentAssessment.behavior_details;
    const suggestions = currentAssessment.behavior_suggestions;
    
    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold">行为维度详情</h2>
            <ScoreCircle score={currentAssessment.behavior_score} grade={currentAssessment.behavior_score >= 80 ? '优秀' : currentAssessment.behavior_score >= 60 ? '良好' : currentAssessment.behavior_score >= 40 ? '一般' : '需改善'} size="medium" />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold mb-3">习惯完成</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">活跃习惯数</span>
                  <span className="font-medium">{details.total_active_habits} 个</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">完成次数</span>
                  <span className="font-medium">{details.completed_habits} 次</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">完成率得分</span>
                  <span className="font-medium">{details.habit_completion_rate}/30</span>
                </div>
              </div>
            </div>
            
            <div>
              <h3 className="font-semibold mb-3">运动锻炼</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">平均每日运动</span>
                  <span className="font-medium">{details.avg_daily_exercise_minutes} 分钟</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">每周运动天数</span>
                  <span className="font-medium">{details.weekly_exercise_days} 天</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">平均每日步数</span>
                  <span className="font-medium">{details.avg_daily_steps} 步</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">运动频率得分</span>
                  <span className="font-medium">{details.exercise_frequency}/25</span>
                </div>
              </div>
            </div>
          </div>
          
          <div className="mt-6">
            <h3 className="font-semibold mb-3">睡眠质量</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">平均睡眠时长</span>
                <span className="font-medium">{details.avg_sleep_hours} 小时</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">睡眠质量得分</span>
                <span className="font-medium">{details.sleep_quality}/25</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">作息规律得分</span>
                <span className="font-medium">{details.routine_regularity}/20</span>
              </div>
            </div>
          </div>
        </div>
        
        {/* Suggestions */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-bold mb-3">行为建议</h3>
          <div className="space-y-2">
            {suggestions.map((suggestion, index) => (
              <div 
                key={index} 
                className={`p-3 rounded-lg ${
                  suggestion.priority === 'high' ? 'bg-red-50' :
                  suggestion.priority === 'medium' ? 'bg-yellow-50' :
                  'bg-green-50'
                }`}
              >
                <p className="text-gray-700">{suggestion.content}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };
  
  const renderEmotionDetail = () => {
    if (!currentAssessment) return null;
    
    const details = currentAssessment.emotion_details;
    const suggestions = currentAssessment.emotion_suggestions;
    
    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold">情感维度详情</h2>
            <ScoreCircle score={currentAssessment.emotion_score} grade={currentAssessment.emotion_score >= 80 ? '优秀' : currentAssessment.emotion_score >= 60 ? '良好' : currentAssessment.emotion_score >= 40 ? '一般' : '需改善'} size="medium" />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold mb-3">情绪状态</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">情绪记录次数</span>
                  <span className="font-medium">{details.emotional_check_ins} 次</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">主要情绪</span>
                  <span className="font-medium">{details.primary_emotion}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">积极情绪比例</span>
                  <span className="font-medium">{details.positive_ratio}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">情绪多样性</span>
                  <span className="font-medium">{details.emotional_variety} 种</span>
                </div>
              </div>
            </div>
            
            <div>
              <h3 className="font-semibold mb-3">评分细分</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">情绪稳定性</span>
                  <span className="font-medium">{details.emotional_stability}/30</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">积极情绪占比</span>
                  <span className="font-medium">{details.positive_emotion_ratio}/25</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">压力水平</span>
                  <span className="font-medium">{details.stress_level}/25</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">心理韧性</span>
                  <span className="font-medium">{details.psychological_resilience}/20</span>
                </div>
              </div>
            </div>
          </div>
          
          {details.stress_indicators && details.stress_indicators.length > 0 && (
            <div className="mt-6">
              <h3 className="font-semibold mb-3">压力指标</h3>
              <div className="flex flex-wrap gap-2">
                {details.stress_indicators.map((indicator, index) => (
                  <span key={index} className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm">
                    {indicator}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
        
        {/* Suggestions */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-bold mb-3">情感建议</h3>
          <div className="space-y-2">
            {suggestions.map((suggestion, index) => (
              <div 
                key={index} 
                className={`p-3 rounded-lg ${
                  suggestion.priority === 'high' ? 'bg-red-50' :
                  suggestion.priority === 'medium' ? 'bg-yellow-50' :
                  'bg-green-50'
                }`}
              >
                <p className="text-gray-700">{suggestion.content}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };
  
  const renderHistory = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold mb-4">评估历史</h2>
        
        {history.length > 0 ? (
          <div className="space-y-4">
            {history.map((item, index) => (
              <div 
                key={item.id} 
                className={`p-4 border rounded-lg ${index === 0 ? 'border-blue-500 bg-blue-50' : 'border-gray-200'}`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-500">
                    {new Date(item.assessment_date).toLocaleDateString('zh-CN')}
                  </span>
                  {index === 0 && <span className="text-xs text-blue-600 font-medium">最新</span>}
                </div>
                
                <div className="flex items-center gap-6">
                  <div className="text-center">
                    <div className={`text-2xl font-bold ${getGradeColor(item.overall_grade)}`}>
                      {item.overall_score}
                    </div>
                    <div className="text-xs text-gray-500">{item.overall_grade}</div>
                  </div>
                  
                  <div className="flex-1 grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">营养</span>
                      <div className="font-medium">{item.nutrition_score}</div>
                    </div>
                    <div>
                      <span className="text-gray-500">行为</span>
                      <div className="font-medium">{item.behavior_score}</div>
                    </div>
                    <div>
                      <span className="text-gray-500">情感</span>
                      <div className="font-medium">{item.emotion_score}</div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-center text-gray-500 py-8">暂无历史评估记录</p>
        )}
      </div>
    </div>
  );
  
  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">健康评估</h1>
          <p className="text-gray-600 mt-2">全面评估您的营养、行为和情感健康状况</p>
        </div>
        
        {/* Error Message */}
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-700">{error}</p>
          </div>
        )}
        
        {/* Tabs */}
        <div className="flex border-b border-gray-200 mb-6">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'overview'
                ? 'border-b-2 border-blue-600 text-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            总体评估
          </button>
          <button
            onClick={() => setActiveTab('nutrition')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'nutrition'
                ? 'border-b-2 border-blue-600 text-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            营养详情
          </button>
          <button
            onClick={() => setActiveTab('behavior')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'behavior'
                ? 'border-b-2 border-blue-600 text-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            行为详情
          </button>
          <button
            onClick={() => setActiveTab('emotion')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'emotion'
                ? 'border-b-2 border-blue-600 text-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            情感详情
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'history'
                ? 'border-b-2 border-blue-600 text-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            历史对比
          </button>
        </div>
        
        {/* Loading State */}
        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          /* Content */
          <>
            {activeTab === 'overview' && renderOverview()}
            {activeTab === 'nutrition' && renderNutritionDetail()}
            {activeTab === 'behavior' && renderBehaviorDetail()}
            {activeTab === 'emotion' && renderEmotionDetail()}
            {activeTab === 'history' && renderHistory()}
          </>
        )}
      </div>
    </div>
  );
}
