/**
 * 自动保存工具
 * 使用 localStorage 保存用户进度
 */

const STORAGE_KEY = 'onboarding_progress';
const EXPIRY_DAYS = 7; // 7 天后过期

export interface OnboardingProgress {
  step: number;
  data: any;
  timestamp: number;
}

/**
 * 保存进度到 localStorage
 */
export const saveProgress = (step: number, data: any): void => {
  try {
    const progress: OnboardingProgress = {
      step,
      data,
      timestamp: Date.now(),
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(progress));
  } catch (error) {
    console.warn('Failed to save onboarding progress:', error);
  }
};

/**
 * 从 localStorage 加载进度
 */
export const loadProgress = (): OnboardingProgress | null => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (!saved) return null;
    
    const progress: OnboardingProgress = JSON.parse(saved);
    
    // 检查是否过期
    const expiryTime = EXPIRY_DAYS * 24 * 60 * 60 * 1000;
    const isExpired = Date.now() - progress.timestamp > expiryTime;
    
    if (isExpired) {
      clearProgress();
      return null;
    }
    
    return progress;
  } catch (error) {
    console.warn('Failed to load onboarding progress:', error);
    return null;
  }
};

/**
 * 清除保存的进度
 */
export const clearProgress = (): void => {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (error) {
    console.warn('Failed to clear onboarding progress:', error);
  }
};

/**
 * 检查是否有保存的进度
 */

/**
 * P1-5: 清理过期进度
 */
export const cleanupExpiredProgress = (): void => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (!saved) return;
    
    const progress: OnboardingProgress = JSON.parse(saved);
    const expiryTime = EXPIRY_DAYS * 24 * 60 * 60 * 1000;
    
    if (Date.now() - progress.timestamp > expiryTime) {
      clearProgress();
      console.log('Cleared expired onboarding progress');
    }
  } catch (error) {
    console.warn('Failed to cleanup expired progress:', error);
  }
};

export const hasSavedProgress = (): boolean => {
  return loadProgress() !== null;
};

/**
 * 获取友好的恢复提示
 */
export const getRestoreMessage = (): string | null => {
  const progress = loadProgress();
  if (!progress) return null;
  
  const stepNames = [
    '欢迎页',
    '基本信息',
    '目标设定',
    '生活方式',
    '健康信息',
    '完成',
  ];
  
  const stepName = stepNames[progress.step] || '未知步骤';
  return `检测到您之前填写到"${stepName}"，是否继续？`;
};
