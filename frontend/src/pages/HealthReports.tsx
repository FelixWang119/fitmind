import React, { useState, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, 
  PieChart, Pie, Cell,
  TrendingUp, TrendingDown, Target, Flame, Droplets, Footprints
} from 'recharts';
import { 
  Calendar, Download, Share2, Award, 
  ArrowUpRight, ArrowDownRight, Eye,
  Clock, Flame as FlameIcon, Droplets as DropletsIcon,
  HeartPulse, Activity
} from 'lucide-react';
import { api } from '../api/client';

const HealthReports = () => {
  const [reportData, setReportData] = useState(null);
  const [weeklyTrends, setWeeklyTrends] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState({
    startDate: new Date(new Date().setDate(new Date().getDate() - 30)).toISOString().split('T')[0],
    endDate: new Date().toISOString().split('T')[0]
  });

  useEffect(() => {
    generateHealthReport();
    getWeeklyTrends();
  }, [dateRange]);

  const generateHealthReport = async () => {
    try {
      setLoading(true);
      const response = await api.client.post('/health-reports/generate-report', {
        start_date: dateRange.startDate,
        end_date: dateRange.endDate
      });
      setReportData(response.data.report);
    } catch (error) {
      console.error('Failed to generate health report:', error);
    } finally {
      setLoading(false);
    }
  };

  const getWeeklyTrends = async () => {
    try {
      const response = await api.client.get('/health-reports/weekly-health-trends', {
        params: { weeks_back: 4 }
      });
      setWeeklyTrends(response.data.weekly_trends);
    } catch (error) {
      console.error('Failed to fetch weekly trends:', error);
    }
  };

  // Prepare chart data
  const weightData = weeklyTrends.map(trend => ({
    name: trend.week,
    weight: trend.avg_weight_kg,
  })).filter(item => item.weight !== null);

  const nutritionData = weeklyTrends.map(trend => ({
    name: trend.week,
    calories: trend.avg_daily_calories,
    protein: Math.round(trend.avg_daily_calories * 0.25 / 4), // Estimate protein in grams
  }));

  const exerciseData = weeklyTrends.map(trend => ({
    name: trend.week,
    minutes: trend.avg_daily_exercise_minutes,
    steps: Math.round(trend.avg_daily_exercise_minutes * 20), // Estimate steps based on exercise
  }));

  // Prepare achievement data for pie chart
  const achievementsData = [
    { name: '达成目标', value: reportData?.achievements?.filter((a: any) => a.achieved).length || 0 },
    { name: '待完成', value: reportData?.achievements?.filter((a: any) => !a.achieved).length || 0 }
  ];

  const COLORS = ['#10B981', '#EF4444'];

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6 p-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">健康报告</h1>
          <p className="text-gray-600 mt-1">综合分析您的健康数据，掌握趋势动态</p>
        </div>
        <div className="flex gap-3">
          <input
            type="date"
            value={dateRange.startDate}
            onChange={(e) => setDateRange({...dateRange, startDate: e.target.value})}
            className="px-4 py-2 border border-gray-300 rounded-xl focus:ring-blue-500 focus:border-blue-500"
          />
          <span className="flex items-center">至</span>
          <input
            type="date"
            value={dateRange.endDate}
            onChange={(e) => setDateRange({...dateRange, endDate: e.target.value})}
            className="px-4 py-2 border border-gray-300 rounded-xl focus:ring-blue-500 focus:border-blue-500"
          />
          <button
            onClick={generateHealthReport}
            className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-xl hover:bg-blue-700 transition-colors"
          >
            <Clock className="w-5 h-5" />
            <span>生成报告</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Weight Card */}
        <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-2xl p-6 text-purple-800">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm opacity-80">体重变化</p>
              <p className="text-2xl font-bold">
                {reportData?.summary?.weight_change_kg !== null && reportData.summary.weight_change_kg !== undefined 
                  ? (
                    <>
                      {reportData.summary.weight_change_kg > 0 ? 
                        <span className="text-red-500 flex items-center"><ArrowUpRight className="w-5 h-5 mr-1" />+{reportData.summary.weight_change_kg.toFixed(2)}kg</span> :
                        <span className="text-green-600 flex items-center"><ArrowDownRight className="w-5 h-5 mr-1" />{reportData.summary.weight_change_kg.toFixed(2)}kg</span>
                      }
                    </>
                  ) : 
                  <span>--</span>
                }
              </p>
              <p className="text-xs opacity-70 mt-1">初始: {reportData?.summary?.starting_weight_kg?.toFixed(1) || '--'}kg</p>
            </div>
            <div className="w-14 h-14 bg-white/50 rounded-xl flex items-center justify-center">
              <Footprints className="w-7 h-7" />
            </div>
          </div>
        </div>

        {/* Calories Card */}
        <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-2xl p-6 text-red-800">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm opacity-80">平均日热量</p>
              <p className="text-2xl font-bold">
                {reportData?.summary?.average_daily_calories !== null && reportData.summary.average_daily_calories !== undefined 
                  ? `${Math.round(reportData.summary.average_daily_calories)}kcal`
                  : '--'}
              </p>
              <p className="text-xs opacity-70 mt-1">总量: {reportData?.summary?.total_calories_consumed ? Math.round(reportData.summary.total_calories_consumed) : '--'} kcal</p>
            </div>
            <div className="w-14 h-14 bg-white/50 rounded-xl flex items-center justify-center">
              <FlameIcon className="w-7 h-7" />
            </div>
          </div>
        </div>

        {/* Exercise Card */}
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl p-6 text-blue-800">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm opacity-80">平均日运动</p>
              <p className="text-2xl font-bold">
                {reportData?.summary?.average_daily_exercise_minutes !== null && reportData.summary.average_daily_exercise_minutes !== undefined
                  ? `${Math.round(reportData.summary.average_daily_exercise_minutes)}分钟`
                  : '--'}
              </p>
              <p className="text-xs opacity-70 mt-1">总时长: {reportData?.summary?.total_exercise_minutes?.toFixed(0) || '--'} 分钟</p>
            </div>
            <div className="w-14 h-14 bg-white/50 rounded-xl flex items-center justify-center">
              <Activity className="w-7 h-7" />
            </div>
          </div>
        </div>

        {/* Steps Card */}
        <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-2xl p-6 text-green-800">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm opacity-80">平均日步数</p>
              <p className="text-2xl font-bold">
                {reportData?.summary?.average_daily_steps !== null && reportData.summary.average_daily_steps !== undefined
                  ? Math.round(reportData.summary.average_daily_steps).toLocaleString()
                  : '--'}
              </p>
              <p className="text-xs opacity-70 mt-1">总步数: {reportData?.summary?.total_steps ? Math.round(reportData.summary.total_steps).toLocaleString() : '--'}</p>
            </div>
            <div className="w-14 h-14 bg-white/50 rounded-xl flex items-center justify-center">
              <DropletsIcon className="w-7 h-7" />
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Weight Trend Chart */}
        <div className="lg:col-span-2 bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">体重变化趋势</h2>
          <div className="h-80">
            {weightData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={weightData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="weight" name="体重(kg)" fill="#8B5CF6" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-gray-400">
                暂无体重数据，请添加体重记录开始追踪
              </div>
            )}
          </div>
        </div>

        {/* Weekly Trends Overview */}
        <div className="space-y-6">
          {/* Achievements */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">成就统计</h2>
              <Eye className="w-5 h-5 text-gray-400" />
            </div>
            <div className="h-40">
              {reportData?.achievements ? (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={achievementsData}
                      cx="50%"
                      cy="50%"
                      innerRadius={40}
                      outerRadius={70}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {achievementsData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex items-center justify-center text-gray-400">
                  暂无成就数据
                </div>
              )}
            </div>
            <div className="mt-3 text-center">
              <p className="text-sm text-gray-600">
                {reportData?.achievements?.filter((a: any) => a.achieved).length || 0} /
                {reportData?.achievements?.length || 1} 
                已达目标
              </p>
            </div>
          </div>

          {/* Activity Trends */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">日常活动趋势</h2>
            <div className="h-48">
              {exerciseData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={exerciseData}>
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="minutes" name="运动分钟" fill="#3B82F6" />
                    <Bar dataKey="steps" name="步行估算" fill="#4F46E5" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex items-center justify-center text-gray-400">
                  暂无活动数据
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Insights */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">详细分析</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-medium text-gray-800 mb-2">体重管理</h3>
            <p className="text-gray-600 text-sm leading-relaxed">
              {reportData?.detailed_insights?.weight_management?.summary ||
                "我们的系统通过持续的体重跟踪帮您了解身体变化趋势，为您的健康管理提供科学依据。"}
            </p>
          </div>
          
          <div>
            <h3 className="font-medium text-gray-800 mb-2">营养评估</h3>
            <p className="text-gray-600 text-sm leading-relaxed">
              {reportData?.detailed_insights?.nutrition_evaluation?.summary ||
                "根据您的饮食记录，系统为您分析营养摄入情况，帮助您制定更均衡的饮食方案。"}
            </p>
          </div>
          
          <div>
            <h3 className="font-medium text-gray-800 mb-2">体育锻炼</h3>
            <p className="text-gray-600 text-sm leading-relaxed">
              {reportData?.detailed_insights?.physical_activity?.summary ||
                "运动是健康体重维持的关键，系统跟踪您的运动情况并提供个性化运动建议。"}
            </p>
          </div>
          
          <div>
            <h3 className="font-medium text-gray-800 mb-2">总体评估</h3>
            <p className="text-gray-600 text-sm leading-relaxed">
              {reportData?.summary?.active_days !== null && reportData.summary.active_days !== undefined 
                ? `在${reportData.period_start}至${reportData.period_end}期间，您共记录了${reportData.summary.active_days}个活跃健康日，展现了良好的健康意识和记录习惯。`
                : "我们正通过您的健康数据积累为您提供更精准的个性化分析。"}
            </p>
          </div>
        </div>
      </div>

      {/* Recommendations */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">AI健康建议</h2>
        <ul className="space-y-2">
          {reportData?.recommendations?.map((rec: string, idx: number) => (
            <li key={idx} className="flex items-start">
              <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 mr-3">
                <Target className="w-4 h-4 text-green-600" />
              </div>
              <span className="text-gray-700">{rec}</span>
            </li>
          )) || [
            "请添加饮食记录以便我们提供更精确的营养建议",
            "继续维持每日记录的良好习惯，这有助于长期健康管理", 
            "适当增加运动频次，结合饮食调节，以达到理想的健康效果"
          ].map((rec, idx) => (
            <li key={idx} className="flex items-start">
              <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 mr-3">
                <Target className="w-4 h-4 text-green-600" />
              </div>
              <span className="text-gray-700">{rec}</span>
            </li>
          ))}
        </ul>
      </div>

      <div className="flex justify-end space-x-3">
        <button className="flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 transition-colors">
          <Download className="w-4 h-4" />
          <span>导出PDF</span>
        </button>
        <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors">
          <Share2 className="w-4 h-4" />
          <span>分享报告</span>
        </button>
      </div>
    </div>
  );
};

export default HealthReports;