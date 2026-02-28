import React from 'react';
import { Steps } from 'antd';

interface StepIndicatorProps {
  current: number;
  total: number;
}

/**
 * Onboarding 步骤指示器
 * 显示当前步骤位置
 */
const StepIndicator: React.FC<StepIndicatorProps> = ({ current, total }) => {
  // 创建步骤标题
  const steps = [
    { title: '欢迎', description: '开始旅程' },
    { title: '基本信息', description: '个人资料' },
    { title: '目标设定', description: '健康目标' },
    { title: '生活方式', description: '生活习惯' },
    { title: '健康信息', description: '可选填写' },
    { title: '完成', description: '开始旅程' },
  ];

  return (
    <div className="w-full mb-8">
      <Steps 
        current={current} 
        items={steps.map((step) => ({
          title: step.title,
          description: step.description,
        }))}
        size="small"
        responsive={false}
      />
    </div>
  );
};

export default StepIndicator;
