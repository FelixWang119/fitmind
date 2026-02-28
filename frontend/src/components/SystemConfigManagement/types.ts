// 类型定义
export interface ConfigOption {
  key: string;
  label: string;
  description: string;
  value: any;
  type: 'switch' | 'input' | 'select' | 'number' | 'slider';
  options?: { label: string; value: any }[];
  min?: number;
  max?: number;
  step?: number;
}
