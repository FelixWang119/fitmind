import { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { 
  Scale, Plus, TrendingUp, TrendingDown, Droplets,
  HeartPulse, Activity, Moon, Utensils, Dumbbell 
} from 'lucide-react';
import { api } from '../api/client';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface WeightRecord {
  id: number;
  date: string; // ISO date string
  weight: number; // in kg
  bodyFat?: number; // percentage
  notes?: string;
}

interface HealthMetrics {
  weight: WeightRecord[];
  sleep_hours?: number[];
  steps_count?: number[];
  heart_rate?: number[];
  calories_intake?: number[];
  blood_pressure_sys?: number[];
  blood_pressure_dia?: number[];
}

const WeightTrackingPage = () => {
  const [records, setRecords] = useState<WeightRecord[]>([]);
  const [metrics, setMetrics] = useState<HealthMetrics>({
    weight: []
  });
  const [loading, setLoading] = useState(true);
  const [newWeight, setNewWeight] = useState('');
  const [newBodyFat, setNewBodyFat] = useState('');
  const [newNotes, setNewNotes] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [currentDate, setCurrentDate] = useState<string>('');

  useEffect(() => {
    fetchWeightData();
    // Initialize date to today's date
    setCurrentDate(new Date().toISOString().split('T')[0]);
  }, []);

  const fetchWeightData = async () => {
    try {
      setLoading(true);
      // For now using the health records API to get weight data
      const data = await api.client.get('/health-data/records', {
        params: { limit: 100 } // Get the last 100 records
      });
      
      const weightRecords = data.data.records
        .filter((record: any) => record.weight)
        .map((record: any) => ({
          id: record.id,
          date: new Date(record.record_date).toISOString().split('T')[0],
          weight: record.weight / 1000, // converted from grams to kg
          bodyFat: record.body_fat_percentage,
          notes: record.notes
        }))
        .sort((a: WeightRecord, b: WeightRecord) => 
          new Date(a.date).getTime() - new Date(b.date).getTime()
        );

      setRecords(weightRecords);
      
      // Prepare metrics for chart
      const groupedData: HealthMetrics = {
        weight: weightRecords.map(r => r.weight),
      };
      setMetrics(groupedData);
    } catch (error) {
      console.error('Error fetching weight data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!newWeight || !currentDate) {
      return;
    }
    
    try {
      // Convert kg to grams as the backend stores in grams
      const weightInGrams = parseFloat(newWeight) * 1000;
      const bodyFatPercent = parseFloat(newBodyFat) || undefined;
      
      // Using health records API to save weight data in the standard format
      const response = await api.client.post('/health-data/records', {
        weight: weightInGrams,
        body_fat_percentage: bodyFatPercent,
        notes: newNotes,
        record_date: `${currentDate}T00:00:00Z` // ISO date format with zero time
      });
      
      // Refresh data
      fetchWeightData();
      setShowAddForm(false); // Hide form after submit
      
      // Reset form
      setNewWeight('');
      setNewBodyFat('');
      setNewNotes('');
    } catch (error) {
      console.error('Error adding weight record:', error);
    }
  };

  // Prepare chart data
  const chartData = {
    labels: records.map(record => record.date),
    datasets: [
      {
        label: '体重 (kg)',
        data: records.map(record => record.weight),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4,
      },
      ...(records.some(r => r.bodyFat !== undefined) ? [{
        label: '体脂 (%)',
        data: records.map(record => record.bodyFat ?? null),
        borderColor: 'rgb(16, 185, 129)',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        fill: true,
        tension: 0.4,
        yAxisID: 'y1',
      }] : []),
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: '体重趋势图',
      },
    },
    scales: {
      y: {
        beginAtZero: false,
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
        },
      },
      ...(records.some(r => r.bodyFat !== undefined) ? {
        y1: {
          beginAtZero: false,
          position: 'right' as const,
          grid: {
            drawOnChartArea: false,
          },
        }
      } : {}),
    },
  };

  // Calculate stats
  const latestRecord = records.length > 0 ? records[records.length - 1] : null;
  const previousRecord = records.length > 1 ? records[records.length - 2] : null;
  const weightChange = latestRecord && previousRecord 
    ? latestRecord.weight - previousRecord.weight
    : 0;

  return (
    <div className="max-w-6xl mx-auto space-y-6 p-4">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">体重记录与追踪</h1>
          <p className="text-gray-600 mt-1">记录体重变化，追踪健康进度</p>
        </div>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="flex items-center justify-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-xl hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-5 h-5" />
          <span>{showAddForm ? '取消' : '添加记录'}</span>
        </button>
      </div>

      {/* Add Record Form */}
      {showAddForm && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">添加体重记录</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="date" className="block text-sm font-medium text-gray-700 mb-1">
                  日期
                </label>
                <input
                  type="date"
                  id="date"
                  value={currentDate}
                  onChange={(e) => setCurrentDate(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
              
              <div>
                <label htmlFor="weight" className="block text-sm font-medium text-gray-700 mb-1">
                  体重 (kg)
                  <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  id="weight"
                  value={newWeight}
                  onChange={(e) => setNewWeight(e.target.value)}
                  step="0.01"
                  min="10"
                  max="500"
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-blue-500 focus:border-blue-500"
                  placeholder="例如: 70.5"
                  required
                />
              </div>
              
              <div>
                <label htmlFor="bodyFat" className="block text-sm font-medium text-gray-700 mb-1">
                  体脂 (%)
                </label>
                <input
                  type="number"
                  id="bodyFat"
                  value={newBodyFat}
                  onChange={(e) => setNewBodyFat(e.target.value)}
                  step="0.1"
                  min="3"
                  max="50"
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-blue-500 focus:border-blue-500"
                  placeholder="例如: 22.5"
                />
              </div>
              
              <div>
                <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-1">
                  备注
                </label>
                <input
                  type="text"
                  id="notes"
                  value={newNotes}
                  onChange={(e) => setNewNotes(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-blue-500 focus:border-blue-500"
                  placeholder="今日感受或特殊情况"
                />
              </div>
            </div>
            
            <div className="flex justify-end">
              <button
                type="submit"
                className="px-6 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors"
              >
                保存记录
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Dashboard Cards */}
      {latestRecord && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-2xl p-5 text-white">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                  <Scale className="w-6 h-6" />
                </div>
                <div>
                  <p className="text-blue-100 text-sm">当前体重</p>
                  <p className="text-2xl font-bold">{latestRecord.weight.toFixed(1)}<span className="text-lg">kg</span></p>
                </div>
              </div>
            </div>
          </div>

          <div className={`bg-gradient-to-r ${
            weightChange > 0 ? 'from-amber-600 to-amber-700' : weightChange < 0 ? 'from-emerald-600 to-emerald-700' : 'from-gray-600 to-gray-700'
          } rounded-2xl p-5 text-white`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                  {weightChange > 0 ? <TrendingUp className="w-6 h-6" /> : weightChange < 0 ? <TrendingDown className="w-6 h-6" /> : <Scale className="w-6 h-6" />}
                </div>
                <div>
                  <p className="text-blue-100 text-sm">对比上次</p>
                  <p className="text-2xl font-bold">
                    {weightChange > 0 ? '+' : ''}{weightChange.toFixed(1)}<span className="text-lg">kg</span>
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-r from-teal-600 to-teal-700 rounded-2xl p-5 text-white">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                  <Activity className="w-6 h-6" />
                </div>
                <div>
                  <p className="text-blue-100 text-sm">记录天数</p>
                  <p className="text-2xl font-bold">{records.length}<span className="text-lg">天</span></p>
                </div>
              </div>
            </div>
          </div>

          {latestRecord.bodyFat !== undefined && (
            <div className="bg-gradient-to-r from-violet-600 to-violet-700 rounded-2xl p-5 text-white">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                    <Droplets className="w-6 h-6" />
                  </div>
                  <div>
                    <p className="text-blue-100 text-sm">体脂百分比</p>
                    <p className="text-2xl font-bold">{latestRecord.bodyFat.toFixed(1)}<span className="text-lg">%</span></p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Weight Trend Chart */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">体重趋势图</h2>
        <div className="h-80">
          {loading ? (
            <div className="h-full flex items-center justify-center">
              <p className="text-gray-500">加载中...</p>
            </div>
          ) : records.length > 0 ? (
            <Line data={chartData} options={chartOptions} />
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-gray-400">
              <Scale className="w-16 h-16 mb-4" />
              <p>暂无体重记录，添加第一条记录开始追踪吧！</p>
            </div>
          )}
        </div>
      </div>

      {/* Weight History List */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">体重记录历史</h2>
        {loading ? (
          <p className="text-gray-500">加载中...</p>
        ) : records.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">日期</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">体重 (kg)</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">体脂 (%)</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">备注</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {[...records].reverse().map((record) => (
                  <tr key={record.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{record.date}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{record.weight.toFixed(1)}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{record.bodyFat ? record.bodyFat.toFixed(1) + '%' : '-'}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{record.notes || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-12 text-gray-400">
            <Scale className="w-12 h-12 mb-3" />
            <p>暂无记录数据</p>
            <p className="text-sm mt-1">请添加第一条体重记录</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default WeightTrackingPage;