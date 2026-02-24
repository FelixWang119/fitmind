import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  Flame, 
  Clock, 
  Timer, 
  Heart, 
  MapPin, 
  Plus, 
  Trash2, 
  Edit, 
  ChevronDown, 
  ChevronUp,
  Dumbbell,
  Zap,
  Footprints,
  Bike,
  Waves,
  TrendingUp,
  Calendar,
  CheckCircle,
  AlertCircle,
  X
} from 'lucide-react';
import { exerciseCheckInApi, ExerciseCheckIn, ExerciseType, ExerciseDailySummary } from '@/services/exerciseCheckIn';

// 运动分类中文映射
const CATEGORY_LABELS: Record<string, string> = {
  'Cardio': '有氧',
  'Strength': '力量',
  'Flexibility': '灵活',
  'Other': '其他',
};

// 运动分类图标映射
const CATEGORY_ICONS: Record<string, React.ElementType> = {
  '有氧': Footprints,
  'Cardio': Footprints,
  '力量': Dumbbell,
  'Strength': Dumbbell,
  '灵活': Zap,
  'Flexibility': Zap,
  '其他': Activity,
  'Other': Activity,
};

// 强度标签配置
const INTENSITY_CONFIG = {
  low: { label: '轻松', color: 'bg-green-100 text-green-800', tip: '可以轻松聊天' },
  medium: { label: '中等', color: 'bg-yellow-100 text-yellow-800', tip: '有点喘但能说话' },
  high: { label: '高强度', color: 'bg-red-100 text-red-800', tip: '喘到说不出话' },
};

// 预设运动类型
const PRESET_EXERCISES: ExerciseType[] = [
  { type: 'Running', met_value: 8.0, category: '有氧' },
  { type: 'Cycling', met_value: 6.0, category: '有氧' },
  { type: 'Swimming', met_value: 6.0, category: '有氧' },
  { type: 'Walking', met_value: 3.5, category: '有氧' },
  { type: 'HIIT', met_value: 8.0, category: '有氧' },
  { type: 'Strength Training', met_value: 3.5, category: '力量' },
  { type: 'Yoga', met_value: 2.5, category: '灵活' },
  { type: 'Pilates', met_value: 3.0, category: '灵活' },
];

// 预设运动类型（英文键值对应中文显示）
const EXERCISE_TYPE_LABELS: Record<string, string> = {
  'Running': '跑步',
  'Cycling': '骑行',
  'Swimming': '游泳',
  'Walking': '步行',
  'HIIT': 'HIIT',
  'Strength Training': '力量训练',
  'Yoga': '瑜伽',
  'Pilates': '普拉提',
  'Jump Rope': '跳绳',
  'Rowing': '划船',
  'Hiking': '徒步',
  'Dancing': '舞蹈',
  'Elliptical': '椭圆机',
  'Basketball': '篮球',
  'Soccer': '足球',
  'Tennis': '网球',
  'CrossFit': 'CrossFit',
};

const ExerciseCheckInPage: React.FC = () => {
  // 状态管理
  const [loading, setLoading] = useState(true);
  const [checkIns, setCheckIns] = useState<ExerciseCheckIn[]>([]);
  const [exerciseTypes, setExerciseTypes] = useState<ExerciseType[]>([]);
  const [dailySummary, setDailySummary] = useState<ExerciseDailySummary | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  
  // 表单状态
  const [formData, setFormData] = useState({
    exercise_type: 'Running',
    category: '有氧',
    duration_minutes: 30,
    intensity: 'medium' as 'low' | 'medium' | 'high',
    distance_km: '',
    heart_rate_avg: '',
    notes: '',
    rating: 3,
  });
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [weightWarning, setWeightWarning] = useState<string | null>(null);

  // 加载数据
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [checkInsData, typesData, summaryData] = await Promise.all([
        exerciseCheckInApi.getList({ limit: 20 }),
        exerciseCheckInApi.getExerciseTypes(),
        exerciseCheckInApi.getDailySummary(),
      ]);
      setCheckIns(checkInsData);
      setExerciseTypes(typesData);
      setDailySummary(summaryData);
    } catch (error) {
      console.error('加载数据失败:', error);
      alert('加载数据失败，请刷新重试');
    } finally {
      setLoading(false);
    }
  };

  // 提交打卡
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setWeightWarning(null);

    try {
      const submitData: any = {
        exercise_type: formData.exercise_type,
        category: formData.category,
        duration_minutes: formData.duration_minutes,
        intensity: formData.intensity,
      };

      // 添加可选字段
      if (formData.distance_km) submitData.distance_km = parseFloat(formData.distance_km);
      if (formData.heart_rate_avg) submitData.heart_rate_avg = parseInt(formData.heart_rate_avg);
      if (formData.notes) submitData.notes = formData.notes;
      if (formData.rating) submitData.rating = formData.rating;

      const result = await exerciseCheckInApi.create(submitData);
      
      // 显示估算详情
      if (result.estimation_details) {
        const detail = result.estimation_details;
        const msg = `✅ 打卡成功！\n\n估算燃烧：${result.calories_burned} kcal\n计算公式：${detail.formula}\nMET 值：${detail.met_value}\n体重：${detail.weight_kg}kg\n时长：${detail.duration_hours}h\n强度系数：${detail.intensity_factor}`;
        if (weightWarning) {
          alert(msg + `\n\n⚠️ ${weightWarning}`);
        } else {
          alert(msg);
        }
      }

      setShowAddModal(false);
      resetForm();
      loadData();
    } catch (error: any) {
      console.error('创建打卡失败:', error);
      if (error.response?.data?.weight_warning) {
        setWeightWarning(error.response.data.weight_warning);
      }
      alert('创建失败：' + (error.response?.data?.detail || error.message));
    } finally {
      setSubmitting(false);
    }
  };

  // 重置表单
  const resetForm = () => {
    setFormData({
      exercise_type: 'Running',
      category: '有氧',
      duration_minutes: 30,
      intensity: 'medium',
      distance_km: '',
      heart_rate_avg: '',
      notes: '',
      rating: 3,
    });
    setShowAdvanced(false);
    setWeightWarning(null);
  };

  // 删除打卡
  const handleDelete = async (id: number) => {
    if (!confirm('确定要删除这条打卡记录吗？')) return;

    try {
      await exerciseCheckInApi.delete(id);
      loadData();
      alert('删除成功');
    } catch (error) {
      console.error('删除失败:', error);
      alert('删除失败：' + (error as any).message);
    }
  };

  // 按分类分组运动类型
  const groupedExercises = exerciseTypes.reduce((acc, ex) => {
    if (!acc[ex.category]) acc[ex.category] = [];
    acc[ex.category].push(ex);
    return acc;
  }, {} as Record<string, ExerciseType[]>);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 头部 */}
      <header className="bg-gradient-to-r from-orange-500 to-red-500 text-white p-6 shadow-md">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold flex items-center gap-2">
                <Activity className="w-8 h-8" />
                运动打卡
              </h1>
              <p className="text-orange-100 mt-1">记录每一次运动，燃烧卡路里！</p>
            </div>
            <button
              onClick={() => setShowAddModal(true)}
              className="bg-white text-orange-600 px-6 py-3 rounded-lg font-semibold hover:bg-orange-50 transition-colors flex items-center gap-2"
            >
              <Plus className="w-5 h-5" />
              快速打卡
            </button>
          </div>
        </div>
      </header>

      {/* 今日概览 */}
      {dailySummary && (
        <section className="max-w-7xl mx-auto px-4 py-6">
          <div className="bg-white rounded-xl shadow-md p-6">
            <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
              <Calendar className="w-5 h-5 text-orange-500" />
              今日概览
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-orange-50 rounded-lg">
                <Clock className="w-8 h-8 text-orange-500 mx-auto mb-2" />
                <div className="text-2xl font-bold text-orange-600">
                  {dailySummary.total_duration_minutes}
                </div>
                <div className="text-sm text-gray-600">分钟</div>
              </div>
              <div className="text-center p-4 bg-red-50 rounded-lg">
                <Flame className="w-8 h-8 text-red-500 mx-auto mb-2" />
                <div className="text-2xl font-bold text-red-600">
                  {dailySummary.total_calories_burned}
                </div>
                <div className="text-sm text-gray-600">kcal</div>
              </div>
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <CheckCircle className="w-8 h-8 text-blue-500 mx-auto mb-2" />
                <div className="text-2xl font-bold text-blue-600">
                  {dailySummary.sessions_count}
                </div>
                <div className="text-sm text-gray-600">次打卡</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <TrendingUp className="w-8 h-8 text-green-500 mx-auto mb-2" />
                <div className="text-2xl font-bold text-green-600">
                  {dailySummary.progress_percentage?.toFixed(0) || 0}%
                </div>
                <div className="text-sm text-gray-600">目标进度</div>
              </div>
            </div>
            {dailySummary.progress_percentage !== undefined && (
              <div className="mt-4">
                <div className="flex justify-between text-sm text-gray-600 mb-1">
                  <span>目标：{dailySummary.goal_duration || 60}分钟 / {dailySummary.goal_calories || 500}kcal</span>
                  <span>{dailySummary.progress_percentage?.toFixed(0) || 0}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div 
                    className="bg-gradient-to-r from-orange-500 to-red-500 h-3 rounded-full transition-all"
                    style={{ width: `${Math.min(dailySummary.progress_percentage ?? 0, 100)}%` }}
                  ></div>
                </div>
              </div>
            )}
          </div>
        </section>
      )}

      {/* 打卡列表 */}
      <section className="max-w-7xl mx-auto px-4 py-6">
        <h2 className="text-xl font-bold text-gray-800 mb-4">打卡记录</h2>
        {checkIns.length === 0 ? (
          <div className="bg-white rounded-xl shadow-md p-12 text-center">
            <Activity className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">还没有打卡记录</p>
            <button
              onClick={() => setShowAddModal(true)}
              className="mt-4 text-orange-600 font-semibold hover:text-orange-700"
            >
              创建第一条打卡 →
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {checkIns.map((checkIn) => {
              const Icon = CATEGORY_ICONS[checkIn.category] || Activity;
              const intensityConfig = INTENSITY_CONFIG[checkIn.intensity];
              
              return (
                <div key={checkIn.id} className="bg-white rounded-xl shadow-md overflow-hidden">
                  <div className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-4 flex-1">
                        <div className="bg-orange-100 p-3 rounded-lg">
                          <Icon className="w-6 h-6 text-orange-600" />
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="text-lg font-bold text-gray-800">{EXERCISE_TYPE_LABELS[checkIn.exercise_type] || checkIn.exercise_type}</h3>
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${intensityConfig.color}`}>
                              {intensityConfig.label}
                            </span>
                          </div>
                          <div className="flex items-center gap-4 text-sm text-gray-600 mb-2">
                            <span className="flex items-center gap-1">
                              <Timer className="w-4 h-4" />
                              {checkIn.duration_minutes}分钟
                            </span>
                            {checkIn.distance_km && (
                              <span className="flex items-center gap-1">
                                <MapPin className="w-4 h-4" />
                                {checkIn.distance_km}km
                              </span>
                            )}
                            {checkIn.heart_rate_avg && (
                              <span className="flex items-center gap-1">
                                <Heart className="w-4 h-4" />
                                {checkIn.heart_rate_avg}bpm
                              </span>
                            )}
                          </div>
                          <div className="flex items-center gap-2">
                            <Flame className="w-5 h-5 text-red-500" />
                            <span className="text-lg font-bold text-red-600">
                              {checkIn.calories_burned} kcal
                            </span>
                            {checkIn.is_estimated && (
                              <span className="text-xs text-gray-500">(估算)</span>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => setExpandedId(expandedId === checkIn.id ? null : checkIn.id)}
                          className="p-2 text-gray-400 hover:text-gray-600"
                        >
                          {expandedId === checkIn.id ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                        </button>
                        <button
                          onClick={() => handleDelete(checkIn.id)}
                          className="p-2 text-red-400 hover:text-red-600"
                        >
                          <Trash2 className="w-5 h-5" />
                        </button>
                      </div>
                    </div>

                    {/* 展开详情 */}
                    {expandedId === checkIn.id && (
                      <div className="mt-4 pt-4 border-t border-gray-100">
                        {checkIn.estimation_details && (
                          <div className="bg-gray-50 rounded-lg p-4 mb-3">
                            <h4 className="font-semibold text-gray-700 mb-2">卡路里估算详情</h4>
                            <div className="grid grid-cols-2 gap-2 text-sm">
                              <div>MET 值：{checkIn.estimation_details.met_value}</div>
                              <div>体重：{checkIn.estimation_details.weight_kg}kg</div>
                              <div>时长：{checkIn.estimation_details.duration_hours}h</div>
                              <div>强度系数：{checkIn.estimation_details.intensity_factor}</div>
                            </div>
                            <div className="mt-2 text-xs text-gray-500">
                              公式：{checkIn.estimation_details.formula}
                            </div>
                          </div>
                        )}
                        {checkIn.notes && (
                          <div className="text-sm text-gray-600 mb-2">
                            <strong>备注:</strong> {checkIn.notes}
                          </div>
                        )}
                        {checkIn.rating && (
                          <div className="text-sm text-gray-600">
                            <strong>感受评分:</strong> {'⭐'.repeat(checkIn.rating)}
                          </div>
                        )}
                        <div className="text-xs text-gray-400 mt-2">
                          创建于 {new Date(checkIn.created_at).toLocaleString('zh-CN')}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>

      {/* 添加打卡弹窗 */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-800">创建运动打卡</h2>
                <button
                  onClick={() => {
                    setShowAddModal(false);
                    resetForm();
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                {/* 快速模式 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    运动类型 *
                  </label>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                    {Object.entries(groupedExercises).map(([category, exercises]) => (
                      <div key={category} className="col-span-2 md:col-span-4">
                        <h4 className="font-medium text-gray-600 mb-2">{CATEGORY_LABELS[category] || category}</h4>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                          {exercises.map((ex) => (
                            <button
                              key={ex.type}
                              type="button"
                              onClick={() => setFormData({ ...formData, exercise_type: ex.type, category: ex.category })}
                              className={`p-2 rounded-lg border-2 text-sm transition-all ${
                                formData.exercise_type === ex.type
                                  ? 'border-orange-500 bg-orange-50 text-orange-700'
                                  : 'border-gray-200 hover:border-gray-300'
                              }`}
                            >
{EXERCISE_TYPE_LABELS[ex.type] || ex.type}
                            </button>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    时长 (分钟) *
                  </label>
                  <input
                    type="number"
                    value={formData.duration_minutes}
                    onChange={(e) => setFormData({ ...formData, duration_minutes: parseInt(e.target.value) || 0 })}
                    min="1"
                    max="1440"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    强度 *
                  </label>
                  <div className="grid grid-cols-3 gap-2">
                    {(['low', 'medium', 'high'] as const).map((intensity) => {
                      const config = INTENSITY_CONFIG[intensity];
                      return (
                        <button
                          key={intensity}
                          type="button"
                          onClick={() => setFormData({ ...formData, intensity })}
                          className={`p-3 rounded-lg border-2 transition-all ${
                            formData.intensity === intensity
                              ? 'border-orange-500 bg-orange-50'
                              : 'border-gray-200 hover:border-gray-300'
                          }`}
                        >
                          <div className="font-medium text-sm">{config.label}</div>
                          <div className="text-xs text-gray-500 mt-1">{config.tip}</div>
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* 高级模式 */}
                {showAdvanced && (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        距离 (公里)
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        value={formData.distance_km}
                        onChange={(e) => setFormData({ ...formData, distance_km: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500"
                        placeholder="可选"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        平均心率 (bpm)
                      </label>
                      <input
                        type="number"
                        value={formData.heart_rate_avg}
                        onChange={(e) => setFormData({ ...formData, heart_rate_avg: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500"
                        placeholder="可选"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        备注
                      </label>
                      <textarea
                        value={formData.notes}
                        onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500"
                        rows={3}
                        placeholder="可选"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        感受评分
                      </label>
                      <div className="flex gap-2">
                        {[1, 2, 3, 4, 5].map((rating) => (
                          <button
                            key={rating}
                            type="button"
                            onClick={() => setFormData({ ...formData, rating })}
                            className={`text-2xl transition-all ${
                              formData.rating === rating ? 'scale-125' : 'opacity-50 hover:opacity-100'
                            }`}
                          >
                            ⭐
                          </button>
                        ))}
                      </div>
                    </div>
                  </>
                )}

                <div className="flex items-center justify-between pt-4 border-t">
                  <button
                    type="button"
                    onClick={() => setShowAdvanced(!showAdvanced)}
                    className="text-orange-600 hover:text-orange-700 flex items-center gap-1"
                  >
                    {showAdvanced ? '收起' : '更多选项'}
                    {showAdvanced ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </button>
                  <div className="flex gap-3">
                    <button
                      type="button"
                      onClick={() => {
                        setShowAddModal(false);
                        resetForm();
                      }}
                      className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                    >
                      取消
                    </button>
                    <button
                      type="submit"
                      disabled={submitting}
                      className="px-6 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50"
                    >
                      {submitting ? '提交中...' : '确认打卡'}
                    </button>
                  </div>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ExerciseCheckInPage;
