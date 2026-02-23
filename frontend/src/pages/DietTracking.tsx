import React, { useState, useEffect } from 'react';
import { Plus, Search, Calendar, Utensils, Flame, Droplets, Apple, Carrot, Milk } from 'lucide-react';
import { Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
} from 'chart.js';
import { api } from '../api/client';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement);

const DietTracking = () => {
  const [meals, setMeals] = useState([]);
  const [foods, setFoods] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  
  // Form state
  const [newMeal, setNewMeal] = useState({
    name: '',
    meal_type: 'breakfast',
    calories: 0,
    protein: 0,
    carbs: 0,
    fat: 0,
    notes: ''
  });
  
  const [newFoodItem, setNewFoodItem] = useState({
    name: '',
    category: 'vegetable',
    serving_size: 100,
    serving_unit: 'g',
    calories_per_serving: 0,
    protein_per_serving: 0,
    carbs_per_serving: 0,
    fat_per_serving: 0,
    is_custom: true
  });

  useEffect(() => {
    fetchDailyMeals();
    fetchFoodDatabase();
  }, [selectedDate]);

  const fetchDailyMeals = async () => {
    try {
      setLoading(true);
      // Note: Actual API endpoint for retrieving meals may differ 
      // This would connect to /api/v1/nutrition/meals endpoint
      const response = await api.client.get('/nutrition/daily-meals', {
        params: { date: selectedDate }
      });
      setMeals(response.data.meals || []);
    } catch (error) {
      console.error('Failed to fetch meals:', error);
      // Set empty array if user hasn't eaten anything this date yet
      setMeals([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchFoodDatabase = async () => {
    try {
      // Retrieve from /api/v1/nutrition/food-items endpoint
      const response = await api.client.get('/nutrition/food-items');
      setFoods(response.data.food_items || []);
    } catch (error) {
      console.error('Failed to fetch food database:', error);
      setFoods([]);
    }
  };

  const handleSaveNewMeal = async (e) => {
    e.preventDefault();
    
    try {
      // Save to /api/v1/nutrition/meals endpoint
      const dataToSend = { 
        ...newMeal, 
        meal_datetime: `${selectedDate}T12:00:00`,
        items: [], // Would add items here if we had food item creation flow
      };
      const response = await api.client.post('/nutrition/meals', dataToSend);
      
      // Add to local state
      setMeals([...meals, response.data]);
      setNewMeal({
        name: '',
        meal_type: 'breakfast',
        calories: 0,
        protein: 0,
        carbs: 0,
        fat: 0,
        notes: ''
      });
      setShowAddForm(false);
    } catch (err) {
      console.error('Failed to add meal:', err);
    }
  };

  const handleSaveNewFood = async (e) => {
    e.preventDefault();
    
    try {
      // Save to /api/v1/nutrition/food-items endpoint
      const response = await api.client.post('/nutrition/food-items', newFoodItem);
      
      setFoods([...foods, response.data]);
      setNewFoodItem({
        name: '',
        category: 'vegetable',
        serving_size: 100,
        serving_unit: 'g',
        calories_per_serving: 0,
        protein_per_serving: 0,
        carbs_per_serving: 0,
        fat_per_serving: 0,
        is_custom: true
      });
    } catch (err) {
      console.error('Failed to add food:', err);
    }
  };

  // Calculate nutrient totals
  const totalCalories = meals.reduce((sum, meal) => sum + (meal.calories || 0), 0);
  const totalProtein = meals.reduce((sum, meal) => sum + (meal.protein || 0), 0);
  const totalCarbs = meals.reduce((sum, meal) => sum + (meal.carbs || 0), 0);
  const totalFat = meals.reduce((sum, meal) => sum + (meal.fat || 0), 0);
  
  // Nutrient distribution for chart
  const chartData = {
    labels: ['蛋白质', '碳水化合物', '脂肪'],
    datasets: [
      {
        data: [totalProtein, totalCarbs, totalFat],
        backgroundColor: [
          'rgba(54, 162, 235, 0.8)',
          'rgba(255, 206, 86, 0.8)',
          'rgba(255, 99, 132, 0.8)',
        ],
        borderColor: [
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(255, 99, 132, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">饮食记录</h1>
          <p className="text-gray-600 mt-1">记录您的日常饮食，掌握营养摄入情况</p>
        </div>
        <div className="flex gap-3">
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-xl focus:ring-blue-500 focus:border-blue-500"
          />
          <button
            onClick={() => setShowAddForm(true)}
            className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-xl hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-5 h-5" />
            <span>添加餐食</span>
          </button>
        </div>
      </div>

      {/* Stats Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-2xl p-5 text-red-800">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-red-200 rounded-xl flex items-center justify-center">
              <Flame className="w-6 h-6" />
            </div>
            <div>
              <p className="text-sm">总热量</p>
              <p className="text-2xl font-bold">{totalCalories?.toFixed(0) || 0} <span className="text-lg">kcal</span></p>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl p-5 text-blue-800">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-blue-200 rounded-xl flex items-center justify-center">
              <Apple className="w-6 h-6" />
            </div>
            <div>
              <p className="text-sm">蛋白质</p>
              <p className="text-2xl font-bold">{totalProtein?.toFixed(1) || 0} <span className="text-lg">g</span></p>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-2xl p-5 text-yellow-800">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-yellow-200 rounded-xl flex items-center justify-center">
              <Carrot className="w-6 h-6" />
            </div>
            <div>
              <p className="text-sm">碳水</p>
              <p className="text-2xl font-bold">{totalCarbs?.toFixed(1) || 0} <span className="text-lg">g</span></p>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-2xl p-5 text-green-800">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-green-200 rounded-xl flex items-center justify-center">
              <Milk className="w-6 h-6" />
            </div>
            <div>
              <p className="text-sm">脂肪</p>
              <p className="text-2xl font-bold">{totalFat?.toFixed(1) || 0} <span className="text-lg">g</span></p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Meal Entries Section */}
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">今日餐食记录</h2>
            </div>
            {meals.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Utensils className="w-12 h-12 mx-auto text-gray-300 mb-3" />
                <p>今天还没有记录任何餐饮</p>
                <p className="text-sm">记录第一餐以开始追踪您的营养摄入</p>
              </div>
            ) : (
              <div className="space-y-4">
                {meals.map((meal) => (
                  <div key={meal.id} className="border border-gray-200 rounded-xl p-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-semibold text-gray-900">{meal.name}</h3>
                        <p className="text-sm text-gray-500 capitalize">{meal.meal_type}</p>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold">{meal.calories || 0} kcal</p>
                        <p className="text-sm text-gray-500">
                          P: {meal.protein || 0}g C: {meal.carbs || 0}g F: {meal.fat || 0}g
                        </p>
                      </div>
                    </div>
                    {meal.notes && <p className="mt-2 text-sm text-gray-600">{meal.notes}</p>}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Nutrition Distribution */}
        <div className="space-y-6">
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">营养分布</h2>
            <div className="h-64">
              <Pie data={chartData} options={{ responsive: true, maintainAspectRatio: false }} />
            </div>
            <div className="mt-4 grid grid-cols-3 gap-2 text-center">
              <div className="bg-blue-50 rounded-lg p-2">
                <p className="text-sm text-blue-600 font-medium">蛋白质</p>
                <p className="text-lg font-bold text-blue-800">{totalProtein?.toFixed(1) || 0}g</p>
              </div>
              <div className="bg-yellow-50 rounded-lg p-2">
                <p className="text-sm text-yellow-600 font-medium">碳水</p>
                <p className="text-lg font-bold text-yellow-800">{totalCarbs?.toFixed(1) || 0}g</p>
              </div>
              <div className="bg-red-50 rounded-lg p-2">
                <p className="text-sm text-red-600 font-medium">脂肪</p>
                <p className="text-lg font-bold text-red-800">{totalFat?.toFixed(1) || 0}g</p>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">快捷操作</h2>
            <div className="space-y-3">
              <button
                onClick={() => document.getElementById('quick-breakfast')?.click()}
                className="w-full text-left p-3 bg-blue-50 hover:bg-blue-100 rounded-lg text-blue-700 transition-colors"
              >
                💛 快速记录早餐
              </button>
              <button
                onClick={() => document.getElementById('quick-lunch')?.click()} 
                className="w-full text-left p-3 bg-purple-50 hover:bg-purple-100 rounded-lg text-purple-700 transition-colors"
              >
                🥗 快速记录午餐
              </button>
              <button
                onClick={() => document.getElementById('quick-dinner')?.click()}
                className="w-full text-left p-3 bg-green-50 hover:bg-green-100 rounded-lg text-green-700 transition-colors"
              >
                🍲 快速记录晚餐
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Add Meal Modal */}
      {showAddForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl w-full max-w-md max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">添加餐食记录</h2>
              <form onSubmit={handleSaveNewMeal}>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">餐名</label>
                    <input
                      type="text"
                      value={newMeal.name}
                      onChange={(e) => setNewMeal({...newMeal, name: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-blue-500 focus:border-blue-500"
                      placeholder="早餐/午餐/晚餐/加餐"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">餐类别</label>
                    <select
                      value={newMeal.meal_type}
                      onChange={(e) => setNewMeal({...newMeal, meal_type: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="breakfast">早餐</option>
                      <option value="lunch">午餐</option>
                      <option value="dinner">晚餐</option>
                      <option value="snack">加餐</option>
                    </select>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">热量 (kcal)</label>
                      <input
                        type="number"
                        value={newMeal.calories}
                        onChange={(e) => setNewMeal({...newMeal, calories: parseFloat(e.target.value) || 0})}
                        className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-blue-500 focus:border-blue-500"
                        min="0"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">蛋白质 (g)</label>
                      <input
                        type="number"
                        value={newMeal.protein}
                        onChange={(e) => setNewMeal({...newMeal, protein: parseFloat(e.target.value) || 0})}
                        className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-blue-500 focus:border-blue-500"
                        min="0"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">碳水 (g)</label>
                      <input
                        type="number"
                        value={newMeal.carbs}
                        onChange={(e) => setNewMeal({...newMeal, carbs: parseFloat(e.target.value) || 0})}
                        className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-blue-500 focus:border-blue-500"
                        min="0"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">脂肪 (g)</label>
                      <input
                        type="number"
                        value={newMeal.fat}
                        onChange={(e) => setNewMeal({...newMeal, fat: parseFloat(e.target.value) || 0})}
                        className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-blue-500 focus:border-blue-500"
                        min="0"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">备注</label>
                    <textarea
                      value={newMeal.notes}
                      onChange={(e) => setNewMeal({...newMeal, notes: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-blue-500 focus:border-blue-500"
                      rows="3"
                      placeholder="用餐时间、食材特殊说明..."
                    ></textarea>
                  </div>
                </div>

                <div className="flex gap-3 mt-6">
                  <button
                    type="button"
                    onClick={() => setShowAddForm(false)}
                    className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 transition-colors"
                  >
                    取消
                  </button>
                  <button
                    type="submit"
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors"
                  >
                    保存记录
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DietTracking;