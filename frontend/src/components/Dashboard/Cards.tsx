import React from 'react';
import { TrendingUp, Activity, Heart, Droplets, Dumbbell, Timer, CheckCircle, ChevronRight } from 'lucide-react';

interface StatCardProps {
  icon: React.ReactNode;
  title: string;
  value: string | number;
  children?: React.ReactNode;
  infoText?: string;
}

export const StatCard: React.FC<StatCardProps> = ({ icon, title, value, children, infoText }) => (
  <div className="bg-white rounded-xl shadow p-6">
    <div className="flex items-center mb-4">
      <div className="bg-green-100 p-3 rounded-full mr-4">
        {icon}
      </div>
      <div className="flex items-start">
        <div>
          <p className="text-sm text-gray-500">{title}</p>
          <p className="text-2xl font-bold text-gray-900">
            {value}
          </p>
        </div>
        {children}
      </div>
    </div>
  </div>
);

interface ExerciseStatProps {
  icon: React.ReactNode;
  value: string | number;
  unit: string;
  label: string;
  infoText: string;
}

export const ExerciseStat: React.FC<ExerciseStatProps> = ({ 
  icon, 
  value, 
  unit, 
  label, 
  infoText 
}) => (
  <div className="text-center relative">
    <div className="flex items-center justify-center mb-1">
      {icon}
    </div>
    <div className="text-lg font-bold text-orange-600">
      {value}
    </div>
    <div className="text-xs text-gray-500">{unit}</div>
    <div className="absolute top-0 right-0 transform translate-x-1/2 -translate-y-1/2 group">
      <button className="text-gray-300 hover:text-gray-500 focus:outline-none">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </button>
      <div className="absolute right-0 top-full mt-2 w-48 p-3 bg-white border border-gray-200 rounded-lg shadow-lg z-10 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300">
        <p className="text-xs text-gray-600">
          <strong>{label}来源：</strong><br/>
          {infoText}
        </p>
      </div>
    </div>
  </div>
);

// 热量卡片组件
export const CalorieCard: React.FC<{ today_calories?: number; intake_calories?: number; basal_metabolism?: number; exercise_calories_burned?: number }> = ({ today_calories, intake_calories, basal_metabolism, exercise_calories_burned }) => (
  <StatCard
    icon={<TrendingUp className="h-6 w-6 text-green-600" />}
    title="今日热量"
    value={`${today_calories || 0} 卡`}
  >
    {/* 提示按钮 */}
    <div className="relative ml-2 group">
      <button className="text-gray-400 hover:text-gray-600 focus:outline-none">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </button>
      {/* 浮窗 - 现在显示具体数值 */}
      <div className="absolute left-0 top-full mt-2 w-72 p-4 bg-white border border-gray-200 rounded-lg shadow-lg z-10 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300">
        <p className="text-xs text-gray-600">
          <strong>热量盈余计算：</strong><br/>
          热量盈余 = 摄入热量 - 基础代谢 - 运动消耗<br/><br/>
          <span className="font-medium">摄入热量：</span>{intake_calories || 0} kcal（来自饮食记录）<br/>
          <span className="font-medium">基础代谢：</span>{basal_metabolism || 2000} kcal（目标值）<br/>
          <span className="font-medium">运动消耗：</span>{exercise_calories_burned || 0} kcal（来自运动记录）<br/><br/>
          <span className="font-medium">计算过程：</span> {intake_calories || 0} - {basal_metabolism || 2000} - {exercise_calories_burned || 0} = {today_calories || 0}
        </p>
      </div>
    </div>
  </StatCard>
);

// 步数卡片组件
export const StepCountCard: React.FC<{ daily_step_count?: number }> = ({ daily_step_count }) => (
  <StatCard
    icon={<Activity className="h-6 w-6 text-blue-600" />}
    title="今日步数"
    value={`${daily_step_count?.toLocaleString() || 0} 步`}
  >
    {/* 步数提示按钮 */}
    <div className="relative ml-2 group">
      <button className="text-gray-400 hover:text-gray-600 focus:outline-none">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </button>
      {/* 步数浮窗 */}
      <div className="absolute left-0 top-full mt-2 w-64 p-4 bg-white border border-gray-200 rounded-lg shadow-lg z-10 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300">
        <p className="text-xs text-gray-600">
          <strong>步数来源：</strong><br/>
          步数数据来自您设备上的计步器<br/>
          或手动输入的步数数据
        </p>
      </div>
    </div>
  </StatCard>
);

// 睡眠卡片组件
export const SleepCard: React.FC<{ sleep_hours?: number }> = ({ sleep_hours }) => (
  <StatCard
    icon={<Heart className="h-6 w-6 text-purple-600" />}
    title="睡眠时长"
    value={`${sleep_hours || 0} 小时`}
  >
    {/* 睡眠提示按钮 */}
    <div className="relative ml-2 group">
      <button className="text-gray-400 hover:text-gray-600 focus:outline-none">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </button>
      {/* 睡眠浮窗 */}
      <div className="absolute left-0 top-full mt-2 w-64 p-4 bg-white border border-gray-200 rounded-lg shadow-lg z-10 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300">
        <p className="text-xs text-gray-600">
          <strong>睡眠时长来源：</strong><br/>
          睡眠数据来自您的设备或<br/>
          手动输入的睡眠记录
        </p>
      </div>
    </div>
  </StatCard>
);

// 水分卡片组件
export const WaterIntakeCard: React.FC<{ water_intake_ml?: number }> = ({ water_intake_ml }) => (
  <StatCard
    icon={<Droplets className="h-6 w-6 text-cyan-600" />}
    title="水分摄入"
    value={`${water_intake_ml || 0} ml`}
  >
    {/* 水分提示按钮 */}
    <div className="relative ml-2 group">
      <button className="text-gray-400 hover:text-gray-600 focus:outline-none">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </button>
      {/* 水分浮窗 */}
      <div className="absolute left-0 top-full mt-2 w-64 p-4 bg-white border border-gray-200 rounded-lg shadow-lg z-10 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300">
        <p className="text-xs text-gray-600">
          <strong>水分摄入来源：</strong><br/>
          水分记录来自您手动记录<br/>
          的饮水活动
        </p>
      </div>
    </div>
  </StatCard>
);
