import React, { useState, useEffect } from 'react';
import { Camera, Trash2, X, ChevronDown, ChevronUp, Scale } from 'lucide-react';
// import { useAuthStore } from '../store/authStore'; // 暂未使用
import { api } from '../api/client';

interface FoodItem {
  id?: number;
  name: string;
  grams?: number;
  calories?: number;
  protein?: number;
  carbs?: number;
  fat?: number;
  serving_size?: number;
  serving_unit?: string;
  quantity?: number;
  calories_per_serving?: number;
  protein_per_serving?: number;
  carbs_per_serving?: number;
  fat_per_serving?: number;
}

interface MealAnalysis {
  meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack';
  items: FoodItem[];
  total_calories: number;
  total_protein: number;
  total_carbs: number;
  total_fat: number;
  notes: string;
}

interface MealRecord {
  id: number;
  name: string;
  meal_type: string;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  meal_datetime: string;
  items?: FoodItem[];
  notes?: string;
}

const DietTracking: React.FC = () => {
  // user 变量已移除，因为当前没有使用
  // const { user } = useAuthStore();
  
  // 餐食记录状态
  const [selectedDate] = useState<string>(() => {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  });
  // setSelectedDate 暂未使用
  const [meals, setMeals] = useState<MealRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  // error 状态已移除，改用 alert 提示错误
  
  // 拍照识别相关状态
  const [selectedPhoto, setSelectedPhoto] = useState<string | null>(null);
  const [showPhotoModal, setShowPhotoModal] = useState<boolean>(false);
  const [analyzingPhoto, setAnalyzingPhoto] = useState<boolean>(false);
  const [photoAnalysis, setPhotoAnalysis] = useState<MealAnalysis | null>(null);
  
  // 餐次选择状态
  const [selectedMealType, setSelectedMealType] = useState<'breakfast' | 'lunch' | 'dinner' | 'snack'>('lunch');
  
  // 餐食详情展开状态
  const [expandedMealId, setExpandedMealId] = useState<number | null>(null);
  
  // 获取时区偏移量
  const getTimezoneOffset = () => {
    const offset = new Date().getTimezoneOffset();
    const hours = Math.abs(Math.floor(offset / 60));
    const minutes = Math.abs(offset % 60);
    const sign = offset <= 0 ? '+' : '-';
    return `${sign}${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`;
  };

  // 根据餐次获取合理的时间
  const getMealDatetime = (mealType: string): string => {
    const hourMap: Record<string, string> = {
      'breakfast': '08',  // 早餐 8 点
      'lunch': '12',      // 午餐 12 点
      'dinner': '19',     // 晚餐 19 点
      'snack': '15'       // 加餐 15 点
    };
    const hour = hourMap[mealType] || '12';
    return `${selectedDate}T${hour}:00:00${getTimezoneOffset()}`;
  };

  // 餐次类型选项
  const mealTypeOptions = [
    { value: 'breakfast', label: '早餐', color: 'bg-blue-100 text-blue-800' },
    { value: 'lunch', label: '午餐', color: 'bg-green-100 text-green-800' },
    { value: 'dinner', label: '晚餐', color: 'bg-purple-100 text-purple-800' },
    { value: 'snack', label: '加餐', color: 'bg-yellow-100 text-yellow-800' },
  ];

  // 获取餐食摘要
  const getMealSummary = (meal: MealRecord): string => {
    if (!meal.items || meal.items.length === 0) {
      return '暂无食材详情';
    }
    
    const validItems = meal.items.filter(item => item.name);
    if (validItems.length === 0) {
      return '暂无食材详情';
    }
    
    const itemNames = validItems.map(item => item.name);
    if (itemNames.length <= 3) {
      return `包含：${itemNames.join('、')}`;
    } else {
      return `包含：${itemNames.slice(0, 3).join('、')}等${itemNames.length}种食材`;
    }
  };
  
  // 获取餐食总热量
  const getMealTotalCalories = (meal: MealRecord): number => {
    if (meal.calories && meal.calories > 0) {
      return Math.round(meal.calories);
    }
    
    // 如果meal.calories为0或未定义，计算items的热量
    if (meal.items && meal.items.length > 0) {
      return Math.round(meal.items.reduce((total, item) => {
        const calories = item.calories_per_serving || item.calories || 0;
        const quantity = item.quantity || 1;
        return total + calories * quantity;
      }, 0));
    }
    
    return 0;
  };

  // 获取每日餐食
  const fetchDailyMeals = async () => {
    try {
      setLoading(true);
      const response = await api.getDailyMeals(selectedDate);
      setMeals(response.meals || []);
    } catch (error: any) {
      console.error('Failed to fetch meals:', error);
      setMeals([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDailyMeals();
  }, [selectedDate]);

  // 处理照片上传
  const handlePhotoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        const dataURL = reader.result as string;
        // 提取纯base64部分（去掉 data:image/jpeg;base64, 前缀）
        // 后端期望纯base64字符串，它会自己添加 data:image/jpeg;base64, 前缀
        const pureBase64 = dataURL.split(',')[1];
        setSelectedPhoto(pureBase64);
        setShowPhotoModal(true);
      };
      reader.readAsDataURL(file);
    }
  };

  // 分析照片
  const handleAnalyzePhoto = async () => {
    if (!selectedPhoto) return;
    
    try {
      setAnalyzingPhoto(true);
      const response = await api.analyzeFoodImage(selectedPhoto);
      setPhotoAnalysis(response);
      
      // 分析成功后关闭模态框，但保留 selectedPhoto 和 photoAnalysis
      setShowPhotoModal(false);
    } catch (error) {
      console.error('Failed to analyze photo:', error);
      alert('照片分析失败，请重试'); // 使用 alert 而不是 setError，避免影响主界面
      // 分析失败时清除状态，允许用户重新上传
      handleClearAll();
    } finally {
      setAnalyzingPhoto(false);
    }
  };

  // 确认保存餐食
  const handleConfirmMeal = async () => {
    if (!photoAnalysis) return;
    
    try {
      // 创建餐食记录 - 完全使用用户选择的餐次，不依赖 AI 识别结果
      const mealData = {
        name: `${selectedMealType}餐食`,
        meal_type: selectedMealType,  // ✅ 使用用户选择的餐次
        calories: photoAnalysis.total_calories,
        protein: photoAnalysis.total_protein,
        carbs: photoAnalysis.total_carbs,
        fat: photoAnalysis.total_fat,
        notes: photoAnalysis.notes,
        meal_datetime: getMealDatetime(selectedMealType), // 根据餐次设置合理时间（仅用于显示）
        items: photoAnalysis.items.map(item => ({
          name: item.name,
          serving_size: item.grams,
          serving_unit: 'g',
          quantity: 1,
          calories_per_serving: item.calories,
          protein_per_serving: item.protein,
          carbs_per_serving: item.carbs,
          fat_per_serving: item.fat
        }))
      };
      
      // 检查是否已存在同类型同时间的餐食
      // 使用更宽松的匹配：同一天、同餐次类型
      const mealDate = new Date(`${selectedDate}T12:00:00`);
      const existingMeal = meals.find(meal => {
        const mealTime = new Date(meal.meal_datetime);
        const isSameDay = mealTime.toDateString() === mealDate.toDateString();
        const isSameMealType = meal.meal_type === selectedMealType; // ✅ 使用用户选择的餐次
        return isSameDay && isSameMealType;
      });
      
      if (existingMeal) {
        // 更新现有餐食
        await api.updateMeal(existingMeal.id, mealData);
      } else {
        // 创建新餐食
        await api.createMeal(mealData);
      }
      
      // 刷新数据
      await fetchDailyMeals();
      
      // 清除状态
      handleClearAll();
      
      // 显示成功提示
      alert(existingMeal ? '餐食记录已更新！' : '餐食记录已保存！');
      
    } catch (error) {
      console.error('Failed to save meal:', error);
      alert('保存餐食记录失败，请重试'); // 使用 alert 而不是 setError，避免影响主界面
      // 不清除状态，允许用户重试
    }
  };

  // 清除所有状态
  const handleClearAll = () => {
    setSelectedPhoto(null);
    setPhotoAnalysis(null);
    setShowPhotoModal(false);
    // 注意：不清除 selectedMealType，让用户的选择保持
    // 如果用户想改变餐次，可以手动点击其他餐次按钮
  };

  // 删除餐食
  const handleDeleteMeal = async (mealId: number) => {
    if (!confirm('确定要删除这条餐食记录吗？')) return;
    
    try {
      await api.deleteMeal(mealId);
      await fetchDailyMeals();
    } catch (error) {
      console.error('Failed to delete meal:', error);
      alert('删除餐食记录失败'); // 使用 alert 而不是 setError
    }
  };

  // 计算今日总热量
  const getTodayTotalCalories = () => {
    return Math.round(meals.reduce((total, meal) => total + getMealTotalCalories(meal), 0));
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">饮食记录</h1>
          <p className="text-gray-600 mt-2">拍照识别食物，自动记录营养成分</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 左侧：拍照识别 */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-6">拍照识别食材</h2>
              
              {/* 餐次选择 */}
              <div className="mb-8">
                <h3 className="text-sm font-medium text-gray-900 mb-3">选择餐次</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {mealTypeOptions.map((option) => (
                    <button
                      key={option.value}
                      onClick={() => setSelectedMealType(option.value as any)}
                      className={`py-3 px-4 rounded-xl border transition-all ${
                        selectedMealType === option.value
                          ? `${option.color} border-transparent`
                          : 'bg-white border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="font-medium">{option.label}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* 拍照区域 */}
              <div className="mb-8">
                <div className="border-2 border-dashed border-gray-300 rounded-2xl p-8 text-center hover:border-purple-400 transition-colors">
                  <input
                    type="file"
                    accept="image/*"
                    capture="environment"
                    onChange={handlePhotoUpload}
                    className="hidden"
                    id="photo-upload"
                  />
                  <label htmlFor="photo-upload" className="cursor-pointer block">
                    <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <Camera className="w-8 h-8 text-purple-500" />
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">拍照识别食材</h3>
                    <p className="text-gray-600 mb-6">
                      点击上方按钮拍照或选择照片，AI将自动识别食材并计算营养成分
                    </p>
                  </label>
                </div>
              </div>

              {/* 照片分析结果 */}
              {photoAnalysis && (
                <div className="bg-gray-50 rounded-2xl p-6">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-lg font-semibold text-gray-900">分析结果</h3>
                    <button
                      onClick={handleClearAll}
                      className="p-2 hover:bg-gray-200 rounded-lg"
                    >
                      <X className="w-5 h-5 text-gray-500" />
                    </button>
                  </div>

                  {/* 食材列表 */}
                  <div className="space-y-4 mb-6">
                    {photoAnalysis.items.map((item, index) => (
                      <div key={index} className="flex items-center justify-between bg-white p-4 rounded-xl">
                        <div>
                          <div className="font-medium text-gray-900">{item.name}</div>
                          <div className="text-sm text-gray-600">{item.grams}g</div>
                        </div>
                        <div className="text-right">
                          <div className="font-bold text-red-600">{item.calories} kcal</div>
                          <div className="text-xs text-gray-600">
                            蛋: {item.protein}g | 碳: {item.carbs}g | 脂: {item.fat}g
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* 总计 */}
                  <div className="bg-white rounded-xl p-4 mb-6">
                    <div className="grid grid-cols-4 gap-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-red-600">{photoAnalysis.total_calories}</div>
                        <div className="text-sm text-gray-600">总热量</div>
                      </div>
                      <div className="text-center">
                        <div className="text-xl font-bold text-blue-600">{photoAnalysis.total_protein}</div>
                        <div className="text-sm text-gray-600">蛋白质</div>
                      </div>
                      <div className="text-center">
                        <div className="text-xl font-bold text-purple-600">{photoAnalysis.total_carbs}</div>
                        <div className="text-sm text-gray-600">碳水</div>
                      </div>
                      <div className="text-center">
                        <div className="text-xl font-bold text-yellow-600">{photoAnalysis.total_fat}</div>
                        <div className="text-sm text-gray-600">脂肪</div>
                      </div>
                    </div>
                  </div>

                  {/* AI 营养评价和建议 */}
                  {photoAnalysis.notes && (
                    <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6">
                      <div className="flex items-start gap-3">
                        <div className="flex-shrink-0">
                          <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                            <Scale className="w-5 h-5 text-blue-600" />
                          </div>
                        </div>
                        <div className="flex-1">
                          <h4 className="text-sm font-semibold text-blue-900 mb-2">
                            🤖 AI 营养评价
                          </h4>
                          <p className="text-sm text-blue-800 leading-relaxed whitespace-pre-wrap">
                            {photoAnalysis.notes}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* 确认按钮 */}
                  <button
                    onClick={handleConfirmMeal}
                    className="w-full py-3 bg-blue-600 text-white font-medium rounded-xl hover:bg-blue-700 transition-colors"
                  >
                    确认保存餐食记录
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* 右侧：今日餐食记录 */}
          <div>
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-lg font-semibold text-gray-900">今日餐食记录</h2>
                {meals.length > 0 && (
                  <div className="text-sm text-gray-600">
                    <span className="font-medium">{meals.length}</span> 餐 · 
                    <span className="font-medium text-red-600 ml-1">
                      {getTodayTotalCalories()}
                    </span> 大卡
                  </div>
                )}
              </div>
              
              {loading && !meals.length ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
                  <p className="text-gray-600">正在加载...</p>
                </div>
              ) : meals.length === 0 ? (
                <div className="text-center py-8">
                  <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <span className="text-gray-400 text-2xl">🍽️</span>
                  </div>
                  <p className="text-gray-600">今日还没有记录餐食</p>
                  <p className="text-sm text-gray-500 mt-1">点击左侧开始记录第一餐</p>
                </div>
              ) : (
                <div className="space-y-4">
                   {meals.map((meal) => (
                    <div key={meal.id} className="bg-white rounded-xl p-4 border border-gray-200 hover:border-gray-300 transition-colors">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className={`px-2 py-0.5 text-xs rounded-full ${mealTypeOptions.find(opt => opt.value === meal.meal_type)?.color || 'bg-gray-100 text-gray-800'}`}>
                              {meal.meal_type === 'breakfast' ? '早餐' : 
                               meal.meal_type === 'lunch' ? '午餐' : 
                               meal.meal_type === 'dinner' ? '晚餐' : '加餐'}
                            </span>
                            <span className="font-medium text-gray-900">{meal.name}</span>
                            <span className="text-sm text-gray-500">
                              {new Date(meal.meal_datetime).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}
                            </span>
                          </div>
                          
                          {/* 餐食内容摘要 */}
                          <div className="mt-2">
                            <div className="text-sm text-gray-700 line-clamp-1">
                              {getMealSummary(meal)}
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex items-center gap-2">
                          {/* 热量显示 */}
                          <div className="text-right">
                            <div className="text-lg font-bold text-red-600">{getMealTotalCalories(meal)}</div>
                            <div className="text-xs text-gray-600">大卡</div>
                          </div>
                          
                          <button
                            onClick={() => setExpandedMealId(expandedMealId === meal.id ? null : meal.id)}
                            className="p-1 hover:bg-gray-100 rounded-lg transition-colors"
                            title={expandedMealId === meal.id ? "收起详情" : "查看详情"}
                          >
                            {expandedMealId === meal.id ? (
                              <ChevronUp className="w-4 h-4 text-gray-600" />
                            ) : (
                              <ChevronDown className="w-4 h-4 text-gray-600" />
                            )}
                          </button>
                          
                          <button
                            onClick={() => handleDeleteMeal(meal.id)}
                            className="p-1 hover:bg-red-50 rounded-lg transition-colors"
                            title="删除餐食"
                          >
                            <Trash2 className="w-4 h-4 text-red-500" />
                          </button>
                        </div>
                      </div>
                      
                      {/* 营养概要 */}
                      <div className="grid grid-cols-3 gap-2 mt-3 pt-3 border-t border-gray-100">
                        <div className="text-center">
                          <div className="font-medium text-blue-600">{Math.round(meal.protein)}g</div>
                          <div className="text-xs text-gray-600">蛋白质</div>
                        </div>
                        <div className="text-center">
                          <div className="font-medium text-purple-600">{Math.round(meal.carbs)}g</div>
                          <div className="text-xs text-gray-600">碳水</div>
                        </div>
                        <div className="text-center">
                          <div className="font-medium text-yellow-600">{Math.round(meal.fat)}g</div>
                          <div className="text-xs text-gray-600">脂肪</div>
                        </div>
                      </div>
                      
                      {/* 展开的详情 */}
                      {expandedMealId === meal.id && meal.items && meal.items.length > 0 && (
                        <div className="mt-4 pt-4 border-t border-gray-100">
                          <div className="mb-2">
                            <h4 className="text-sm font-medium text-gray-900 mb-2">食材详情</h4>
                            <div className="space-y-2">
                              {meal.items.map((item, index) => (
                                <div key={index} className="flex justify-between items-center text-sm">
                                  <div className="flex-1">
                                    <span className="text-gray-800">{item.name}</span>
                                    <span className="text-gray-500 text-xs ml-2">
                                      {item.serving_size}{item.serving_unit} × {item.quantity || 1}
                                    </span>
                                  </div>
                                  <div className="text-right">
                                    <span className="text-gray-700 font-medium">
                                      {Math.round(((item.calories_per_serving || item.calories || 0) * (item.quantity || 1)))} kcal
                                    </span>
                                    <div className="text-xs text-gray-500 flex gap-2 mt-0.5">
                                      <span>蛋: {Math.round(item.protein_per_serving || item.protein || 0)}g</span>
                                      <span>碳: {Math.round(item.carbs_per_serving || item.carbs || 0)}g</span>
                                      <span>脂: {Math.round(item.fat_per_serving || item.fat || 0)}g</span>
                                    </div>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                          
                          {meal.notes && (
                            <div className="mt-3 pt-3 border-t border-gray-100">
                              <h4 className="text-sm font-medium text-gray-900 mb-1">备注</h4>
                              <p className="text-sm text-gray-600">{meal.notes}</p>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* 照片预览模态框 */}
      {showPhotoModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-900">照片预览</h3>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setShowPhotoModal(false)}
                    className="p-2 hover:bg-gray-100 rounded-lg"
                  >
                    <X className="w-5 h-5 text-gray-500" />
                  </button>
                </div>
              </div>

               <div className="mb-6">
                {selectedPhoto && (
                  <img
                    src={`data:image/jpeg;base64,${selectedPhoto}`}
                    alt="预览"
                    className="w-full h-auto rounded-xl"
                  />
                )}
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setShowPhotoModal(false)}
                  className="flex-1 py-3 border border-gray-300 text-gray-700 font-medium rounded-xl hover:bg-gray-50 transition-colors"
                >
                  取消
                </button>
                <button
                  onClick={handleAnalyzePhoto}
                  disabled={analyzingPhoto}
                  className="flex-1 py-3 bg-blue-600 text-white font-medium rounded-xl hover:bg-blue-700 transition-colors disabled:opacity-50"
                >
                  {analyzingPhoto ? '分析中...' : '开始分析'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DietTracking;