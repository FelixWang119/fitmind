import React from 'react';
import { Progress } from 'antd';

interface ProgressBarProps {
  current: number;
  total: number;
}

/**
 * Onboarding 进度条组件
 * 显示当前完成进度百分比
 */
const ProgressBar: React.FC<ProgressBarProps> = ({ current, total }) => {
  // 计算进度百分比 (不包括欢迎页)
  const progressStep = Math.max(0, current);
  const percent = Math.round((progressStep / total) * 100);

  return (
    <div className="w-full mb-6">
      <Progress 
        percent={percent} 
        strokeColor={{
          '0%': '#108ee9',
          '100%': '#87d068',
        }}
        showInfo={false}
        size="small"
      />
      <div className="text-center text-gray-500 text-sm mt-2">
        进度：{progressStep}/{total}
      </div>
    </div>
  );
};

export default ProgressBar;
