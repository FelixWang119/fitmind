// 类型定义
export interface HealthScoreData {
  overall: number;
  exercise: number;
  nutrition: number;
  sleep: number;
  weight: number;
}

export interface TrendData {
  date: string;
  value: number;
  target: number;
  category: string;
}

export interface EvidenceItem {
  id: string;
  title: string;
  description: string;
  evidenceLevel: 'A' | 'B' | 'C';
  source: string;
  date: string;
}
