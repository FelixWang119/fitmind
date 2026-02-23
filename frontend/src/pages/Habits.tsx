import { useEffect, useState } from 'react';
import { Plus, Check, Calendar, Award, X, Edit2, Trash2, ChevronLeft, ChevronRight } from 'lucide-react';
import { api } from '../api/client';
import toast from 'react-hot-toast';

// Types
interface Habit {
  id: number;
  name: string;
  description?: string;
  category: string;
  frequency: string;
  target_value?: number | string;
  preferred_time?: string;
  target_unit?: string;
  reminder_enabled: boolean;
  reminder_time?: string;
  streak_days: number;
  total_completions: number;
  is_active: boolean;
  created_at: string;
}

interface HabitCompletion {
  id: number;
  habit_id: number;
  completion_date: string;
  actual_value?: number;
  notes?: string;
  mood_rating?: number;
  difficulty_rating?: number;
}

// Habit Templates
const HABIT_TEMPLATES = [
  { name: '每日喝水8杯', category: 'hydration', frequency: 'daily', target_value: 8, target_unit: 'cups', description: '保持身体水分平衡' },
  { name: '每周运动3次', category: 'exercise', frequency: 'weekly', target_value: 3, target_unit: 'times', description: '增强体质' },
  { name: '每晚10点前入睡', category: 'sleep', frequency: 'daily', description: '保证充足睡眠' },
  { name: '每日冥想10分钟', category: 'mental_health', frequency: 'daily', target_value: 10, target_unit: 'minutes', description: '减轻压力' },
  { name: '每天吃早餐', category: 'diet', frequency: 'daily', description: '均衡营养摄入' },
  { name: '每日步行10000步', category: 'exercise', frequency: 'daily', target_value: 10000, target_unit: 'steps', description: '保持活力' },
];

const CATEGORIES = [
  { value: 'diet', label: '饮食', emoji: '🥗' },
  { value: 'exercise', label: '运动', emoji: '🏃' },
  { value: 'sleep', label: '睡眠', emoji: '😴' },
  { value: 'mental_health', label: '心理', emoji: '🧘' },
  { value: 'hydration', label: '饮水', emoji: '💧' },
  { value: 'other', label: '其他', emoji: '📌' },
];

const FREQUENCIES = [
  { value: 'daily', label: '每日' },
  { value: 'weekly', label: '每周' },
  { value: 'monthly', label: '每月' },
];

export default function Habits() {
  const [habits, setHabits] = useState<Habit[]>([]);
  const [checklist, setChecklist] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [selectedHabit, setSelectedHabit] = useState<Habit | null>(null);
  const [showCalendar, setShowCalendar] = useState(false);
  const [calendarCompletions, setCalendarCompletions] = useState<HabitCompletion[]>([]);
  const [currentMonth, setCurrentMonth] = useState(new Date());
  
  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category: 'other',
    frequency: 'daily',
    target_value: '',
    target_unit: '',
    reminder_enabled: false,
    reminder_time: '',
  });

  useEffect(() => {
    loadHabits();
  }, []);

  const loadHabits = async () => {
    try {
      setLoading(true);
      const [habitsData, checklistData] = await Promise.all([
        api.getHabits(),
        api.getDailyChecklist(),
      ]);
      setHabits(habitsData);
      setChecklist(checklistData);
    } catch (error) {
      console.error('Failed to load habits:', error);
      toast.error('加载习惯失败');
    } finally {
      setLoading(false);
    }
  };

  const handleCompleteHabit = async (habitId: number) => {
    try {
      await api.completeHabit(habitId, {
        completion_date: new Date().toISOString(),
      });
      toast.success('打卡成功！继续保持！💪');
      await loadHabits();
    } catch (error: any) {
      if (error.response?.data?.detail?.includes('already completed')) {
        toast.error('今天已经打过卡了！');
      } else {
        console.error('Failed to complete habit:', error);
        toast.error('打卡失败，请重试');
      }
    }
  };

  const handleCreateHabit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const habitData = {
        name: formData.name,
        description: formData.description,
        category: formData.category,
        frequency: formData.frequency,
        target_value: formData.target_value ? parseInt(formData.target_value as string) : undefined,
        target_unit: formData.target_unit || undefined,
        reminder_enabled: formData.reminder_enabled,
        reminder_time: formData.reminder_time || undefined,
      };
      await api.createHabit(habitData);
      toast.success('习惯创建成功！');
      setShowAddModal(false);
      resetForm();
      await loadHabits();
    } catch (error: any) {
      console.error('Failed to create habit:', error);
      toast.error(error.response?.data?.detail || '创建习惯失败');
    }
  };

  const handleUpdateHabit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedHabit) return;
    try {
      const habitData = {
        name: formData.name,
        description: formData.description,
        category: formData.category,
        frequency: formData.frequency,
        target_value: formData.target_value ? parseInt(formData.target_value as string) : undefined,
        target_unit: formData.target_unit || undefined,
        reminder_enabled: formData.reminder_enabled,
        reminder_time: formData.reminder_time || undefined,
      };
      await api.updateHabit(selectedHabit.id, habitData);
      toast.success('习惯更新成功！');
      setShowEditModal(false);
      setSelectedHabit(null);
      resetForm();
      await loadHabits();
    } catch (error: any) {
      console.error('Failed to update habit:', error);
      toast.error(error.response?.data?.detail || '更新习惯失败');
    }
  };

  const handleDeleteHabit = async () => {
    if (!selectedHabit) return;
    try {
      await api.deleteHabit(selectedHabit.id);
      toast.success('习惯已删除');
      setShowDeleteConfirm(false);
      setSelectedHabit(null);
      await loadHabits();
    } catch (error) {
      console.error('Failed to delete habit:', error);
      toast.error('删除习惯失败');
    }
  };

  const handleViewCalendar = async (habit: Habit) => {
    setSelectedHabit(habit);
    setShowCalendar(true);
    await loadCalendarCompletions(habit.id);
  };

  const loadCalendarCompletions = async (habitId: number) => {
    const year = currentMonth.getFullYear();
    const month = currentMonth.getMonth();
    const startDate = new Date(year, month, 1).toISOString().split('T')[0];
    const endDate = new Date(year, month + 1, 0).toISOString().split('T')[0];
    
    try {
      const completions = await api.getHabitCompletions(habitId, startDate, endDate);
      setCalendarCompletions(completions);
    } catch (error) {
      console.error('Failed to load completions:', error);
    }
  };

  const openEditModal = (habit: Habit) => {
    setSelectedHabit(habit);
    setFormData({
      name: habit.name,
      description: habit.description || '',
      category: habit.category,
      frequency: habit.frequency,
      target_value: habit.target_value?.toString() || '',
      target_unit: habit.target_unit || '',
      reminder_enabled: habit.reminder_enabled,
      reminder_time: habit.reminder_time || '',
    });
    setShowEditModal(true);
  };

  const openDeleteConfirm = (habit: Habit) => {
    setSelectedHabit(habit);
    setShowDeleteConfirm(true);
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      category: 'other',
      frequency: 'daily',
      target_value: '',
      target_unit: '',
      reminder_enabled: false,
      reminder_time: '',
    });
  };

  const applyTemplate = (template: typeof HABIT_TEMPLATES[0]) => {
    setFormData({
      ...formData,
      name: template.name,
      description: template.description,
      category: template.category,
      frequency: template.frequency,
      target_value: template.target_value?.toString() || '',
      target_unit: template.target_unit || '',
    });
  };

  const getCategoryIcon = (category: string) => {
    const cat = CATEGORIES.find(c => c.value === category);
    return cat?.emoji || '📌';
  };

  const getCategoryLabel = (category: string) => {
    const cat = CATEGORIES.find(c => c.value === category);
    return cat?.label || '其他';
  };

  const getFrequencyLabel = (frequency: string) => {
    const freq = FREQUENCIES.find(f => f.value === frequency);
    return freq?.label || frequency;
  };

  const getStreakBadge = (streak: number) => {
    if (streak >= 100) return { label: '百日坚持', color: 'bg-purple-100 text-purple-700 border-purple-200' };
    if (streak >= 30) return { label: '月度坚持', color: 'bg-yellow-100 text-yellow-700 border-yellow-200' };
    if (streak >= 7) return { label: '一周坚持', color: 'bg-green-100 text-green-700 border-green-200' };
    return null;
  };

  const getCalendarDays = () => {
    const year = currentMonth.getFullYear();
    const month = currentMonth.getMonth();
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const days: (number | null)[] = [];
    
    // Add empty slots for days before the first day of month
    for (let i = 0; i < firstDay; i++) {
      days.push(null);
    }
    
    // Add days of the month
    for (let i = 1; i <= daysInMonth; i++) {
      days.push(i);
    }
    
    return days;
  };

  const isCompletionDate = (day: number) => {
    const year = currentMonth.getFullYear();
    const month = currentMonth.getMonth();
    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    return calendarCompletions.some(c => 
      c.completion_date.startsWith(dateStr)
    );
  };

  const getTodayDateStr = () => {
    const today = new Date();
    return `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">习惯追踪</h1>
          <p className="text-gray-600 mt-1">培养健康习惯，建立长期生活方式</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-xl hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-5 h-5" />
          <span>新建习惯</span>
        </button>
      </div>

      {/* Progress Overview */}
      {checklist && checklist.total_count > 0 && (
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-2xl p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 mb-1">今日完成进度</p>
              <div className="flex items-baseline space-x-2">
                <span className="text-4xl font-bold">{checklist.completed_count}</span>
                <span className="text-2xl text-blue-200">/ {checklist.total_count}</span>
              </div>
            </div>
            <div className="text-right">
              <p className="text-3xl font-bold">{checklist.completion_percentage}%</p>
              <p className="text-blue-100">完成率</p>
            </div>
          </div>
          <div className="mt-4 bg-blue-800 rounded-full h-2">
            <div
              className="bg-white rounded-full h-2 transition-all duration-500"
              style={{ width: `${checklist.completion_percentage}%` }}
            />
          </div>
        </div>
      )}

      {/* Today's Habits */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">今日习惯</h2>
        
        {checklist?.habits?.length > 0 ? (
          <div className="space-y-3">
            {checklist.habits.map((habit: any) => (
              <div
                key={habit.habit_id}
                className={`flex items-center justify-between p-4 rounded-xl border-2 transition-all ${
                  habit.completed
                    ? 'bg-green-50 border-green-200'
                    : 'bg-white border-gray-200 hover:border-blue-300'
                }`}
              >
                <div className="flex items-center space-x-4">
                  <button
                    onClick={() => !habit.completed && handleCompleteHabit(habit.habit_id)}
                    className={`w-10 h-10 rounded-full flex items-center justify-center transition-colors ${
                      habit.completed
                        ? 'bg-green-500 text-white'
                        : 'bg-gray-200 hover:bg-blue-500 hover:text-white'
                    }`}
                  >
                    {habit.completed ? <Check className="w-6 h-6" /> : <Plus className="w-5 h-5" />}
                  </button>
                  <div>
                    <p className={`font-medium ${habit.completed ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                      {habit.name}
                    </p>
                    {habit.description && (
                      <p className="text-sm text-gray-500">{habit.description}</p>
                    )}
                  </div>
                </div>
                
                <div className="flex items-center space-x-3">
                  <span className="text-lg">{getCategoryIcon(habit.category)}</span>
                  <span className="text-sm text-gray-500 px-2 py-1 bg-gray-100 rounded">
                    {getCategoryLabel(habit.category)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Calendar className="w-8 h-8 text-gray-400" />
            </div>
            <p className="text-gray-500">还没有习惯，开始创建你的第一个习惯吧！</p>
          </div>
        )}
      </div>

      {/* All Habits with Edit/Delete */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">所有习惯</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {habits.filter(h => h.is_active).map((habit) => {
            const streakBadge = getStreakBadge(habit.streak_days);
            return (
              <div
                key={habit.id}
                className="p-4 border border-gray-200 rounded-xl hover:border-blue-300 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl">{getCategoryIcon(habit.category)}</span>
                    <div>
                      <h3 className="font-medium text-gray-900">{habit.name}</h3>
                      <p className="text-sm text-gray-500">{habit.description}</p>
                      <p className="text-xs text-gray-400 mt-1">
                        {getFrequencyLabel(habit.frequency)} · {getCategoryLabel(habit.category)}
                        {habit.target_value && ` · ${habit.target_value} ${habit.target_unit || '次'}`}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-1">
                    <button
                      onClick={() => handleViewCalendar(habit)}
                      className="p-2 text-gray-400 hover:text-blue-500 hover:bg-blue-50 rounded-lg transition-colors"
                      title="查看历史"
                    >
                      <Calendar className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => openEditModal(habit)}
                      className="p-2 text-gray-400 hover:text-blue-500 hover:bg-blue-50 rounded-lg transition-colors"
                      title="编辑"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => openDeleteConfirm(habit)}
                      className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                      title="删除"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                
                <div className="mt-4 flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className="flex items-center space-x-1 bg-orange-50 px-3 py-1 rounded-full">
                      <Award className="w-4 h-4 text-orange-500" />
                      <span className="text-sm font-medium text-orange-600">{habit.streak_days}天</span>
                    </div>
                    {streakBadge && (
                      <span className={`text-xs px-2 py-1 rounded-full border ${streakBadge.color}`}>
                        {streakBadge.label}
                      </span>
                    )}
                  </div>
                  <div className="text-sm text-gray-500">
                    总完成: {habit.total_completions}次
                  </div>
                </div>
              </div>
            );
          })}
        </div>
        
        {habits.filter(h => h.is_active).length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <p>暂无活跃习惯</p>
          </div>
        )}
      </div>

      {/* Add Habit Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-gray-900">创建新习惯</h2>
                <button onClick={() => { setShowAddModal(false); resetForm(); }} className="text-gray-400 hover:text-gray-600">
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>
            
            <form onSubmit={handleCreateHabit} className="p-6 space-y-4">
              {/* Template Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">快速创建（选择模板）</label>
                <div className="grid grid-cols-2 gap-2">
                  {HABIT_TEMPLATES.map((template, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => applyTemplate(template)}
                      className="text-left p-2 text-sm border border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
                    >
                      <span className="mr-1">{getCategoryIcon(template.category)}</span>
                      {template.name}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">习惯名称 *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="例如：每日喝水"
                  maxLength={50}
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">描述</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="添加习惯描述（可选）"
                  rows={2}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">分类</label>
                  <select
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    {CATEGORIES.map((cat) => (
                      <option key={cat.value} value={cat.value}>
                        {cat.emoji} {cat.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">频率</label>
                  <select
                    value={formData.frequency}
                    onChange={(e) => setFormData({ ...formData, frequency: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    {FREQUENCIES.map((freq) => (
                      <option key={freq.value} value={freq.value}>{freq.label}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">目标值</label>
                  <input
                    type="number"
                    value={formData.target_value}
                    onChange={(e) => setFormData({ ...formData, target_value: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="如：8"
                    min="1"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">单位</label>
                  <input
                    type="text"
                    value={formData.target_unit}
                    onChange={(e) => setFormData({ ...formData, target_unit: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="如：杯、分钟、次"
                  />
                </div>
              </div>

              <div className="border-t border-gray-200 pt-4">
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm font-medium text-gray-700">开启提醒</label>
                  <button
                    type="button"
                    onClick={() => setFormData({ ...formData, reminder_enabled: !formData.reminder_enabled })}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      formData.reminder_enabled ? 'bg-blue-600' : 'bg-gray-200'
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        formData.reminder_enabled ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>
                {formData.reminder_enabled && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">提醒时间</label>
                    <input
                      type="time"
                      value={formData.reminder_time}
                      onChange={(e) => setFormData({ ...formData, reminder_time: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                )}
              </div>

              <div className="flex space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => { setShowAddModal(false); resetForm(); }}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  取消
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  创建习惯
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Habit Modal */}
      {showEditModal && selectedHabit && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-gray-900">编辑习惯</h2>
                <button onClick={() => { setShowEditModal(false); setSelectedHabit(null); resetForm(); }} className="text-gray-400 hover:text-gray-600">
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>
            
            <form onSubmit={handleUpdateHabit} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">习惯名称 *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  maxLength={50}
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">描述</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  rows={2}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">分类</label>
                  <select
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    {CATEGORIES.map((cat) => (
                      <option key={cat.value} value={cat.value}>
                        {cat.emoji} {cat.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">频率</label>
                  <select
                    value={formData.frequency}
                    onChange={(e) => setFormData({ ...formData, frequency: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    {FREQUENCIES.map((freq) => (
                      <option key={freq.value} value={freq.value}>{freq.label}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">目标值</label>
                  <input
                    type="number"
                    value={formData.target_value}
                    onChange={(e) => setFormData({ ...formData, target_value: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    min="1"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">单位</label>
                  <input
                    type="text"
                    value={formData.target_unit}
                    onChange={(e) => setFormData({ ...formData, target_unit: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              <div className="border-t border-gray-200 pt-4">
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm font-medium text-gray-700">开启提醒</label>
                  <button
                    type="button"
                    onClick={() => setFormData({ ...formData, reminder_enabled: !formData.reminder_enabled })}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      formData.reminder_enabled ? 'bg-blue-600' : 'bg-gray-200'
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        formData.reminder_enabled ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>
                {formData.reminder_enabled && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">提醒时间</label>
                    <input
                      type="time"
                      value={formData.reminder_time}
                      onChange={(e) => setFormData({ ...formData, reminder_time: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                )}
              </div>

              <div className="flex space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => { setShowEditModal(false); setSelectedHabit(null); resetForm(); }}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  取消
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  保存修改
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation */}
      {showDeleteConfirm && selectedHabit && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl w-full max-w-md p-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Trash2 className="w-8 h-8 text-red-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">确认删除</h3>
              <p className="text-gray-600 mb-6">
                确定要删除习惯 "<strong>{selectedHabit.name}</strong>" 吗？
                <br />
                <span className="text-red-500 text-sm">删除后历史记录将不可恢复</span>
              </p>
              <div className="flex space-x-3">
                <button
                  onClick={() => { setShowDeleteConfirm(false); setSelectedHabit(null); }}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  取消
                </button>
                <button
                  onClick={handleDeleteHabit}
                  className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                >
                  确认删除
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Calendar Modal */}
      {showCalendar && selectedHabit && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl w-full max-w-lg">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">{selectedHabit.name}</h2>
                  <p className="text-sm text-gray-500">打卡记录</p>
                </div>
                <button onClick={() => { setShowCalendar(false); setSelectedHabit(null); }} className="text-gray-400 hover:text-gray-600">
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>
            
            <div className="p-6">
              {/* Month Navigation */}
              <div className="flex items-center justify-between mb-4">
                <button
                  onClick={() => {
                    const newMonth = new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1);
                    setCurrentMonth(newMonth);
                    loadCalendarCompletions(selectedHabit.id);
                  }}
                  className="p-2 hover:bg-gray-100 rounded-lg"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <span className="font-medium">
                  {currentMonth.getFullYear()}年 {currentMonth.getMonth() + 1}月
                </span>
                <button
                  onClick={() => {
                    const newMonth = new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1);
                    setCurrentMonth(newMonth);
                    loadCalendarCompletions(selectedHabit.id);
                  }}
                  className="p-2 hover:bg-gray-100 rounded-lg"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>

              {/* Calendar Grid */}
              <div className="grid grid-cols-7 gap-1 text-center mb-2">
                {['日', '一', '二', '三', '四', '五', '六'].map((day, idx) => (
                  <div key={idx} className="text-xs font-medium text-gray-500 py-2">
                    {day}
                  </div>
                ))}
              </div>
              <div className="grid grid-cols-7 gap-1">
                {getCalendarDays().map((day, idx) => {
                  if (day === null) {
                    return <div key={idx} className="h-10"></div>;
                  }
                  const isCompleted = isCompletionDate(day);
                  const isToday = getTodayDateStr() === `${currentMonth.getFullYear()}-${String(currentMonth.getMonth() + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
                  return (
                    <div
                      key={idx}
                      className={`h-10 flex items-center justify-center text-sm rounded-lg ${
                        isCompleted
                          ? 'bg-green-500 text-white'
                          : isToday
                          ? 'bg-blue-100 text-blue-700'
                          : 'text-gray-700'
                      }`}
                    >
                      {day}
                    </div>
                  );
                })}
              </div>

              {/* Legend */}
              <div className="flex items-center justify-center space-x-4 mt-4 text-sm text-gray-500">
                <div className="flex items-center">
                  <div className="w-4 h-4 bg-green-500 rounded mr-2"></div>
                  <span>已打卡</span>
                </div>
                <div className="flex items-center">
                  <div className="w-4 h-4 bg-blue-100 rounded mr-2"></div>
                  <span>今日</span>
                </div>
              </div>

              {/* Stats */}
              <div className="mt-6 pt-4 border-t border-gray-200">
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <p className="text-2xl font-bold text-gray-900">{selectedHabit.total_completions}</p>
                    <p className="text-sm text-gray-500">总打卡次数</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-orange-500">{selectedHabit.streak_days}</p>
                    <p className="text-sm text-gray-500">当前连续</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-green-500">{calendarCompletions.length}</p>
                    <p className="text-sm text-gray-500">本月打卡</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
