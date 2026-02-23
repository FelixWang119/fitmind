import { useState } from 'react';
import { Scale, Plus, TrendingDown } from 'lucide-react';

export default function HealthTracker() {
  const [showAddModal, setShowAddModal] = useState(false);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">健康记录</h1>
          <p className="text-gray-600 mt-1">追踪体重和健康指标变化</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-xl hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-5 h-5" />
          <span>记录体重</span>
        </button>
      </div>

      <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-2xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center">
              <Scale className="w-8 h-8" />
            </div>
            <div>
              <p className="text-blue-100">当前体重</p>
              <p className="text-4xl font-bold">70.5 <span className="text-xl">kg</span></p>
            </div>
          </div>
          
          <div className="text-right">
            <div className="flex items-center justify-end space-x-2">
              <TrendingDown className="w-5 h-5 text-green-300" />
              <span className="text-green-300 font-semibold">-2.3 kg</span>
            </div>
            <p className="text-blue-100 text-sm">较上月</p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">体重趋势</h2>
        <div className="h-64 bg-gray-50 rounded-xl flex items-center justify-center">
          <p className="text-gray-400">体重趋势图表将在这里显示</p>
        </div>
      </div>
    </div>
  );
}

export function EmotionalSupport() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">情感支持</h1>
        <p className="text-gray-600 mt-1">关注心理健康，获得情感支持</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gradient-to-r from-purple-600 to-purple-700 rounded-2xl p-6 text-white">
          <h3 className="text-lg font-semibold mb-2">今日情感签到</h3>
          <p className="text-purple-100 mb-4">记录你今天的感受，获得个性化支持</p>
          <button className="bg-white text-purple-600 px-4 py-2 rounded-xl font-medium hover:bg-purple-50 transition-colors">
            开始签到
          </button>
        </div>

        <div className="bg-gradient-to-r from-teal-600 to-teal-700 rounded-2xl p-6 text-white">
          <h3 className="text-lg font-semibold mb-2">正念练习</h3>
          <p className="text-teal-100 mb-4">每天10分钟正念练习，减轻压力</p>
          <button className="bg-white text-teal-600 px-4 py-2 rounded-xl font-medium hover:bg-teal-50 transition-colors">
            开始练习
          </button>
        </div>
      </div>
    </div>
  );
}

export function Gamification() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">成就中心</h1>
        <p className="text-gray-600 mt-1">坚持健康习惯，解锁徽章和奖励</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {['🥉', '🥈', '🥇', '🏆'].map((emoji, index) => (
          <div key={index} className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 text-center">
            <div className="text-4xl mb-2">{emoji}</div>
            <p className="font-medium text-gray-900">徽章 {index + 1}</p>
            <p className="text-sm text-gray-500">描述</p>
          </div>
        ))}
      </div>
    </div>
  );
}