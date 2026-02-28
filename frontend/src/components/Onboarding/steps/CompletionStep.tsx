import React from 'react';
import { Button, Typography, Result } from 'antd';
import { CheckCircleOutlined } from '@ant-design/icons';

const { Title, Paragraph } = Typography;

interface CompletionStepProps {
  onComplete: () => void;
}

/**
 * Step 5: 完成页
 * 庆祝完成并跳转到主页
 */
const CompletionStep: React.FC<CompletionStepProps> = ({ onComplete }) => {
  return (
    <div className="text-center py-8">
      <Result
        icon={<CheckCircleOutlined className="text-green-500 text-6xl" />}
        title="太棒了！🎉"
        subTitle="您已完成个人信息设置，让我们开始健康旅程吧！"
        extra={[
          <Button 
            type="primary" 
            size="large" 
            key="start"
            onClick={onComplete}
            className="px-8"
          >
            开始我的健康旅程
          </Button>,
        ]}
      />
      
      <div className="mt-8 p-6 bg-gradient-to-r from-blue-50 to-green-50 rounded-lg">
        <Title level={4} className="mb-2">接下来您可以：</Title>
        <Paragraph className="text-gray-600">
          📊 查看个性化仪表板<br/>
          🎯 开始追踪您的第一个目标<br/>
          🤖 与 AI 营养师对话<br/>
          🏆 解锁您的第一个成就
        </Paragraph>
      </div>
    </div>
  );
};

export default CompletionStep;
