import React from 'react';
import { Button, Typography, Space } from 'antd';
import { Rocket, Heart, Target, Users } from '@ant-design/icons';

const { Title, Paragraph } = Typography;

interface WelcomeStepProps {
  onNext: () => void;
}

/**
 * Step 0: 欢迎页
 * 介绍 Onboarding 流程和价值
 */
const WelcomeStep: React.FC<WelcomeStepProps> = ({ onNext }) => {
  return (
    <div className="text-center py-8">
      <div className="mb-6">
        <Rocket className="text-primary text-6xl" />
      </div>
      
      <Title level={2} className="mb-4">
        欢迎来到体重管理 AI 助手！🎉
      </Title>
      
      <Paragraph className="text-lg text-gray-600 mb-8">
        让我们花 5 分钟时间，为您定制专属的健康管理计划
      </Paragraph>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8 text-left">
        <div className="p-4 bg-blue-50 rounded-lg">
          <Space>
            <Heart className="text-red-500 text-xl" />
            <div>
              <strong>个性化建议</strong>
              <p className="text-sm text-gray-600">AI 根据您的身体数据提供定制建议</p>
            </div>
          </Space>
        </div>

        <div className="p-4 bg-green-50 rounded-lg">
          <Space>
            <Target className="text-green-500 text-xl" />
            <div>
              <strong>智能目标追踪</strong>
              <p className="text-sm text-gray-600">实时进度监控，AI 反馈调整</p>
            </div>
          </Space>
        </div>

        <div className="p-4 bg-purple-50 rounded-lg">
          <Space>
            <Users className="text-purple-500 text-xl" />
            <div>
              <strong>专业团队支持</strong>
              <p className="text-sm text-gray-600">营养师 + 行为教练全程陪伴</p>
            </div>
          </Space>
        </div>

        <div className="p-4 bg-orange-50 rounded-lg">
          <Space>
            <Heart className="text-orange-500 text-xl" />
            <div>
              <strong>游戏化激励</strong>
              <p className="text-sm text-gray-600">成就系统让坚持更有趣</p>
            </div>
          </Space>
        </div>
      </div>

      <div className="bg-gray-100 p-4 rounded-lg mb-6">
        <p className="text-sm text-gray-600">
          ⏱️ 预计耗时：<strong>5 分钟</strong> | 共 <strong>5 步</strong> | 可随时保存退出
        </p>
      </div>

      <Button 
        type="primary" 
        size="large"
        onClick={onNext}
        className="px-8"
      >
        开始我的健康旅程
      </Button>
    </div>
  );
};

export default WelcomeStep;
