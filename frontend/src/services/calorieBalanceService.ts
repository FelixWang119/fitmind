/**
 * Calorie Balance API Service
 * Story 3.1: 热量平衡三栏展示
 */

import api from '@/api/client';

// Calorie Balance Types
export interface CalorieBalanceData {
  date: string;
  intake: number;      // 摄入热量 (from meals)
  bmr: number;          // 基础代谢 (calculated from profile)
  burn: number;         // 运动消耗 (from exercise_checkins)
  surplus: number;       // 热量盈余 = 摄入 - 基础代谢 - 运动消耗
  net: number;          // 净消耗 = 基础代谢 + 运动消耗 - 摄入
  progress: number;     // 进度百分比 (摄入/BMR * 100)
  target: number;       // 目标摄入 (= BMR)
}

export interface CalorieHistoryItem {
  date: string;
  intake: number;
  bmr: number;
  burn: number;
  surplus: number;
}

export interface CalorieBalanceHistory {
  history: CalorieHistoryItem[];
  days: number;
}

/**
 * 获取热量平衡数据
 * @param date 日期 (YYYY-MM-DD格式，默认今天)
 * @returns 热量平衡数据
 */
export const getCalorieBalance = async (date?: string): Promise<CalorieBalanceData> => {
  const params = date ? { date } : {};
  const response = await api.client.get('/calorie-balance', { params });
  return response.data;
};

/**
 * 获取热量平衡历史数据
 * @param days 历史天数 (默认7天，最大30天)
 * @returns 历史数据数组
 */
export const getCalorieBalanceHistory = async (days: number = 7): Promise<CalorieBalanceHistory> => {
  const response = await api.client.get('/calorie-balance/history', { params: { days } });
  return response.data;
};

/**
 * 格式化热量显示
 * @param value 热量值
 * @returns 格式化后的字符串
 */
export const formatCalories = (value: number): string => {
  return value.toLocaleString();
};

/**
 * 获取热量状态
 * @param surplus 热量盈余值
 * @returns 状态: 'deficit' | 'surplus' | 'neutral'
 */
export const getCalorieStatus = (surplus: number): 'deficit' | 'surplus' | 'neutral' => {
  if (surplus < 0) return 'deficit';
  if (surplus > 0) return 'surplus';
  return 'neutral';
};

/**
 * 获取热量状态文本
 * @param surplus 热量盈余值
 * @returns 状态描述文本
 */
export const getCalorieStatusText = (surplus: number): string => {
  if (surplus < 0) return '热量缺口';
  if (surplus > 0) return '热量盈余';
  return '收支平衡';
};

/**
 * 获取进度条颜色
 * @param progress 进度百分比
 * @returns 颜色类名
 */
export const getProgressColor = (progress: number): string => {
  if (progress < 70) return 'bg-green-500';
  if (progress <= 100) return 'bg-yellow-500';
  return 'bg-red-500';
};
