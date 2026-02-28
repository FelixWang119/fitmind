// 类型定义
export interface NotificationTemplate {
  id: string;
  name: string;
  description: string;
  category: 'exercise' | 'nutrition' | 'weight' | 'community' | 'system';
  type: 'daily' | 'weekly' | 'reminder' | 'achievement' | 'alert';
  subject: string;
  content: string;
  variables: string[];
  isDefault: boolean;
  isActive: boolean;
  usageCount: number;
  lastModified: string;
}

export interface NotificationHistory {
  id: string;
  templateId: string;
  templateName: string;
  sentAt: string;
  recipients: number;
  successRate: number;
  status: 'success' | 'partial' | 'failed';
}
