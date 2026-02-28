// Design System Export
// 导出所有P2-P3模块组件

// P2 模块
export { GamificationSystem } from './GamificationSystem';
export { ExerciseTypeManagement } from './ExerciseTypeManagement';
export { NotificationTemplateManagement } from './NotificationTemplateManagement';
export { ScientificQuantitativeDisplay } from './ScientificQuantitativeDisplay';
export { SystemConfigManagement } from './SystemConfigManagement';

// P3 模块
export { ExerciseAchievementExtended } from './ExerciseAchievementExtended';
export { CommunityFeatures } from './CommunityFeatures';
export { SmartHardwareIntegration } from './SmartHardwareIntegration';

// 导出类型定义
export type { GamificationStore } from './gamificationStore';
export type { ExerciseType, MovementStatistics } from './ExerciseTypeManagement/types';
export type { NotificationTemplate, NotificationHistory } from './NotificationTemplateManagement/types';
export type { HealthScoreData, TrendData, EvidenceItem } from './ScientificQuantitativeDisplay/types';
export type { ConfigOption } from './SystemConfigManagement/types';
export type { Achievement } from './ExerciseAchievementExtended/types';
