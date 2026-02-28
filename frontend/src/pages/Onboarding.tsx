import React, { useState, useEffect } from 'react';
import { Card, message, Alert, Button, Modal } from 'antd';
import { ExclamationCircleOutlined } from '@ant-design/icons';
import ProgressBar from './ProgressBar';
import StepIndicator from './StepIndicator';
import WelcomeStep from './components/Onboarding/steps/WelcomeStep';
import BasicInfoStep from './components/Onboarding/steps/BasicInfoStep';
import CompletionStep from './components/Onboarding/steps/CompletionStep';
import { getEncouragement, getCompletionEncouragement } from './components/Onboarding/utils/encouragement';
import { validateWithFriendlyMessages } from './components/Onboarding/utils/friendlyErrors';
import { saveProgress, loadProgress, clearProgress, hasSavedProgress, getRestoreMessage } from './components/Onboarding/utils/autoSave';
import api from '@/api/client';

/**
 * Onboarding 引导流程主组件
 * 5 步引导用户完成个人档案设置
 * 包含防反感设计：鼓励文案、自动保存、友好错误提示
 */
const Onboarding: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [encouragement, setEncouragement] = useState('');
  const [formData, setFormData] = useState<any>({
    age: undefined,
    gender: undefined,
    height: undefined,
    initial_weight: undefined,
    target_weight: undefined,
    activity_level: undefined,
    dietary_preferences: [],
    // 新增字段
    current_weight: undefined,
    waist_circumference: undefined,
    hip_circumference: undefined,
    body_fat_percentage: undefined,
    muscle_mass: undefined,
    bone_density: undefined,
    metabolism_rate: undefined,
    health_conditions: {},
    medications: {},
    allergies: [],
    sleep_quality: undefined,
  });

  // 初始化时检查是否有保存的进度
  useEffect(() => {
    const savedProgress = loadProgress();
    if (savedProgress && savedProgress.step > 0 && savedProgress.step < 5) {
      Modal.confirm({
        title: '发现未完成的进度',
        icon: <ExclamationCircleOutlined />,
        content: getRestoreMessage(),
        okText: '继续',
        cancelText: '重新开始',
        onOk: () => {
          setCurrentStep(savedProgress.step);
          setFormData(savedProgress.data);
          setEncouragement('继续加油！我们接着来～💪');
        },
        onCancel: () => {
          clearProgress();
          setCurrentStep(0);
        },
      });
    }
  }, []);

  // 自动保存进度
  useEffect(() => {
    if (currentStep > 0 && currentStep < 5) {
      saveProgress(currentStep, formData);
    } else if (currentStep === 5) {
      // 完成后清除保存的进度
      clearProgress();
    }
  }, [currentStep, formData]);

  // 页面关闭前提醒
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (currentStep > 0 && currentStep < 5) {
        e.preventDefault();
        e.returnValue = '您的进度已自动保存，下次可以继续';
      }
    };
    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [currentStep]);

  // 更新鼓励文案
  useEffect(() => {
    setEncouragement(getEncouragement(currentStep));
  }, [currentStep]);

  const handleNext = () => {
    setCurrentStep(currentStep + 1);
    if (currentStep + 1 <= 5) {
      setEncouragement(getCompletionEncouragement(currentStep));
    }
  };

  const handleBack = () => {
    setCurrentStep(currentStep - 1);
  };

  const handleDataChange = (data: any) => {
    setFormData(data);
  };

  const handleSubmit = async () => {
    // 友好验证
    const errors = validateWithFriendlyMessages(formData);
    if (errors.length > 0) {
      message.error(errors[0].message);
      return;
    }

    try {
      // 单位转换：kg → g
      const apiData = {
        ...formData,
        initial_weight: formData.initial_weight * 1000,
        target_weight: formData.target_weight * 1000,
        current_weight: formData.current_weight ? formData.current_weight * 1000 : null,
        muscle_mass: formData.muscle_mass ? formData.muscle_mass * 1000 : null,
      };

      // 调用 API 保存数据
      await api.put('/users/profile', apiData);
      
      message.success('档案设置成功！🎉');
      setCurrentStep(currentStep + 1);
      clearProgress(); // 完成后清除
    } catch (error: any) {
      message.error(`保存失败：${error.message}`);
    }
  };

  const handleComplete = () => {
    // 跳转到主页
    window.location.href = '/dashboard';
  };

  const renderStep = () => {
    switch (currentStep) {
      case 0:
        return <WelcomeStep onNext={handleNext} />;
      
      case 1:
        return (
          <BasicInfoStep
            data={formData}
            onChange={handleDataChange}
            onNext={handleNext}
            onBack={handleBack}
          />
        );
      
      case 2:
        // Step 2: 目标设定 (简化版)
        return (
          <div className="py-4 text-center">
            <h3 className="text-xl mb-4">目标设定</h3>
            <p className="text-gray-600 mb-4">此步骤将在后续版本实现</p>
            <button onClick={handleNext} className="btn-primary">跳过</button>
          </div>
        );
      
      case 3:
        // Step 3: 生活方式 (简化版)
        return (
          <div className="py-4 text-center">
            <h3 className="text-xl mb-4">生活方式</h3>
            <p className="text-gray-600 mb-4">此步骤将在后续版本实现</p>
            <button onClick={handleNext} className="btn-primary">跳过</button>
          </div>
        );
      
      case 4:
        // Step 4: 健康信息 (选填，简化版)
        return (
          <div className="py-4 text-center">
            <h3 className="text-xl mb-4">健康信息</h3>
            <Alert
              message="选填提示"
              description="这些信息可以帮助我们提供更精准的建议，但也可以跳过，稍后填写。"
              type="info"
              showIcon
              className="mb-4"
            />
            <div className="flex justify-center gap-4 mt-6">
              <button onClick={handleNext} className="btn-secondary">跳过此步</button>
            </div>
          </div>
        );
      
      case 5:
        return <CompletionStep onComplete={handleComplete} />;
      
      default:
        return <div>未知步骤</div>;
    }
  };

  return (
    <div className="max-w-3xl mx-auto py-8 px-4">
      <Card className="shadow-lg">
        {currentStep > 0 && currentStep < 5 && (
          <>
            <ProgressBar current={currentStep} total={5} />
            <StepIndicator current={currentStep} total={5} />
            
            {/* 鼓励文案 */}
            {encouragement && (
              <Alert
                message={encouragement}
                type="success"
                showIcon
                className="mb-6"
                closable
              />
            )}
          </>
        )}
        
        {renderStep()}
        
        {currentStep === 4 && (
          <div className="flex justify-center mt-8">
            <button 
              onClick={handleSubmit} 
              className="btn-primary px-8"
            >
              完成设置
            </button>
          </div>
        )}
      </Card>
    </div>
  );
};

export default Onboarding;
