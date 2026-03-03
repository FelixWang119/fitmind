/**
 * 每日科普 API 模块
 * Story 9.2: Dashboard 科普卡片组件
 */

import api from './client';

export interface DailyTip {
  id: number;
  date: string;
  topic: string;
  title: string;
  summary: string;
  content: string;
  disclaimer: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

/**
 * 获取当日科普内容
 */
export async function getTodayTip(): Promise<DailyTip> {
  const response = await api.client.get<DailyTip>('/daily-tips/today');
  return response.data;
}

/**
 * 获取科普内容列表（历史记录）
 */
export async function getTipList(params?: {
  skip?: number;
  limit?: number;
  topic?: string;
}): Promise<{ total: number; items: DailyTip[] }> {
  const response = await api.client.get<{ total: number; items: DailyTip[] }>(
    '/daily-tips',
    { params }
  );
  return response.data;
}

/**
 * 获取特定科普内容
 */
export async function getTipById(tipId: number): Promise<DailyTip> {
  const response = await api.client.get<DailyTip>(`/daily-tips/${tipId}`);
  return response.data;
}

export default {
  getTodayTip,
  getTipList,
  getTipById,
};
